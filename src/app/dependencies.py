from __future__ import annotations

from functools import lru_cache

from app.config import Settings
from app.data.ingest import load_interactions, load_properties
from app.recommendation.recommender import PropertyRecommender


@lru_cache(maxsize=1)
def get_recommender() -> PropertyRecommender:
    settings = Settings.from_env()
    properties = load_properties(
        settings.properties_path if settings.properties_path.exists() else None
    )
    interactions = (
        load_interactions(settings.interactions_path)
        if settings.interactions_path.exists()
        else None
    )
    ranker_path = settings.ranker_path if settings.use_learned_ranker else None
    return PropertyRecommender(properties, interactions, ranker_path)
