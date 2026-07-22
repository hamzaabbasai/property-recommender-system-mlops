from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import pandas as pd

from app.config import PROJECT_ROOT
from app.data.ingest import load_interactions, load_properties
from app.features.user_features import user_preferences_from_history
from app.ranking.baseline_ranker import BaselineRanker
from app.ranking.lgbm_ranker import LearnedRanker
from app.retrieval.hybrid_retriever import HybridRetriever


def _add_missing_positives(
    candidates: pd.DataFrame,
    properties: pd.DataFrame,
    positive_ids: set[str],
    retriever: HybridRetriever,
    user_id: str,
) -> pd.DataFrame:
    present_ids = set(candidates["property_id"].astype(str))
    missing_ids = positive_ids - present_ids
    extra = properties.loc[properties["property_id"].astype(str).isin(missing_ids)].copy()

    candidate_ids = set(candidates["property_id"].astype(str)) | missing_ids
    if not (candidate_ids - positive_ids):
        negatives = properties.loc[
            ~properties["property_id"].astype(str).isin(positive_ids)
        ].head(3)
        extra = pd.concat([extra, negatives], ignore_index=True)

    if extra.empty:
        return candidates
    extra["semantic_score"] = 0.0
    extra["collaborative_score"] = extra["property_id"].astype(str).map(
        retriever.collaborative.scores(user_id, extra["property_id"].astype(str).tolist())
    )
    extra["retrieval_score"] = extra["collaborative_score"] * 0.2
    return pd.concat([candidates, extra], ignore_index=True).drop_duplicates("property_id")


def build_training_data(
    properties_path: Path | None = None,
    interactions_path: Path | None = None,
    max_users: int = 1500,
    candidate_count: int = 40,
    min_user_interactions: int = 2,
    properties_frame: pd.DataFrame | None = None,
    interactions_frame: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, list[int], list[int]]:
    properties = (
        properties_frame.copy()
        if properties_frame is not None
        else load_properties(properties_path)
    )
    interactions = (
        interactions_frame.copy()
        if interactions_frame is not None
        else load_interactions(interactions_path)
    )
    retriever = HybridRetriever(properties, interactions)
    baseline = BaselineRanker()

    user_counts = interactions.groupby("user_id").size()
    user_ids = user_counts.loc[
        user_counts >= min_user_interactions
    ].index.astype(str).tolist()
    if len(user_ids) > max_users:
        user_ids = pd.Series(user_ids).sample(max_users, random_state=42).tolist()

    groups: list[int] = []
    rows: list[pd.DataFrame] = []
    labels: list[int] = []

    for user_id in user_ids:
        user_history = interactions.loc[interactions["user_id"].astype(str) == user_id]
        positive_ids = set(user_history["property_id"].astype(str))
        preferences = user_preferences_from_history(properties, interactions, user_id)
        preferences["query"] = " ".join(
            ["Berlin", *preferences.get("property_types", []), *preferences.get("amenities", [])]
        )

        candidates = retriever.retrieve(
            preferences,
            user_id=user_id,
            candidate_count=candidate_count,
            exclude_seen=False,
        )
        candidates = _add_missing_positives(
            candidates, properties, positive_ids, retriever, user_id
        )
        if candidates.empty:
            continue

        features = baseline.add_features(candidates, preferences)
        group_labels = [
            int(property_id in positive_ids)
            for property_id in features["property_id"].astype(str)
        ]
        if len(set(group_labels)) < 2:
            continue

        rows.append(features)
        labels.extend(group_labels)
        groups.append(len(features))

    if not rows:
        raise RuntimeError("No ranking training data was created.")
    return pd.concat(rows, ignore_index=True), labels, groups


def train_ranker(max_users: int = 1500) -> str:
    frame, labels, groups = build_training_data(max_users=max_users)
    ranker = LearnedRanker()
    mlflow.set_experiment("berlin-property-ranking")
    with mlflow.start_run():
        ranker.fit(frame, labels, groups)
        mlflow.log_params(
            {
                "groups": len(groups),
                "rows": len(frame),
                "positive_rate": round(sum(labels) / len(labels), 4),
                "model": "lightgbm-lambdarank",
                "feedback": "inside-airbnb-reviews",
            }
        )
        path = PROJECT_ROOT / "artifacts" / "models" / "lgbm_ranker.joblib"
        ranker.save(path)
        mlflow.log_artifact(str(path), artifact_path="model")
    return str(path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare data and train the ranking model.")
    parser.add_argument("--max-users", type=int, default=1500)
    parser.add_argument("--skip-prepare", action="store_true")
    args = parser.parse_args()

    if not args.skip_prepare:
        from app.pipelines.prepare_data import prepare_data

        prepare_data()
    print(train_ranker(max_users=args.max_users))


if __name__ == "__main__":
    main()
