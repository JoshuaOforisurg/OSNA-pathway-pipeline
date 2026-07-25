# Command-line operation

The local command separates three outcomes that an automated runner must not confuse.

| Exit code | Meaning | Outputs |
| --- | --- | --- |
| `0` | Processing completed under the selected quality policy | All outputs written |
| `2` | Processing completed, but `--fail-on-quality-errors` found error-severity issues | All outputs written for review |
| `3` | A required source file or header contract prevented processing | Structured error on standard error; no analytical outputs |

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
