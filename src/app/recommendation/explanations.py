from __future__ import annotations


def recommendation_reasons(row: dict, preferences: dict) -> list[str]:
    reasons: list[str] = []
    max_budget = preferences.get("max_budget")
    if max_budget and float(row["price"]) <= float(max_budget):
        reasons.append("Within nightly budget")

    wanted = {item.casefold() for item in preferences.get("amenities", [])}
    available = {item.casefold(): item for item in row.get("amenities", [])}
    for item in wanted:
        if item in available:
            reasons.append(available[item])
            break

    rating = float(row.get("rating", 0))
    if rating >= 4.7:
        reasons.append(f"{rating:.1f} guest rating")
    elif int(row.get("review_count", 0)) >= 50:
        reasons.append("Popular with guests")

    return reasons[:3] or ["Matches your search"]
