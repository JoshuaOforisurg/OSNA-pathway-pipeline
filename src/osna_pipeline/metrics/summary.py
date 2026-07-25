"""Descriptive pathway statistics with explicit missing and exclusion counts."""

from __future__ import annotations

import math
from statistics import median


METRIC_NAMES = (
    "transport_minutes",
    "assay_minutes",
    "laboratory_turnaround_minutes",
    "communication_minutes",
    "acknowledgement_minutes",
    "total_pathway_minutes",
)

METRIC_SUMMARY_FIELDS = (
    "metric_name",
    "unit",
    "eligible_specimen_count",
    "observed_value_count",
    "missing_value_count",
    "excluded_invalid_specimen_count",
    "minimum",
    "median",
    "p90",
    "maximum",
)


def _percentile(values: list[float], percentile: float) -> float:
    """Calculate a linearly interpolated percentile from sorted values."""

    if not values:
        raise ValueError("At least one value is required")
    if not 0 <= percentile <= 1:
        raise ValueError("Percentile must be between 0 and 1")

    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    lower_index = math.floor(rank)
    upper_index = math.ceil(rank)
    if lower_index == upper_index:
        return ordered[lower_index]
    fraction = rank - lower_index
    return ordered[lower_index] + (
        ordered[upper_index] - ordered[lower_index]
    ) * fraction


def _format_statistic(value: float) -> str:
    return f"{value:.1f}"


def build_metric_summary(timelines: list[dict[str, str]]) -> list[dict[str, str]]:
    """Summarise valid metric values without treating missing data as zero."""

    eligible_rows = [
        row
        for row in timelines
        if row.get("pathway_status") in {"complete", "incomplete"}
    ]
    excluded_invalid_count = len(timelines) - len(eligible_rows)
    summaries: list[dict[str, str]] = []

    for metric_name in METRIC_NAMES:
        values = [
            float(row[metric_name])
            for row in eligible_rows
            if row.get(metric_name, "") != ""
        ]
        statistic_values = {
            "minimum": _format_statistic(min(values)) if values else "",
            "median": _format_statistic(median(values)) if values else "",
            "p90": _format_statistic(_percentile(values, 0.9)) if values else "",
            "maximum": _format_statistic(max(values)) if values else "",
        }
        summaries.append(
            {
                "metric_name": metric_name,
                "unit": "minutes",
                "eligible_specimen_count": str(len(eligible_rows)),
                "observed_value_count": str(len(values)),
                "missing_value_count": str(len(eligible_rows) - len(values)),
                "excluded_invalid_specimen_count": str(excluded_invalid_count),
                **statistic_values,
            }
        )
    return summaries
