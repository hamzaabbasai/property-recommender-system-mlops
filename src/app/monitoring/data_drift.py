from __future__ import annotations

import pandas as pd


def numeric_drift(reference: pd.DataFrame, current: pd.DataFrame, columns: list[str]) -> dict:
    report: dict[str, float] = {}
    for column in columns:
        baseline = float(reference[column].mean())
        latest = float(current[column].mean())
        report[column] = abs(latest - baseline) / max(abs(baseline), 1e-9)
    return report
