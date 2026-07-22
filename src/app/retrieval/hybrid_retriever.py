from __future__ import annotations

import pandas as pd

from app.retrieval.collaborative import CollaborativeRetriever
from app.retrieval.content_based import ContentRetriever


class HybridRetriever:
    def __init__(
        self,
        properties: pd.DataFrame,
        interactions: pd.DataFrame | None = None,
    ) -> None:
        self.properties = properties.copy()
        self.content = ContentRetriever().fit(self.properties)
        self.collaborative = CollaborativeRetriever().fit(interactions)

    def retrieve(
        self,
        preferences: dict,
        user_id: str | None = None,
        candidate_count: int = 100,
        exclude_seen: bool = False,
    ) -> pd.DataFrame:
        query = preferences.get("query") or self._query_from_preferences(preferences)
        content_scores = self.content.search(
            query,
            min(len(self.properties), max(candidate_count * 2, candidate_count)),
        )
        collaborative_candidates = self.collaborative.candidates(
            user_id, min(len(self.properties), candidate_count * 2)
        )
        candidate_ids = set(content_scores) | set(collaborative_candidates)

        candidates = self.properties[
            self.properties["property_id"].astype(str).isin(candidate_ids)
        ].copy()
        candidates = self._apply_hard_filters(candidates, preferences)
        if exclude_seen:
            candidates = candidates.loc[
                ~candidates["property_id"].astype(str).isin(
                    self.collaborative.seen_items(user_id)
                )
            ]
        candidates["semantic_score"] = (
            candidates["property_id"].astype(str).map(content_scores).fillna(0.0)
        )

        collaborative_scores = self.collaborative.scores(
            user_id,
            candidates["property_id"].astype(str).tolist(),
        )
        candidates["collaborative_score"] = (
            candidates["property_id"].astype(str).map(collaborative_scores).fillna(0.0)
        )
        candidates["retrieval_score"] = (
            candidates["semantic_score"] * 0.8 + candidates["collaborative_score"] * 0.2
        )
        return candidates.sort_values("retrieval_score", ascending=False).head(candidate_count)

    @staticmethod
    def _apply_hard_filters(frame: pd.DataFrame, preferences: dict) -> pd.DataFrame:
        data = frame.loc[frame["available"]].copy()
        if preferences.get("city"):
            data = data.loc[data["city"].str.lower() == str(preferences["city"]).lower()]
        if preferences.get("bedrooms") is not None:
            wanted_bedrooms = int(preferences["bedrooms"])
            data = data.loc[data["bedrooms"] >= wanted_bedrooms]
        if preferences.get("property_types"):
            data = data.loc[data["property_type"].isin(preferences["property_types"])]
        if preferences.get("max_budget"):
            data = data.loc[data["price"] <= float(preferences["max_budget"]) * 1.1]
        return data

    @staticmethod
    def _query_from_preferences(preferences: dict) -> str:
        parts = [
            preferences.get("city", ""),
            f"{preferences.get('bedrooms')} bedroom" if preferences.get("bedrooms") else "",
            " ".join(preferences.get("property_types", [])),
            " ".join(preferences.get("amenities", [])),
        ]
        return " ".join(part for part in parts if part)
