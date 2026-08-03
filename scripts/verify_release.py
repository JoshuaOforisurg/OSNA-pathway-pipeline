"""Verify public contracts and deterministic synthetic outputs for CI."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator, validate

from osna_pipeline.pipeline import run_pipeline, validate_source_files


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"
SYNTHETIC_INPUT = PROJECT_ROOT / "data" / "raw" / "synthetic"
EXAMPLE_MAPPING = PROJECT_ROOT / "config" / "source_mapping.example.json"


def _read_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    if not isinstance(document, dict):
        raise AssertionError(f"Expected a JSON object: {path}")
    return document


def _validate_schema_documents() -> None:
    schema_paths = sorted(SCHEMA_ROOT.rglob("*.json"))
    if not schema_paths:
        raise AssertionError("No JSON Schema documents were found")
    for schema_path in schema_paths:
        Draft202012Validator.check_schema(_read_json(schema_path))


def _assert_same_files(first: Path, second: Path) -> None:
    first_files = {
        path.relative_to(first): path
        for path in first.rglob("*")
        if path.is_file()
    }
    second_files = {
        path.relative_to(second): path
        for path in second.rglob("*")
        if path.is_file()
    }
    if set(first_files) != set(second_files):
        raise AssertionError("Repeated runs produced different output filenames")
    for relative_path in sorted(first_files):
        if first_files[relative_path].read_bytes() != second_files[
            relative_path
        ].read_bytes():
            raise AssertionError(
                f"Repeated runs produced different bytes: {relative_path}"
            )


def main() -> None:
    """Run dependency-light release checks using only synthetic repository data."""

    _validate_schema_documents()
    mapping_schema = _read_json(
        SCHEMA_ROOT / "config" / "source_mapping.schema.json"
    )
    readiness_schema = _read_json(
        SCHEMA_ROOT / "exports" / "source_readiness_report.schema.json"
    )
    manifest_schema = _read_json(
        SCHEMA_ROOT / "exports" / "run_manifest.schema.json"
    )
    validate(_read_json(EXAMPLE_MAPPING), mapping_schema)

    built_in_report = validate_source_files(SYNTHETIC_INPUT)
    mapped_report = validate_source_files(SYNTHETIC_INPUT, EXAMPLE_MAPPING)
    validate(built_in_report, readiness_schema)
    validate(mapped_report, readiness_schema)
    if mapped_report["quality_status"] != "clean":
        raise AssertionError("The mapped synthetic source batch must validate cleanly")
    if mapped_report["validation_finding_count"] != 0:
        raise AssertionError("The mapped synthetic source batch has readiness findings")
    if mapped_report["privacy_boundary"] != {
        "contains_row_identifiers": False,
        "contains_source_values": False,
        "counts_are_suppressed": False,
    }:
        raise AssertionError("The readiness-report privacy boundary changed")

    with TemporaryDirectory() as temporary_directory:
        temporary_root = Path(temporary_directory)
        first_output = temporary_root / "first"
        second_output = temporary_root / "second"
        first_summary = run_pipeline(
            SYNTHETIC_INPUT,
            first_output,
            EXAMPLE_MAPPING,
        )
        second_summary = run_pipeline(
            SYNTHETIC_INPUT,
            second_output,
            EXAMPLE_MAPPING,
        )
        if first_summary != second_summary:
            raise AssertionError("Repeated runs produced different summaries")
        _assert_same_files(first_output, second_output)
        manifest = _read_json(first_output / "run_manifest.json")
        validate(manifest, manifest_schema)
        if manifest["source_mapping"]["sha256"] != mapped_report[
            "mapping_sha256"
        ]:
            raise AssertionError("Readiness and manifest mapping checksums differ")

    print("Release verification passed using synthetic data only.")


if __name__ == "__main__":
    main()
