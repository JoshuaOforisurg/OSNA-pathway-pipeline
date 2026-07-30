"""Read, map, and validate the four event-shaped CSV source extracts."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from osna_pipeline.checksums import sha256_file
from osna_pipeline.connectors.mapping import (
    MAPPING_VERSION,
    MappingConfigError,
    SourceFileMapping,
    SourceMapping,
)
from osna_pipeline.domain.models import QualityIssue


@dataclass(frozen=True)
class SourceContract:
    filename: str
    required_fields: tuple[str, ...]
    timestamp_fields: tuple[str, ...]
    controlled_fields: dict[str, frozenset[str]]
    optional_value_fields: frozenset[str] = frozenset()


@dataclass(frozen=True)
class RowValidationFinding:
    """One field-level validation failure without retaining its source value."""

    field_name: str
    rule_code: str
    message: str


@dataclass(frozen=True)
class SourceFieldReadiness:
    """Aggregate completeness and rule findings for one mapped canonical field."""

    source_column: str
    requirement: str
    record_count: int
    populated_value_count: int
    finding_counts: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "source_column": self.source_column,
            "requirement": self.requirement,
            "record_count": self.record_count,
            "populated_value_count": self.populated_value_count,
            "missing_value_count": self.record_count - self.populated_value_count,
            "finding_counts": dict(sorted(self.finding_counts.items())),
        }


@dataclass(frozen=True)
class LoadedSources:
    rows: dict[str, list[dict[str, str]]]
    issues: list[QualityIssue]
    input_record_count: int
    source_record_counts: dict[str, int]
    source_file_hashes: dict[str, str]
    source_filenames: dict[str, str]
    mapping_version: str
    mapping_filename: str
    mapping_sha256: str
    data_classification: str
    source_field_readiness: dict[str, dict[str, SourceFieldReadiness]]


class DataContractError(ValueError):
    """Raised when a required source file or header contract is unavailable."""


class TimestampValidationError(ValueError):
    """A timestamp failure carrying its stable aggregate reporting code."""

    def __init__(self, message: str, rule_code: str) -> None:
        super().__init__(message)
        self.rule_code = rule_code


CONTRACTS = {
    "theatre": SourceContract(
        filename="theatre_events.csv",
        required_fields=(
            "source_record_id",
            "case_id",
            "procedure_id",
            "specimen_id",
            "event_type",
            "event_time",
        ),
        timestamp_fields=("event_time",),
        controlled_fields={
            "event_type": frozenset({"specimen_removed", "specimen_sent"})
        },
    ),
    "laboratory": SourceContract(
        filename="laboratory_events.csv",
        required_fields=(
            "source_record_id",
            "specimen_id",
            "assay_run_id",
            "event_type",
            "event_time",
            "result_category",
        ),
        timestamp_fields=("event_time",),
        controlled_fields={
            "event_type": frozenset({"specimen_received", "result_verified"}),
            "result_category": frozenset({"positive", "negative", "invalid"}),
        },
        optional_value_fields=frozenset({"assay_run_id", "result_category"}),
    ),
    "osna_analyser": SourceContract(
        filename="osna_runs.csv",
        required_fields=(
            "source_record_id",
            "assay_run_id",
            "specimen_id",
            "run_sequence",
            "repeat_of_run_id",
            "repeat_reason",
            "run_started_at",
            "run_completed_at",
            "instrument_result_code",
            "qc_status",
        ),
        timestamp_fields=("run_started_at", "run_completed_at"),
        controlled_fields={
            "instrument_result_code": frozenset({"positive", "negative", "invalid"}),
            "qc_status": frozenset({"pass", "fail"}),
            "repeat_reason": frozenset({"qc_failure", "inhibited", "technical", "other"}),
        },
        optional_value_fields=frozenset({"repeat_of_run_id", "repeat_reason"}),
    ),
    "communication": SourceContract(
        filename="communication_events.csv",
        required_fields=(
            "source_record_id",
            "specimen_id",
            "assay_run_id",
            "event_type",
            "event_time",
            "channel",
        ),
        timestamp_fields=("event_time",),
        controlled_fields={
            "event_type": frozenset({"result_communicated", "theatre_acknowledged"}),
            "channel": frozenset({"telephone", "electronic", "in_person"}),
        },
    ),
}


def parse_timestamp(value: str, field_name: str) -> datetime:
    """Parse an ISO 8601 timestamp and require an explicit time-zone offset."""

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise TimestampValidationError(
            f"{field_name} is not a valid ISO 8601 timestamp",
            "INVALID_TIMESTAMP",
        ) from exc
    if parsed.utcoffset() is None:
        raise TimestampValidationError(
            f"{field_name} must include a time-zone offset",
            "TIMEZONE_OFFSET_MISSING",
        )
    return parsed


def _validate_row(
    row: dict[str, str],
    contract: SourceContract,
) -> list[RowValidationFinding]:
    findings: list[RowValidationFinding] = []
    for field in contract.required_fields:
        if field not in contract.optional_value_fields and not row.get(field, "").strip():
            findings.append(
                RowValidationFinding(
                    field_name=field,
                    rule_code="REQUIRED_VALUE_MISSING",
                    message=f"{field} is required",
                )
            )

    if contract.filename == "laboratory_events.csv" and row.get("event_type") == "result_verified":
        for field in ("assay_run_id", "result_category"):
            if not row.get(field, "").strip():
                findings.append(
                    RowValidationFinding(
                        field_name=field,
                        rule_code="CONDITIONAL_VALUE_MISSING",
                        message=f"{field} is required for result_verified",
                    )
                )

    if contract.filename == "osna_runs.csv":
        sequence_value = row.get("run_sequence", "")
        try:
            run_sequence = int(sequence_value)
            if run_sequence < 1:
                raise ValueError
        except ValueError:
            findings.append(
                RowValidationFinding(
                    field_name="run_sequence",
                    rule_code="INVALID_POSITIVE_INTEGER",
                    message="run_sequence must be a positive integer",
                )
            )
        else:
            repeat_of_run_id = row.get("repeat_of_run_id", "")
            repeat_reason = row.get("repeat_reason", "")
            if run_sequence == 1 and repeat_of_run_id:
                findings.append(
                    RowValidationFinding(
                        field_name="repeat_of_run_id",
                        rule_code="INITIAL_RUN_REPEAT_METADATA",
                        message="repeat_of_run_id must be empty for initial runs",
                    )
                )
            if run_sequence == 1 and repeat_reason:
                findings.append(
                    RowValidationFinding(
                        field_name="repeat_reason",
                        rule_code="INITIAL_RUN_REPEAT_METADATA",
                        message="repeat_reason must be empty for initial runs",
                    )
                )
            if run_sequence > 1:
                if not repeat_of_run_id:
                    findings.append(
                        RowValidationFinding(
                            field_name="repeat_of_run_id",
                            rule_code="CONDITIONAL_VALUE_MISSING",
                            message="repeat_of_run_id is required for repeat runs",
                        )
                    )
                if not repeat_reason:
                    findings.append(
                        RowValidationFinding(
                            field_name="repeat_reason",
                            rule_code="CONDITIONAL_VALUE_MISSING",
                            message="repeat_reason is required for repeat runs",
                        )
                    )

    for field in contract.timestamp_fields:
        value = row.get(field, "").strip()
        if value:
            try:
                parse_timestamp(value, field)
            except TimestampValidationError as exc:
                findings.append(
                    RowValidationFinding(
                        field_name=field,
                        rule_code=exc.rule_code,
                        message=str(exc),
                    )
                )

    for field, allowed_values in contract.controlled_fields.items():
        value = row.get(field, "").strip()
        if value and value not in allowed_values:
            findings.append(
                RowValidationFinding(
                    field_name=field,
                    rule_code="UNSUPPORTED_CONTROLLED_VALUE",
                    message=f"{field} has unsupported value {value!r}",
                )
            )
    return findings


def _field_requirement(contract: SourceContract, field_name: str) -> str:
    return (
        "conditional"
        if field_name in contract.optional_value_fields
        else "required"
    )


def _mapping_for_source(
    source_system: str,
    contract: SourceContract,
    mapping: SourceMapping | None,
) -> SourceFileMapping:
    if mapping is None:
        return SourceFileMapping(
            filename=contract.filename,
            columns={field: field for field in contract.required_fields},
            value_mappings={},
        )

    source_mapping = mapping.sources[source_system]
    required_fields = set(contract.required_fields)
    mapped_fields = set(source_mapping.columns)
    missing_fields = sorted(required_fields - mapped_fields)
    unexpected_fields = sorted(mapped_fields - required_fields)
    if missing_fields:
        raise MappingConfigError(
            f"{source_system}.columns is missing canonical fields: "
            f"{', '.join(missing_fields)}"
        )
    if unexpected_fields:
        raise MappingConfigError(
            f"{source_system}.columns contains unsupported canonical fields: "
            f"{', '.join(unexpected_fields)}"
        )

    unsupported_value_fields = sorted(
        set(source_mapping.value_mappings) - set(contract.controlled_fields)
    )
    if unsupported_value_fields:
        raise MappingConfigError(
            f"{source_system}.value_mappings may only target controlled fields; "
            f"unsupported: {', '.join(unsupported_value_fields)}"
        )
    for field, field_mapping in source_mapping.value_mappings.items():
        allowed_values = contract.controlled_fields[field]
        invalid_targets = sorted(
            {
                canonical_value
                for canonical_value in field_mapping.values()
                if canonical_value and canonical_value not in allowed_values
            }
        )
        if invalid_targets:
            raise MappingConfigError(
                f"{source_system}.value_mappings.{field} contains unsupported "
                f"canonical values: {', '.join(invalid_targets)}"
            )
    return source_mapping


def _source_path(input_dir: Path, filename: str) -> Path:
    path = input_dir / filename
    if not path.is_file():
        raise DataContractError(f"Required source file not found: {path}")
    if path.resolve().parent != input_dir.resolve():
        raise DataContractError(
            f"Required source file resolves outside the input directory: {path}"
        )
    return path


def _load_one(
    input_dir: Path,
    source_system: str,
    source_mapping: SourceFileMapping,
) -> tuple[
    list[dict[str, str]],
    list[QualityIssue],
    int,
    dict[str, SourceFieldReadiness],
]:
    contract = CONTRACTS[source_system]
    path = _source_path(input_dir, source_mapping.filename)

    valid_rows: list[dict[str, str]] = []
    issues: list[QualityIssue] = []
    seen_record_ids: set[str] = set()
    record_count = 0
    populated_counts: Counter[str] = Counter()
    finding_counts: dict[str, Counter[str]] = {
        field: Counter() for field in contract.required_fields
    }

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = tuple(reader.fieldnames or ())
        duplicate_headers = sorted(
            {header for header in headers if headers.count(header) > 1}
        )
        if duplicate_headers:
            raise DataContractError(
                f"{source_mapping.filename} contains duplicate columns: "
                f"{', '.join(duplicate_headers)}"
            )
        missing_headers = [
            source_mapping.columns[field]
            for field in contract.required_fields
            if source_mapping.columns[field] not in headers
        ]
        if missing_headers:
            raise DataContractError(
                f"{source_mapping.filename} is missing mapped source columns: "
                f"{', '.join(missing_headers)}"
            )

        for row_number, original_row in enumerate(reader, start=2):
            record_count += 1
            row = {
                canonical_field: (
                    original_row.get(source_column) or ""
                ).strip()
                for canonical_field, source_column in source_mapping.columns.items()
            }
            for field, field_mapping in source_mapping.value_mappings.items():
                if row[field] in field_mapping:
                    row[field] = field_mapping[row[field]]
            for field in contract.required_fields:
                if row[field]:
                    populated_counts[field] += 1
            record_id = row.get("source_record_id", "")
            findings = _validate_row(row, contract)
            if record_id and record_id in seen_record_ids:
                findings.append(
                    RowValidationFinding(
                        field_name="source_record_id",
                        rule_code="DUPLICATE_SOURCE_RECORD_ID",
                        message=(
                            "source_record_id is duplicated within this source"
                        ),
                    )
                )
            if record_id:
                seen_record_ids.add(record_id)
            for finding in findings:
                finding_counts[finding.field_name][finding.rule_code] += 1
            if findings:
                issues.append(
                    QualityIssue(
                        issue_code="SOURCE_VALIDATION_ERROR",
                        severity="error",
                        details=(
                            f"Row {row_number}: "
                            f"{'; '.join(finding.message for finding in findings)}"
                        ),
                        specimen_id=row.get("specimen_id", ""),
                        source_system=source_system,
                        source_record_id=record_id,
                        event_type=row.get("event_type", ""),
                    )
                )
                continue
            valid_rows.append(row)

    field_readiness = {
        field: SourceFieldReadiness(
            source_column=source_mapping.columns[field],
            requirement=_field_requirement(contract, field),
            record_count=record_count,
            populated_value_count=populated_counts[field],
            finding_counts=dict(finding_counts[field]),
        )
        for field in contract.required_fields
    }
    return valid_rows, issues, record_count, field_readiness


def load_sources(
    input_dir: Path,
    mapping: SourceMapping | None = None,
) -> LoadedSources:
    """Load all required extracts, quarantining invalid rows as quality issues."""

    input_dir = Path(input_dir)
    source_rows: dict[str, list[dict[str, str]]] = {}
    all_issues: list[QualityIssue] = []
    total_records = 0
    source_record_counts: dict[str, int] = {}
    source_file_hashes: dict[str, str] = {}
    source_filenames: dict[str, str] = {}
    source_field_readiness: dict[str, dict[str, SourceFieldReadiness]] = {}
    for source_system, contract in CONTRACTS.items():
        source_mapping = _mapping_for_source(source_system, contract, mapping)
        source_path = _source_path(input_dir, source_mapping.filename)
        checksum_before_load = sha256_file(source_path)
        rows, issues, count, field_readiness = _load_one(
            input_dir,
            source_system,
            source_mapping,
        )
        checksum_after_load = sha256_file(source_path)
        if checksum_before_load != checksum_after_load:
            raise DataContractError(
                f"Source file changed while it was being read: {source_path}"
            )
        source_rows[source_system] = rows
        all_issues.extend(issues)
        total_records += count
        source_record_counts[source_system] = count
        source_file_hashes[source_system] = checksum_before_load
        source_filenames[source_system] = source_mapping.filename
        source_field_readiness[source_system] = field_readiness
    return LoadedSources(
        rows=source_rows,
        issues=all_issues,
        input_record_count=total_records,
        source_record_counts=source_record_counts,
        source_file_hashes=source_file_hashes,
        source_filenames=source_filenames,
        mapping_version=mapping.mapping_version if mapping else MAPPING_VERSION,
        mapping_filename=mapping.filename if mapping else "",
        mapping_sha256=mapping.sha256 if mapping else "",
        data_classification=(
            mapping.data_classification if mapping else "synthetic"
        ),
        source_field_readiness=source_field_readiness,
    )
