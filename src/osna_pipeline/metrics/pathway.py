"""Transparent pathway-duration calculations."""

from __future__ import annotations

from datetime import datetime


def minutes_between(start: datetime | None, end: datetime | None) -> str:
    """Return whole or decimal minutes, or blank when the duration is unavailable or negative."""

    if start is None or end is None or end < start:
        return ""
    minutes = (end - start).total_seconds() / 60
    return f"{minutes:.1f}"
