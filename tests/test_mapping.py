import csv
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from osna_pipeline.connectors import (
    DataContractError,
    MappingConfigError,
    load_source_mapping,
)
from osna_pipeline.pipeline import run_pipeline, validate_source_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"
EXAMPLE_MAPPING = PROJECT_ROOT / "config" / "source_mapping.example.json"


def read_example_mapping() -> dict[str, object]:
    with EXAMPLE_MAPPING.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_mapping(path: Path, document: dict[str, object]) -> None:
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class SourceMappingTests(unittest.TestCase):
    def test_mapping_file_must_use_json_suffix(self):
        with TemporaryDirectory() as temporary_directory:
            mapping_path = Path(temporary_directory) / "mapping.txt"
            write_mapping(mapping_path, read_example_mapping())

            with self.assertRaisesRegex(
                MappingConfigError,
                "filename must end with .json",
            ):
                load_source_mapping(mapping_path)

    def test_rejects_duplicate_json_keys(self):
        with TemporaryDirectory() as temporary_directory:
            mapping_path = Path(temporary_directory) / "duplicates.json"
            mapping_path.write_text(
                '{"mapping_version":"1.0.0","mapping_version":"1.0.0"}\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                MappingConfigError,
                "duplicated JSON key: mapping_version",
            ):
                load_source_mapping(mapping_path)

    def test_example_mapping_reproduces_the_builtin_contract(self):
        with TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "output"

            summary = run_pipeline(
                SYNTHETIC_INPUT,
                output_dir,
                EXAMPLE_MAPPING,
            )
            with (output_dir / "run_manifest.json").open(
                "r", encoding="utf-8"
            ) as handle:
                manifest = json.load(handle)

            self.assertEqual(summary["canonical_event_count"], 41)
            self.assertEqual(summary["mapping_version"], "1.0.0")
            self.assertEqual(
                summary["mapping_filename"],
                "source_mapping.example.json",
            )
            self.assertEqual(
                manifest["source_mapping"]["filename"],
                "source_mapping.example.json",
            )
            self.assertEqual(len(manifest["source_mapping"]["sha256"]), 64)

    def test_maps_renamed_columns_and_controlled_values(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            copied_input = root / "input"
            shutil.copytree(SYNTHETIC_INPUT, copied_input)
            mapping_document = read_example_mapping()
            theatre_mapping = mapping_document["sources"]["theatre"]
            theatre_mapping["filename"] = "fictional_theatre_export.csv"
            theatre_mapping["columns"] = {
                "source_record_id": "record_key",
                "case_id": "case_key",
                "procedure_id": "procedure_key",
                "specimen_id": "specimen_key",
                "event_type": "event_code",
                "event_time": "recorded_at",
            }
            theatre_mapping["value_mappings"] = {
                "event_type": {
                    "REMOVED": "specimen_removed",
                    "SENT": "specimen_sent",
                }
            }

            with (copied_input / "theatre_events.csv").open(
                "r", encoding="utf-8", newline=""
            ) as handle:
                source_rows = list(csv.DictReader(handle))
            alias_path = copied_input / "fictional_theatre_export.csv"
            with alias_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=(
                        "record_key",
                        "case_key",
                        "procedure_key",
                        "specimen_key",
                        "event_code",
                        "recorded_at",
                    ),
                )
                writer.writeheader()
                for row in source_rows:
                    writer.writerow(
                        {
                            "record_key": row["source_record_id"],
                            "case_key": row["case_id"],
                            "procedure_key": row["procedure_id"],
                            "specimen_key": row["specimen_id"],
                            "event_code": (
                                "REMOVED"
                                if row["event_type"] == "specimen_removed"
                                else "SENT"
                            ),
                            "recorded_at": row["event_time"],
                        }
                    )

            mapping_path = root / "renamed_mapping.json"
            write_mapping(mapping_path, mapping_document)
            output_dir = root / "output"
            readiness = validate_source_files(copied_input, mapping_path)
            summary = run_pipeline(copied_input, output_dir, mapping_path)

            self.assertEqual(
                readiness["source_counts"]["theatre"]["field_readiness"][
                    "event_type"
                ]["source_column"],
                "event_code",
            )
            self.assertEqual(summary["canonical_event_count"], 41)
            with (output_dir / "run_manifest.json").open(
                "r", encoding="utf-8"
            ) as handle:
                manifest = json.load(handle)
            theatre_input = next(
                item
                for item in manifest["inputs"]
                if item["source_system"] == "theatre"
            )
            self.assertEqual(
                theatre_input["filename"],
                "fictional_theatre_export.csv",
            )

    def test_rejects_unsafe_source_filename(self):
        for unsafe_filename in ("../theatre.csv", "..\\theatre.csv"):
            with self.subTest(unsafe_filename=unsafe_filename):
                with TemporaryDirectory() as temporary_directory:
                    mapping_document = read_example_mapping()
                    mapping_document["sources"]["theatre"][
                        "filename"
                    ] = unsafe_filename
                    mapping_path = Path(temporary_directory) / "unsafe.json"
                    write_mapping(mapping_path, mapping_document)

                    with self.assertRaisesRegex(
                        MappingConfigError,
                        "without directories",
                    ):
                        load_source_mapping(mapping_path)

    def test_rejects_duplicate_source_filenames(self):
        with TemporaryDirectory() as temporary_directory:
            mapping_document = read_example_mapping()
            mapping_document["sources"]["laboratory"][
                "filename"
            ] = "theatre_events.csv"
            mapping_path = Path(temporary_directory) / "duplicate-files.json"
            write_mapping(mapping_path, mapping_document)

            with self.assertRaisesRegex(
                MappingConfigError,
                "different CSV filename",
            ):
                load_source_mapping(mapping_path)

    def test_rejects_unsupported_canonical_value_mapping(self):
        with TemporaryDirectory() as temporary_directory:
            mapping_document = read_example_mapping()
            mapping_document["sources"]["theatre"]["value_mappings"] = {
                "event_type": {"SENT": "probably_sent"}
            }
            mapping_path = Path(temporary_directory) / "unsupported-value.json"
            write_mapping(mapping_path, mapping_document)

            with self.assertRaisesRegex(
                MappingConfigError,
                "unsupported canonical values: probably_sent",
            ):
                validate_source_files(SYNTHETIC_INPUT, mapping_path)

    def test_rejects_missing_canonical_mapping_field(self):
        with TemporaryDirectory() as temporary_directory:
            mapping_document = read_example_mapping()
            del mapping_document["sources"]["theatre"]["columns"]["case_id"]
            mapping_path = Path(temporary_directory) / "incomplete.json"
            write_mapping(mapping_path, mapping_document)

            with self.assertRaisesRegex(
                MappingConfigError,
                "missing canonical fields: case_id",
            ):
                run_pipeline(
                    SYNTHETIC_INPUT,
                    Path(temporary_directory) / "output",
                    mapping_path,
                )

    def test_governed_clinical_mapping_is_validation_only(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            mapping_document = read_example_mapping()
            mapping_document["data_classification"] = "governed_clinical"
            mapping_path = root / "governed.json"
            write_mapping(mapping_path, mapping_document)

            validation = validate_source_files(SYNTHETIC_INPUT, mapping_path)
            self.assertEqual(
                validation["data_classification"],
                "governed_clinical",
            )
            self.assertEqual(validation["quality_status"], "clean")

            with self.assertRaisesRegex(
                DataContractError,
                "Full pathway processing remains synthetic-only",
            ):
                run_pipeline(
                    root / "input-that-must-not-be-read",
                    root / "output",
                    mapping_path,
                )
            self.assertFalse((root / "output").exists())


if __name__ == "__main__":
    unittest.main()
