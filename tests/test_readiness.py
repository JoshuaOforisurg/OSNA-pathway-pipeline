import csv
from collections.abc import Callable
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from osna_pipeline.pipeline import validate_source_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"
EXAMPLE_MAPPING = PROJECT_ROOT / "config" / "source_mapping.example.json"


def rewrite_csv(
    path: Path,
    update_rows: Callable[[list[dict[str, str]]], None],
) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = tuple(reader.fieldnames or ())
        rows = list(reader)
    update_rows(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class SourceReadinessReportTests(unittest.TestCase):
    def test_clean_report_contains_aggregate_field_completeness_only(self):
        report = validate_source_files(SYNTHETIC_INPUT, EXAMPLE_MAPPING)

        self.assertEqual(report["report_version"], "1.0.0")
        self.assertEqual(
            report["privacy_boundary"],
            {
                "contains_row_identifiers": False,
                "contains_source_values": False,
                "counts_are_suppressed": False,
            },
        )
        self.assertEqual(report["validation_finding_count"], 0)
        self.assertEqual(
            report["input_record_count"],
            report["accepted_source_record_count"]
            + report["source_validation_rejected_record_count"],
        )
        source_finding_total = 0
        for source in report["source_counts"].values():
            self.assertEqual(
                source["record_count"],
                source["accepted_record_count"]
                + source["rejected_record_count"],
            )
            source_finding_total += source["validation_finding_count"]
            for field in source["field_readiness"].values():
                self.assertEqual(
                    field["record_count"],
                    field["populated_value_count"]
                    + field["missing_value_count"],
                )
        self.assertEqual(
            report["validation_finding_count"],
            source_finding_total,
        )
        laboratory_fields = report["source_counts"]["laboratory"][
            "field_readiness"
        ]
        self.assertEqual(
            laboratory_fields["assay_run_id"],
            {
                "source_column": "assay_run_id",
                "requirement": "conditional",
                "record_count": 11,
                "populated_value_count": 5,
                "missing_value_count": 6,
                "finding_counts": {},
            },
        )

        serialized = json.dumps(report)
        for fictional_identifier in (
            "CASE-SYN",
            "PROC-SYN",
            "SPEC-SYN",
            "RUN-SYN",
            "THR-",
            "LAB-",
        ):
            self.assertNotIn(fictional_identifier, serialized)

    def test_report_groups_validation_findings_by_source_and_field(self):
        with TemporaryDirectory() as temporary_directory:
            copied_input = Path(temporary_directory) / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)

            def introduce_findings(rows):
                rows[0]["case_id"] = ""
                rows[0]["event_type"] = "UNPUBLISHED-SOURCE-VALUE"
                rows[0]["event_time"] = "not-a-timestamp"
                rows[1]["source_record_id"] = rows[0]["source_record_id"]

            rewrite_csv(
                copied_input / "theatre_events.csv",
                introduce_findings,
            )
            report = validate_source_files(copied_input)

        self.assertEqual(report["quality_status"], "errors_detected")
        self.assertEqual(report["accepted_source_record_count"], 34)
        self.assertEqual(
            report["source_validation_rejected_record_count"],
            2,
        )
        self.assertEqual(report["validation_finding_count"], 4)
        self.assertEqual(report["exception_count"], 2)

        theatre = report["source_counts"]["theatre"]
        self.assertEqual(theatre["accepted_record_count"], 8)
        self.assertEqual(theatre["rejected_record_count"], 2)
        self.assertEqual(theatre["validation_finding_count"], 4)
        fields = theatre["field_readiness"]
        self.assertEqual(fields["case_id"]["missing_value_count"], 1)
        self.assertEqual(
            fields["case_id"]["finding_counts"],
            {"REQUIRED_VALUE_MISSING": 1},
        )
        self.assertEqual(
            fields["event_time"]["finding_counts"],
            {"INVALID_TIMESTAMP": 1},
        )
        self.assertEqual(
            fields["event_type"]["finding_counts"],
            {"UNSUPPORTED_CONTROLLED_VALUE": 1},
        )
        self.assertEqual(
            fields["source_record_id"]["finding_counts"],
            {"DUPLICATE_SOURCE_RECORD_ID": 1},
        )
        self.assertNotIn("UNPUBLISHED-SOURCE-VALUE", json.dumps(report))

    def test_report_distinguishes_conditional_missing_values(self):
        with TemporaryDirectory() as temporary_directory:
            copied_input = Path(temporary_directory) / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)

            def remove_verified_result_fields(rows):
                verified = next(
                    row
                    for row in rows
                    if row["event_type"] == "result_verified"
                )
                verified["assay_run_id"] = ""
                verified["result_category"] = ""

            rewrite_csv(
                copied_input / "laboratory_events.csv",
                remove_verified_result_fields,
            )
            report = validate_source_files(copied_input)

        laboratory = report["source_counts"]["laboratory"]
        self.assertEqual(laboratory["rejected_record_count"], 1)
        self.assertEqual(laboratory["validation_finding_count"], 2)
        fields = laboratory["field_readiness"]
        self.assertEqual(
            fields["assay_run_id"]["finding_counts"],
            {"CONDITIONAL_VALUE_MISSING": 1},
        )
        self.assertEqual(
            fields["result_category"]["finding_counts"],
            {"CONDITIONAL_VALUE_MISSING": 1},
        )

    def test_report_distinguishes_missing_timezone_offset(self):
        with TemporaryDirectory() as temporary_directory:
            copied_input = Path(temporary_directory) / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)

            def remove_timezone_offset(rows):
                rows[0]["event_time"] = "2026-07-20T09:05:00"

            rewrite_csv(
                copied_input / "theatre_events.csv",
                remove_timezone_offset,
            )
            report = validate_source_files(copied_input)

        event_time = report["source_counts"]["theatre"]["field_readiness"][
            "event_time"
        ]
        self.assertEqual(
            event_time["finding_counts"],
            {"TIMEZONE_OFFSET_MISSING": 1},
        )

    def test_report_groups_analyser_sequence_and_repeat_rules(self):
        with TemporaryDirectory() as temporary_directory:
            copied_input = Path(temporary_directory) / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)

            def introduce_analyser_findings(rows):
                rows[0]["run_sequence"] = "0"
                rows[1]["repeat_of_run_id"] = "UNPUBLISHED-RUN-VALUE"
                rows[1]["repeat_reason"] = "technical"
                repeat_row = next(
                    row for row in rows if row["run_sequence"] == "2"
                )
                repeat_row["repeat_of_run_id"] = ""
                repeat_row["repeat_reason"] = ""

            rewrite_csv(
                copied_input / "osna_runs.csv",
                introduce_analyser_findings,
            )
            report = validate_source_files(copied_input)

        analyser = report["source_counts"]["osna_analyser"]
        self.assertEqual(analyser["rejected_record_count"], 3)
        self.assertEqual(analyser["validation_finding_count"], 5)
        fields = analyser["field_readiness"]
        self.assertEqual(
            fields["run_sequence"]["finding_counts"],
            {"INVALID_POSITIVE_INTEGER": 1},
        )
        expected_repeat_findings = {
            "CONDITIONAL_VALUE_MISSING": 1,
            "INITIAL_RUN_REPEAT_METADATA": 1,
        }
        self.assertEqual(
            fields["repeat_of_run_id"]["finding_counts"],
            expected_repeat_findings,
        )
        self.assertEqual(
            fields["repeat_reason"]["finding_counts"],
            expected_repeat_findings,
        )
        self.assertNotIn("UNPUBLISHED-RUN-VALUE", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
