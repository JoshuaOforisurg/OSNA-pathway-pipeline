# Documentation

This directory holds the discovery evidence, product boundaries, clinical definitions, safety
work, integration assumptions, and architecture decisions that guide implementation.

- `product/` explains the problem, vision, scope, and first deliverable.
- `clinical/` describes the pathway and the meaning of the data.
- `discovery/` separates observed local practice from unanswered questions.
- `governance/` defines the gate before any retrospective clinical-data work.
- `integrations/` records source ownership and system boundaries.
- `operations/` documents command behaviour and automation outcomes.
- `safety/` records boundaries, hazards, and future assurance work.
- `architecture/` explains the system shape and why technical decisions were made.

The discovery section also contains
[provisional Sysmex source-integration research](discovery/sysmex-source-integration-research.md).
It preserves possible connector patterns and the questions needed to verify them without treating
unconfirmed device or interface details as product requirements.

The
[frontline value and human-factors research note](discovery/frontline-value-and-human-factors-notes.md)
preserves possible benefits for theatre and laboratory staff while separating retrospective value
from unapproved real-time tracking, alerting, and clinical decision support.

Documentation should change alongside the product. Material architectural decisions should be
recorded in `architecture/decisions/` rather than being left only in code or chat history.
