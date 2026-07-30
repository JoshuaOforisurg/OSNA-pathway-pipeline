# OSNA Pathway Pipeline

**A synthetic-first data product for reconstructing and measuring the intraoperative OSNA
pathway between breast surgery and the molecular laboratory.**

> **Project status:** Early technical prototype. It is not validated, deployed, or approved for
> clinical use. Full pathway processing is restricted to deliberately generated synthetic data.
> Approved clinical extracts may only use the validation-only path inside a governed environment.

## What this project does

One-Step Nucleic Acid Amplification (OSNA) is an intraoperative molecular method used to assess
sentinel lymph nodes in breast cancer surgery. The test is performed in the laboratory, but the
surrounding process crosses theatre, specimen transport, the analyser, laboratory systems,
telephone communication, and the electronic patient record.

This project turns those separate records into traceable specimen timelines, assay-run histories,
and procedure summaries. The pipeline will:

1. receive event extracts from theatre, laboratory, analyser, and communication sources;
2. standardise them into a common OSNA event model;
3. safely match events belonging to the same fictional case and specimen;
4. detect missing, duplicated, contradictory, or incorrectly ordered events;
5. retain failed and repeated analyser runs without confusing them with the verified result;
6. calculate pathway timings; and
7. produce specimen timelines, procedure summaries, exception reports, and audit-ready data.

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
- Was an assay repeated, why was it repeated, and which run supplied the verified result?
- Did every specimen from the procedure complete the recorded pathway?
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
Laboratory events ────┼─→ validation and matching ─→ specimen timelines
OSNA analyser runs ───┤                              assay-run audit
Communication events ┘                              procedure summaries
                                                     exceptions and metrics
```

For each case, it aims to reconstruct:

```text
specimen removed → specimen sent → laboratory received → one or more assay runs
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
- `case_timelines.csv` — one reconstructed pathway row per specimen;
- `assay_runs.csv` — every initial or repeat run, including QC failures and result selection;
- `procedure_summaries.csv` — specimen and run counts rolled up to each procedure;
- `metric_summary.csv` — descriptive timing statistics with missing and exclusion counts;
- `exceptions.csv` — detailed missing links, missing events, and sequence problems;
- `quality_summary.csv` — grouped errors and warnings for rapid review;
- `pipeline_summary.json` — a compact run summary; and
- `run_manifest.json` — input/output checksums, counts, versions, and a reproducible batch ID.

An `errors_detected` quality status does not mean the program crashed. It means the batch completed
and produced reviewable exception records. The supplied synthetic batch intentionally includes
incomplete, contradictory, and orphan scenarios so these controls remain testable.

The timing summary is descriptive only. It excludes invalid specimen pathways, does not convert
missing values to zero, and contains no invented performance target or clinical threshold.

## Validate a mapped extract

The validation-only workflow checks source structure and row-level values without matching
specimens, reconstructing pathways, calculating metrics, or writing analytical outputs:

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --mapping config/source_mapping.example.json \
  --validate-only
```

Mapping version `1.0.0` supports event-shaped CSV files with different filenames, column headers,
and controlled source codes. It does not infer events from wide reports or free text. The supplied
mapping is fictional and synthetic; hospital-specific mappings and extracts must remain in an
approved private environment.

For an automated job that should return a non-zero status when error-severity findings are
present, add the optional quality gate:

```bash
PYTHONPATH=src python3 -m osna_pipeline \
  --input data/raw/synthetic \
  --output data/outputs \
  --fail-on-quality-errors
```

The pipeline writes the review outputs before returning exit code `2`. The supplied synthetic
batch intentionally triggers that code. A source-contract failure returns exit code `3` with a
structured JSON error and does not create analytical outputs. See
[command-line operation](docs/operations/README.md) for the complete behaviour.

Run the tests with:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```

## Repository structure

```text
.
├── config/                 Synthetic mapping example; local mappings are ignored
├── data/                   Synthetic inputs and generated local outputs
├── docs/
│   ├── architecture/       System design and architecture decisions
│   ├── clinical/           Pathway and data definitions
│   ├── discovery/          Confirmed observations and open questions
│   ├── governance/         Retrospective data-readiness boundary
│   ├── integrations/       Ownership and system boundaries
│   ├── operations/         Command behaviour and automation boundaries
│   ├── product/            Vision, scope, and MVP
│   └── safety/             Clinical-safety boundaries
├── schemas/
│   ├── config/             Source-mapping configuration contract
│   ├── source/             Contracts for each incoming source
│   ├── canonical/          Common OSNA pathway event model
│   └── exports/            Local audit and future governed export contracts
├── src/osna_pipeline/      Pipeline implementation
├── tests/                  Unit and end-to-end tests
└── infra/azure/            Deferred Azure deployment work
```

## Documentation

- [Product vision](docs/product/vision.md)
- [Minimum viable product](docs/product/mvp.md)
- [Current workflow discovery](docs/discovery/current-state.md)
- [Source-field discovery pack](docs/discovery/source-field-mapping.md)
- [System boundaries](docs/integrations/system-boundaries.md)
- [Draft OSNA pathway](docs/clinical/osna-pathway.md)
- [Retrospective evaluation protocol](docs/product/retrospective-evaluation-protocol.md)
- [Retrospective data-readiness gate](docs/governance/README.md)
- [Architecture](docs/architecture/README.md)
- [Command-line operation](docs/operations/README.md)
- [Clinical-safety boundaries](docs/safety/README.md)

## Safety and data governance

Identifiable or pseudonymised patient information must not be added to this repository. Prototype
outputs must not be used for diagnosis, treatment, intraoperative decisions, or as the
authoritative source of an OSNA result.

Any validation of clinical data or future analytical use would require local workflow validation,
information governance, security assurance, clinical risk management, human-factors work, and
assessment against applicable NHS and medical-device requirements.

## Roadmap

1. Prove the event model using representative synthetic cases and failure scenarios.
2. Complete the source-field discovery pack with theatre, laboratory, pathology IT, and cancer
   teams.
3. Replace the fictional example mapping with a locally approved private mapping.
4. Validate an approved retrospective extract inside the governed organisational environment.
5. Obtain explicit approval before enabling full retrospective pathway processing.
6. Add a minimal status or exception view only if user discovery demonstrates a need.
7. Consider an approved Azure architecture after the workflow and product value are established.

## Licence

No licence has been selected. Unless and until a licence is added, the repository should not be
treated as open-source software.
