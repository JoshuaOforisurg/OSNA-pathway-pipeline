# OSNA Pathway Pipeline

**A synthetic-first data product for reconstructing and measuring the intraoperative OSNA
pathway between breast surgery and the molecular laboratory.**

> **Project status:** Early technical prototype. It is not validated, deployed, or approved for
> clinical use. Only deliberately generated synthetic data is permitted.

## What this project does

One-Step Nucleic Acid Amplification (OSNA) is an intraoperative molecular method used to assess
sentinel lymph nodes in breast cancer surgery. The test is performed in the laboratory, but the
surrounding process crosses theatre, specimen transport, the analyser, laboratory systems,
telephone communication, and the electronic patient record.

This project turns those separate records into one traceable timeline for each OSNA case. The
pipeline will:

1. receive event extracts from theatre, laboratory, analyser, and communication sources;
2. standardise them into a common OSNA event model;
3. safely match events belonging to the same fictional case and specimen;
4. detect missing, duplicated, contradictory, or incorrectly ordered events;
5. calculate pathway timings; and
6. produce case timelines, exception reports, and audit-ready data.

The initial prototype uses synthetic CSV files rather than clinical-system connections. This
allows the event model and validation rules to be tested without patient data or operational
risk.

## Why it may be needed

An urgent result can be communicated successfully by telephone while the wider pathway remains
difficult to reconstruct. Relevant timestamps may be split between a theatre board, a laboratory
system, the OSNA analyser, and a communication record. This makes it harder to answer questions
such as:

- How long did the specimen take to reach the laboratory?
- How long elapsed between receipt, analysis, verification, and communication?
- Was the verified result acknowledged in theatre?
- Which cases contain missing or conflicting records?
- Can the service produce consistent evidence for audit and improvement?

The repository tests whether an integration and evidence layer can answer those questions without
replacing systems that already perform ordering, analysis, result reporting, or clinical record
keeping.

## Product boundary

This is an **OSNA pathway data pipeline**, not a new LIMS, EPR, analyser, theatre scheduler, or
clinical decision-support system.

Existing clinical systems remain authoritative for their records. The pipeline preserves each
source identifier and records the origin of every event. It does not diagnose disease, interpret
an OSNA result, recommend treatment, or replace the laboratory's time-critical result telephone
call.

A small status or audit interface may later sit on top of the pipeline if discovery shows that
users need it. A full clinical application is not required to prove the first product hypothesis.

## First end-to-end slice

The first runnable version models four deliberately separate source extracts:

```text
Theatre events ───────┐
Laboratory events ────┼─→ validation and matching ─→ OSNA case timeline
OSNA analyser runs ───┤                              exception report
Communication events ┘                              pathway metrics
```

For each case, it aims to reconstruct:

```text
specimen removed → specimen sent → laboratory received → assay run
→ result verified → result communicated → theatre acknowledged
```

The first metrics cover specimen transport time, laboratory turnaround time, communication time,
and total recorded intraoperative pathway time. They are prototype service measures, not approved
clinical targets.

## Run the prototype

Python 3.11 or later is required. The pipeline has no third-party runtime dependencies.

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --output data/outputs
```

The command writes:

- `canonical_events.csv` — standardised events with source lineage;
- `case_timelines.csv` — one reconstructed row per specimen;
- `exceptions.csv` — missing links, missing events, and sequence problems; and
- `pipeline_summary.json` — a compact run summary.

Run the tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

## Repository structure

```text
.
├── data/                   Synthetic inputs and generated local outputs
├── docs/
│   ├── architecture/       System design and architecture decisions
│   ├── clinical/           Pathway and data definitions
│   ├── discovery/          Confirmed observations and open questions
│   ├── integrations/       Ownership and system boundaries
│   ├── product/            Vision, scope, and MVP
│   └── safety/             Clinical-safety boundaries
├── schemas/
│   ├── source/             Contracts for each incoming source
│   ├── canonical/          Common OSNA pathway event model
│   └── exports/            Future audit and registry contracts
├── src/osna_pipeline/      Pipeline implementation
├── tests/                  Unit and end-to-end tests
└── infra/azure/            Deferred Azure deployment work
```

## Documentation

- [Product vision](docs/product/vision.md)
- [Minimum viable product](docs/product/mvp.md)
- [Current workflow discovery](docs/discovery/current-state.md)
- [System boundaries](docs/integrations/system-boundaries.md)
- [Draft OSNA pathway](docs/clinical/osna-pathway.md)
- [Architecture](docs/architecture/README.md)
- [Clinical-safety boundaries](docs/safety/README.md)

## Safety and data governance

Identifiable or pseudonymised patient information must not be added to this repository. Prototype
outputs must not be used for diagnosis, treatment, intraoperative decisions, or as the
authoritative source of an OSNA result.

Any future use with clinical data would require local workflow validation, information
governance, security assurance, clinical risk management, human-factors work, and assessment
against applicable NHS and medical-device requirements.

## Roadmap

1. Prove the event model using representative synthetic cases and failure scenarios.
2. Validate the proposed source fields with theatre, laboratory, pathology IT, and cancer teams.
3. Replace assumptions with documented local system contracts and ownership.
4. Evaluate retrospective approved exports before any live integration.
5. Add a minimal status or exception view only if user discovery demonstrates a need.
6. Consider an approved Azure architecture after the workflow and product value are established.

## Licence

No licence has been selected. Unless and until a licence is added, the repository should not be
treated as open-source software.
