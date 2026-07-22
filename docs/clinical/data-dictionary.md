# Draft clinical data dictionary

This is the synthetic prototype dictionary, not a final clinical-system specification. Field
meaning, ownership, terminology, and availability require local review.

## Identity and event fields

| Field | Meaning | Rule |
| --- | --- | --- |
| `case_id` | Fictional pathway identity | Established from the theatre source in version 1 |
| `procedure_id` | Fictional operative episode | May contain one or more specimens |
| `specimen_id` | Fictional sentinel-node specimen identity | Exact matching only; ambiguity is quarantined |
| `assay_run_id` | Fictional technical OSNA run identity | Must map to one specimen |
| `run_sequence` | Order of assay attempts for the specimen | Positive integer; `1` is the initial run |
| `repeat_of_run_id` | Earlier run that prompted a repeat | Required for every run after sequence `1` |
| `repeat_reason` | Synthetic controlled reason for a repeat | Required for repeat runs; never inferred from QC alone |
| `event_type` | One controlled pathway event | Uses the ordered event list in the pathway model |
| `event_time` | Time recorded for that event | ISO 8601 with an explicit offset |

## Result and communication fields

| Field | Meaning | Safety rule |
| --- | --- | --- |
| `instrument_result_code` | Synthetic code attached to the completed analyser run | Not treated as verified |
| `qc_status` | Synthetic technical run QC state | Preserved from the analyser source |
| `result_category` | Synthetic category on the laboratory-verified record | Preserved; not clinically interpreted by the pipeline |
| `communication_channel` | How the result handoff was recorded | Does not prove receipt without a separate acknowledgement event |

The initial values `positive`, `negative`, and `invalid` are simplified synthetic categories. They
must be replaced by confirmed local source codes and approved mappings before any real-data work.

Every technical assay attempt remains in the run audit. A failed or earlier run is not overwritten
when a repeat occurs. Exactly one laboratory `result_verified` event selects the run used in the
specimen timeline; if verification is missing or ambiguous, the pipeline does not guess.

## Lineage fields

| Field | Meaning |
| --- | --- |
| `source_system` | Proposed origin: theatre, laboratory, analyser, or communication |
| `source_record_id` | Source-local record identity |
| `source_field` | Exact timestamp field that produced the canonical event |
| `schema_version` | Version of the canonical event contract |

Derived values never overwrite these fields.

## Prototype metrics

| Metric | Start | End |
| --- | --- | --- |
| `transport_minutes` | `specimen_sent` | `specimen_received` |
| `assay_minutes` | `assay_started` | `assay_completed` |
| `laboratory_turnaround_minutes` | `specimen_received` | `result_verified` |
| `communication_minutes` | `result_verified` | `result_communicated` |
| `acknowledgement_minutes` | `result_communicated` | `theatre_acknowledged` |
| `total_pathway_minutes` | `specimen_removed` | `theatre_acknowledged` |

A metric is blank when either timestamp is missing or when its end precedes its start. These are
descriptive prototype measures, not performance targets.

## Missing-data rule

Missing records are reported as missing data. The pipeline must never claim that a clinical event
did not occur merely because no corresponding extract row was available.
