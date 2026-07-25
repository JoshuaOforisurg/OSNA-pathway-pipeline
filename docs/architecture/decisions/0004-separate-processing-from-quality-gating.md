# ADR 0004: Separate completed processing from quality gating

- **Status:** Proposed for review
- **Date:** 2026-07-25

## Context

The synthetic test batch deliberately contains errors and warnings. A pipeline can process that
batch successfully while still discovering data that requires review. Treating every quality
finding as a software crash would prevent evidence files from being produced; always returning
success would make scheduled jobs unable to enforce a review policy.

## Decision

Keep reporting mode as the default. When processing completes, it writes all outputs and returns
success regardless of the reported quality status.

Provide an explicit `--fail-on-quality-errors` policy for automation. It writes the same outputs
and then returns a distinct exit code when error-severity findings exist. Source-contract failures
that prevent processing use a separate exit code and structured error.

## Consequences

- Review evidence exists even when the optional quality gate fails.
- Exploratory synthetic runs remain convenient.
- Scheduled jobs can require explicit handling of error-severity findings.
- Data-quality status is not confused with software execution status.
- The gate remains a technical workflow control and cannot be used as a clinical decision.
