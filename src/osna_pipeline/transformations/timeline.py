"""Construct one transparent pathway row for each known specimen."""

from __future__ import annotations

from collections import defaultdict

from osna_pipeline.domain.models import CanonicalEvent, EVENT_ORDER, QualityIssue, SpecimenContext
from osna_pipeline.metrics import minutes_between
from osna_pipeline.validation import validate_specimen_timeline


TIMELINE_FIELDS = (
    "case_id",
    "procedure_id",
    "specimen_id",
    *EVENT_ORDER,
    "result_category",
    "instrument_result_code",
    "qc_status",
    "communication_channel",
    "pathway_status",
    "transport_minutes",
    "assay_minutes",
    "laboratory_turnaround_minutes",
    "communication_minutes",
    "acknowledgement_minutes",
    "total_pathway_minutes",
)


def _time(unique_events: dict[str, CanonicalEvent], event_type: str):
    event = unique_events.get(event_type)
    return event.event_time if event else None


def build_timelines(
    contexts: dict[str, SpecimenContext],
    events: list[CanonicalEvent],
) -> tuple[list[dict[str, str]], list[QualityIssue]]:
    """Build specimen timelines and return derived validation findings."""

    events_by_specimen: dict[str, list[CanonicalEvent]] = defaultdict(list)
    for event in events:
        events_by_specimen[event.specimen_id].append(event)

    timeline_rows: list[dict[str, str]] = []
    issues: list[QualityIssue] = []
    for specimen_id, context in sorted(contexts.items()):
        unique, specimen_issues, status = validate_specimen_timeline(
            context, events_by_specimen.get(specimen_id, [])
        )
        issues.extend(specimen_issues)

        row = {
            "case_id": context.case_id,
            "procedure_id": context.procedure_id,
            "specimen_id": context.specimen_id,
        }
        for event_type in EVENT_ORDER:
            event_time = _time(unique, event_type)
            row[event_type] = event_time.isoformat(timespec="seconds") if event_time else ""

        result_event = unique.get("result_verified")
        assay_completed_event = unique.get("assay_completed")
        communication_event = unique.get("result_communicated")
        row.update(
            {
                "result_category": result_event.result_category if result_event else "",
                "instrument_result_code": (
                    assay_completed_event.instrument_result_code if assay_completed_event else ""
                ),
                "qc_status": assay_completed_event.qc_status if assay_completed_event else "",
                "communication_channel": (
                    communication_event.communication_channel if communication_event else ""
                ),
                "pathway_status": status,
                "transport_minutes": minutes_between(
                    _time(unique, "specimen_sent"), _time(unique, "specimen_received")
                ),
                "assay_minutes": minutes_between(
                    _time(unique, "assay_started"), _time(unique, "assay_completed")
                ),
                "laboratory_turnaround_minutes": minutes_between(
                    _time(unique, "specimen_received"), _time(unique, "result_verified")
                ),
                "communication_minutes": minutes_between(
                    _time(unique, "result_verified"), _time(unique, "result_communicated")
                ),
                "acknowledgement_minutes": minutes_between(
                    _time(unique, "result_communicated"),
                    _time(unique, "theatre_acknowledged"),
                ),
                "total_pathway_minutes": minutes_between(
                    _time(unique, "specimen_removed"),
                    _time(unique, "theatre_acknowledged"),
                ),
            }
        )
        timeline_rows.append(row)
    return timeline_rows, issues
