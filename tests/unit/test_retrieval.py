from pathlib import Path

from app.data.ingest import load_properties
from app.retrieval.hybrid_retriever import HybridRetriever

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_retrieval_applies_budget_and_bedroom_filters() -> None:
    properties = load_properties(FIXTURES / "properties.csv")
    result = HybridRetriever(properties).retrieve(
        {
            "query": "one bedroom apartment with wifi in Berlin",
            "city": "Berlin",
            "max_budget": 180,
            "bedrooms": 1,
            "property_types": ["Entire home/apt"],
        }
    )
    assert set(result["property_id"]) == {"p-1", "p-2"}
