"""OSNA clinical pathway data pipeline."""

from .pipeline import run_pipeline, validate_source_files
from .version import __version__

__all__ = ["run_pipeline", "validate_source_files"]
