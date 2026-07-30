# Data contracts

The prototype separates contracts by responsibility:

- `config/` describes the source-mapping configuration.
- `source/` describes the fictional extracts received from each source.
- `canonical/` describes the common event produced by the pipeline.
- `exports/` describes local audit outputs and reserves space for governed external contracts.

The JSON Schema files document the intended structure. The dependency-free prototype also
enforces the essential required-field, timestamp, controlled-value, uniqueness, and relationship
rules in Python.

These contracts are hypotheses for product development. They do not claim that a local theatre
system, LIMS, analyser, or EPR exposes these exact fields.
