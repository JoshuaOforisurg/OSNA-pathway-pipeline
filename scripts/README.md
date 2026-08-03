# Scripts

Developer utilities live here for repeatable repository checks and synthetic-only local work.

`verify_release.py` validates every JSON Schema document, the example mapping, built-in and mapped
readiness reports, the run manifest, mapping-checksum lineage, and byte-for-byte deterministic
outputs. It operates only on the committed synthetic fixtures and writes to a temporary directory.

Run it after installing the development dependency:

```bash
python3 -m pip install --editable ".[dev]"
python3 scripts/verify_release.py
```

Scripts must avoid hidden business logic. Reusable validation and transformation behaviour belongs
in `src/osna_pipeline/`.
