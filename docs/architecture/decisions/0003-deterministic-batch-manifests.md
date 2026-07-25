# ADR 0003: Produce deterministic batch manifests

- **Status:** Proposed for review
- **Date:** 2026-07-24

## Context

Event-level source identifiers show where an accepted canonical event originated, but they do not
identify the complete group of files processed in a pipeline run. A reviewer also needs to know
whether two runs used the exact same input bytes and produced the same output bytes.

Adding the computer's current time to local outputs would make identical synthetic runs differ
without changing their clinical or technical content.

## Decision

Write a deterministic `run_manifest.json` containing:

- one content-derived batch identifier;
- logical input and output filenames;
- SHA-256 checksums and record counts;
- accepted and source-validation-rejected input counts;
- pipeline, manifest, and canonical schema versions; and
- the overall data-quality status and exception count.

The local manifest contains no wall-clock execution timestamp or absolute filesystem path.
Each input is checksummed before and after it is read; processing stops if the file changes during
ingestion.

## Consequences

- Exact synthetic batches and outputs can be compared reproducibly.
- A changed byte in any source file produces a different batch identifier.
- File paths cannot leak workstation details into the manifest.
- A changing source file cannot silently be described as the batch that was processed.
- Checksums demonstrate byte identity, not clinical correctness or source authenticity.
- A future governed orchestrator must separately record execution time, actor or service identity,
  environment, access controls, and retention metadata.
