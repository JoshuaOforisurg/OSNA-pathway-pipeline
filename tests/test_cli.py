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
            self.assertIn("missing required columns", error["message"])
            self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
