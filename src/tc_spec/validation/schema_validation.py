"""
TC Insight – Validation JSON Schema

Ce module valide un Spec TC Insight sérialisé
contre le JSON Schema officiel (V2).
"""

import json
from pathlib import Path
from typing import Any, Dict

from jsonschema import Draft7Validator

from tc_spec.utils.errors import SchemaValidationError

def validate_spec_schema(
    spec: Dict[str, Any],
    schema_path: str | Path,
) -> None:
    """
    Valide un Spec sérialisé contre le JSON Schema officiel.

    :param spec: dictionnaire Python (Spec.to_dict())
    :param schema_path: chemin vers le fichier schema JSON
    :raises SchemaValidationError: si invalide
    """

    schema_path = Path(schema_path)

    if not schema_path.exists():
        raise SchemaValidationError(
            f"Schema file not found: {schema_path}"
        )

    try:
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
    except Exception as e:
        raise SchemaValidationError(
            f"Unable to load schema '{schema_path}': {e}"
        ) from e

    validator = Draft7Validator(schema)

    errors = sorted(
        validator.iter_errors(spec),
        key=lambda e: e.path
    )
    if errors:
        messages = []

        for error in errors:
            path = ".".join(str(p) for p in error.path)
            location = f"at '{path}'" if path else "at root"

            messages.append(
                f"{location}: {error.message}"
            )

        raise SchemaValidationError(
            "Schema validation failed:\n"
            + "\n".join(f"- {m}" for m in messages)
        )
