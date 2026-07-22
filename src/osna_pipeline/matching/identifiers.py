"""Build exact synthetic identifier indexes without probabilistic matching."""

from __future__ import annotations

from osna_pipeline.domain.models import QualityIssue, SpecimenContext


def build_specimen_index(
    theatre_rows: list[dict[str, str]],
) -> tuple[dict[str, SpecimenContext], list[QualityIssue]]:
    """Map each specimen to exactly one case and procedure."""

    index: dict[str, SpecimenContext] = {}
    ambiguous: set[str] = set()
    issues: list[QualityIssue] = []

    for row in theatre_rows:
        context = SpecimenContext(
            case_id=row["case_id"],
            procedure_id=row["procedure_id"],
            specimen_id=row["specimen_id"],
        )
        previous = index.get(context.specimen_id)
        if previous is None:
            index[context.specimen_id] = context
        elif previous != context and context.specimen_id not in ambiguous:
            ambiguous.add(context.specimen_id)
            issues.append(
                QualityIssue(
                    issue_code="AMBIGUOUS_SPECIMEN_CONTEXT",
                    severity="error",
                    details="Specimen maps to more than one case or procedure; records were quarantined",
                    specimen_id=context.specimen_id,
                    source_system="theatre",
                    source_record_id=row["source_record_id"],
                    event_type=row["event_type"],
                )
            )

    for specimen_id in ambiguous:
        index.pop(specimen_id, None)
    return index, issues


def build_run_index(
    analyser_rows: list[dict[str, str]],
) -> tuple[dict[str, str], set[str], list[QualityIssue]]:
    """Map each assay run to one specimen and reject duplicated run identifiers."""

    index: dict[str, str] = {}
    invalid_runs: set[str] = set()
    issues: list[QualityIssue] = []
    for row in analyser_rows:
        run_id = row["assay_run_id"]
        if run_id in index and run_id not in invalid_runs:
            invalid_runs.add(run_id)
            issues.append(
                QualityIssue(
                    issue_code="DUPLICATE_ASSAY_RUN",
                    severity="error",
                    details="Assay run identifier occurs more than once; run records were quarantined",
                    specimen_id=row["specimen_id"],
                    source_system="osna_analyser",
                    source_record_id=row["source_record_id"],
                )
            )
        else:
            index[run_id] = row["specimen_id"]

    for run_id in invalid_runs:
        index.pop(run_id, None)
    return index, invalid_runs, issues
