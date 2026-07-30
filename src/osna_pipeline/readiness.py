"""Build a non-identifying readiness report for mapped source extracts."""

from __future__ import annotations

from collections import Counter

from osna_pipeline.connectors.csv_sources import LoadedSources


READINESS_REPORT_VERSION = "1.0.0"


def _quality_status(severity_counts: Counter[str]) -> str:
    if severity_counts["error"]:
        return "errors_detected"
    if severity_counts["warning"]:
        return "warnings_detected"
    return "clean"


def build_source_readiness_report(
    loaded: LoadedSources,
) -> dict[str, object]:
    """Summarise field completeness and validation failures without row data."""

    severity_counts = Counter(issue.severity for issue in loaded.issues)
    issue_counts = Counter(issue.issue_code for issue in loaded.issues)
    source_counts: dict[str, dict[str, object]] = {}
    validation_finding_count = 0

    for source_system, rows in loaded.rows.items():
        field_readiness = {
            field_name: profile.to_dict()
            for field_name, profile in loaded.source_field_readiness[
                source_system
            ].items()
        }
        source_finding_count = sum(
            sum(profile.finding_counts.values())
            for profile in loaded.source_field_readiness[
                source_system
            ].values()
        )
        validation_finding_count += source_finding_count
        source_counts[source_system] = {
            "filename": loaded.source_filenames[source_system],
            "record_count": loaded.source_record_counts[source_system],
            "accepted_record_count": len(rows),
            "rejected_record_count": (
                loaded.source_record_counts[source_system] - len(rows)
            ),
            "validation_finding_count": source_finding_count,
            "field_readiness": field_readiness,
        }

    accepted_record_count = sum(len(rows) for rows in loaded.rows.values())
    return {
        "report_version": READINESS_REPORT_VERSION,
        "mode": "validate_only",
        "privacy_boundary": {
            "contains_row_identifiers": False,
            "contains_source_values": False,
            "counts_are_suppressed": False,
        },
        "mapping_version": loaded.mapping_version,
        "mapping_filename": loaded.mapping_filename,
        "mapping_sha256": loaded.mapping_sha256,
        "data_classification": loaded.data_classification,
        "quality_status": _quality_status(severity_counts),
        "input_record_count": loaded.input_record_count,
        "accepted_source_record_count": accepted_record_count,
        "source_validation_rejected_record_count": (
            loaded.input_record_count - accepted_record_count
        ),
        "validation_finding_count": validation_finding_count,
        "exception_count": len(loaded.issues),
        "exception_counts_by_severity": dict(sorted(severity_counts.items())),
        "exception_counts_by_code": dict(sorted(issue_counts.items())),
        "source_counts": source_counts,
    }
