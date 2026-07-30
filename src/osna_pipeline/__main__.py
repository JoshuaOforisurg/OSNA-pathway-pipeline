"""Command-line entry point for the local synthetic prototype."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from osna_pipeline.connectors import DataContractError, MappingConfigError
from osna_pipeline.pipeline import run_pipeline, validate_source_files


EXIT_SUCCESS = 0
EXIT_QUALITY_ERRORS = 2
EXIT_DATA_CONTRACT_ERROR = 3


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an automation-friendly process exit code."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate event-shaped OSNA extracts or build synthetic pathway outputs."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/synthetic"),
        help="Directory containing the four required event-shaped CSV extracts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/outputs"),
        help="Directory for full-run outputs; ignored by --validate-only.",
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        help="Optional JSON file mapping source filenames, columns, and controlled values.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Print an aggregate mapped-source readiness report without linking "
            "pathways, exposing row values, or writing outputs."
        ),
    )
    parser.add_argument(
        "--fail-on-quality-errors",
        action="store_true",
        help=(
            "Return exit code 2 when the selected mode completes with "
            "error-severity quality findings."
        ),
    )
    args = parser.parse_args(argv)
    try:
        if args.validate_only:
            summary = validate_source_files(args.input, args.mapping)
        else:
            summary = run_pipeline(args.input, args.output, args.mapping)
    except (DataContractError, MappingConfigError) as exc:
        error = {
            "status": "failed",
            "error_code": (
                "MAPPING_CONFIG_ERROR"
                if isinstance(exc, MappingConfigError)
                else "DATA_CONTRACT_ERROR"
            ),
            "message": str(exc),
        }
        print(json.dumps(error, indent=2, sort_keys=True), file=sys.stderr)
        return EXIT_DATA_CONTRACT_ERROR

    print(json.dumps(summary, indent=2, sort_keys=True))
    if (
        args.fail_on_quality_errors
        and summary.get("quality_status") == "errors_detected"
    ):
        return EXIT_QUALITY_ERRORS
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
