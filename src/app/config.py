from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    properties_path: Path = PROJECT_ROOT / "data" / "processed" / "properties.csv"
    interactions_path: Path = PROJECT_ROOT / "data" / "processed" / "interactions.csv"
    ranker_path: Path = PROJECT_ROOT / "artifacts" / "models" / "lgbm_ranker.joblib"
    use_learned_ranker: bool = False
    default_top_k: int = 10
    allowed_origin: str = "http://localhost:3000"

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            properties_path=Path(os.getenv("PROPERTIES_PATH", cls.properties_path)),
            interactions_path=Path(os.getenv("INTERACTIONS_PATH", cls.interactions_path)),
            ranker_path=Path(os.getenv("RANKER_PATH", cls.ranker_path)),
            use_learned_ranker=os.getenv("USE_LEARNED_RANKER", "false").lower()
            in {"1", "true", "yes"},
            default_top_k=int(os.getenv("DEFAULT_TOP_K", "10")),
            allowed_origin=os.getenv("ALLOWED_ORIGIN", "http://localhost:3000"),
        )


def load_yaml(name: str) -> dict:
    path = PROJECT_ROOT / "configs" / name
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
