from __future__ import annotations

import pandas as pd


def metric_by_segment(frame: pd.DataFrame, segment: str, metric: str) -> pd.DataFrame:
    if segment not in frame or metric not in frame:
        raise ValueError("Segment and metric columns must exist.")
    return frame.groupby(segment, as_index=False)[metric].agg(["mean", "count"]).reset_index()
