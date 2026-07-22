from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from app.data.ingest import load_interactions, load_properties
from app.data.split import temporal_split
from app.evaluation.offline_evaluation import evaluate_user_rankings
from app.evaluation.ranking_metrics import catalog_coverage
from app.features.user_features import user_preferences_from_history
from app.pipelines.train_ranker import build_training_data
from app.ranking.lgbm_ranker import LearnedRanker
from app.recommendation.recommender import PropertyRecommender


def _predict(
    recommender: PropertyRecommender,
    properties: pd.DataFrame,
    train: pd.DataFrame,
    user_ids: list[str],
    k: int,
) -> dict[str, list[str]]:
    predictions: dict[str, list[str]] = {}
    for user_id in user_ids:
        preferences = user_preferences_from_history(properties, train, user_id)
        preferences["bedrooms"] = None
        preferences["max_budget"] = None
        preferences["property_types"] = []
        preferences["query"] = " ".join(
            ["Berlin", *preferences.get("amenities", [])]
        )
        results = recommender.recommend(preferences, user_id=user_id, top_k=k)
        predictions[user_id] = [item["id"] for item in results]
    return predictions


def _named_metrics(
    name: str,
    predictions: dict[str, list[str]],
    test: pd.DataFrame,
    catalog_size: int,
    k: int,
) -> dict[str, float]:
    metrics = evaluate_user_rankings(predictions, test, k=k)
    metrics["catalog_coverage"] = catalog_coverage(
        list(predictions.values()), catalog_size
    )
    return {f"{name}_{key}": value for key, value in metrics.items()}


def evaluate(
    k: int = 10,
    max_users: int = 500,
    max_training_users: int = 1500,
) -> dict[str, float]:
    properties = load_properties()
    interactions = load_interactions()
    user_counts = interactions.groupby("user_id").size()
    eligible_users = user_counts.loc[user_counts >= 2].index.astype(str).tolist()
    if len(eligible_users) > max_users:
        eligible_users = (
            pd.Series(eligible_users).sample(max_users, random_state=42).tolist()
        )

    train, test = temporal_split(interactions)
    test = test.loc[test["user_id"].astype(str).isin(eligible_users)]

    baseline = PropertyRecommender(properties, train)
    baseline_predictions = _predict(baseline, properties, train, eligible_users, k)

    features, labels, groups = build_training_data(
        max_users=max_training_users,
        min_user_interactions=1,
        properties_frame=properties,
        interactions_frame=train,
    )
    validation_ranker = LearnedRanker()
    validation_ranker.fit(features, labels, groups)
    learned = PropertyRecommender(properties, train, learned_ranker=validation_ranker)
    learned_predictions = _predict(learned, properties, train, eligible_users, k)

    metrics = _named_metrics(
        "baseline", baseline_predictions, test, len(properties), k
    )
    metrics.update(
        _named_metrics("learned", learned_predictions, test, len(properties), k)
    )
    metrics["evaluated_users"] = float(len(eligible_users))
    metrics["training_users"] = float(len(groups))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Run offline ranking evaluation.")
    parser.add_argument("--k", type=int, default=10)
    parser.add_argument("--max-users", type=int, default=500)
    parser.add_argument("--max-training-users", type=int, default=1500)
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation.json"))
    args = parser.parse_args()

    metrics = evaluate(
        k=args.k,
        max_users=args.max_users,
        max_training_users=args.max_training_users,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"Saved metrics: {args.output}")


if __name__ == "__main__":
    main()
