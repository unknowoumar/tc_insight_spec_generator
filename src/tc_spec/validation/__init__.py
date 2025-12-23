"""
TC Insight – Validation

Ce module expose les fonctions de validation officielles du
générateur de Specs TC Insight (V2).
"""

from tc_spec.validation.excel_validation import validate_excel
from tc_spec.validation.schema_validation import validate_spec_schema

__all__ = [
    "validate_excel",
    "validate_spec_schema",
]
