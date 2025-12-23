"""
TC Insight – Utilitaires

Ce module expose les fonctions utilitaires et exceptions
utilisées dans l'ensemble du générateur de Specs TC Insight.
"""

from tc_spec.utils.errors import (
    SpecError,
    ExcelValidationError,
    BuilderError,
    ModelError,
    SchemaValidationError,
    ExportError,
)

from tc_spec.utils.helpers import (
    normalize_str,
    safe_int,
    safe_number,
    parse_csv,
    has_duplicates,
    clean_dict,
)

__all__ = [
    # Errors
    "SpecError",
    "ExcelValidationError",
    "BuilderError",
    "ModelError",
    "SchemaValidationError",
    "ExportError",

    # Helpers
    "normalize_str",
    "safe_int",
    "safe_number",
    "parse_csv",
    "has_duplicates",
    "clean_dict",
]
