"""
Lists Mapper

Agrège toutes les sources de listes Excel (AREA, SKU, constantes)
en une seule DataFrame LISTS machine-first.
"""

from typing import Dict, List
import pandas as pd

from tc_spec.utils.errors import ExcelValidationError
from tc_spec.excel_mapper.areas_mapper import map_areas_to_lists
from tc_spec.excel_mapper.skus_mapper import map_skus_to_lists

def map_lists(
    sheets: Dict[str, pd.DataFrame],
    include_constants: bool = True,
) -> pd.DataFrame:
    """
    Agrège toutes les LISTS machine-first à partir des feuilles Excel.
    """

    dfs: List[pd.DataFrame] = []

    # AREA lists
    try:
        area_lists = map_areas_to_lists(sheets)
        dfs.append(area_lists)
    except ExcelValidationError:
        # AREA optionnel selon questionnaire
        pass

    # SKU lists
    try:
        sku_lists = map_skus_to_lists(sheets)
        dfs.append(sku_lists)
    except ExcelValidationError:
        # SKU optionnel
        pass

    if include_constants:
        constants = pd.DataFrame([
            {
                "list_code": "LST-YES-NO",
                "value": "Y",
                "order": 1,
                "lang_SYS": "Yes",
                "parent": None,
            },
            {
                "list_code": "LST-YES-NO",
                "value": "N",
                "order": 2,
                "lang_SYS": "No",
                "parent": None,
            },
        ])
        dfs.append(constants)

    if not dfs:
        raise ExcelValidationError(
            "No LISTS could be generated from the Excel file"
        )

    lists_df = pd.concat(dfs, ignore_index=True)

    required_columns = {
        "list_code",
        "value",
        "order",
        "lang_SYS",
        "parent",
    }

    if not required_columns.issubset(lists_df.columns):
        raise ExcelValidationError(
            f"LISTS missing required columns: {required_columns}"
        )

    lists_df = lists_df[list(required_columns)]

    if lists_df.duplicated(subset=["list_code", "value"]).any():
        duplicates = lists_df[
            lists_df.duplicated(subset=["list_code", "value"], keep=False)
        ]
        raise ExcelValidationError(
            f"Duplicate LIST entries detected:\n{duplicates}"
        )

    all_values = set(lists_df["value"])

    invalid_parents = lists_df[
        lists_df["parent"].notna()
        & ~lists_df["parent"].isin(all_values)
    ]

    if not invalid_parents.empty:
        raise ExcelValidationError(
            f"Invalid parent references detected:\n{invalid_parents}"
        )

    lists_df = lists_df.sort_values(
        by=["list_code", "order"],
        ignore_index=True,
    )

    return lists_df