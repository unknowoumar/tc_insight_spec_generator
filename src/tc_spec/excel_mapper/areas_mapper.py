"""
AREA Mapper

Transforme les feuilles AREA-LV* en entrées LISTS hiérarchiques
machine-first.
"""

from typing import Dict, List
import re
import pandas as pd

from tc_spec.utils.helpers import normalize_str
from tc_spec.utils.errors import ExcelValidationError


AREA_SHEET_PATTERN = re.compile(r"^AREA-LV(\d+)$")
LIST_CODE_TEMPLATE = "LST-AREA-LV{level}"

def get_area_sheets(sheets: Dict[str, pd.DataFrame]) -> List[tuple[int, str, pd.DataFrame]]:
    """
    Retourne les feuilles AREA-LV* triées par niveau.
    """
    areas = []

    for name, df in sheets.items():
        match = AREA_SHEET_PATTERN.match(name)
        if match:
            level = int(match.group(1))
            areas.append((level, name, df))

    if not areas:
        raise ExcelValidationError(
            "No AREA-LV* sheets found (expected AREA-LV1, AREA-LV2, ...)"
        )

    return sorted(areas, key=lambda x: x[0])

def map_areas_to_lists(
    sheets: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Mappe les feuilles AREA-LV* vers une DataFrame LISTS hiérarchique.
    """

    area_sheets = get_area_sheets(sheets)

    rows: List[dict] = []

    # Dictionnaire pour vérifier l'existence des parents
    values_by_level: Dict[int, set] = {}

    for level, sheet_name, df in area_sheets:
        if df.empty:
            continue

        list_code = LIST_CODE_TEMPLATE.format(level=level)

        # Colonnes attendues (adaptables)
        possible_code_cols = ["Code", "AREA_CODE", "Value"]
        possible_label_cols = ["Label", "Name", "Description"]
        possible_parent_cols = ["Parent", "PARENT_CODE", "ParentCode"]

        code_col = next((c for c in possible_code_cols if c in df.columns), None)
        label_col = next((c for c in possible_label_cols if c in df.columns), None)

        if not code_col or not label_col:
            raise ExcelValidationError(
                f"{sheet_name} must contain a code and label column"
            )

        parent_col = None
        if level > 1:
            parent_col = next(
                (c for c in possible_parent_cols if c in df.columns),
                None
            )
            if not parent_col:
                raise ExcelValidationError(
                    f"{sheet_name} must contain a parent column (level > 1)"
                )

        order = 1
        current_values = set()

        for _, row in df.iterrows():
            value = normalize_str(row.get(code_col))
            label = normalize_str(row.get(label_col))

            if not value or not label:
                continue

            parent = None
            if parent_col:
                parent = normalize_str(row.get(parent_col))
                if not parent:
                    raise ExcelValidationError(
                        f"Missing parent value in {sheet_name} for '{value}'"
                    )

                if parent not in values_by_level.get(level - 1, set()):
                    raise ExcelValidationError(
                        f"Invalid parent '{parent}' for '{value}' in {sheet_name}"
                    )

            rows.append({
                "list_code": list_code,
                "value": value,
                "order": order,
                "lang_SYS": label,
                "parent": parent,
            })

            current_values.add(value)
            order += 1

        values_by_level[level] = current_values

    lists_df = pd.DataFrame(rows)

    if lists_df.empty:
        raise ExcelValidationError(
            "AREA mapping produced an empty LISTS DataFrame"
        )

    if lists_df.duplicated(subset=["list_code", "value"]).any():
        raise ExcelValidationError(
            "Duplicate AREA values detected in LISTS"
        )

    return lists_df
