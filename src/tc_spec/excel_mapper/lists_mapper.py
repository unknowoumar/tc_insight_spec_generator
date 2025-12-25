"""
Lists Mapper

Agrège toutes les sources de listes Excel (AREA, SKU, constantes)
en une seule DataFrame LISTS machine-first.
"""

from typing import Dict, List

import logging
import pandas as pd

from tc_spec.utils.errors import ExcelValidationError
from tc_spec.excel_mapper.areas_mapper import map_areas_to_lists
from tc_spec.excel_mapper.skus_mapper import map_skus_to_lists
from tc_spec.excel_mapper.constants_mapper import map_constants_lists
from tc_spec.excel_mapper.metier_utils import (
    ANSWER_OPTIONS_COLS,
    answer_options_is_yes_no,
    normalize_sheet_df,
    parse_sheet_cell_ref,
    slugify_list_code,
)


QUESTION_SHEETS_EXCLUDE = {
    "Instructions",
    "Constants",
    "Lists to Update",
}

logger = logging.getLogger(__name__)


def _extract_vertical_values(raw_df: pd.DataFrame, start_row: int, col: int) -> List[str]:
    values: List[str] = []

    if raw_df.empty:
        return values

    max_rows = len(raw_df)
    for r in range(start_row, max_rows):
        if col >= len(raw_df.columns):
            break
        v = raw_df.iat[r, col]
        if v is None or pd.isna(v) or str(v).strip() == "":
            break
        values.append(str(v).strip())
    return values


def _map_dynamic_lists_from_answer_options(
    sheets: Dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: List[dict] = []
    seen: set[tuple[str, str]] = set()

    logger.info("Dynamic lists: scanning %d sheets for ANSWER OPTIONS", len(sheets))

    for sheet_name, raw_df in sheets.items():
        if sheet_name in QUESTION_SHEETS_EXCLUDE:
            continue

        df = normalize_sheet_df(raw_df)
        if df.empty:
            logger.debug("Dynamic lists: sheet '%s' ignored (empty or header not detected)", sheet_name)
            continue

        answer_col = next((c for c in ANSWER_OPTIONS_COLS if c in df.columns), None)
        if not answer_col:
            logger.debug("Dynamic lists: sheet '%s' has no ANSWER OPTIONS column", sheet_name)
            continue

        logger.debug("Dynamic lists: sheet '%s' uses ANSWER OPTIONS column '%s'", sheet_name, answer_col)

        for _, row in df.iterrows():
            ref_value = row.get(answer_col)

            if ref_value is None or pd.isna(ref_value) or str(ref_value).strip() == "":
                continue

            if answer_options_is_yes_no(ref_value):
                logger.debug("Dynamic lists: '%s' -> Yes/No constant list (skip dynamic creation)", ref_value)
                continue

            parsed = parse_sheet_cell_ref(ref_value)
            if not parsed:
                logger.debug("Dynamic lists: unable to parse ANSWER OPTIONS ref '%s'", ref_value)
                continue

            target_sheet, start_row, col = parsed
            target_raw = sheets.get(target_sheet)
            if target_raw is None:
                logger.warning(
                    "Dynamic lists: target sheet '%s' not found (ref '%s' from sheet '%s')",
                    target_sheet,
                    ref_value,
                    sheet_name,
                )
                continue

            list_code = slugify_list_code(target_sheet)
            values = _extract_vertical_values(target_raw, start_row, col)
            if not values:
                logger.warning(
                    "Dynamic lists: extracted 0 values for list '%s' from '%s' starting at row=%d col=%d (ref '%s')",
                    list_code,
                    target_sheet,
                    start_row,
                    col,
                    ref_value,
                )
                continue

            logger.info(
                "Dynamic lists: creating/updating list '%s' from '%s' (%d values)",
                list_code,
                target_sheet,
                len(values),
            )
            for i, v in enumerate(values, start=1):
                key = (list_code, v)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "list_code": list_code,
                        "value": v,
                        "order": i,
                        "lang_SYS": v,
                        "parent": None,
                    }
                )

    logger.info(
        "Dynamic lists: generated %d rows across %d unique (list_code,value) pairs",
        len(rows),
        len(seen),
    )

    return pd.DataFrame(rows)

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
    except ExcelValidationError as e:
        # AREA optionnel selon questionnaire
        logger.warning("AREA lists mapping skipped: %s", e)

    # Constants lists from C&C Lists and I&M Lists sheets
    try:
        constants_lists = map_constants_lists(sheets)
        if not constants_lists.empty:
            dfs.append(constants_lists)
    except Exception as e:
        logger.warning("Constants lists mapping skipped: %s", e)

    # Dynamic lists referenced from question sheets (ANSWER OPTIONS)
    dynamic_lists = _map_dynamic_lists_from_answer_options(sheets)
    if not dynamic_lists.empty:
        dfs.append(dynamic_lists)

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