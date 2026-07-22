from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Depends

from app.dependencies import get_recommender
from app.recommendation.recommender import PropertyRecommender
from app.schemas import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/api/v1", tags=["recommendations"])


@router.post("/recommendations", response_model=RecommendationResponse)
def recommendations(
    request: RecommendationRequest,
    recommender: PropertyRecommender = Depends(get_recommender),
) -> RecommendationResponse:
    started = perf_counter()
    preferences = request.model_dump(exclude={"user_id", "top_k"})
    results = recommender.recommend(
        preferences,
        user_id=request.user_id,
        top_k=request.top_k,
    )
    latency_ms = round((perf_counter() - started) * 1000, 2)
    return RecommendationResponse(results=results, count=len(results), latency_ms=latency_ms)
