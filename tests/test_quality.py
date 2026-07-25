import unittest

from osna_pipeline.domain.models import QualityIssue
from osna_pipeline.transformations import build_quality_summary


class QualitySummaryTests(unittest.TestCase):
    def test_groups_equivalent_findings_without_losing_distinct_sources(self):
        issues = [
            QualityIssue(
                issue_code="MISSING_EVENT",
                severity="warning",
                details="First specimen",
                event_type="theatre_acknowledged",
            ),
            QualityIssue(
                issue_code="MISSING_EVENT",
                severity="warning",
                details="Second specimen",
                event_type="theatre_acknowledged",
            ),
            QualityIssue(
                issue_code="MISSING_EVENT",
                severity="warning",
                details="Laboratory extract",
                source_system="laboratory",
                event_type="theatre_acknowledged",
            ),
        ]

        rows = build_quality_summary(issues)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["issue_count"], "2")
        self.assertEqual(rows[0]["source_system"], "")
        self.assertEqual(rows[1]["issue_count"], "1")
        self.assertEqual(rows[1]["source_system"], "laboratory")


if __name__ == "__main__":
    unittest.main()
