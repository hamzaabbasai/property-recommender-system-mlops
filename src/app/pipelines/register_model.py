from __future__ import annotations

import mlflow


def register_model(run_id: str, name: str = "property-ranking-model") -> str:
    model_uri = f"runs:/{run_id}/model"
    result = mlflow.register_model(model_uri, name)
    return str(result.version)
