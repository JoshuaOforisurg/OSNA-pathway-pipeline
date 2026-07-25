# Architecture

## Prototype context

The first implementation is a local, batch-oriented pipeline operating only on synthetic CSV
files. Each file represents a different source system so that integration problems are visible
rather than hidden inside one convenient dataset.

```text
theatre events ─────────┐
laboratory events ──────┼─→ source validation ─→ explicit-ID matching
OSNA analyser runs ─────┤                              ↓
communication events ──┘                    canonical event stream
                                                     ↓
                               run, sequence, and completeness checks
                                                     ↓
                              run audit and specimen-level timelines
                                                     ↓
                      procedure summaries, timing and quality metrics
                                                     ↓
                              checksummed batch audit manifest
```

## Component responsibilities

- **Connectors:** read a named source contract without changing its clinical meaning.
- **Validation:** check fields, controlled values, timestamps, uniqueness, and relationships.
- **Matching:** link source events only when the identifier evidence is sufficient.
- **Canonical model:** represent all accepted events consistently while retaining lineage.
- **Transformations:** retain run histories, construct specimen timelines, and aggregate procedures.
- **Metrics:** calculate documented durations only when both required timestamps are valid.
- **Exports:** produce analysis and audit outputs without becoming a clinical source of truth.
- **Lineage:** identify exact input and output bytes through a deterministic batch manifest.
- **CLI:** distinguish completed processing, optional quality-gate failure, and contract failure.

## System ownership

The pipeline owns derived links, flags, durations, and export tables. It does not own the clinical
facts received from theatre, laboratory, analyser, communication, EPR, or cancer systems. See the
[system boundary document](../integrations/system-boundaries.md).

## Architectural principles

- Preserve the source record and never silently rewrite a clinical fact.
- Make every accepted canonical event traceable to its source system and record identifier.
- Make each batch reproducible through logical filenames, counts, versions, and checksums.
- Quarantine or flag ambiguity instead of guessing.
- Keep source facts, quality findings, and analytical derivations visibly distinct.
- Calculate metrics only from explicitly defined events.
- Treat absence of a record as missing data, not proof that the real-world event did not happen.
- Keep the core pipeline independent of Azure so it is reproducible and testable locally.
- Add live integration or presentation components only after discovery establishes a need.

## Future deployment shape

An approved future deployment could replace CSV connectors with governed interfaces while keeping
the canonical model and validation logic. Storage, orchestration, access control, monitoring, and
retention would then be mapped to locally approved Azure and NHS architecture. Those decisions are
intentionally deferred.

See `decisions/` for individual architecture decision records.
