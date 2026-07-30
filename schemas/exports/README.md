# Export contracts

The local `run_manifest.json` contract describes the exact source files and analytical outputs in
one synthetic batch. It records logical filenames, record counts, SHA-256 checksums, the pipeline
version, the canonical schema version, the source-mapping version and checksum, and a deterministic
batch identifier. Blank mapping filename and checksum values mean the built-in identity mapping
was used.

The manifest is a reproducibility and technical-audit record. It is not a clinical result report,
does not prove that a real-world event occurred, and deliberately contains no wall-clock execution
time. A governed scheduler can add execution identity and timestamps if the pipeline is deployed.
The manifest does not checksum itself; its output inventory covers the eight analytical and
quality outputs generated before the manifest is written.

The `quality_summary.csv` contract groups detailed exception rows by:

- severity;
- issue code;
- source system, when known;
- event type, when known; and
- issue count.

It is a review aid. `exceptions.csv` remains the detailed evidence, and neither output proves that
a missing extract record means the real-world clinical event did not occur.

The `metric_summary.csv` contract provides descriptive statistics for the six documented pathway
durations. It reports eligible, observed, missing, and excluded counts alongside the minimum,
median, linearly interpolated 90th percentile, and maximum. It excludes invalid pathways entirely,
allows incomplete pathways to contribute individual available metrics, and never treats missing
values as zero.

Formal registry, COSD mapping, or other external clinical contracts will be added only after the
receiving use case, information standard, lawful basis, field ownership, and governance are
confirmed.

The `source_readiness_report.schema.json` contract describes the JSON printed by validation-only
mode. It records mapping identity, source acceptance counts, and per-field completeness and rule
findings. It contains no row identifiers or source values and is not written automatically. Its
filenames, column metadata, and unsuppressed aggregate counts must still be handled within the
approved environment.
