import pandas as pd

from tc_spec.excel_mapper.questions_mapper import map_questions
from tc_spec.excel_mapper.lists_mapper import map_lists


def test_area_answer_options_region_maps_to_area_lv1_and_lists_created_from_area_level_sheets():
    # Minimal raw AREA Level 1 sheet with header=None
    area_lv1_raw = pd.DataFrame(
        {
            0: [None, "SEQ ID", 1, 2],
            1: [None, "ID", "CAM1", "CAM2"],
            2: [None, "Name -Reporting", "Adamaoua", "Centre"],
            3: [None, "Name - App", "Adamaoua", "Centre"],
        }
    )

    # Minimal question sheet with detected header
    questions_sheet = pd.DataFrame(
        [
            {
                "ID": "A-10",
                "Question / Action Detail": "Region",
                "ANSWER OPTIONS": "Region",
                "Type": "Single",
            }
        ]
    )

    sheets = {
        "Area": questions_sheet,
        "AREA Level 1": area_lv1_raw,
    }

    q_df = map_questions(sheets)
    assert len(q_df) == 1
    assert q_df.loc[0, "list_code"] == "LST-AREA-LV1"

    lists_df = map_lists(sheets)
    assert (lists_df["list_code"] == "LST-AREA-LV1").any()
    lv1 = lists_df[lists_df["list_code"] == "LST-AREA-LV1"].sort_values("order")
    assert lv1["value"].tolist() == ["CAM1", "CAM2"]
