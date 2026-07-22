# Draft OSNA pathway model

This is the information pathway represented by the first prototype. It is not a clinical protocol
and must not be treated as a description of the local approved workflow until clinical discovery
confirms it.

## Initial pathway boundary

```text
specimen removed
    → specimen sent from theatre
    → specimen received by the laboratory
    → OSNA assay started
    → OSNA assay completed and, when necessary, repeated
    → result verified under laboratory governance
    → result communicated
    → theatre acknowledgement recorded
```

The prototype ends at acknowledgement. Final histopathology, MDT decisions, treatment, recurrence,
and outcomes are possible later linkages, not part of the first pipeline.

## Proposed events

| Event | Meaning in the prototype | Proposed source | Confirmation status |
| --- | --- | --- | --- |
| `specimen_removed` | Sentinel-node specimen removed during the procedure | Theatre record | Unconfirmed locally |
| `specimen_sent` | Specimen leaves theatre for the laboratory | Theatre record | Unconfirmed locally |
| `specimen_received` | Laboratory accepts the specimen | LIMS/laboratory record | Unconfirmed locally |
| `assay_started` | Technical OSNA run begins | Analyser or LIMS | Unconfirmed locally |
| `assay_completed` | Technical run and QC complete | Analyser or LIMS | Unconfirmed locally |
| `result_verified` | Result is authorised for communication under local laboratory practice | LIMS/laboratory record | Unconfirmed locally |
| `result_communicated` | Verified result is communicated to the surgical team | Communication record | Telephone call observed; timestamp record unknown |
| `theatre_acknowledged` | Theatre receipt is explicitly recorded | Communication/theatre record | Whether this is recorded is unknown |

The pipeline deliberately distinguishes an analyser result code from a verified result. It must
not infer verification merely because an instrument run completed.

## Core relationships

```text
Case
 └── Procedure
      ├── Specimen A
      │    ├── Theatre and laboratory events
      │    ├── Assay run 1
      │    ├── Assay run 2 (optional repeat)
      │    └── Communication events for the verified run
      └── Specimen B (optional additional specimen)
```

The synthetic prototype links these records with exact fictional identifiers. It does not use
names, dates of birth, or probabilistic patient matching.

An assay completion is a technical fact, not proof that its result was authorised. The single
laboratory verification identifies the result-bearing run for the specimen timeline. Earlier,
failed, or repeated attempts remain visible in the assay-run audit.

## Known observation and open interpretation

An "OSNA time" is recorded on the theatre board in the observed setting. It is not yet known
whether this represents removal, dispatch, expected result, communicated result, or another event.
The prototype must not assign that value to one of the defined events until the meaning and
retention of the field are confirmed.

See [current-state discovery](../discovery/current-state.md) for the outstanding workflow and
system questions.
