from __future__ import annotations

import numpy as np

try:
    import faiss
except ImportError:  # pragma: no cover - used when the optional package is missing
    faiss = None


class VectorIndex:
    def __init__(self) -> None:
        self.index = None
        self.vectors: np.ndarray | None = None
        self.engine = "numpy"

    def build(self, vectors: np.ndarray) -> None:
        vectors = np.asarray(vectors, dtype="float32")
        self.vectors = vectors
        if faiss is not None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.index.add(vectors)
            self.engine = "faiss"

    def search(self, query: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        if self.vectors is None:
            raise RuntimeError("Build the vector index before search.")

        query = np.asarray(query, dtype="float32")
        top_k = min(top_k, len(self.vectors))
        if self.index is not None:
            scores, indexes = self.index.search(query, top_k)
            return indexes[0], scores[0]

        scores = self.vectors @ query[0]
        indexes = np.argsort(scores)[::-1][:top_k]
        return indexes, scores[indexes]
