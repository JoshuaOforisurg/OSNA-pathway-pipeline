"""Load a safe, versioned mapping for event-shaped source extracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


MAPPING_VERSION = "1.0.0"
SOURCE_SYSTEMS = (
    "theatre",
    "laboratory",
    "osna_analyser",
    "communication",
)
DATA_CLASSIFICATIONS = frozenset({"synthetic", "governed_clinical"})


class MappingConfigError(ValueError):
    """Raised when a source-mapping configuration is missing or unsafe."""


@dataclass(frozen=True)
class SourceFileMapping:
    """Describe one source filename, its columns, and controlled-code translations."""

    filename: str
    columns: dict[str, str]
    value_mappings: dict[str, dict[str, str]]


@dataclass(frozen=True)
class SourceMapping:
    """A complete mapping for all four source systems."""

    mapping_version: str
    data_classification: str
    sources: dict[str, SourceFileMapping]
    filename: str
    sha256: str


def _object_without_duplicate_keys(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise MappingConfigError(
                f"Source mapping contains a duplicated JSON key: {key}"
            )
        document[key] = value
    return document


def _require_object(value: object, context: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise MappingConfigError(f"{context} must be a JSON object")
    return value


def _require_exact_keys(
    value: dict[str, object],
    required: set[str],
    context: str,
) -> None:
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - required)
    if missing:
        raise MappingConfigError(f"{context} is missing: {', '.join(missing)}")
    if unexpected:
        raise MappingConfigError(
            f"{context} contains unsupported keys: {', '.join(unexpected)}"
        )


def _parse_columns(value: object, source_system: str) -> dict[str, str]:
    columns_object = _require_object(value, f"{source_system}.columns")
    columns: dict[str, str] = {}
    for canonical_field, source_column in columns_object.items():
        if not isinstance(canonical_field, str) or not canonical_field:
            raise MappingConfigError(
                f"{source_system}.columns contains an invalid canonical field"
            )
        if (
            not isinstance(source_column, str)
            or not source_column
            or source_column != source_column.strip()
        ):
            raise MappingConfigError(
                f"{source_system}.columns.{canonical_field} must be a non-empty "
                "source header without surrounding whitespace"
            )
        columns[canonical_field] = source_column
    if len(set(columns.values())) != len(columns):
        raise MappingConfigError(
            f"{source_system}.columns must not map one source column to multiple fields"
        )
    return columns


def _parse_value_mappings(
    value: object,
    source_system: str,
) -> dict[str, dict[str, str]]:
    mappings_object = _require_object(value, f"{source_system}.value_mappings")
    value_mappings: dict[str, dict[str, str]] = {}
    for canonical_field, field_mapping_value in mappings_object.items():
        field_mapping_object = _require_object(
            field_mapping_value,
            f"{source_system}.value_mappings.{canonical_field}",
        )
        field_mapping: dict[str, str] = {}
        for source_value, canonical_value in field_mapping_object.items():
            if (
                not isinstance(source_value, str)
                or not source_value
                or source_value != source_value.strip()
            ):
                raise MappingConfigError(
                    f"{source_system}.value_mappings.{canonical_field} contains "
                    "an invalid source value"
                )
            if not isinstance(canonical_value, str):
                raise MappingConfigError(
                    f"{source_system}.value_mappings.{canonical_field}.{source_value} "
                    "must map to a string"
                )
            field_mapping[source_value] = canonical_value
        value_mappings[canonical_field] = field_mapping
    return value_mappings


def _parse_source(
    source_system: str,
    value: object,
) -> SourceFileMapping:
    source_object = _require_object(value, source_system)
    _require_exact_keys(
        source_object,
        {"filename", "columns", "value_mappings"},
        source_system,
    )
    filename = source_object["filename"]
    if (
        not isinstance(filename, str)
        or not filename
        or filename != filename.strip()
    ):
        raise MappingConfigError(f"{source_system}.filename must be a non-empty string")
    if (
        Path(filename).name != filename
        or "/" in filename
        or "\\" in filename
        or filename in {".", ".."}
        or not Path(filename).stem
        or not filename.lower().endswith(".csv")
    ):
        raise MappingConfigError(
            f"{source_system}.filename must be a CSV filename without directories"
        )
    return SourceFileMapping(
        filename=filename,
        columns=_parse_columns(source_object["columns"], source_system),
        value_mappings=_parse_value_mappings(
            source_object["value_mappings"],
            source_system,
        ),
    )


def load_source_mapping(path: Path) -> SourceMapping:
    """Load and structurally validate a mapping without reading source data."""

    path = Path(path)
    if path.suffix != ".json":
        raise MappingConfigError("Source mapping filename must end with .json")
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        raise MappingConfigError(f"Source mapping could not be read: {path}") from exc
    try:
        document = json.loads(
            raw_bytes.decode("utf-8"),
            object_pairs_hook=_object_without_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MappingConfigError(
            f"Source mapping is not valid UTF-8 JSON: {path}"
        ) from exc

    root = _require_object(document, "source mapping")
    _require_exact_keys(
        root,
        {"mapping_version", "data_classification", "sources"},
        "source mapping",
    )
    if root["mapping_version"] != MAPPING_VERSION:
        raise MappingConfigError(
            f"mapping_version must be {MAPPING_VERSION!r}"
    )
    data_classification = root["data_classification"]
    if (
        not isinstance(data_classification, str)
        or data_classification not in DATA_CLASSIFICATIONS
    ):
        allowed = ", ".join(sorted(DATA_CLASSIFICATIONS))
        raise MappingConfigError(
            f"data_classification must be one of: {allowed}"
        )

    sources_object = _require_object(root["sources"], "sources")
    _require_exact_keys(sources_object, set(SOURCE_SYSTEMS), "sources")
    sources = {
        source_system: _parse_source(source_system, sources_object[source_system])
        for source_system in SOURCE_SYSTEMS
    }
    source_filenames = [source.filename for source in sources.values()]
    if len(set(source_filenames)) != len(source_filenames):
        raise MappingConfigError(
            "Each source system must use a different CSV filename"
        )
    return SourceMapping(
        mapping_version=MAPPING_VERSION,
        data_classification=str(data_classification),
        sources=sources,
        filename=path.name,
        sha256=hashlib.sha256(raw_bytes).hexdigest(),
    )
