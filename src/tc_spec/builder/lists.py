from typing import Dict

import pandas as pd

from tc_spec.model.list import SpecList, ListItem
from tc_spec.utils.errors import ExcelValidationError

LISTS_REQUIRED_COLS = {
    "list_code",
    "value",
    "lang_SYS",
}

def _validate_columns(df: pd.DataFrame):
    missing = LISTS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"LISTS missing columns: {missing}"
        )

def build_lists(lists_df: pd.DataFrame) -> Dict[str, SpecList]:
    """
    Construit les listes du spec.

    Retour :
      {
        "LST-SEGMENT": SpecList,
        "LST-CHANNEL": SpecList
      }
    """

    _validate_columns(lists_df)
    lists: Dict[str, SpecList] = {}

    grouped = lists_df.sort_values("order").groupby("list_code")
    for list_code, group in grouped:
        items = []

        for _, row in group.iterrows():
            labels = {
                k.replace("lang_", ""): v
                for k, v in row.items()
                if k.startswith("lang_") and pd.notna(v)
            }

            item = ListItem(
                value=str(row["value"]),
                labels=labels,
            )

            items.append(item)
        spec_list = SpecList(
            code=list_code,
            items=items,
        )

        lists[list_code] = spec_list
    return lists
