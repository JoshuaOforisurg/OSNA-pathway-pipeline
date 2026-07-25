# Minimum viable product

## Goal

Demonstrate with synthetic data that four fragmented OSNA source extracts can be converted into
traceable specimen timelines, assay-run histories, procedure summaries, an exception report, and
a small set of reproducible service metrics.

## Source extracts

- Theatre events: case, procedure, specimen, removal, and dispatch events
- Laboratory events: specimen receipt and laboratory workflow events
- OSNA analyser runs: initial and repeat run, QC, completion, and instrument-result data
- Communication events: result communication and theatre acknowledgement

These are proposed contracts, not representations of any confirmed local system interface.

## Required behaviour

- Check required fields, identifiers, timestamp format, and controlled values.
- Standardise source rows into a versioned canonical event model.
- Match only on explicit synthetic identifiers in the first version.
- Preserve source system and source record identifiers for every event.
- Quarantine or flag records when a safe link cannot be established.
- Detect missing events and impossible timestamp sequences.
- Preserve every assay attempt and validate repeat-run ancestry and QC state.
- Select a result-bearing run only from one unambiguous laboratory verification.
- Support multiple specimens within one procedure without collapsing their timelines.
- Calculate documented transport, laboratory, communication, and total timings.
- Summarise quality findings by type and severity without replacing their detailed records.
- Produce descriptive timing statistics with explicit missing and invalid-pathway exclusions.
- Produce a deterministic manifest of the exact input and output files.
- Expose distinct automation outcomes for completed processing and source-contract failure.
- Allow an optional error-severity quality gate after review outputs have been written.
- Produce deterministic CSV and JSON outputs.
- Test successful, incomplete, and contradictory synthetic cases.

## Explicitly out of scope

- Real patient or staff data
- Live clinical-system or analyser integration
- Acting as the authoritative result record
- Automated time-critical result communication
- Replacement of the laboratory-to-surgeon telephone call
- Diagnosis, treatment recommendations, or predictive machine learning
- Genomic sequence processing
- Live operational dashboard or full-stack application
- Production Azure deployment
- Other surgical specialties

## Acceptance criteria

The first prototype is complete when it can:

1. process the supplied synthetic batch repeatedly with the same result;
2. link every safe source event to the correct fictional case and specimen;
3. preserve lineage from each canonical event back to its source row;
4. report incomplete and incorrectly ordered pathways without guessing;
5. calculate documented metrics only when their required timestamps exist;
6. distinguish failed, repeated, and laboratory-verified assay runs;
7. roll multiple specimen pathways up to their procedure without losing detail;
8. write readable canonical, assay-run, timeline, procedure, exception, and summary outputs;
9. record input and output checksums, counts, and versions in a deterministic batch manifest;
10. calculate descriptive timing summaries without including invalid pathways or inventing
    clinical targets;
11. write review evidence before applying an optional automation quality gate; and
12. pass automated unit and end-to-end tests using only local resources.

## Evidence required before the next phase

- Confirmation of the local LIMS and cancer-pathway systems
- Confirmation of whether analyser results interface with the LIMS
- Definition of the OSNA timestamp currently recorded in theatre
- Identification of available case and specimen identifiers at each handoff
- Confirmation of who owns booking, readiness, verification, communication, and audit records
- Evidence that the proposed output answers a recurring operational or audit need
