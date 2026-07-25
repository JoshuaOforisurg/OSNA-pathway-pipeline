"""Build a deterministic receipt for each processed input batch."""

from __future__ import annotations

import hashlib
from pathlib import Path

from osna_pipeline.checksums import sha256_file
from osna_pipeline.connectors.csv_sources import CONTRACTS, LoadedSources
from osna_pipeline.version import __version__


MANIFEST_VERSION = "1.0.0"


def _input_inventory(
    loaded: LoadedSources,
) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    for source_system, contract in CONTRACTS.items():
        record_count = loaded.source_record_counts[source_system]
        accepted_record_count = len(loaded.rows[source_system])
        inventory.append(
            {
                "source_system": source_system,
                "filename": contract.filename,
                "sha256": loaded.source_file_hashes[source_system],
                "record_count": record_count,
                "accepted_record_count": accepted_record_count,
                "source_validation_rejected_record_count": (
                    record_count - accepted_record_count
                ),
            }
        )
    return inventory


def _batch_id(inputs: list[dict[str, object]]) -> str:
    digest = hashlib.sha256()
    for item in inputs:
        digest.update(str(item["source_system"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["filename"]).encode("utf-8"))
        digest.update(b"\0")
        digest.update(str(item["sha256"]).encode("ascii"))
        digest.update(b"\0")
    return f"osna-{digest.hexdigest()[:20]}"


def _output_inventory(
    output_dir: Path,
    output_record_counts: dict[str, int],
) -> list[dict[str, object]]:
    return [
        {
            "filename": filename,
            "sha256": sha256_file(output_dir / filename),
            "record_count": output_record_counts[filename],
        }
        for filename in sorted(output_record_counts)
    ]


def build_run_manifest(
    output_dir: Path,
    loaded: LoadedSources,
    output_record_counts: dict[str, int],
    *,
    canonical_schema_version: str,
    quality_status: str,
    exception_count: int,
) -> dict[str, object]:
    """Describe the exact inputs and outputs of one deterministic pipeline run."""

    inputs = _input_inventory(loaded)
    accepted_source_record_count = sum(len(rows) for rows in loaded.rows.values())
    return {
        "manifest_version": MANIFEST_VERSION,
        "pipeline_version": __version__,
        "canonical_schema_version": canonical_schema_version,
        "batch_id": _batch_id(inputs),
        "synthetic_data_only": True,
        "quality_status": quality_status,
        "input_record_count": loaded.input_record_count,
        "accepted_source_record_count": accepted_source_record_count,
        "source_validation_rejected_record_count": (
            loaded.input_record_count - accepted_source_record_count
        ),
        "exception_count": exception_count,
        "inputs": inputs,
        "outputs": _output_inventory(output_dir, output_record_counts),
    }
