"""Command-line entry point for the local synthetic prototype."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from osna_pipeline.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build synthetic OSNA pathway timelines, exceptions, and metrics."
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
    args = parser.parse_args()
    summary = run_pipeline(args.input, args.output)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
