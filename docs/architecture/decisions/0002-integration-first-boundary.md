# ADR 0002: Use an integration-first product boundary

- **Status:** Accepted for the prototype
- **Date:** 2026-07-22

## Context

Mature systems already perform theatre documentation, laboratory workflow, assay operation,
result reporting, and cancer-pathway management. The unproven opportunity is the seam between
those systems: reconstructing the intraoperative OSNA timeline and producing consistent evidence.

## Decision

Build an OSNA-specific integration, validation, and audit pipeline. Existing systems remain
authoritative. The prototype will capture no clinical event through its own user interface and
will make no clinical decision.

## Consequences

- The first deliverable is a batch pipeline rather than a full-stack application.
- Source lineage and safe matching are core product capabilities.
- Connectors are replaceable; the canonical event model is stable and source-neutral.
- A user interface is deferred until discovery identifies a missing operational interaction.
- The project can be stopped or narrowed if existing local systems already solve the problem.
