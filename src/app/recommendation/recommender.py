from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.ranking.baseline_ranker import BaselineRanker
from app.ranking.diversity_reranker import diversify
from app.ranking.lgbm_ranker import LearnedRanker
from app.recommendation.explanations import recommendation_reasons
from app.retrieval.hybrid_retriever import HybridRetriever


class PropertyRecommender:
    def __init__(
        self,
        properties: pd.DataFrame,
        interactions: pd.DataFrame | None = None,
        ranker_path: Path | None = None,
        learned_ranker: LearnedRanker | None = None,
    ) -> None:
        self.retriever = HybridRetriever(properties, interactions)
        self.baseline_ranker = BaselineRanker()
        self.learned_ranker = learned_ranker or (
            LearnedRanker.load(ranker_path) if ranker_path else LearnedRanker()
        )

    def recommend(
        self,
        preferences: dict,
        user_id: str | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        candidates = self.retriever.retrieve(
            preferences,
            user_id=user_id,
            candidate_count=max(top_k * 8, 40),
            exclude_seen=bool(user_id),
        )
        if candidates.empty:
            return []

        ranked = self.baseline_ranker.rank(candidates, preferences)
        model_name = "weighted-baseline"
        if self.learned_ranker.ready:
            ranked["ranking_score"] = self.learned_ranker.predict(ranked)
            ranked = ranked.sort_values("ranking_score", ascending=False).reset_index(drop=True)
            model_name = "lightgbm-lambdarank"

        ranked = diversify(ranked, top_k=top_k)
        results: list[dict] = []
        for index, row in ranked.iterrows():
            item = row.to_dict()
            item["id"] = str(item.pop("property_id"))
            item["reasons"] = recommendation_reasons(item, preferences)
            item["match_label"] = "Best match" if index == 0 else "Good match"
            item["model_name"] = model_name
            item["ranking_score"] = round(float(item["ranking_score"]), 4)
            for column in [
                "bedrooms",
                "beds",
                "accommodates",
                "minimum_nights",
                "availability_365",
                "review_count",
            ]:
                item[column] = int(item[column])
            item["bathrooms"] = float(item["bathrooms"])
            item["rating"] = round(float(item["rating"]), 2)
            results.append(item)
        return results
