from __future__ import annotations

import pandas as pd

from app.features.property_features import (
    amenity_overlap,
    availability_fit,
    budget_fit,
    quality_fit,
)

RANKING_FEATURES = [
    "semantic_score",
    "collaborative_score",
    "budget_score",
    "amenity_score",
    "quality_score",
    "popularity_score",
    "availability_score",
]


class BaselineRanker:
    def add_features(self, candidates: pd.DataFrame, preferences: dict) -> pd.DataFrame:
        data = candidates.copy()
        data["budget_score"] = data["price"].map(
            lambda price: budget_fit(float(price), preferences.get("max_budget"))
        )
        data["amenity_score"] = data["amenities"].map(
            lambda amenities: amenity_overlap(amenities, preferences.get("amenities", []))
        )
        data["quality_score"] = data["rating"].map(quality_fit)
        data["availability_score"] = data["availability_365"].map(availability_fit)
        data["popularity_score"] = data["popularity_score"].fillna(0.0).clip(0.0, 1.0)
        return data

    def rank(self, candidates: pd.DataFrame, preferences: dict) -> pd.DataFrame:
        data = self.add_features(candidates, preferences)
        data["ranking_score"] = (
            data["semantic_score"] * 0.32
            + data["collaborative_score"] * 0.18
            + data["budget_score"] * 0.18
            + data["amenity_score"] * 0.12
            + data["quality_score"] * 0.12
            + data["popularity_score"] * 0.05
            + data["availability_score"] * 0.03
        )
        return data.sort_values("ranking_score", ascending=False).reset_index(drop=True)
