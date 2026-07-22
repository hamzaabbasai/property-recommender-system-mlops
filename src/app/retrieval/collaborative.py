from __future__ import annotations

import math
from collections import Counter, defaultdict

import pandas as pd

from app.features.interaction_features import add_interaction_weights


class CollaborativeRetriever:
    """A small item-to-item collaborative model."""

    def __init__(self, max_history: int = 30) -> None:
        self.max_history = max_history
        self.user_items: dict[str, set[str]] = {}
        self.item_counts: Counter[str] = Counter()
        self.cooccurrence: dict[str, Counter[str]] = defaultdict(Counter)
        self.popularity: dict[str, float] = {}

    def fit(self, interactions: pd.DataFrame | None) -> CollaborativeRetriever:
        if interactions is None or interactions.empty:
            return self

        weighted = add_interaction_weights(interactions)
        weighted = weighted.loc[weighted["event_weight"] > 0].sort_values("timestamp")
        grouped = weighted.groupby("user_id")["property_id"]

        for user_id, values in grouped:
            items = list(dict.fromkeys(values.astype(str).tolist()))[-self.max_history :]
            self.user_items[str(user_id)] = set(items)
            self.item_counts.update(items)
            for source in items:
                self.cooccurrence[source].update(item for item in items if item != source)

        if self.item_counts:
            max_count = math.log1p(max(self.item_counts.values()))
            self.popularity = {
                item: math.log1p(count) / max_count for item, count in self.item_counts.items()
            }
        return self

    def seen_items(self, user_id: str | None) -> set[str]:
        return self.user_items.get(str(user_id), set()) if user_id else set()

    def candidates(self, user_id: str | None, top_k: int) -> dict[str, float]:
        history = self.seen_items(user_id)
        if not history:
            ordered = sorted(
                self.popularity.items(), key=lambda item: item[1], reverse=True
            )
            return dict(ordered[:top_k])

        candidate_ids = {
            candidate
            for source in history
            for candidate in self.cooccurrence[source]
            if candidate not in history
        }
        scores = self.scores(user_id, list(candidate_ids))
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        return dict(ordered[:top_k])

    def scores(self, user_id: str | None, property_ids: list[str]) -> dict[str, float]:
        history = self.seen_items(user_id)
        if not history:
            return {item: self.popularity.get(item, 0.0) for item in property_ids}

        raw_scores: dict[str, float] = {}
        for candidate in property_ids:
            if candidate in history:
                raw_scores[candidate] = 1.0
                continue
            score = 0.0
            for source in history:
                count = self.cooccurrence[source][candidate]
                if not count:
                    continue
                denominator = math.sqrt(
                    self.item_counts[source] * max(self.item_counts[candidate], 1)
                )
                score += count / denominator
            raw_scores[candidate] = score

        max_score = max(raw_scores.values(), default=0.0)
        if max_score > 0:
            return {item: score / max_score for item, score in raw_scores.items()}
        return {item: self.popularity.get(item, 0.0) for item in property_ids}
