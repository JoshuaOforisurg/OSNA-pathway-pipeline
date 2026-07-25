"""Command-line entry point for the local synthetic prototype."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from osna_pipeline.connectors import DataContractError
from osna_pipeline.pipeline import run_pipeline


EXIT_SUCCESS = 0
EXIT_QUALITY_ERRORS = 2
EXIT_DATA_CONTRACT_ERROR = 3


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return an automation-friendly process exit code."""

    parser = argparse.ArgumentParser(
        description=(
            "Build synthetic OSNA timelines, timing and quality summaries, and audit manifests."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/synthetic"),
        help="Directory containing the four required synthetic CSV extracts.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/outputs"),
        help="Directory for generated CSV and JSON outputs.",
    )
    parser.add_argument(
        "--fail-on-quality-errors",
        action="store_true",
        help=(
            "Write all outputs, then return exit code 2 when error-severity "
            "quality findings are present."
        ),
    )
    args = parser.parse_args(argv)
    try:
        summary = run_pipeline(args.input, args.output)
    except DataContractError as exc:
        error = {
            "status": "failed",
            "error_code": "DATA_CONTRACT_ERROR",
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
