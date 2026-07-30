# ADR 0005: Configure only event-shaped source mappings

- **Status:** Proposed for review
- **Date:** 2026-07-26

## Context

Real source exports may use different filenames, headers, and controlled codes. Hard-coding each
local variation would make the canonical pipeline difficult to test and reuse. However, the actual
row grain and timestamp semantics of local exports remain unknown.

A generic configuration language that tries to reshape arbitrary reports could silently create
incorrect clinical events.

## Decision

Provide a versioned JSON mapping for event-shaped CSV extracts. It may:

- select one filename for each required source;
- map one source header to each canonical source field; and
- translate explicitly listed controlled values.

It may not combine fields, parse free text, infer events, perform probabilistic linkage, convert
undocumented timestamps, or reshape wide reports. Those requirements need a dedicated connector
after source discovery.

Mappings declared `governed_clinical` are restricted to validation-only mode.

## Consequences

- Fictional and locally named event-shaped extracts can use the same canonical pipeline.
- Mapping behaviour is deterministic, checksummed, and recorded in the batch manifest.
- Unknown codes remain visible validation errors.
- Source discovery cannot be replaced by configuration.
- A wide or semantically different export requires new design, review, fixtures, and tests.
