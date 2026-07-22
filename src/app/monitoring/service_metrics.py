from __future__ import annotations

from contextlib import contextmanager
from time import perf_counter


@contextmanager
def measure_latency(metrics: dict[str, float], name: str):
    started = perf_counter()
    try:
        yield
    finally:
        metrics[name] = round((perf_counter() - started) * 1000, 2)
