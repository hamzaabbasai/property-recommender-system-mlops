from __future__ import annotations

import pandas as pd


def temporal_split(
    interactions: pd.DataFrame,
    test_items_per_user: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = interactions.sort_values(["user_id", "timestamp"])
    test_index = ordered.groupby("user_id").tail(test_items_per_user).index
    test = ordered.loc[test_index].reset_index(drop=True)
    train = ordered.drop(test_index).reset_index(drop=True)
    return train, test
