# Source-field discovery pack

This pack is for structured discussion with theatre, laboratory, pathology IT, analyser support,
EPR, cancer-service, audit, and information-governance colleagues. It must be completed before a
hospital-specific connector or retrospective extract is treated as usable.

Do not add completed hospital-specific answers, staff names, internal screenshots, interface
documents, credentials, or clinical data to the public repository.

## 1. Source inventory

Complete one row for every candidate extract.

| Question | Theatre | Laboratory/LIMS | OSNA analyser | Communication/EPR |
| --- | --- | --- | --- | --- |
| Product and version | Unknown | Unknown | Unknown | Millennium observed; exact module unknown |
| Operational owner | To confirm | To confirm | To confirm | To confirm |
| Technical owner | To confirm | To confirm | To confirm | To confirm |
| Extract method | To confirm | To confirm | To confirm | To confirm |
| Row grain | To confirm | To confirm | To confirm | To confirm |
| Earliest retained date | To confirm | To confirm | To confirm | To confirm |
| Refresh frequency | To confirm | To confirm | To confirm | To confirm |
| Time zone and daylight-saving handling | To confirm | To confirm | To confirm | To confirm |
| Stable record identifier | To confirm | To confirm | To confirm | To confirm |
| Stable specimen/run identifier | To confirm | To confirm | To confirm | To confirm |

## 2. Field mapping

For each proposed canonical field, record the exact source header, source definition, data type,
example using fictional values, null behaviour, owner, and confirmation status.

| Canonical field | Source system | Exact source header | Source meaning | Type/format | Null meaning | Confirmed by |
| --- | --- | --- | --- | --- | --- | --- |
| `source_record_id` | Every source |  |  |  |  |  |
| `case_id` | Theatre |  |  |  |  |  |
| `procedure_id` | Theatre |  |  |  |  |  |
| `specimen_id` | Theatre/laboratory/analyser/communication |  |  |  |  |  |
| `assay_run_id` | Laboratory/analyser/communication |  |  |  |  |  |
| `event_type` | Event sources |  |  |  |  |  |
| Event timestamp | Event sources |  |  |  |  |  |
| `run_sequence` | Analyser |  |  |  |  |  |
| `repeat_of_run_id` | Analyser |  |  |  |  |  |
| `repeat_reason` | Analyser |  |  |  |  |  |
| `instrument_result_code` | Analyser |  |  |  |  |  |
| `qc_status` | Analyser |  |  |  |  |  |
| `result_category` | Laboratory |  |  |  |  |  |
| `channel` | Communication |  |  |  |  |  |

## 3. Timestamp semantics

For every candidate timestamp, answer:

1. What exact real-world event creates it?
2. Is it entered manually, generated automatically, or copied from another system?
3. Can it be edited retrospectively, and is the original retained?
4. Does it represent event time, entry time, verification time, or interface-transfer time?
5. What time zone is stored, and how are daylight-saving transitions represented?
6. How often is it missing, duplicated, or delayed?
7. Is the observed theatre-board "OSNA time" persisted, and what does it mean?

No timestamp should be assigned to a canonical event until its semantics are confirmed.

## 4. Controlled values

Record every observed source code and its owner-approved meaning before adding a value mapping.

| Source field | Source value | Proposed canonical value | Meaning confirmed? | Owner |
| --- | --- | --- | --- | --- |
| Event code |  |  |  |  |
| Instrument result |  |  |  |  |
| QC status |  |  |  |  |
| Repeat reason |  |  |  |  |
| Verified result |  |  |  |  |
| Communication channel |  |  |  |  |

Unknown values must remain validation errors. They must not be silently grouped into the nearest
canonical category.

## 5. Linkage assessment

Document which exact identifiers cross each handoff:

```text
case → procedure → specimen → assay run → verified result → communication
```

For each link, record uniqueness, completeness, reuse rules, formatting changes, and whether the
identifier is scanned, typed, generated, or interfaced. Do not approve probabilistic linkage as a
substitute for an absent specimen or run identifier in this prototype.

## 6. Extract decision

Before requesting records, agree:

- the minimum fields genuinely required;
- the retrospective date range and expected record count;
- whether the work is service evaluation, audit, research, or another locally determined purpose;
- who authorises extraction and who may access it;
- the approved storage, transfer, retention, and deletion arrangements;
- how patient and staff identifiers will be minimised;
- whether small-number and disclosure controls are required for outputs; and
- who will validate source meanings and analytical results.

The output of discovery is a locally approved mapping and extract specification—not clinical data
in this repository.

After approval, the validation-only readiness report can quantify completeness and rule failures
for the proposed fields. Keep that report in the governed environment: although it contains no row
identifiers or source values, its column metadata and unsuppressed counts may still be sensitive.
