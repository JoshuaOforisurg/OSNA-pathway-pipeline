# Canonical event model

All accepted input fields are represented as events with a common identity, timestamp, and source
lineage. Optional assay and communication attributes are populated only for relevant events.

The model is event-based so that new source connectors can be added without turning one source's
table structure into the product's permanent clinical model.
