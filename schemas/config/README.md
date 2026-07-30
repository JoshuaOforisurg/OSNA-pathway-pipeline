# Configuration contracts

`source_mapping.schema.json` describes the versioned JSON structure used to map event-shaped source
extracts to the pipeline's four source contracts.

The JSON Schema checks the outer structure, source-system set, filenames, column mappings, and
value-mapping shapes. The Python loader additionally verifies that:

- every canonical field required by the selected source contract is mapped;
- no unsupported canonical field is introduced;
- one source column is not reused for multiple canonical fields;
- value mappings target only controlled fields and approved canonical values; and
- filenames cannot escape the selected input directory.

Passing the configuration schema does not prove that a source field has the proposed clinical
meaning. That requires the completed discovery and ownership review.
