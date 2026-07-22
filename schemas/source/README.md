# Source contracts

Each CSV is deliberately source-specific. The pipeline must not assume that every system contains
the complete case timeline.

| File | Represents |
| --- | --- |
| `theatre_events.csv` | Case, procedure, specimen, removal, and dispatch events |
| `laboratory_events.csv` | Specimen receipt and laboratory-controlled result verification |
| `osna_runs.csv` | Initial and repeat assay execution, instrument result code, and QC |
| `communication_events.csv` | Result communication and theatre acknowledgement |

Every row requires a fictional, source-local `source_record_id`. Timestamps use ISO 8601 with an
explicit UTC offset.

Analyser rows also carry a positive `run_sequence`. An initial run has sequence `1` and no repeat
metadata. Later attempts must identify an earlier run in `repeat_of_run_id` and provide a
controlled `repeat_reason`; cross-row relationship checks are performed by the pipeline.
