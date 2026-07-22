from __future__ import annotations

from collections import defaultdict

import pandas as pd


def diversify(frame: pd.DataFrame, top_k: int, max_per_neighborhood: int = 2) -> pd.DataFrame:
    chosen: list[int] = []
    counts: defaultdict[str, int] = defaultdict(int)

    for index, row in frame.iterrows():
        neighborhood = str(row["neighborhood"])
        if counts[neighborhood] >= max_per_neighborhood:
            continue
        chosen.append(index)
        counts[neighborhood] += 1
        if len(chosen) == top_k:
            break

    return frame.loc[chosen].reset_index(drop=True)
