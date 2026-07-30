# Source mapping configuration

`source_mapping.example.json` is a public, synthetic example of the mapping contract. A mapping
allows an event-shaped CSV extract to use different filenames, column headers, and controlled
source codes without changing the pipeline's canonical field names.

Each of the four source systems requires:

- one CSV filename without a directory path;
- one source header for every canonical field in that source contract; and
- optional source-to-canonical translations for controlled fields.

For example, a fictional theatre extract could map `event_code` values:

```json
{
  "columns": {
    "event_type": "event_code"
  },
  "value_mappings": {
    "event_type": {
      "REMOVED": "specimen_removed",
      "SENT": "specimen_sent"
    }
  }
}
```

The actual mapping must still include every required canonical field. See the complete example and
the [mapping schema](../schemas/config/source_mapping.schema.json).

## Supported boundary

Mapping version `1.0.0` supports event-shaped CSV extracts:

- one record represents one pathway event, or one analyser run in `osna_analyser`;
- timestamps are ISO 8601 and include a time-zone offset;
- identifiers and timestamps are already available as distinct columns; and
- controlled codes can be translated without clinical interpretation.

It does not reshape wide reports, combine columns, parse free text, infer identifiers, convert
local date formats, or derive events from undocumented fields. Those transformations require a
confirmed source specification and a separately tested connector.

## Data classification

- `synthetic` permits validation and full prototype processing.
- `governed_clinical` permits validation-only mode. Full pathway processing is rejected.

The classification is a declared handling mode, not proof that governance approval exists.
Hospital-specific mappings may disclose system structure and must remain in an approved private
workspace. Files under `config/local/` and `config/*.local.json` are ignored by Git.
