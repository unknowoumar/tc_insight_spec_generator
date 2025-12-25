import pytest
from pathlib import Path

from tc_spec.validation import validate_spec_schema
from tc_spec.utils.errors import SchemaValidationError

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "spec_v2.schema.json"

def test_valid_spec_schema():
    valid_spec = {
        "n": "TC Insight Test",
        "v": "2.0.0",
        "s": {
            "V": {
                "n": "Volume",
                "p": [
                    {
                        "V-50": {
                            "label": "Q_V_50",
                            "n": {
                                "SYS": "How many units?"
                            },
                            "t": [
                                {
                                    "t": "N"
                                }
                            ]
                        }
                    }
                ]
            }
        },
        "l": {},
        "a": {}
    }

    # Ne doit pas lever d'erreur
    validate_spec_schema(valid_spec, SCHEMA_PATH)

def test_missing_required_field_fails():
    invalid_spec = {
        # "n" manquant
        "v": "2.0.0",
        "s": [],
        "l": {},
        "a": {}
    }

    with pytest.raises(SchemaValidationError):
        validate_spec_schema(invalid_spec, SCHEMA_PATH)

def test_invalid_question_type_fails():
    invalid_spec = {
        "n": "Invalid Spec",
        "v": "2.0.0",
        "s": [
            {
                "c": "V",
                "n": "Volume",
                "q": [
                    {
                        "r": "V-50",
                        "l": "Q_V_50",
                        "n": {
                            "SYS": "How many units?"
                        },
                        "t": {
                            "t": "X"  # type invalide
                        }
                    }
                ]
            }
        ],
        "l": {},
        "a": {}
    }

    with pytest.raises(SchemaValidationError):
        validate_spec_schema(invalid_spec, SCHEMA_PATH)

def test_invalid_sections_structure():
    invalid_spec = {
        "n": "Invalid Spec",
        "v": "2.0.0",
        "s": [  # devrait être un objet (mapping)
            {
                "c": "V"
            }
        ],
        "l": {},
        "a": {}
    }

    with pytest.raises(SchemaValidationError):
        validate_spec_schema(invalid_spec, SCHEMA_PATH)
