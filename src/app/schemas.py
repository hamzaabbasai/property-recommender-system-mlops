from __future__ import annotations

from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    query: str = ""
    user_id: str | None = None
    city: str = "Berlin"
    max_budget: float | None = Field(default=None, gt=0)
    bedrooms: int | None = Field(default=None, ge=0)
    property_types: list[str] = Field(default_factory=list)
    amenities: list[str] = Field(default_factory=list)
    top_k: int = Field(default=10, ge=1, le=50)


class RecommendationItem(BaseModel):
    id: str
    title: str
    city: str
    neighborhood: str
    price: float
    bedrooms: int
    beds: int
    bathrooms: float
    accommodates: int
    property_type: str
    room_detail: str
    amenities: list[str]
    minimum_nights: int
    availability_365: int
    rating: float
    review_count: int
    latitude: float
    longitude: float
    image_url: str
    match_label: str
    reasons: list[str]
    ranking_score: float
    model_name: str


class RecommendationResponse(BaseModel):
    results: list[RecommendationItem]
    count: int
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    service: str
