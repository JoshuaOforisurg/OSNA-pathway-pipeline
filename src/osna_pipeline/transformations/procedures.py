"""Aggregate specimen timelines into procedure-level service summaries."""

from __future__ import annotations

from collections import Counter, defaultdict


PROCEDURE_FIELDS = (
    "case_id",
    "procedure_id",
    "specimen_count",
    "complete_specimen_count",
    "incomplete_specimen_count",
    "invalid_specimen_count",
    "assay_run_count",
    "repeat_run_count",
    "failed_qc_run_count",
    "procedure_status",
)


def build_procedure_summaries(
    timelines: list[dict[str, str]],
    assay_runs: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Roll specimen and run state up without losing the underlying records."""

    timelines_by_procedure: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    runs_by_procedure: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in timelines:
        timelines_by_procedure[(row["case_id"], row["procedure_id"])].append(row)
    for row in assay_runs:
        runs_by_procedure[(row["case_id"], row["procedure_id"])].append(row)

    summaries: list[dict[str, str]] = []
    for (case_id, procedure_id), specimen_rows in sorted(timelines_by_procedure.items()):
        run_rows = runs_by_procedure.get((case_id, procedure_id), [])
        status_counts = Counter(row["pathway_status"] for row in specimen_rows)
        if status_counts["invalid"]:
            procedure_status = "invalid"
        elif status_counts["incomplete"]:
            procedure_status = "incomplete"
        else:
            procedure_status = "complete"

        summaries.append(
            {
                "case_id": case_id,
                "procedure_id": procedure_id,
                "specimen_count": str(len(specimen_rows)),
                "complete_specimen_count": str(status_counts["complete"]),
                "incomplete_specimen_count": str(status_counts["incomplete"]),
                "invalid_specimen_count": str(status_counts["invalid"]),
                "assay_run_count": str(len(run_rows)),
                "repeat_run_count": str(
                    sum(int(row["run_sequence"] or 0) > 1 for row in run_rows)
                ),
                "failed_qc_run_count": str(
                    sum(row["qc_status"] == "fail" for row in run_rows)
                ),
                "procedure_status": procedure_status,
            }
        )
    return summaries
