# ADR 0001: Begin with a local, synthetic-data pipeline

- **Status:** Accepted for the initial scaffold
- **Date:** 2026-07-22

## Context

The long-term product may use Azure and integrate with clinical systems, but the clinical event
model, validation behaviour, and product value have not yet been proven. Using real patient data
or production cloud infrastructure would add risk and complexity before those fundamentals are
understood.

## Decision

Build the first end-to-end slice locally with synthetic data. Keep pipeline components modular so
that storage, orchestration, and compute can later be mapped to approved Azure services without
rewriting the clinical model.

## Consequences

- Early development remains low-cost and reproducible.
- No real patient data is required.
- Tests can run without cloud access.
- Azure deployment and integration decisions are intentionally deferred.
- The prototype must not be represented as production-ready or clinically validated.
