from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from app.config import PROJECT_ROOT
from app.data.clean import (
    clean_inside_airbnb_listings,
    clean_inside_airbnb_reviews,
)
from app.data.validate import validate_properties


def prepare_data(
    listings_path: Path | None = None,
    reviews_path: Path | None = None,
    output_dir: Path | None = None,
    min_user_interactions: int = 2,
) -> tuple[Path, Path]:
    listings_source = listings_path or PROJECT_ROOT / "data" / "raw" / "listings.csv.gz"
    reviews_source = reviews_path or PROJECT_ROOT / "data" / "raw" / "reviews.csv.gz"
    destination = output_dir or PROJECT_ROOT / "data" / "processed"

    properties = clean_inside_airbnb_listings(pd.read_csv(listings_source))
    validate_properties(properties)
    interactions = clean_inside_airbnb_reviews(
        pd.read_csv(reviews_source),
        set(properties["property_id"]),
        min_user_interactions=min_user_interactions,
        user_id_salt=os.getenv("USER_ID_SALT", "berlin-recommender"),
    )

    destination.mkdir(parents=True, exist_ok=True)
    properties_path = destination / "properties.csv"
    interactions_path = destination / "interactions.csv"

    saved_properties = properties.copy()
    saved_properties["amenities"] = saved_properties["amenities"].map("|".join)
    saved_properties.to_csv(properties_path, index=False)
    interactions.to_csv(interactions_path, index=False)
    return properties_path, interactions_path


if __name__ == "__main__":
    for path in prepare_data():
        print(path)
