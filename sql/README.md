# SQL transformations

- `staging/` will standardise source columns without changing their meaning.
- `intermediate/` will join pathway entities and calculate reusable derived fields.
- `marts/` will expose documented case-timeline, data-quality, and service-metric tables.

SQL logic should be deterministic, tested, and traceable to the source fields defined in the data
contracts. A future decision can determine whether these transformations remain plain SQL or move
to dbt.
