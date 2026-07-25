"""Aggregate detailed quality findings for operational review."""

from __future__ import annotations

from collections import Counter

from osna_pipeline.domain.models import QualityIssue


QUALITY_SUMMARY_FIELDS = (
    "severity",
    "issue_code",
    "source_system",
    "event_type",
    "issue_count",
)


def build_quality_summary(issues: list[QualityIssue]) -> list[dict[str, str]]:
    """Count equivalent findings without hiding the detailed exception rows."""

    counts = Counter(
        (
            issue.severity,
            issue.issue_code,
            issue.source_system,
            issue.event_type,
        )
        for issue in issues
    )
    return [
        {
            "severity": severity,
            "issue_code": issue_code,
            "source_system": source_system,
            "event_type": event_type,
            "issue_count": str(issue_count),
        }
        for (
            severity,
            issue_code,
            source_system,
            event_type,
        ), issue_count in sorted(counts.items())
    ]
