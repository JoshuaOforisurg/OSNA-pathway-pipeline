# Data contracts

The prototype separates contracts by responsibility:

- `source/` describes the fictional extracts received from each source.
- `canonical/` describes the common event produced by the pipeline.
- `exports/` reserves governed contracts for audit, registry, and other consumers.

The JSON Schema files document the intended structure. The dependency-free prototype also
enforces the essential required-field, timestamp, controlled-value, uniqueness, and relationship
rules in Python.

These contracts are hypotheses for product development. They do not claim that a local theatre
system, LIMS, analyser, or EPR exposes these exact fields.
