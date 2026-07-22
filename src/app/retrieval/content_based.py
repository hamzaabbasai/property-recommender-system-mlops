from __future__ import annotations

import pandas as pd

from app.features.property_features import build_listing_text
from app.features.text_embeddings import TextEmbedder
from app.retrieval.faiss_index import VectorIndex


class ContentRetriever:
    def __init__(self) -> None:
        self.embedder = TextEmbedder()
        self.index = VectorIndex()
        self.property_ids: list[str] = []

    def fit(self, properties: pd.DataFrame) -> ContentRetriever:
        texts = [build_listing_text(row) for row in properties.to_dict("records")]
        vectors = self.embedder.fit_transform(texts)
        self.index.build(vectors)
        self.property_ids = properties["property_id"].astype(str).tolist()
        return self

    def search(self, query: str, top_k: int) -> dict[str, float]:
        query_vector = self.embedder.transform([query])
        indexes, scores = self.index.search(query_vector, top_k)
        return {
            self.property_ids[int(index)]: float(score)
            for index, score in zip(indexes, scores, strict=True)
            if index >= 0
        }
