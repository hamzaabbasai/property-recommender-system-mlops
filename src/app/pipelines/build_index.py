from __future__ import annotations

import joblib

from app.config import PROJECT_ROOT
from app.data.ingest import load_properties
from app.retrieval.content_based import ContentRetriever


def build_index() -> str:
    retriever = ContentRetriever().fit(load_properties())
    path = PROJECT_ROOT / "artifacts" / "indexes" / "content_retriever.joblib"
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(retriever, path)
    return retriever.index.engine


if __name__ == "__main__":
    print(f"Index engine: {build_index()}")
