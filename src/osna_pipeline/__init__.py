"""OSNA clinical pathway data pipeline."""

from .pipeline import run_pipeline
from .version import __version__

__all__ = ["run_pipeline"]
