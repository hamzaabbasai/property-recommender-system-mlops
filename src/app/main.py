from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.apis.health import router as health_router
from app.apis.recommendations import router as recommendation_router
from app.config import Settings

settings = Settings.from_env()
app = FastAPI(
    title="Hybrid Property Recommender API",
    version="0.1.0",
    description="Candidate retrieval and personalized property ranking.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(recommendation_router)
