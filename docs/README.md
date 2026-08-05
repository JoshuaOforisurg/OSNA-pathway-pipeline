# Documentation

This is the documentation hub for the OSNA Pathway Pipeline. It explains the product hypothesis,
the pathway represented by the synthetic prototype, the implemented architecture, and the
evidence and approvals required before any work with clinical data.

> **Documentation baseline:** Version `0.5.0` is a local, synthetic-first command-line pipeline.
> It includes mapped-source readiness reporting and end-to-end synthetic reconstruction, but no
> hospital connection, clinical-data processing, dashboard, alerting workflow, or cloud
> deployment.

## Start here

| If you want to understand... | Read... |
| --- | --- |
| why the product exists, who it may serve, and what value still needs to be proven | [Product vision](product/vision.md) |
| exactly what the current prototype must and must not do | [Minimum viable product](product/mvp.md) |
| how records move through the pipeline | [Architecture](architecture/README.md) |
| which clinical events and timings the prototype represents | [Draft OSNA pathway](clinical/osna-pathway.md) and [data dictionary](clinical/data-dictionary.md) |
| what is locally observed and what remains unknown | [Current-state discovery](discovery/current-state.md) and [source-field discovery pack](discovery/source-field-mapping.md) |
| how the work could affect theatre and laboratory staff | [Frontline value and human-factors research](discovery/frontline-value-and-human-factors-notes.md) |
| how to run the pipeline and interpret its exit codes | [Command-line operation](operations/README.md) |
| what must happen before retrospective clinical evaluation | [Evaluation protocol](product/retrospective-evaluation-protocol.md) and [data-readiness gate](governance/README.md) |
| what the pipeline owns and what remains authoritative elsewhere | [System boundaries](integrations/system-boundaries.md) |
| current hazards, restrictions, and future assurance work | [Clinical safety](safety/README.md) |

## Documentation areas

- `product/` explains the problem, vision, scope, evaluation plan, and first deliverable.
- `clinical/` describes the proposed pathway and the meaning of the synthetic data.
- `discovery/` separates observations and research from unanswered local questions.
- `governance/` defines the gate before any retrospective clinical-data work.
- `integrations/` records proposed source ownership and system boundaries.
- `operations/` documents command behaviour and automation outcomes.
- `safety/` records current restrictions, hazards, and future assurance work.
- `architecture/` explains the system shape and records technical decisions.

The [provisional Sysmex source-integration research](discovery/sysmex-source-integration-research.md)
preserves possible connector patterns without treating unconfirmed interface details as product
requirements. The [frontline research note](discovery/frontline-value-and-human-factors-notes.md)
similarly preserves possible benefits while separating retrospective evidence from unapproved
real-time tracking, alerting, and clinical decision support.

Documentation must change alongside the product. Material architectural decisions belong in
`architecture/decisions/`, while unverified local workflow assumptions belong in `discovery/`.
