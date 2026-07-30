"""End-to-end orchestration for the local OSNA pathway prototype."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from osna_pipeline.connectors.csv_sources import (
    DataContractError,
    LoadedSources,
    load_sources,
    parse_timestamp,
)
from osna_pipeline.connectors.mapping import SourceMapping, load_source_mapping
from osna_pipeline.domain.models import (
    CANONICAL_FIELDS,
    EXCEPTION_FIELDS,
    CanonicalEvent,
    QualityIssue,
    SCHEMA_VERSION,
    SpecimenContext,
)
from osna_pipeline.lineage import build_run_manifest
from osna_pipeline.matching import build_run_index, build_specimen_index
from osna_pipeline.metrics import METRIC_SUMMARY_FIELDS, build_metric_summary
from osna_pipeline.readiness import build_source_readiness_report
from osna_pipeline.transformations import (
    ASSAY_RUN_FIELDS,
    PROCEDURE_FIELDS,
    QUALITY_SUMMARY_FIELDS,
    TIMELINE_FIELDS,
    build_assay_run_summaries,
    build_procedure_summaries,
    build_quality_summary,
    build_timelines,
)


def _orphan_specimen_issue(row: dict[str, str], source_system: str) -> QualityIssue:
    return QualityIssue(
        issue_code="ORPHAN_SPECIMEN",
        severity="error",
        details="No unambiguous theatre case and procedure matched this specimen; record was quarantined",
        specimen_id=row["specimen_id"],
        source_system=source_system,
        source_record_id=row["source_record_id"],
        event_type=row.get("event_type", ""),
    )


def _canonicalise_theatre(
    rows: list[dict[str, str]], contexts: dict[str, SpecimenContext]
) -> list[CanonicalEvent]:
    events: list[CanonicalEvent] = []
    for row in rows:
        context = contexts.get(row["specimen_id"])
        if context is None:
            continue
        events.append(
            CanonicalEvent(
                case_id=context.case_id,
                procedure_id=context.procedure_id,
                specimen_id=context.specimen_id,
                event_type=row["event_type"],
                event_time=parse_timestamp(row["event_time"], "event_time"),
                source_system="theatre",
                source_record_id=row["source_record_id"],
                source_field="event_time",
            )
        )
    return events


def _canonicalise_laboratory(
    rows: list[dict[str, str]],
    contexts: dict[str, SpecimenContext],
    run_index: dict[str, str],
) -> tuple[list[CanonicalEvent], list[QualityIssue]]:
    events: list[CanonicalEvent] = []
    issues: list[QualityIssue] = []
    for row in rows:
        context = contexts.get(row["specimen_id"])
        if context is None:
            issues.append(_orphan_specimen_issue(row, "laboratory"))
            continue

        assay_run_id = row["assay_run_id"]
        if row["event_type"] == "result_verified":
            run_specimen_id = run_index.get(assay_run_id)
            if run_specimen_id is None:
                issues.append(
                    QualityIssue(
                        issue_code="ORPHAN_ASSAY_RUN",
                        severity="error",
                        details="No unique analyser run matched this verified result; record was quarantined",
                        case_id=context.case_id,
                        procedure_id=context.procedure_id,
                        specimen_id=context.specimen_id,
                        source_system="laboratory",
                        source_record_id=row["source_record_id"],
                        event_type=row["event_type"],
                    )
                )
                continue
            if run_specimen_id != row["specimen_id"]:
                issues.append(
                    QualityIssue(
                        issue_code="ASSAY_SPECIMEN_MISMATCH",
                        severity="error",
                        details="Verified result specimen does not match the analyser run; record was quarantined",
                        case_id=context.case_id,
                        procedure_id=context.procedure_id,
                        specimen_id=context.specimen_id,
                        source_system="laboratory",
                        source_record_id=row["source_record_id"],
                        event_type=row["event_type"],
                    )
                )
                continue
        events.append(
            CanonicalEvent(
                case_id=context.case_id,
                procedure_id=context.procedure_id,
                specimen_id=context.specimen_id,
                assay_run_id=assay_run_id,
                event_type=row["event_type"],
                event_time=parse_timestamp(row["event_time"], "event_time"),
                result_category=row["result_category"],
                source_system="laboratory",
                source_record_id=row["source_record_id"],
                source_field="event_time",
            )
        )
    return events, issues


def _canonicalise_analyser(
    rows: list[dict[str, str]],
    contexts: dict[str, SpecimenContext],
    invalid_runs: set[str],
) -> tuple[list[CanonicalEvent], list[QualityIssue]]:
    events: list[CanonicalEvent] = []
    issues: list[QualityIssue] = []
    event_fields = (
        ("assay_started", "run_started_at"),
        ("assay_completed", "run_completed_at"),
    )
    for row in rows:
        if row["assay_run_id"] in invalid_runs:
            continue
        context = contexts.get(row["specimen_id"])
        if context is None:
            issues.append(_orphan_specimen_issue(row, "osna_analyser"))
            continue
        for event_type, source_field in event_fields:
            is_completed = event_type == "assay_completed"
            events.append(
                CanonicalEvent(
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    assay_run_id=row["assay_run_id"],
                    run_sequence=row["run_sequence"],
                    repeat_of_run_id=row["repeat_of_run_id"],
                    repeat_reason=row["repeat_reason"],
                    event_type=event_type,
                    event_time=parse_timestamp(row[source_field], source_field),
                    instrument_result_code=(
                        row["instrument_result_code"] if is_completed else ""
                    ),
                    qc_status=row["qc_status"] if is_completed else "",
                    source_system="osna_analyser",
                    source_record_id=row["source_record_id"],
                    source_field=source_field,
                )
            )
    return events, issues


def _canonicalise_communication(
    rows: list[dict[str, str]],
    contexts: dict[str, SpecimenContext],
    run_index: dict[str, str],
) -> tuple[list[CanonicalEvent], list[QualityIssue]]:
    events: list[CanonicalEvent] = []
    issues: list[QualityIssue] = []
    for row in rows:
        context = contexts.get(row["specimen_id"])
        if context is None:
            issues.append(_orphan_specimen_issue(row, "communication"))
            continue

        run_specimen_id = run_index.get(row["assay_run_id"])
        if run_specimen_id is None:
            issues.append(
                QualityIssue(
                    issue_code="ORPHAN_ASSAY_RUN",
                    severity="error",
                    details="No unique analyser run matched this communication; record was quarantined",
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    source_system="communication",
                    source_record_id=row["source_record_id"],
                    event_type=row["event_type"],
                )
            )
            continue
        if run_specimen_id != row["specimen_id"]:
            issues.append(
                QualityIssue(
                    issue_code="ASSAY_SPECIMEN_MISMATCH",
                    severity="error",
                    details="Communication specimen does not match the analyser run; record was quarantined",
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    source_system="communication",
                    source_record_id=row["source_record_id"],
                    event_type=row["event_type"],
                )
            )
            continue

        events.append(
            CanonicalEvent(
                case_id=context.case_id,
                procedure_id=context.procedure_id,
                specimen_id=context.specimen_id,
                assay_run_id=row["assay_run_id"],
                event_type=row["event_type"],
                event_time=parse_timestamp(row["event_time"], "event_time"),
                communication_channel=row["channel"],
                source_system="communication",
                source_record_id=row["source_record_id"],
                source_field="event_time",
            )
        )
    return events, issues


def canonicalise_sources(
    loaded: LoadedSources,
) -> tuple[list[CanonicalEvent], dict[str, SpecimenContext], list[QualityIssue]]:
    """Match valid source rows and convert them to canonical events."""

    issues = list(loaded.issues)
    contexts, matching_issues = build_specimen_index(loaded.rows["theatre"])
    issues.extend(matching_issues)
    run_index, invalid_runs, run_issues = build_run_index(loaded.rows["osna_analyser"])
    issues.extend(run_issues)

    events = _canonicalise_theatre(loaded.rows["theatre"], contexts)

    laboratory_events, laboratory_issues = _canonicalise_laboratory(
        loaded.rows["laboratory"], contexts, run_index
    )
    events.extend(laboratory_events)
    issues.extend(laboratory_issues)

    analyser_events, analyser_issues = _canonicalise_analyser(
        loaded.rows["osna_analyser"], contexts, invalid_runs
    )
    events.extend(analyser_events)
    issues.extend(analyser_issues)

    communication_events, communication_issues = _canonicalise_communication(
        loaded.rows["communication"], contexts, run_index
    )
    events.extend(communication_events)
    issues.extend(communication_issues)

    events.sort(
        key=lambda event: (
            event.case_id,
            event.specimen_id,
            event.event_time,
            event.event_type,
            event.source_system,
            event.source_record_id,
        )
    )
    return events, contexts, issues


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _write_json(path: Path, value: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _issue_sort_key(issue: QualityIssue) -> tuple[str, ...]:
    return (
        issue.case_id,
        issue.specimen_id,
        issue.assay_run_id,
        issue.issue_code,
        issue.source_system,
        issue.source_record_id,
        issue.event_type,
    )


def _quality_status(issues: list[QualityIssue]) -> tuple[str, Counter[str]]:
    severity_counts = Counter(issue.severity for issue in issues)
    if severity_counts["error"]:
        return "errors_detected", severity_counts
    if severity_counts["warning"]:
        return "warnings_detected", severity_counts
    return "clean", severity_counts


def _load_with_mapping(
    input_dir: Path,
    mapping_path: Path | None,
) -> tuple[LoadedSources, SourceMapping | None]:
    mapping = load_source_mapping(mapping_path) if mapping_path else None
    return load_sources(Path(input_dir), mapping), mapping


def validate_source_files(
    input_dir: Path,
    mapping_path: Path | None = None,
) -> dict[str, object]:
    """Validate source contracts without linking events or writing outputs."""

    loaded, _ = _load_with_mapping(Path(input_dir), mapping_path)
    return build_source_readiness_report(loaded)


def run_pipeline(
    input_dir: Path,
    output_dir: Path,
    mapping_path: Path | None = None,
) -> dict[str, object]:
    """Run the local prototype and write deterministic analytical outputs."""

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    mapping = load_source_mapping(mapping_path) if mapping_path else None
    if mapping and mapping.data_classification != "synthetic":
        raise DataContractError(
            "Full pathway processing remains synthetic-only; use --validate-only "
            "for a governed clinical extract"
        )
    loaded = load_sources(input_dir, mapping)
    events, contexts, issues = canonicalise_sources(loaded)
    assay_runs, assay_run_issues, invalid_run_ids = build_assay_run_summaries(events)
    issues.extend(assay_run_issues)
    timelines, timeline_issues = build_timelines(contexts, events, invalid_run_ids)
    issues.extend(timeline_issues)
    procedures = build_procedure_summaries(timelines, assay_runs)
    metric_summary = build_metric_summary(timelines)
    issues.sort(key=_issue_sort_key)
    quality_summary = build_quality_summary(issues)

    status_counts = Counter(row["pathway_status"] for row in timelines)
    issue_counts = Counter(issue.issue_code for issue in issues)
    quality_status, severity_counts = _quality_status(issues)
    accepted_source_record_count = sum(len(rows) for rows in loaded.rows.values())
    summary: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "synthetic_data_only": True,
        "mapping_version": loaded.mapping_version,
        "mapping_filename": loaded.mapping_filename,
        "mapping_sha256": loaded.mapping_sha256,
        "data_classification": loaded.data_classification,
        "quality_status": quality_status,
        "input_record_count": loaded.input_record_count,
        "accepted_source_record_count": accepted_source_record_count,
        "source_validation_rejected_record_count": (
            loaded.input_record_count - accepted_source_record_count
        ),
        "canonical_event_count": len(events),
        "procedure_count": len(procedures),
        "specimen_count": len(contexts),
        "assay_run_count": len(assay_runs),
        "repeat_run_count": sum(int(row["run_sequence"] or 0) > 1 for row in assay_runs),
        "failed_qc_run_count": sum(row["qc_status"] == "fail" for row in assay_runs),
        "timeline_status_counts": dict(sorted(status_counts.items())),
        "exception_count": len(issues),
        "exception_counts_by_severity": dict(sorted(severity_counts.items())),
        "exception_counts_by_code": dict(sorted(issue_counts.items())),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    canonical_rows = [event.to_row() for event in events]
    exception_rows = [issue.to_row() for issue in issues]
    _write_csv(output_dir / "canonical_events.csv", CANONICAL_FIELDS, canonical_rows)
    _write_csv(output_dir / "case_timelines.csv", TIMELINE_FIELDS, timelines)
    _write_csv(output_dir / "assay_runs.csv", ASSAY_RUN_FIELDS, assay_runs)
    _write_csv(output_dir / "procedure_summaries.csv", PROCEDURE_FIELDS, procedures)
    _write_csv(
        output_dir / "metric_summary.csv",
        METRIC_SUMMARY_FIELDS,
        metric_summary,
    )
    _write_csv(output_dir / "exceptions.csv", EXCEPTION_FIELDS, exception_rows)
    _write_csv(
        output_dir / "quality_summary.csv",
        QUALITY_SUMMARY_FIELDS,
        quality_summary,
    )
    _write_json(output_dir / "pipeline_summary.json", summary)

    output_record_counts = {
        "assay_runs.csv": len(assay_runs),
        "canonical_events.csv": len(canonical_rows),
        "case_timelines.csv": len(timelines),
        "exceptions.csv": len(exception_rows),
        "metric_summary.csv": len(metric_summary),
        "pipeline_summary.json": 1,
        "procedure_summaries.csv": len(procedures),
        "quality_summary.csv": len(quality_summary),
    }
    manifest = build_run_manifest(
        output_dir,
        loaded,
        output_record_counts,
        canonical_schema_version=SCHEMA_VERSION,
        quality_status=quality_status,
        exception_count=len(issues),
    )
    _write_json(output_dir / "run_manifest.json", manifest)
    return summary
