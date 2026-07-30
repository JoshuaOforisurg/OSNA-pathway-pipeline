# ADR 0006: Report aggregate source readiness without row values

- **Status:** Proposed for review
- **Date:** 2026-07-30

## Context

A pass-or-fail source check is insufficient for planning a retrospective evaluation. Reviewers
need to know which mapped fields are populated, which are conditionally applicable, and which
validation rules fail. Printing rejected rows or distinct source values could expose clinical
information and is unnecessary for the first readiness decision.

## Decision

Validation-only mode will print a versioned JSON readiness report containing:

- the mapping version, filename, checksum, and declared data classification;
- accepted and rejected record counts for each source;
- the mapped source-column name and requirement type for each canonical field;
- populated and missing value counts; and
- validation-finding counts grouped by field and rule.

The report will contain no row identifiers or source values. It will not perform cross-source
matching, calculate pathway metrics, or write a report file automatically. Its privacy metadata
will state explicitly that aggregate counts are not suppressed.

## Consequences

- Field availability and contract failures can be assessed before pathway reconstruction.
- Conditional blanks remain distinguishable from validation failures.
- An unexpected controlled value contributes a count but its value is not disclosed.
- Filenames, column names, and aggregate counts may still be sensitive.
- The operator must keep terminal output in the governed environment and apply any required
  small-number or disclosure controls before sharing it.
- A later approved profiling use case may require separately reviewed statistics; they are not
  implied by this report.
