from app.features.property_features import amenity_overlap, budget_fit


def test_budget_fit_prefers_a_property_inside_budget() -> None:
    assert budget_fit(170, 180) > budget_fit(220, 180)


def test_amenity_overlap_counts_shared_items() -> None:
    score = amenity_overlap(["Balcony", "Wifi"], ["Balcony", "Parking"])
    assert score == 0.5
