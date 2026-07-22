from __future__ import annotations

import pandas as pd


def find_ranking_errors(frame: pd.DataFrame, relevance_column: str = "label") -> pd.DataFrame:
    data = frame.copy()
    data["error"] = data[relevance_column] - data["ranking_score"]
    return data.reindex(data["error"].abs().sort_values(ascending=False).index)
