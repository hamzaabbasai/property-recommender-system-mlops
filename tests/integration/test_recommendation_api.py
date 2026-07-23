from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_recommendation_endpoint() -> None:
    response = client.post(
        "/api/v1/recommendations",
        json={
            "query": "one bedroom apartment with wifi in Berlin",
            "city": "Berlin",
            "max_budget": 180,
            "bedrooms": 1,
            "property_types": ["Entire home/apt"],
            "amenities": ["Wifi", "Balcony"],
            "top_k": 3,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] <= 3
    assert all(item["price"] <= 198 for item in body["results"])
