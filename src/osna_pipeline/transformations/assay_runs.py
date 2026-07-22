"""Build auditable summaries for initial and repeat OSNA assay runs."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from osna_pipeline.domain.models import CanonicalEvent, QualityIssue
from osna_pipeline.metrics import minutes_between


ASSAY_RUN_FIELDS = (
    "case_id",
    "procedure_id",
    "specimen_id",
    "assay_run_id",
    "run_sequence",
    "repeat_of_run_id",
    "repeat_reason",
    "run_started_at",
    "run_completed_at",
    "qc_status",
    "instrument_result_code",
    "result_verified_at",
    "verified_result_category",
    "selected_for_result",
    "run_status",
    "assay_minutes",
)


def _run_issue(
    code: str,
    details: str,
    event: CanonicalEvent,
    event_type: str = "",
) -> QualityIssue:
    return QualityIssue(
        issue_code=code,
        severity="error",
        details=details,
        case_id=event.case_id,
        procedure_id=event.procedure_id,
        specimen_id=event.specimen_id,
        assay_run_id=event.assay_run_id,
        event_type=event_type,
    )


def build_assay_run_summaries(
    events: list[CanonicalEvent],
) -> tuple[list[dict[str, str]], list[QualityIssue], set[str]]:
    """Summarise each run without hiding failed or repeated attempts."""

    grouped: dict[str, list[CanonicalEvent]] = defaultdict(list)
    for event in events:
        if event.assay_run_id:
            grouped[event.assay_run_id].append(event)

    rows: list[dict[str, str]] = []
    issues: list[QualityIssue] = []
    invalid_run_ids: set[str] = set()
    verification_run_ids_by_specimen: dict[str, list[str]] = defaultdict(list)
    for event in events:
        if event.event_type == "result_verified" and event.assay_run_id:
            verification_run_ids_by_specimen[event.specimen_id].append(event.assay_run_id)
    selected_run_ids = {
        run_ids[0]
        for run_ids in verification_run_ids_by_specimen.values()
        if len(run_ids) == 1
    }

    for run_id, run_events in sorted(grouped.items()):
        starts = [event for event in run_events if event.event_type == "assay_started"]
        completions = [event for event in run_events if event.event_type == "assay_completed"]
        verifications = [event for event in run_events if event.event_type == "result_verified"]
        representative = (starts or completions or run_events)[0]
        run_invalid = False

        if len(starts) != 1:
            run_invalid = True
            issues.append(
                _run_issue(
                    "INVALID_RUN_EVENT_COUNT",
                    f"Expected one assay_started event but found {len(starts)}",
                    representative,
                    "assay_started",
                )
            )
        if len(completions) != 1:
            run_invalid = True
            issues.append(
                _run_issue(
                    "INVALID_RUN_EVENT_COUNT",
                    f"Expected one assay_completed event but found {len(completions)}",
                    representative,
                    "assay_completed",
                )
            )
        if len(verifications) > 1:
            run_invalid = True
            issues.append(
                _run_issue(
                    "DUPLICATE_RUN_VERIFICATION",
                    "More than one laboratory verification refers to this assay run",
                    representative,
                    "result_verified",
                )
            )

        start = starts[0] if len(starts) == 1 else None
        completion = completions[0] if len(completions) == 1 else None
        verification = verifications[0] if len(verifications) == 1 else None
        metadata = start or completion or representative

        if start and completion and completion.event_time < start.event_time:
            run_invalid = True
            issues.append(
                _run_issue(
                    "INVALID_ASSAY_RUN_SEQUENCE",
                    "Assay completion precedes assay start",
                    representative,
                    "assay_completed",
                )
            )
        if completion and verification and completion.qc_status == "fail":
            run_invalid = True
            issues.append(
                _run_issue(
                    "VERIFIED_FAILED_QC_RUN",
                    "A laboratory verification refers to an assay run with failed QC",
                    representative,
                    "result_verified",
                )
            )
        if (
            completion
            and verification
            and completion.instrument_result_code
            and verification.result_category
            and completion.instrument_result_code != verification.result_category
        ):
            run_invalid = True
            issues.append(
                _run_issue(
                    "RESULT_CODE_MISMATCH",
                    "Instrument result code and laboratory-verified result category differ",
                    representative,
                    "result_verified",
                )
            )

        if run_invalid:
            run_status = "invalid"
            invalid_run_ids.add(run_id)
        elif verification:
            run_status = "verified"
        elif completion and completion.qc_status == "fail":
            run_status = "qc_failed"
        elif completion:
            run_status = "completed"
        else:
            run_status = "incomplete"

        rows.append(
            {
                "case_id": representative.case_id,
                "procedure_id": representative.procedure_id,
                "specimen_id": representative.specimen_id,
                "assay_run_id": run_id,
                "run_sequence": metadata.run_sequence,
                "repeat_of_run_id": metadata.repeat_of_run_id,
                "repeat_reason": metadata.repeat_reason,
                "run_started_at": (
                    start.event_time.isoformat(timespec="seconds") if start else ""
                ),
                "run_completed_at": (
                    completion.event_time.isoformat(timespec="seconds") if completion else ""
                ),
                "qc_status": completion.qc_status if completion else "",
                "instrument_result_code": (
                    completion.instrument_result_code if completion else ""
                ),
                "result_verified_at": (
                    verification.event_time.isoformat(timespec="seconds")
                    if verification
                    else ""
                ),
                "verified_result_category": (
                    verification.result_category if verification else ""
                ),
                "selected_for_result": "true" if run_id in selected_run_ids else "false",
                "run_status": run_status,
                "assay_minutes": minutes_between(
                    start.event_time if start else None,
                    completion.event_time if completion else None,
                ),
            }
        )

    row_by_run = {row["assay_run_id"]: row for row in rows}
    sequence_index: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rows:
        sequence_index[(row["specimen_id"], row["run_sequence"])].append(row["assay_run_id"])

    for run_ids in sequence_index.values():
        if len(run_ids) > 1:
            for run_id in run_ids:
                row = row_by_run[run_id]
                invalid_run_ids.add(run_id)
                row["run_status"] = "invalid"
                representative = grouped[run_id][0]
                issues.append(
                    _run_issue(
                        "DUPLICATE_RUN_SEQUENCE",
                        "More than one assay run has this sequence number for the specimen",
                        representative,
                    )
                )

    for row in rows:
        if not row["run_sequence"] or int(row["run_sequence"]) == 1:
            continue
        run_id = row["assay_run_id"]
        parent = row_by_run.get(row["repeat_of_run_id"])
        representative = grouped[run_id][0]
        relationship_error = ""
        if parent is None:
            relationship_error = "Referenced previous assay run does not exist"
        elif parent["specimen_id"] != row["specimen_id"]:
            relationship_error = "Repeated run references a run from a different specimen"
        elif int(parent["run_sequence"]) >= int(row["run_sequence"]):
            relationship_error = "Repeated run must reference an earlier run sequence"
        elif parent["run_completed_at"] and row["run_started_at"]:
            repeat_started_at = datetime.fromisoformat(row["run_started_at"])
            parent_completed_at = datetime.fromisoformat(parent["run_completed_at"])
            if repeat_started_at < parent_completed_at:
                relationship_error = "Repeated run starts before the referenced run completes"

        if relationship_error:
            invalid_run_ids.add(run_id)
            row["run_status"] = "invalid"
            issues.append(
                _run_issue(
                    "INVALID_REPEAT_RELATIONSHIP",
                    relationship_error,
                    representative,
                )
            )

    rows.sort(
        key=lambda row: (
            row["case_id"],
            row["procedure_id"],
            row["specimen_id"],
            int(row["run_sequence"] or 0),
            row["assay_run_id"],
        )
    )
    return rows, issues, invalid_run_ids
