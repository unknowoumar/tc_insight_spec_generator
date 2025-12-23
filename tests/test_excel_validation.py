import pandas as pd
import pytest

from tc_spec.validation import validate_excel
from tc_spec.utils.errors import ExcelValidationError

def make_valid_sheets():
    return {
        "QUESTIONS": pd.DataFrame([
            {
                "section": "V",
                "q_num": "50",
                "label": "Q_V_50",
                "lang_SYS": "How many units?",
            }
        ]),
        "QUESTION_TYPES": pd.DataFrame([
            {
                "section": "V",
                "q_num": "50",
                "type": "N",
            }
        ]),
        "SECTIONS": pd.DataFrame([
            {
                "section_code": "V",
                "section_label": "Volume",
                "order": 1,
            }
        ]),
        "LISTS": pd.DataFrame([
            {
                "list_code": "LST-TEST",
                "value": "A",
                "lang_SYS": "Option A",
            }
        ]),
        "VISIBILITY_RULES": pd.DataFrame([
            {
                "target_type": "question",
                "target_ref": "V-50",
                "r_ref": "I-10",
                "operator": "=",
                "value_type": "v",
                "value": "YES",
            }
        ]),
        "ANOMALIES": pd.DataFrame([
            {
                "anomaly_code": "ANO-A1",
                "weight": 10,
            }
        ]),
    }

def test_validate_excel_ok():
    sheets = make_valid_sheets()
    validate_excel(sheets)  # ne doit pas lever d’erreur

def test_empty_sheet_fails():
    sheets = make_valid_sheets()
    sheets["QUESTIONS"] = pd.DataFrame()

    with pytest.raises(ExcelValidationError):
        validate_excel(sheets)

def test_missing_required_column_in_questions():
    sheets = make_valid_sheets()
    sheets["QUESTIONS"] = sheets["QUESTIONS"].drop(columns=["label"])

    with pytest.raises(ExcelValidationError):
        validate_excel(sheets)

def test_duplicate_questions_fails():
    sheets = make_valid_sheets()
    sheets["QUESTIONS"] = pd.concat(
        [sheets["QUESTIONS"], sheets["QUESTIONS"]],
        ignore_index=True,
    )

    with pytest.raises(ExcelValidationError):
        validate_excel(sheets)

def test_invalid_question_type():
    sheets = make_valid_sheets()
    sheets["QUESTION_TYPES"].loc[0, "type"] = "X"

    with pytest.raises(ExcelValidationError):
        validate_excel(sheets)

def test_invalid_anomaly_weight():
    sheets = make_valid_sheets()
    sheets["ANOMALIES"].loc[0, "weight"] = -5

    with pytest.raises(ExcelValidationError):
        validate_excel(sheets)
