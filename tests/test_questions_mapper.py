import pandas as pd
import pytest

from tc_spec.excel_mapper.questions_mapper import map_questions


def test_map_questions_visibility_columns_build_roles_e_b_bp():
    sheets = {
        "Sheet1": pd.DataFrame(
            [
                {
                    "ID": "V-50",
                    "Question / Action Detail": "How many units?",
                    "Type": "Numeric",
                    "Visible ENUMERATOR": "Yes",
                    "VISIBLE BC": "Yes",
                    "PREFILLED FOR BC": "Yes",
                }
            ]
        )
    }

    df = map_questions(sheets)

    assert len(df) == 1
    assert df.loc[0, "section"] == "V"
    assert df.loc[0, "q_num"] == "50"
    assert df.loc[0, "roles"] == "e,b,bp"


def test_map_questions_visibility_columns_all_no_omits_roles():
    sheets = {
        "Sheet1": pd.DataFrame(
            [
                {
                    "ID": "V-50",
                    "Question / Action Detail": "How many units?",
                    "Type": "Numeric",
                    "Visible ENUMERATOR": "No",
                    "VISIBLE BC": "No",
                    "PREFILLED FOR BC": "No",
                }
            ]
        )
    }

    df = map_questions(sheets)

    assert len(df) == 1
    assert pd.isna(df.loc[0, "roles"])


def test_map_questions_without_visibility_columns_falls_back_to_roles_column():
    sheets = {
        "Sheet1": pd.DataFrame(
            [
                {
                    "ID": "V-50",
                    "Question / Action Detail": "How many units?",
                    "Type": "Numeric",
                    "Roles": "e,bp",
                }
            ]
        )
    }

    df = map_questions(sheets)

    assert len(df) == 1
    assert df.loc[0, "roles"] == "e,bp"
