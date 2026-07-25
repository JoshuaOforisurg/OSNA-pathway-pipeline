# Tests

The automated tests cover:

- exact identifier matching and rejection of ambiguity;
- repeat-run relationships, QC failures, and result-code disagreements;
- multiple specimens within one procedure;
- duration behaviour for missing or incorrectly ordered timestamps;
- descriptive metric aggregation, missingness, exclusions, and percentile behaviour;
- batch identity, checksums, source rejection counts, and quality summaries;
- command-line success, quality-gate, and source-contract failure outcomes;
- the complete synthetic end-to-end batch;
- expected complete, incomplete, invalid, and orphan conditions; and
- deterministic output files.

Run them from the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```
