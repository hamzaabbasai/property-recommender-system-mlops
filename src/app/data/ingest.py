from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import PROJECT_ROOT
from app.data.clean import clean_interactions, clean_properties


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    return pd.read_csv(path)


def load_properties(path: Path | None = None) -> pd.DataFrame:
    source = path or PROJECT_ROOT / "data" / "processed" / "properties.csv"
    if not source.exists():
        source = PROJECT_ROOT / "data" / "sample" / "properties.csv"
    return clean_properties(_read_csv(source))


def load_interactions(path: Path | None = None) -> pd.DataFrame:
    source = path or PROJECT_ROOT / "data" / "processed" / "interactions.csv"
    if not source.exists():
        source = PROJECT_ROOT / "data" / "sample" / "interactions.csv"
    return clean_interactions(_read_csv(source))
