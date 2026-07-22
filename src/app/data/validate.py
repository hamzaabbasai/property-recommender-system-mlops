from __future__ import annotations

import pandas as pd

REQUIRED_PROPERTY_COLUMNS = {
    "property_id",
    "title",
    "city",
    "neighborhood",
    "price",
    "bedrooms",
    "beds",
    "bathrooms",
    "accommodates",
    "property_type",
    "amenities",
    "description",
    "minimum_nights",
    "availability_365",
    "rating",
    "review_count",
    "available",
    "latitude",
    "longitude",
}


def validate_properties(frame: pd.DataFrame) -> None:
    missing = REQUIRED_PROPERTY_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Missing property columns: {sorted(missing)}")
    if frame["property_id"].duplicated().any():
        raise ValueError("Property IDs must be unique.")
    if (frame["price"] <= 0).any():
        raise ValueError("Property prices must be positive.")
    if (frame[["bedrooms", "beds", "bathrooms", "accommodates"]] < 0).any().any():
        raise ValueError("Property capacity values cannot be negative.")
