"""Completeness, duplication, and chronological pathway rules."""

from __future__ import annotations

from collections import defaultdict

from osna_pipeline.domain.models import CanonicalEvent, EVENT_ORDER, QualityIssue, SpecimenContext


def validate_specimen_timeline(
    context: SpecimenContext,
    events: list[CanonicalEvent],
) -> tuple[dict[str, CanonicalEvent], list[QualityIssue], str]:
    """Return unique events, quality issues, and the specimen-level pathway status."""

    grouped: dict[str, list[CanonicalEvent]] = defaultdict(list)
    for event in events:
        grouped[event.event_type].append(event)

    unique_events: dict[str, CanonicalEvent] = {}
    issues: list[QualityIssue] = []
    has_error = False
    has_missing = False

    for event_type in EVENT_ORDER:
        matches = grouped.get(event_type, [])
        if not matches:
            has_missing = True
            issues.append(
                QualityIssue(
                    issue_code="MISSING_EVENT",
                    severity="warning",
                    details=f"No {event_type} record was available; absence does not prove the event did not occur",
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    event_type=event_type,
                )
            )
        elif len(matches) > 1:
            has_error = True
            issues.append(
                QualityIssue(
                    issue_code="DUPLICATE_EVENT",
                    severity="error",
                    details=f"More than one {event_type} record was available; no event was selected",
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    event_type=event_type,
                )
            )
        else:
            unique_events[event_type] = matches[0]

    for earlier_type, later_type in zip(EVENT_ORDER, EVENT_ORDER[1:]):
        earlier = unique_events.get(earlier_type)
        later = unique_events.get(later_type)
        if earlier and later and later.event_time < earlier.event_time:
            has_error = True
            issues.append(
                QualityIssue(
                    issue_code="INVALID_SEQUENCE",
                    severity="error",
                    details=(
                        f"{later_type} at {later.event_time.isoformat()} precedes "
                        f"{earlier_type} at {earlier.event_time.isoformat()}"
                    ),
                    case_id=context.case_id,
                    procedure_id=context.procedure_id,
                    specimen_id=context.specimen_id,
                    event_type=later_type,
                )
            )

    if has_error:
        status = "invalid"
    elif has_missing:
        status = "incomplete"
    else:
        status = "complete"
    return unique_events, issues, status
