from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd


def _amenities(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if pd.isna(value):
        return []

    text = str(value).strip()
    if text.startswith("["):
        try:
            values = json.loads(text)
            return [str(item).strip() for item in values if str(item).strip()]
        except json.JSONDecodeError:
            pass
    return [item.strip() for item in text.split("|") if item.strip()]


def _price(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str).str.replace(r"[$€,]", "", regex=True),
        errors="coerce",
    )


def _bathrooms(frame: pd.DataFrame) -> pd.Series:
    values = pd.to_numeric(frame.get("bathrooms"), errors="coerce")
    if "bathrooms_text" in frame:
        extracted = frame["bathrooms_text"].astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0]
        values = values.fillna(pd.to_numeric(extracted, errors="coerce"))
    return values.fillna(0.0)


def clean_inside_airbnb_listings(frame: pd.DataFrame) -> pd.DataFrame:
    source = frame.copy()
    source.columns = [column.strip().lower() for column in source.columns]

    prices = _price(source["price"])
    review_count = pd.to_numeric(source["number_of_reviews"], errors="coerce").fillna(0)
    max_reviews = float(np.log1p(review_count).max()) or 1.0
    availability = pd.to_numeric(source["availability_365"], errors="coerce").fillna(0)

    data = pd.DataFrame(
        {
            "property_id": source["id"].astype(str),
            "title": source["name"].fillna("Berlin stay").astype(str).str.strip(),
            "city": "Berlin",
            "neighborhood": source["neighbourhood_cleansed"].fillna("Berlin"),
            "price": prices,
            "bedrooms": pd.to_numeric(source["bedrooms"], errors="coerce").fillna(0),
            "beds": pd.to_numeric(source["beds"], errors="coerce").fillna(0),
            "bathrooms": _bathrooms(source),
            "accommodates": pd.to_numeric(source["accommodates"], errors="coerce").fillna(1),
            "property_type": source["room_type"].fillna("Other"),
            "room_detail": source["property_type"].fillna("Property"),
            "amenities": source["amenities"].map(_amenities),
            "description": source["description"].fillna(""),
            "minimum_nights": pd.to_numeric(
                source["minimum_nights"], errors="coerce"
            ).fillna(1),
            "availability_365": availability,
            "rating": pd.to_numeric(
                source["review_scores_rating"], errors="coerce"
            ).fillna(0),
            "review_count": review_count,
            "popularity_score": np.log1p(review_count) / max_reviews,
            "available": availability.gt(0),
            "latitude": pd.to_numeric(source["latitude"], errors="coerce"),
            "longitude": pd.to_numeric(source["longitude"], errors="coerce"),
            "created_at": pd.to_datetime(source["last_scraped"], errors="coerce"),
            "image_url": source["picture_url"].fillna("/properties/property-1.png"),
        }
    )

    data = data.drop_duplicates(subset=["property_id"])
    data = data.loc[data["price"].between(20, 1500)]
    data = data.dropna(subset=["latitude", "longitude"])

    integer_columns = [
        "bedrooms",
        "beds",
        "accommodates",
        "minimum_nights",
        "availability_365",
        "review_count",
    ]
    for column in integer_columns:
        data[column] = data[column].clip(lower=0).astype(int)
    return data.reset_index(drop=True)


def clean_properties(frame: pd.DataFrame) -> pd.DataFrame:
    columns = {column.strip().lower() for column in frame.columns}
    if {"id", "room_type", "number_of_reviews"}.issubset(columns):
        return clean_inside_airbnb_listings(frame)

    data = frame.copy()
    data.columns = [column.strip().lower() for column in data.columns]
    data = data.drop_duplicates(subset=["property_id"]).reset_index(drop=True)
    data["price"] = pd.to_numeric(data["price"], errors="coerce")
    for column in [
        "bedrooms",
        "beds",
        "accommodates",
        "minimum_nights",
        "availability_365",
        "review_count",
    ]:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0).astype(int)
    for column in ["bathrooms", "rating", "popularity_score", "latitude", "longitude"]:
        data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0.0)
    data["available"] = data["available"].astype(str).str.lower().isin(["true", "1", "yes"])
    data["amenities"] = data["amenities"].map(_amenities)
    data["created_at"] = pd.to_datetime(data["created_at"], errors="coerce")
    return data.dropna(subset=["price"])


def _private_user_id(value: object, salt: str) -> str:
    raw = f"{salt}:{value}".encode()
    return hashlib.sha256(raw).hexdigest()[:20]


def clean_inside_airbnb_reviews(
    frame: pd.DataFrame,
    valid_property_ids: set[str],
    min_user_interactions: int = 2,
    user_id_salt: str = "berlin-recommender",
) -> pd.DataFrame:
    data = frame[["reviewer_id", "listing_id", "date"]].copy()
    data = data.dropna(subset=["reviewer_id", "listing_id", "date"])
    data["property_id"] = data.pop("listing_id").astype(str)
    data = data.loc[data["property_id"].isin(valid_property_ids)]

    user_counts = data["reviewer_id"].value_counts()
    active_users = user_counts.loc[user_counts >= min_user_interactions].index
    data = data.loc[data["reviewer_id"].isin(active_users)].copy()
    data["user_id"] = data.pop("reviewer_id").map(
        lambda value: _private_user_id(value, user_id_salt)
    )
    data["event_type"] = "review"
    data["relevance"] = 1.0
    data["timestamp"] = pd.to_datetime(data.pop("date"), utc=True, errors="coerce")
    data = data.dropna(subset=["timestamp"])
    return data[["user_id", "property_id", "event_type", "relevance", "timestamp"]]


def clean_interactions(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    data["user_id"] = data["user_id"].astype(str)
    data["property_id"] = data["property_id"].astype(str)
    data["timestamp"] = pd.to_datetime(data["timestamp"], utc=True, errors="coerce")
    if "relevance" not in data:
        data["relevance"] = 1.0
    data["relevance"] = pd.to_numeric(data["relevance"], errors="coerce").fillna(1.0)
    return data.dropna(subset=["user_id", "property_id", "event_type", "timestamp"])
