from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from app.ranking.baseline_ranker import RANKING_FEATURES

try:
    from lightgbm import LGBMRanker
except ImportError:  # pragma: no cover - optional dependency
    LGBMRanker = None


class LearnedRanker:
    def __init__(self, model=None) -> None:
        self.model = model

    @property
    def ready(self) -> bool:
        return self.model is not None

    def fit(self, frame: pd.DataFrame, labels: list[float], groups: list[int]) -> None:
        if LGBMRanker is None:
            raise RuntimeError("Install the ml extra to train the LightGBM ranker.")
        self.model = LGBMRanker(
            objective="lambdarank",
            metric="ndcg",
            n_estimators=180,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=30,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            verbosity=-1,
        )
        self.model.fit(frame[RANKING_FEATURES], labels, group=groups)

    def predict(self, frame: pd.DataFrame) -> list[float]:
        if not self.ready:
            raise RuntimeError("The learned ranker is not trained.")
        return self.model.predict(frame[RANKING_FEATURES]).tolist()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load(cls, path: Path) -> LearnedRanker:
        return cls(joblib.load(path)) if path.exists() else cls()
