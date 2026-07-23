from __future__ import annotations

import pandas as pd


def cold_start_candidates(properties: pd.DataFrame, city: str, top_k: int = 20) -> pd.DataFrame:
    data = properties.loc[
        properties["available"] & properties["city"].str.casefold().eq(city.casefold())
    ].copy()
    return data.sort_values(
        ["rating", "popularity_score", "availability_365"],
        ascending=[False, False, False],
    ).head(top_k)
