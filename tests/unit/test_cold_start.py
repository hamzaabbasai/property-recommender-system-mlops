from pathlib import Path

from app.data.ingest import load_properties
from app.recommendation.cold_start import cold_start_candidates

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_cold_start_returns_available_city_properties() -> None:
    properties = load_properties(FIXTURES / "properties.csv")
    result = cold_start_candidates(properties, city="Berlin")
    assert len(result) == 3
