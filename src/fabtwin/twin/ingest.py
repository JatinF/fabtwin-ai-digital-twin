"""Telemetry boundary.

The committed benchmark calls this function in-process. A Kafka consumer would
hand the same reading list to the twin. The broker was not started.
"""

from __future__ import annotations


def ingest_batch(readings: list[dict]) -> list[dict]:
    return [dict(item) for item in readings]
