# Data

Only synthetic data is permitted here during early development.

- `raw/synthetic/` contains small, deliberately authored fictional source extracts.
- `processed/validated/` will contain schema-valid intermediate records.
- `processed/curated/` will contain linked pathway tables.
- `outputs/` will contain generated run audits, specimen timelines, procedure summaries, reports,
  quality summaries, metrics, and deterministic batch manifests.

Generated outputs are ignored by default. The supplied synthetic CSV files are versionable test
inputs and must use only the visibly fictional `*-SYN-*` identifiers.

Never add identifiable or pseudonymised patient data to this directory or repository.
Approved clinical extracts must remain in the organisation's governed environment and outside this
public working tree, including when using validation-only mode.
