# System boundaries

The product is an integration and evidence layer. It must retain a clear distinction between
source facts and pipeline-derived records.

| Domain | Expected authoritative source | Pipeline responsibility |
| --- | --- | --- |
| Operative case and theatre events | Theatre record or EPR | Ingest an approved extract and retain its identifiers |
| Specimen accession and receipt | LIMS | Validate and link the receipt event |
| Assay execution and QC | OSNA analyser and/or LIMS | Standardise run events without reinterpreting them |
| Verified result | LIMS or locally confirmed authoritative source | Preserve value, verification state, time, and lineage |
| Urgent result communication | Locally approved communication record | Represent sent, received, and acknowledged events if recorded |
| Final pathology and cancer outcome | Histopathology, cancer, or EPR system | Later governed linkage only |
| Cross-system timeline | This pipeline | Derive ordering, completeness, and provenance |
| Pathway metrics and exceptions | This pipeline | Calculate transparent, reproducible analytical outputs |

The expected sources in this table remain hypotheses until local discovery confirms them.

## What the product must not become

- A duplicate LIMS or analyser result store
- The authoritative clinical record
- An independent result-verification mechanism
- A replacement for approved urgent communication
- A generic theatre scheduling or specimen-tracking product
- A treatment-recommendation or diagnostic system

## Integration order

1. Synthetic files with deliberately separate source contracts
2. Retrospective, approved, de-identified or synthetic-like extracts
3. Governed scheduled exports if a recurring need is demonstrated
4. Near-real-time interfaces only if timing evidence justifies the added safety and operational risk

## Safe matching principle

The prototype links records only through exact synthetic identifiers. A future design must define
which local identifiers are available, how collisions are prevented, and when a case is too
ambiguous to link automatically. Names, dates of birth, or other patient details must not be added
to the repository to make matching easier.
