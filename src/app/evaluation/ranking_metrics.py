from __future__ import annotations

import math
from collections.abc import Iterable


def precision_at_k(recommended: Iterable[str], relevant: set[str], k: int) -> float:
    items = list(recommended)[:k]
    if not items or k <= 0:
        return 0.0
    return len(set(items) & relevant) / k


def recall_at_k(recommended: Iterable[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(list(recommended)[:k]) & relevant) / len(relevant)


def average_precision_at_k(recommended: Iterable[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = 0
    score = 0.0
    for position, item in enumerate(list(recommended)[:k], start=1):
        if item in relevant:
            hits += 1
            score += hits / position
    return score / min(len(relevant), k)


def ndcg_at_k(recommended: Iterable[str], relevant: set[str], k: int) -> float:
    items = list(recommended)[:k]
    dcg = sum(
        1 / math.log2(position + 1)
        for position, item in enumerate(items, start=1)
        if item in relevant
    )
    ideal_hits = min(len(relevant), k)
    ideal = sum(1 / math.log2(position + 1) for position in range(1, ideal_hits + 1))
    return dcg / ideal if ideal else 0.0


def catalog_coverage(recommendation_lists: list[list[str]], catalog_size: int) -> float:
    if catalog_size <= 0:
        return 0.0
    unique_items = {item for values in recommendation_lists for item in values}
    return len(unique_items) / catalog_size
