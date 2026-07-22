# Tests

The automated tests cover:

- exact identifier matching and rejection of ambiguity;
- duration behaviour for missing or incorrectly ordered timestamps;
- the complete synthetic end-to-end batch;
- expected complete, incomplete, invalid, and orphan conditions; and
- deterministic output files.

Run them from the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'
```
