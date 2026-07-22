from __future__ import annotations

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


class TextEmbedder:
    """Small local text model used for listing retrieval."""

    def __init__(self, max_features: int = 512) -> None:
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english",
        )

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.fit_transform(texts).astype("float32")
        return normalize(matrix).toarray().astype("float32")

    def transform(self, texts: list[str]) -> np.ndarray:
        matrix = self.vectorizer.transform(texts).astype("float32")
        return normalize(matrix).toarray().astype("float32")
