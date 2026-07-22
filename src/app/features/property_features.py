from __future__ import annotations

from collections.abc import Iterable


def build_listing_text(row: dict) -> str:
    amenities = row.get("amenities", [])
    if isinstance(amenities, str):
        amenities = amenities.split("|")
    values = [
        row.get("title", ""),
        row.get("description", ""),
        row.get("city", ""),
        row.get("neighborhood", ""),
        row.get("property_type", ""),
        " ".join(amenities),
    ]
    return " ".join(str(value) for value in values if value).strip()


def budget_fit(price: float, max_budget: float | None) -> float:
    if not max_budget:
        return 1.0
    if price <= max_budget:
        return max(0.7, 1.0 - ((max_budget - price) / max_budget) * 0.15)
    return max(0.0, 1.0 - (price - max_budget) / max_budget * 4)


def amenity_overlap(property_amenities: Iterable[str], wanted: Iterable[str]) -> float:
    wanted_set = {item.lower() for item in wanted}
    if not wanted_set:
        return 1.0
    property_set = {item.lower() for item in property_amenities}
    return len(property_set & wanted_set) / len(wanted_set)


def quality_fit(rating: float) -> float:
    return max(0.0, min(1.0, rating / 5.0))


def availability_fit(days: float) -> float:
    return max(0.0, min(1.0, days / 365.0))
