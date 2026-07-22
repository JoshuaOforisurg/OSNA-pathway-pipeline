"""Core, source-neutral models for the OSNA pathway pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


SCHEMA_VERSION = "1.1.0"

EVENT_ORDER = (
    "specimen_removed",
    "specimen_sent",
    "specimen_received",
    "assay_started",
    "assay_completed",
    "result_verified",
    "result_communicated",
    "theatre_acknowledged",
)

CANONICAL_FIELDS = (
    "schema_version",
    "case_id",
    "procedure_id",
    "specimen_id",
    "assay_run_id",
    "run_sequence",
    "repeat_of_run_id",
    "repeat_reason",
    "event_type",
    "event_time",
    "result_category",
    "instrument_result_code",
    "qc_status",
    "communication_channel",
    "source_system",
    "source_record_id",
    "source_field",
)

EXCEPTION_FIELDS = (
    "issue_code",
    "severity",
    "case_id",
    "procedure_id",
    "specimen_id",
    "assay_run_id",
    "source_system",
    "source_record_id",
    "event_type",
    "details",
)


@dataclass(frozen=True)
class SpecimenContext:
    """The case and procedure identity established by the theatre source."""

    case_id: str
    procedure_id: str
    specimen_id: str


@dataclass(frozen=True)
class CanonicalEvent:
    """A common pathway event with an explicit source lineage."""

    case_id: str
    procedure_id: str
    specimen_id: str
    event_type: str
    event_time: datetime
    source_system: str
    source_record_id: str
    source_field: str
    assay_run_id: str = ""
    run_sequence: str = ""
    repeat_of_run_id: str = ""
    repeat_reason: str = ""
    result_category: str = ""
    instrument_result_code: str = ""
    qc_status: str = ""
    communication_channel: str = ""

    def to_row(self) -> dict[str, str]:
        return {
            "schema_version": SCHEMA_VERSION,
            "case_id": self.case_id,
            "procedure_id": self.procedure_id,
            "specimen_id": self.specimen_id,
            "assay_run_id": self.assay_run_id,
            "run_sequence": self.run_sequence,
            "repeat_of_run_id": self.repeat_of_run_id,
            "repeat_reason": self.repeat_reason,
            "event_type": self.event_type,
            "event_time": self.event_time.isoformat(timespec="seconds"),
            "result_category": self.result_category,
            "instrument_result_code": self.instrument_result_code,
            "qc_status": self.qc_status,
            "communication_channel": self.communication_channel,
            "source_system": self.source_system,
            "source_record_id": self.source_record_id,
            "source_field": self.source_field,
        }


@dataclass(frozen=True)
class QualityIssue:
    """A source, matching, completeness, or sequence problem."""

    issue_code: str
    severity: str
    details: str
    case_id: str = ""
    procedure_id: str = ""
    specimen_id: str = ""
    assay_run_id: str = ""
    source_system: str = ""
    source_record_id: str = ""
    event_type: str = ""

    def to_row(self) -> dict[str, str]:
        return {field: getattr(self, field) for field in EXCEPTION_FIELDS}
