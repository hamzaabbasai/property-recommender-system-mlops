from __future__ import annotations

import pandas as pd

from app.evaluation.ranking_metrics import (
    average_precision_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def evaluate_user_rankings(
    predictions: dict[str, list[str]],
    test_interactions: pd.DataFrame,
    k: int = 10,
) -> dict[str, float]:
    rows: list[dict[str, float]] = []
    relevant_by_user = test_interactions.groupby("user_id")["property_id"].apply(set)

    for user_id, relevant in relevant_by_user.items():
        recommended = predictions.get(str(user_id), [])
        rows.append(
            {
                "precision": precision_at_k(recommended, relevant, k),
                "recall": recall_at_k(recommended, relevant, k),
                "map": average_precision_at_k(recommended, relevant, k),
                "ndcg": ndcg_at_k(recommended, relevant, k),
            }
        )

    if not rows:
        return {f"{name}@{k}": 0.0 for name in ["precision", "recall", "map", "ndcg"]}
    frame = pd.DataFrame(rows)
    return {f"{column}@{k}": float(frame[column].mean()) for column in frame.columns}
