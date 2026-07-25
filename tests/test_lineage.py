import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from osna_pipeline.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"


def read_manifest(output_dir: Path) -> dict[str, object]:
    with (output_dir / "run_manifest.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


class BatchManifestTests(unittest.TestCase):
    def test_batch_id_changes_when_input_bytes_change(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)

            first_output = root / "first-output"
            run_pipeline(copied_input, first_output)
            first_manifest = read_manifest(first_output)

            theatre_path = copied_input / "theatre_events.csv"
            theatre_path.write_text(
                theatre_path.read_text(encoding="utf-8") + "\n",
                encoding="utf-8",
            )
            second_output = root / "second-output"
            run_pipeline(copied_input, second_output)
            second_manifest = read_manifest(second_output)

            self.assertNotEqual(
                first_manifest["batch_id"],
                second_manifest["batch_id"],
            )

    def test_manifest_counts_source_validation_rejections(self):
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

            output_dir = root / "output"
            summary = run_pipeline(copied_input, output_dir)
            manifest = read_manifest(output_dir)
            theatre_inventory = next(
                item
                for item in manifest["inputs"]
                if item["source_system"] == "theatre"
            )

            self.assertEqual(summary["accepted_source_record_count"], 35)
            self.assertEqual(summary["source_validation_rejected_record_count"], 1)
            self.assertEqual(manifest["accepted_source_record_count"], 35)
            self.assertEqual(
                manifest["source_validation_rejected_record_count"],
                1,
            )
            self.assertEqual(theatre_inventory["record_count"], 10)
            self.assertEqual(theatre_inventory["accepted_record_count"], 9)
            self.assertEqual(
                theatre_inventory["source_validation_rejected_record_count"],
                1,
            )


if __name__ == "__main__":
    unittest.main()
