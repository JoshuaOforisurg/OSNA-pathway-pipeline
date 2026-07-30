# Retrospective data-readiness gate

This document is a product-development checklist, not legal or information-governance advice.
The responsible healthcare organisation must determine the applicable approval route.

## Before receiving any clinical extract

- Define the intended purpose and determine its local classification.
- Identify the data controller, operational owner, analytical owner, and authorised users.
- Obtain the required information-governance, security, audit/service-evaluation, research, and
  clinical-safety decisions as locally applicable.
- Agree the minimum cohort, fields, date range, and linkage identifiers.
- Use an approved organisational environment for storage and analysis.
- Document access control, transfer, retention, backup, incident, and deletion arrangements.
- Confirm how results will be checked by clinical and source-system owners.

Pseudonymised data remains personal data. Replacing a hospital number with another identifier does
not make a dataset anonymous.

## Repository boundary

The public repository may contain:

- deliberately generated synthetic fixtures;
- empty field-mapping templates;
- public schemas and code; and
- fictional example mappings.

It must not contain:

- identifiable or pseudonymised patient or staff records;
- real row-level exports, even if they appear de-identified;
- hospital-specific credentials, network paths, screenshots, or interface secrets;
- small-number clinical results that create disclosure risk; or
- completed internal mapping documents unless publication is explicitly approved.

## Validation-only mode

`governed_clinical` mappings are accepted only by `--validate-only`. That mode:

- checks required mapped headers;
- validates row-level required values, controlled codes, and timestamp format;
- ignores columns that are not explicitly selected by the mapping;
- prints aggregate counts and issue categories;
- does not link specimens, reconstruct pathways, calculate timings, or write analytical files.

This technical restriction does not grant permission to use clinical data. Validation must still
run inside the approved environment, and terminal output must be handled under local policy.
The classification is supplied by the operator; it does not inspect the extract and cannot prove
that data labelled `synthetic` is genuinely synthetic. A governed extract must always use a
mapping explicitly declared `governed_clinical`.

## Gate before analytical processing

Full retrospective pathway processing should not be enabled until:

1. source meanings and identifier linkage are confirmed;
2. the approved data flow and environment are documented;
3. the prototype's intended purpose and safety boundary are reviewed;
4. the cohort and statistical analysis plan are agreed;
5. expected failure modes are tested with synthetic fixtures; and
6. an authorised reviewer approves progression beyond validation-only.
