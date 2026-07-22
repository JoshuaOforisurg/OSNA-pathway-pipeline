from datetime import datetime
import unittest

from osna_pipeline.domain.models import CanonicalEvent
from osna_pipeline.transformations import build_assay_run_summaries


def assay_event(
    event_type: str,
    event_time: str,
    *,
    run_id: str = "RUN-SYN-TEST",
    run_sequence: str = "1",
    repeat_of_run_id: str = "",
    repeat_reason: str = "",
    qc_status: str = "",
    instrument_result_code: str = "",
    result_category: str = "",
    source_system: str = "osna_analyser",
) -> CanonicalEvent:
    return CanonicalEvent(
        case_id="CASE-SYN-TEST",
        procedure_id="PROC-SYN-TEST",
        specimen_id="SPEC-SYN-TEST",
        assay_run_id=run_id,
        run_sequence=run_sequence,
        repeat_of_run_id=repeat_of_run_id,
        repeat_reason=repeat_reason,
        event_type=event_type,
        event_time=datetime.fromisoformat(event_time),
        qc_status=qc_status,
        instrument_result_code=instrument_result_code,
        result_category=result_category,
        source_system=source_system,
        source_record_id=f"SOURCE-{event_type}",
        source_field="event_time",
    )


class AssayRunSummaryTests(unittest.TestCase):
    def test_rejects_verification_of_failed_qc_run(self):
        events = [
            assay_event("assay_started", "2026-07-20T09:00:00+01:00"),
            assay_event(
                "assay_completed",
                "2026-07-20T09:30:00+01:00",
                qc_status="fail",
                instrument_result_code="invalid",
            ),
            assay_event(
                "result_verified",
                "2026-07-20T09:35:00+01:00",
                result_category="invalid",
                source_system="laboratory",
            ),
        ]

        rows, issues, invalid_run_ids = build_assay_run_summaries(events)

        self.assertEqual(rows[0]["run_status"], "invalid")
        self.assertIn("RUN-SYN-TEST", invalid_run_ids)
        self.assertIn("VERIFIED_FAILED_QC_RUN", [issue.issue_code for issue in issues])

    def test_rejects_result_code_disagreement(self):
        events = [
            assay_event("assay_started", "2026-07-20T09:00:00+01:00"),
            assay_event(
                "assay_completed",
                "2026-07-20T09:30:00+01:00",
                qc_status="pass",
                instrument_result_code="positive",
            ),
            assay_event(
                "result_verified",
                "2026-07-20T09:35:00+01:00",
                result_category="negative",
                source_system="laboratory",
            ),
        ]

        _, issues, invalid_run_ids = build_assay_run_summaries(events)

        self.assertIn("RUN-SYN-TEST", invalid_run_ids)
        self.assertIn("RESULT_CODE_MISMATCH", [issue.issue_code for issue in issues])

    def test_rejects_repeat_with_unknown_parent(self):
        events = [
            assay_event(
                "assay_started",
                "2026-07-20T09:00:00+01:00",
                run_sequence="2",
                repeat_of_run_id="RUN-SYN-MISSING",
                repeat_reason="technical",
            ),
            assay_event(
                "assay_completed",
                "2026-07-20T09:30:00+01:00",
                run_sequence="2",
                repeat_of_run_id="RUN-SYN-MISSING",
                repeat_reason="technical",
                qc_status="pass",
                instrument_result_code="negative",
            ),
        ]

        rows, issues, invalid_run_ids = build_assay_run_summaries(events)

        self.assertEqual(rows[0]["run_status"], "invalid")
        self.assertIn("RUN-SYN-TEST", invalid_run_ids)
        self.assertIn("INVALID_REPEAT_RELATIONSHIP", [issue.issue_code for issue in issues])

    def test_does_not_select_a_run_when_two_results_are_verified(self):
        events = []
        for run_id, sequence, result, started_at, completed_at, verified_at in (
            (
                "RUN-SYN-TEST-A",
                "1",
                "negative",
                "2026-07-20T09:00:00+01:00",
                "2026-07-20T09:30:00+01:00",
                "2026-07-20T09:35:00+01:00",
            ),
            (
                "RUN-SYN-TEST-B",
                "2",
                "positive",
                "2026-07-20T10:00:00+01:00",
                "2026-07-20T10:30:00+01:00",
                "2026-07-20T10:35:00+01:00",
            ),
        ):
            events.extend(
                [
                    assay_event(
                        "assay_started",
                        started_at,
                        run_id=run_id,
                        run_sequence=sequence,
                        repeat_of_run_id="RUN-SYN-TEST-A" if sequence == "2" else "",
                        repeat_reason="technical" if sequence == "2" else "",
                    ),
                    assay_event(
                        "assay_completed",
                        completed_at,
                        run_id=run_id,
                        run_sequence=sequence,
                        repeat_of_run_id="RUN-SYN-TEST-A" if sequence == "2" else "",
                        repeat_reason="technical" if sequence == "2" else "",
                        qc_status="pass",
                        instrument_result_code=result,
                    ),
                    assay_event(
                        "result_verified",
                        verified_at,
                        run_id=run_id,
                        result_category=result,
                        source_system="laboratory",
                    ),
                ]
            )

        rows, _, _ = build_assay_run_summaries(events)

        self.assertEqual(
            [row["selected_for_result"] for row in rows],
            ["false", "false"],
        )


if __name__ == "__main__":
    unittest.main()
