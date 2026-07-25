import csv
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from osna_pipeline.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"


class PipelineIntegrationTests(unittest.TestCase):
    def test_supplied_batch_produces_expected_timelines_and_exceptions(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            summary = run_pipeline(SYNTHETIC_INPUT, output_dir)

            self.assertEqual(summary["input_record_count"], 36)
            self.assertEqual(summary["canonical_event_count"], 41)
            self.assertEqual(summary["procedure_count"], 4)
            self.assertEqual(summary["specimen_count"], 5)
            self.assertEqual(summary["assay_run_count"], 6)
            self.assertEqual(summary["repeat_run_count"], 1)
            self.assertEqual(summary["failed_qc_run_count"], 1)
            self.assertEqual(summary["accepted_source_record_count"], 36)
            self.assertEqual(summary["source_validation_rejected_record_count"], 0)
            self.assertEqual(summary["quality_status"], "errors_detected")
            self.assertEqual(
                summary["exception_counts_by_severity"],
                {"error": 2, "warning": 1},
            )
            self.assertEqual(
                summary["timeline_status_counts"],
                {"complete": 3, "incomplete": 1, "invalid": 1},
            )
            self.assertEqual(
                summary["exception_counts_by_code"],
                {"INVALID_SEQUENCE": 1, "MISSING_EVENT": 1, "ORPHAN_SPECIMEN": 1},
            )

            with (output_dir / "case_timelines.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                timelines = {row["specimen_id"]: row for row in csv.DictReader(handle)}

            self.assertEqual(timelines["SPEC-SYN-001"]["pathway_status"], "complete")
            self.assertEqual(timelines["SPEC-SYN-001"]["transport_minutes"], "9.0")
            self.assertEqual(timelines["SPEC-SYN-002"]["pathway_status"], "incomplete")
            self.assertEqual(timelines["SPEC-SYN-002"]["total_pathway_minutes"], "")
            self.assertEqual(timelines["SPEC-SYN-003"]["pathway_status"], "invalid")
            self.assertEqual(timelines["SPEC-SYN-003"]["transport_minutes"], "")
            self.assertEqual(timelines["SPEC-SYN-004A"]["pathway_status"], "complete")
            self.assertEqual(
                timelines["SPEC-SYN-004A"]["selected_assay_run_id"], "RUN-SYN-004B"
            )
            self.assertEqual(timelines["SPEC-SYN-004A"]["assay_run_count"], "2")
            self.assertEqual(timelines["SPEC-SYN-004A"]["repeat_run_count"], "1")
            self.assertEqual(timelines["SPEC-SYN-004A"]["failed_qc_run_count"], "1")

            with (output_dir / "assay_runs.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                assay_runs = {row["assay_run_id"]: row for row in csv.DictReader(handle)}

            self.assertEqual(assay_runs["RUN-SYN-004A"]["run_status"], "qc_failed")
            self.assertEqual(assay_runs["RUN-SYN-004A"]["selected_for_result"], "false")
            self.assertEqual(assay_runs["RUN-SYN-004B"]["run_status"], "verified")
            self.assertEqual(assay_runs["RUN-SYN-004B"]["repeat_reason"], "qc_failure")

            with (output_dir / "procedure_summaries.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                procedures = {row["procedure_id"]: row for row in csv.DictReader(handle)}

            self.assertEqual(procedures["PROC-SYN-004"]["specimen_count"], "2")
            self.assertEqual(procedures["PROC-SYN-004"]["assay_run_count"], "3")
            self.assertEqual(procedures["PROC-SYN-004"]["repeat_run_count"], "1")
            self.assertEqual(procedures["PROC-SYN-004"]["failed_qc_run_count"], "1")
            self.assertEqual(procedures["PROC-SYN-004"]["procedure_status"], "complete")

            with (output_dir / "canonical_events.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                canonical_events = list(csv.DictReader(handle))

            verified = next(
                row
                for row in canonical_events
                if row["specimen_id"] == "SPEC-SYN-001"
                and row["event_type"] == "result_verified"
            )
            completed = next(
                row
                for row in canonical_events
                if row["specimen_id"] == "SPEC-SYN-001"
                and row["event_type"] == "assay_completed"
            )
            self.assertEqual(verified["source_system"], "laboratory")
            self.assertEqual(verified["result_category"], "positive")
            self.assertEqual(completed["source_system"], "osna_analyser")
            self.assertEqual(completed["instrument_result_code"], "positive")
            self.assertEqual(completed["result_category"], "")

            with (output_dir / "pipeline_summary.json").open("r", encoding="utf-8") as handle:
                written_summary = json.load(handle)
            self.assertEqual(written_summary, summary)

            with (output_dir / "quality_summary.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                quality_rows = {
                    row["issue_code"]: row for row in csv.DictReader(handle)
                }
            self.assertEqual(quality_rows["INVALID_SEQUENCE"]["severity"], "error")
            self.assertEqual(quality_rows["ORPHAN_SPECIMEN"]["source_system"], "laboratory")
            self.assertEqual(quality_rows["MISSING_EVENT"]["severity"], "warning")

            with (output_dir / "metric_summary.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                metric_rows = {
                    row["metric_name"]: row for row in csv.DictReader(handle)
                }
            self.assertEqual(metric_rows["transport_minutes"]["observed_value_count"], "4")
            self.assertEqual(metric_rows["transport_minutes"]["median"], "9.0")
            self.assertEqual(metric_rows["transport_minutes"]["p90"], "13.2")
            self.assertEqual(
                metric_rows["total_pathway_minutes"]["observed_value_count"],
                "3",
            )
            self.assertEqual(
                metric_rows["total_pathway_minutes"]["missing_value_count"],
                "1",
            )
            self.assertEqual(metric_rows["total_pathway_minutes"]["p90"], "72.4")
            for row in metric_rows.values():
                self.assertEqual(row["excluded_invalid_specimen_count"], "1")

            with (output_dir / "run_manifest.json").open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)

            self.assertEqual(manifest["manifest_version"], "1.0.0")
            self.assertEqual(manifest["pipeline_version"], "0.3.0")
            self.assertEqual(manifest["canonical_schema_version"], "1.1.0")
            self.assertEqual(manifest["quality_status"], "errors_detected")
            self.assertEqual(manifest["input_record_count"], 36)
            self.assertEqual(manifest["accepted_source_record_count"], 36)
            self.assertEqual(
                manifest["source_validation_rejected_record_count"],
                0,
            )
            self.assertTrue(manifest["batch_id"].startswith("osna-"))
            self.assertEqual(len(manifest["inputs"]), 4)
            for item in manifest["inputs"]:
                input_path = SYNTHETIC_INPUT / item["filename"]
                self.assertEqual(
                    item["sha256"],
                    hashlib.sha256(input_path.read_bytes()).hexdigest(),
                )
            self.assertEqual(
                {item["filename"] for item in manifest["outputs"]},
                {
                    "assay_runs.csv",
                    "canonical_events.csv",
                    "case_timelines.csv",
                    "exceptions.csv",
                    "metric_summary.csv",
                    "pipeline_summary.json",
                    "procedure_summaries.csv",
                    "quality_summary.csv",
                },
            )
            for item in manifest["outputs"]:
                output_path = output_dir / item["filename"]
                self.assertEqual(
                    item["sha256"],
                    hashlib.sha256(output_path.read_bytes()).hexdigest(),
                )

    def test_same_input_produces_identical_files(self):
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            run_pipeline(SYNTHETIC_INPUT, Path(first))
            run_pipeline(SYNTHETIC_INPUT, Path(second))

            for filename in (
                "canonical_events.csv",
                "case_timelines.csv",
                "assay_runs.csv",
                "procedure_summaries.csv",
                "exceptions.csv",
                "metric_summary.csv",
                "quality_summary.csv",
                "pipeline_summary.json",
                "run_manifest.json",
            ):
                self.assertEqual(
                    (Path(first) / filename).read_bytes(),
                    (Path(second) / filename).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
