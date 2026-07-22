# Data

Only synthetic data is permitted here during early development.

- `raw/synthetic/` contains small, deliberately authored fictional source extracts.
- `processed/validated/` will contain schema-valid intermediate records.
- `processed/curated/` will contain linked pathway tables.
- `outputs/` will contain generated reports and metrics.

Generated outputs are ignored by default. The supplied synthetic CSV files are versionable test
inputs and must use only the visibly fictional `*-SYN-*` identifiers.

Never add identifiable or pseudonymised patient data to this directory or repository.
