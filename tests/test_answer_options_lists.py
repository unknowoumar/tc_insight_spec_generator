import pandas as pd

from tc_spec.excel_mapper.lists_mapper import map_lists
from tc_spec.excel_mapper.questions_mapper import map_questions


def test_answer_options_yes_no_maps_to_lst_yes_no():
    sheets = {
        "Questions": pd.DataFrame(
            [
                {
                    "ID": "V-01",
                    "Question / Action Detail": "Do you agree?",
                    "ANSWER OPTIONS": "Yes/No",
                    "Type": "Single",
                }
            ]
        )
    }

    questions_df = map_questions(sheets)
    assert len(questions_df) == 1
    assert questions_df.loc[0, "list_code"] == "LST-YES-NO"

    lists_df = map_lists(sheets)
    assert (lists_df["list_code"] == "LST-YES-NO").any()


def test_answer_options_sheet_ref_creates_dynamic_list_and_maps_question_list_code():
    sheets = {
        "Questions": pd.DataFrame(
            [
                {
                    "ID": "V-02",
                    "Question / Action Detail": "Select province",
                    "ANSWER OPTIONS": "Province List!D2",
                    "Type": "Single",
                }
            ]
        ),
        # Simulate a raw Excel sheet loaded with header=None
        # We want values starting at D2 => row index 1, col index 3
        "Province List": pd.DataFrame(
            {
                0: [None, None, None, None],
                1: [None, None, None, None],
                2: [None, None, None, None],
                3: [None, "Centre", "Littoral", None],
            }
        ),
    }

    questions_df = map_questions(sheets)
    assert len(questions_df) == 1
    assert questions_df.loc[0, "list_code"] == "LST-PROVINCE-LIST-DYN"

    lists_df = map_lists(sheets)
    dyn = lists_df[lists_df["list_code"] == "LST-PROVINCE-LIST-DYN"].sort_values("order")
    assert dyn["value"].tolist() == ["Centre", "Littoral"]
