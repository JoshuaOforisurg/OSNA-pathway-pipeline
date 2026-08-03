# Provisional Sysmex OSNA source-integration research

> **Status:** Unverified discovery note. This is not an interface specification, architecture
> decision, clinical requirement, or authorisation to connect to an analyser or process clinical
> data.

## Why this note exists

This document preserves source-integration ideas supplied during product development on
3 August 2026. The material described possible ways that a Sysmex OSNA analyser could pass data
through local laboratory infrastructure into the OSNA Pathway Pipeline.

The supplied material was generated through an AI-assisted discussion and may contain mistakes.
Every device-specific, protocol-specific, field-level, clinical, and network claim must be checked
against the installed instrument's approved documentation and confirmed by Sysmex, the OSNA
laboratory team, pathology IT, the LIMS owner, the interface team, information governance, cyber
security, and clinical safety as locally applicable.

## Useful integration hypothesis

The most useful idea to retain is that the pipeline should not initially connect directly to the
OSNA analyser. It should first determine whether an existing, supported hospital interface already
receives and persists the analyser data.

A preferred conceptual route is:

```text
OSNA analyser
    |
    v
Existing approved analyser interface, middleware, or LIMS
    |
    v
Governed staging view or scheduled export
    |
    v
Batch source connector
    |
    v
Mapping and source validation
    |
    +----> Validation-only readiness report
    |
    v
Exact-identifier matching and canonical OSNA events
    |
    v
Run histories, specimen timelines, quality findings, metrics, and audit outputs
```

This route would isolate the analytical pipeline from instrument connectivity and allow existing
laboratory support, acknowledgement, retry, and downtime arrangements to remain authoritative.
It is a hypothesis until the local system design is confirmed.

## Candidate connector patterns to investigate

### 1. Existing LIMS or interface-engine extract

The analyser may already send results to the LIMS directly or through approved middleware. If the
relevant events are retained, the pipeline could receive a scheduled export, governed database
view, or approved API response from that layer.

The future connector could use an agreed incremental watermark, immutable source-record
identifier, or extract window. The real method must support replay, deduplication, late records,
and reconciliation without writing back to the clinical system.

This is the preferred pattern to investigate first because it avoids making the analytical
pipeline responsible for receiving instrument messages.

### 2. Controlled analyser or host-PC file export

The installed analyser software may support an approved report or file export. If so, an
organisation-managed process could copy new files to a governed landing area while retaining the
original bytes, logical filename, checksum, and extraction metadata.

The connector would need an approved approach for determining whether a file is complete, avoiding
duplicates, detecting changes during transfer, handling partial batches, and retaining or deleting
source files. No agent should be installed on an instrument or host computer without vendor and
local technical approval.

### 3. Direct analyser protocol or legacy connection

The supplied material suggested that some laboratory instruments may use HL7 v2, ASTM, MLLP over
TCP/IP, or legacy serial communication. Whether the installed Sysmex OSNA system supports any of
these methods is not yet confirmed.

Direct receipt would make this product responsible for connection state, acknowledgements,
retries, duplicate messages, downtime recovery, monitoring, and potentially time-critical
interfaces. That responsibility is outside the present product boundary and should not be adopted
without a separate architecture decision, vendor support, operational ownership, and clinical
safety assessment.

## Candidate data elements mentioned in the supplied material

The following are discovery prompts, not confirmed fields or requirements:

- specimen or sample identifier and barcode;
- assay-run identifier;
- run start and completion timestamps;
- rack or position information;
- assay target or analyte description;
- quantitative instrument measurement and unit;
- qualitative instrument category;
- control and QC status;
- repeat-run relationship and reason;
- instrument, software, message, or export version; and
- the source record or message identifier needed for deduplication and lineage.

The current canonical model deliberately stores only the fields required for the documented
pathway use case. A real connector must not add or reinterpret a field until its local meaning,
format, unit, null behaviour, ownership, and permitted purpose are confirmed.

## Claims that must not be treated as confirmed

| Claim from the supplied discussion | Required verification |
| --- | --- |
| Particular Sysmex models provide a specific network, file, or serial interface | Installed model, software version, licensed options, vendor interface manual, and local configuration |
| The analyser sends HL7 `ORU_R01` or ASTM messages using MLLP | Vendor documentation, message conformance profile, interface-engine configuration, and a safely obtained fictional example |
| A particular TCP port is used | Locally approved network configuration; never assume or scan an instrument network |
| An instrument host writes CSV, TXT, DAT, or a particular folder path | Vendor-supported export method, file lifecycle, permissions, completion behaviour, and local support ownership |
| Patient or observation data appears in specific HL7 segments | Actual conformance profile and local interface mapping |
| Quantitative CK19 measurements and units are present in the available export | Installed assay output, LIMS storage, unit definition, rounding, censoring, and result-reporting policy |
| Specific positive, negative, micro-, or macro-metastasis thresholds should be implemented | Current approved assay instructions, laboratory verification policy, intended purpose, and clinical review |
| A run supports a stated number of nodes, rack positions, or samples | Installed instrument documentation and local operating procedure |
| A staging database contains a `processed` flag or `last_modified` watermark | Actual governed view, stable incremental field, late-update behaviour, and extract contract |

Thresholds and clinical categories must never be recreated from an unverified numeric value when a
locally verified result already exists. The pipeline currently preserves the instrument result and
the laboratory-verified result as separate facts.

## Questions for local discovery

1. What exact Sysmex analyser model, software version, and interface licences are installed?
2. Does the analyser currently communicate with LIMS or middleware? If so, who owns and supports
   that interface?
3. Which LIMS and interface engine are used, and where are raw and verified OSNA records retained?
4. Is there an approved retrospective export, reporting database, vendor API, or governed view?
5. What is the row or message grain: specimen, node, assay run, result, control, or another unit?
6. Which stable identifiers cross theatre, specimen reception, analyser, laboratory verification,
   communication, and acknowledgement?
7. Which timestamps are event times, entry times, verification times, or interface-transfer times?
8. What time zone, daylight-saving, correction, and late-entry behaviour applies?
9. Are initial runs, repeats, QC failures, controls, and verified result-bearing runs all retained?
10. Are result communication and theatre acknowledgement recorded in any approved system?
11. How are interface acknowledgements, retries, downtime, duplicate messages, corrections, and
    cancellations handled today?
12. What minimum extract is permitted for the retrospective evaluation, and where may it be
    processed?

## Effect on the current repository

This research does not change the current synthetic source contracts or authorise a new connector.
It strengthens the source-discovery work and gives the team three integration patterns to test in
order:

1. existing LIMS or interface-engine extract;
2. vendor-supported controlled file export; and
3. direct instrument interface only if the first two cannot meet an approved requirement.

Once local evidence identifies the real source and protocol, the chosen connector should receive
its own versioned contract, synthetic fixtures, tests, hazard review, and architecture decision
record before implementation.
