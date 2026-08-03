# Command-line operation

The local command separates three outcomes that an automated runner must not confuse.

| Exit code | Meaning | Outputs |
| --- | --- | --- |
| `0` | Full processing or validation-only completed under the selected quality policy | Full mode writes all outputs; validation-only writes none |
| `2` | The selected mode completed, but `--fail-on-quality-errors` found error-severity issues | Full mode writes review outputs; validation-only writes none |
| `3` | An invalid mapping or required source contract prevented processing | Structured error on standard error; no analytical outputs |

Unexpected software or environment failures are not converted into data-quality findings. They
retain a normal Python failure and non-zero process status so the underlying defect remains
visible.

## Default reporting mode

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --output data/outputs
```

Reporting mode returns `0` when processing completes, even if `quality_status` is
`errors_detected`. This supports exploratory local review of deliberately incomplete and invalid
synthetic scenarios.

## Optional quality gate

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --output data/outputs \
  --fail-on-quality-errors
```

The quality gate writes every timeline, exception, summary, and manifest first. It then returns
`2` if any error-severity quality finding exists. Warning-only batches do not trigger the gate.

This is a technical automation policy, not a clinical threshold. It must not control surgery,
authorise an OSNA result, replace telephone communication, or be presented as evidence that a
real-world event did or did not occur.

## Mapping and validation-only mode

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --mapping config/source_mapping.example.json \
  --validate-only
```

Validation-only reads all four mapped sources and prints source-readiness report version `1.0.0`.
The report includes source-level accepted and rejected counts, the mapping identity, and these
aggregate measures for every mapped canonical field:

- its mapped source-column name;
- whether its value is always required or conditionally required;
- populated and missing value counts; and
- validation-finding counts grouped by rule.

The validation rules cover:

- mapped filenames and required headers;
- required row values;
- ISO 8601 timestamps with explicit offsets;
- controlled values after configured translations; and
- duplicate source-record identifiers.

The report declares that it contains no row identifiers or source values and that its counts are
not suppressed. Its structure is defined by
[`source_readiness_report.schema.json`](../../schemas/exports/source_readiness_report.schema.json).
Filename and source-column metadata remain visible. Aggregate and small-number counts may still be
sensitive, so terminal output must remain inside the approved environment.

Missing counts do not automatically mean errors. For example, an assay-run identifier is
conditionally required for `result_verified` but may legitimately be blank for
`specimen_received`. The field's `finding_counts` distinguish a rule failure from an expected
blank. `exception_count` counts rejected source rows, while `validation_finding_count` counts
individual field-rule failures; one rejected row can therefore contribute several findings.

It does not perform cross-source matching, so a source-valid orphan record or an invalid
cross-source timeline will not appear until full synthetic processing. The `--output` argument is
ignored and no output directory is created.

Mappings declared `governed_clinical` are restricted to validation-only. This restriction is a
technical safety boundary, not evidence of information-governance approval.

## Source-contract failure

A missing required source file or required CSV header returns structured JSON on standard error:

```json
{
  "error_code": "DATA_CONTRACT_ERROR",
  "message": "Required source file not found: ...",
  "status": "failed"
}
```

The pipeline does not create its output directory for this failure. Row-level validation problems
are different: valid rows continue through processing, rejected rows are counted, and the
resulting findings remain visible in the exception, quality, summary, and manifest outputs.

An invalid mapping returns the same exit code with `MAPPING_CONFIG_ERROR`.

## Continuous integration

`.github/workflows/ci.yml` runs for pushes and pull requests targeting `main`, and can also be
started manually. It tests Python 3.11, 3.12, and 3.13; compiles the Python sources; runs the full
automated test suite; validates the public contracts; confirms deterministic synthetic outputs;
builds a wheel; and smoke-tests the installed command.

The workflow has read-only repository permission, checks out without persisted credentials, uses
only synthetic repository fixtures, uploads no data or build artifacts, and performs no
deployment. Its GitHub-maintained actions are pinned to full commit SHAs. A passing workflow
demonstrates that the checked-in technical tests succeeded in GitHub's runner environment; it is
not clinical validation or approval for real-data processing.
