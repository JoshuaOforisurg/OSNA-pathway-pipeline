import io
import json
import shutil
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from osna_pipeline.__main__ import (
    EXIT_DATA_CONTRACT_ERROR,
    EXIT_QUALITY_ERRORS,
    EXIT_SUCCESS,
    main,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"
EXAMPLE_MAPPING = PROJECT_ROOT / "config" / "source_mapping.example.json"


class CommandLineTests(unittest.TestCase):
    def test_default_run_reports_findings_without_failing(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "output"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(SYNTHETIC_INPUT),
                        "--output",
                        str(output_dir),
                    ]
                )

            summary = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, EXIT_SUCCESS)
            self.assertEqual(summary["quality_status"], "errors_detected")
            self.assertTrue((output_dir / "run_manifest.json").is_file())

    def test_quality_gate_fails_after_writing_review_outputs(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "output"

            with redirect_stdout(io.StringIO()):
                exit_code = main(
                    [
                        "--input",
                        str(SYNTHETIC_INPUT),
                        "--output",
                        str(output_dir),
                        "--fail-on-quality-errors",
                    ]
                )

            self.assertEqual(exit_code, EXIT_QUALITY_ERRORS)
            self.assertTrue((output_dir / "exceptions.csv").is_file())
            self.assertTrue((output_dir / "quality_summary.csv").is_file())
            self.assertTrue((output_dir / "run_manifest.json").is_file())

    def test_quality_gate_allows_warning_only_batch(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)
            laboratory_path = copied_input / "laboratory_events.csv"
            laboratory_rows = laboratory_path.read_text(encoding="utf-8").splitlines()
            laboratory_path.write_text(
                "\n".join(
                    row.replace(
                        "2026-07-20T11:08:00+01:00",
                        "2026-07-20T11:14:00+01:00",
                    )
                    for row in laboratory_rows
                    if not row.startswith("LAB-007,")
                )
                + "\n",
                encoding="utf-8",
            )
            output_dir = root / "output"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(copied_input),
                        "--output",
                        str(output_dir),
                        "--fail-on-quality-errors",
                    ]
                )

            summary = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, EXIT_SUCCESS)
            self.assertEqual(summary["quality_status"], "warnings_detected")
            self.assertEqual(summary["exception_counts_by_severity"], {"warning": 1})

    def test_validate_only_checks_sources_without_writing_outputs(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "unused-output"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(SYNTHETIC_INPUT),
                        "--output",
                        str(output_dir),
                        "--validate-only",
                    ]
                )

            summary = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, EXIT_SUCCESS)
            self.assertEqual(summary["mode"], "validate_only")
            self.assertEqual(summary["quality_status"], "clean")
            self.assertEqual(summary["input_record_count"], 36)
            self.assertEqual(summary["exception_count"], 0)
            self.assertFalse(output_dir.exists())

    def test_validate_only_reports_exact_mapping_identity(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "--input",
                    str(SYNTHETIC_INPUT),
                    "--mapping",
                    str(EXAMPLE_MAPPING),
                    "--validate-only",
                ]
            )

        summary = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, EXIT_SUCCESS)
        self.assertEqual(summary["mapping_version"], "1.0.0")
        self.assertEqual(
            summary["mapping_filename"],
            "source_mapping.example.json",
        )
        self.assertEqual(len(summary["mapping_sha256"]), 64)

    def test_validate_only_quality_gate_reports_rejected_rows(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)
            theatre_path = copied_input / "theatre_events.csv"
            theatre_path.write_text(
                theatre_path.read_text(encoding="utf-8").replace(
                    "2026-07-20T09:05:00+01:00",
                    "not-a-timestamp",
                    1,
                ),
                encoding="utf-8",
            )
            output_dir = root / "unused-output"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "--input",
                        str(copied_input),
                        "--output",
                        str(output_dir),
                        "--validate-only",
                        "--fail-on-quality-errors",
                    ]
                )

            summary = json.loads(stdout.getvalue())
            self.assertEqual(exit_code, EXIT_QUALITY_ERRORS)
            self.assertEqual(summary["quality_status"], "errors_detected")
            self.assertEqual(summary["accepted_source_record_count"], 35)
            self.assertEqual(
                summary["source_validation_rejected_record_count"],
                1,
            )
            self.assertFalse(output_dir.exists())

    def test_invalid_mapping_returns_structured_configuration_error(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            mapping_path = root / "invalid.json"
            mapping_path.write_text("{}\n", encoding="utf-8")
            output_dir = root / "unused-output"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--input",
                        str(SYNTHETIC_INPUT),
                        "--output",
                        str(output_dir),
                        "--mapping",
                        str(mapping_path),
                        "--validate-only",
                    ]
                )

            error = json.loads(stderr.getvalue())
            self.assertEqual(exit_code, EXIT_DATA_CONTRACT_ERROR)
            self.assertEqual(error["error_code"], "MAPPING_CONFIG_ERROR")
            self.assertFalse(output_dir.exists())

    def test_contract_failure_is_structured_and_does_not_write_outputs(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            missing_input = root / "missing-input"
            output_dir = root / "output"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--input",
                        str(missing_input),
                        "--output",
                        str(output_dir),
                    ]
                )

            error = json.loads(stderr.getvalue())
            self.assertEqual(exit_code, EXIT_DATA_CONTRACT_ERROR)
            self.assertEqual(error["status"], "failed")
            self.assertEqual(error["error_code"], "DATA_CONTRACT_ERROR")
            self.assertIn("Required source file not found", error["message"])
            self.assertFalse(output_dir.exists())

    def test_broken_header_is_a_contract_failure(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)
            theatre_path = copied_input / "theatre_events.csv"
            theatre_path.write_text(
                theatre_path.read_text(encoding="utf-8").replace(
                    "source_record_id,",
                    "unexpected_column,",
                    1,
                ),
                encoding="utf-8",
            )
            output_dir = root / "output"
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--input",
                        str(copied_input),
                        "--output",
                        str(output_dir),
                    ]
                )

            error = json.loads(stderr.getvalue())
            self.assertEqual(exit_code, EXIT_DATA_CONTRACT_ERROR)
            self.assertEqual(error["error_code"], "DATA_CONTRACT_ERROR")
            self.assertIn("missing mapped source columns", error["message"])
            self.assertFalse(output_dir.exists())

    def test_duplicate_header_is_a_contract_failure(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)
            theatre_path = copied_input / "theatre_events.csv"
            theatre_path.write_text(
                theatre_path.read_text(encoding="utf-8").replace(
                    "source_record_id,case_id,",
                    "source_record_id,case_id,case_id,",
                    1,
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with redirect_stderr(stderr):
                exit_code = main(
                    [
                        "--input",
                        str(copied_input),
                        "--validate-only",
                    ]
                )

            error = json.loads(stderr.getvalue())
            self.assertEqual(exit_code, EXIT_DATA_CONTRACT_ERROR)
            self.assertIn("contains duplicate columns: case_id", error["message"])


if __name__ == "__main__":
    unittest.main()
