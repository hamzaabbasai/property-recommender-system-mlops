from __future__ import annotations

from collections import Counter

import pandas as pd


def user_preferences_from_history(
    properties: pd.DataFrame,
    interactions: pd.DataFrame,
    user_id: str,
) -> dict:
    item_ids = interactions.loc[
        interactions["user_id"].astype(str) == str(user_id), "property_id"
    ].astype(str)
    history = properties.loc[properties["property_id"].astype(str).isin(item_ids)].copy()
    if history.empty:
        return {"city": "Berlin", "property_types": [], "amenities": []}

    amenity_counts = Counter(
        amenity
        for values in history["amenities"]
        for amenity in values
    )
    property_types = history["property_type"].value_counts().head(2).index.tolist()
    bedrooms = int(round(float(history["bedrooms"].median())))
    budget = float(history["price"].quantile(0.75) * 1.2)

    return {
        "city": "Berlin",
        "max_budget": round(budget, 2),
        "bedrooms": bedrooms,
        "property_types": property_types,
        "amenities": [name for name, _ in amenity_counts.most_common(5)],
    }
