from __future__ import annotations

import pandas as pd

EVENT_WEIGHTS = {
    "review": 1.0,
    "impression": 0.1,
    "click": 1.0,
    "save": 2.5,
    "contact": 4.0,
    "viewing_request": 5.0,
    "dismiss": -1.5,
}


def add_interaction_weights(interactions: pd.DataFrame) -> pd.DataFrame:
    data = interactions.copy()
    default_weight = data.get("relevance", pd.Series(1.0, index=data.index))
    data["event_weight"] = data["event_type"].map(EVENT_WEIGHTS).fillna(default_weight)
    return data
