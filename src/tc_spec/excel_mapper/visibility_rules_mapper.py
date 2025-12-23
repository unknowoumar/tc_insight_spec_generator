"""
Visibility Rules Mapper

Transforme la logique conditionnelle Excel en règles
VISIBILITY_RULES machine-first.
"""

from typing import Dict, List
import pandas as pd

from tc_spec.utils.helpers import normalize_str
from tc_spec.utils.errors import ExcelValidationError

LOGIC_SHEETS = {
    "Outlet details",
    "Interview Start",
}

_REQUIRED_COLUMNS = [
    "target_type",
    "target_ref",
    "r_ref",
    "operator",
    "value_type",
    "value",
]

def map_visibility_rules(
    sheets: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Mappe les règles de visibilité Excel vers VISIBILITY_RULES machine-first.
    """

    logic_sheets = {
        name: df
        for name, df in sheets.items()
        if name in LOGIC_SHEETS
    }

    rows: List[dict] = []
    for sheet_name, df in logic_sheets.items():
        if df.empty:
            continue

        if not {"DependsOn", "ShowIfValue"}.issubset(df.columns):
            continue
        for _, row in df.iterrows():
            target = normalize_str(row.get("Code"))
            depends_on = normalize_str(row.get("DependsOn"))
            show_value = normalize_str(row.get("ShowIfValue"))

            if not target or not depends_on or not show_value:
                continue
            rows.append({
                "target_type": "question",
                "target_ref": target,
                "r_ref": depends_on,
                "operator": "=",
                "value_type": "a",
                "value": show_value,
            })
    rules_df = pd.DataFrame(rows)

    if rules_df.empty:
        # Pas forcément une erreur → questionnaire sans logique
        return pd.DataFrame(columns=_REQUIRED_COLUMNS)

    required_columns = set(_REQUIRED_COLUMNS)

    if not required_columns.issubset(rules_df.columns):
        raise ExcelValidationError(
            f"VISIBILITY_RULES missing required columns: {required_columns}"
        )

    return rules_df
