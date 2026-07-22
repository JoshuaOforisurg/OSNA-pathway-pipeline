import unittest

from osna_pipeline.matching import build_specimen_index


class SpecimenMatchingTests(unittest.TestCase):
    def test_rejects_specimen_mapped_to_two_cases(self):
        rows = [
            {
                "source_record_id": "THR-001",
                "case_id": "CASE-SYN-001",
                "procedure_id": "PROC-SYN-001",
                "specimen_id": "SPEC-SYN-001",
                "event_type": "specimen_removed",
            },
            {
                "source_record_id": "THR-002",
                "case_id": "CASE-SYN-999",
                "procedure_id": "PROC-SYN-999",
                "specimen_id": "SPEC-SYN-001",
                "event_type": "specimen_sent",
            },
        ]

        index, issues = build_specimen_index(rows)

        self.assertNotIn("SPEC-SYN-001", index)
        self.assertEqual([issue.issue_code for issue in issues], ["AMBIGUOUS_SPECIMEN_CONTEXT"])


if __name__ == "__main__":
    unittest.main()
