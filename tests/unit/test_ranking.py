from pathlib import Path

from app.data.ingest import load_properties
from app.ranking.baseline_ranker import BaselineRanker

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_ranker_returns_highest_score_first() -> None:
    data = load_properties(FIXTURES / "properties.csv").head(2)
    data["semantic_score"] = [0.9, 0.5]
    data["collaborative_score"] = [0.4, 0.2]
    ranked = BaselineRanker().rank(
        data,
        {"max_budget": 180, "amenities": ["Wifi", "Balcony"]},
    )
    assert ranked.iloc[0]["property_id"] == "p-1"
