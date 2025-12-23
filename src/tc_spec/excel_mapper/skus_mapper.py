"""
SKU Mapper

Transforme les feuilles SKU (V70 / V80 / V90 ...)
en entrées LISTS machine-first.
"""

from typing import Dict, List
import pandas as pd

from tc_spec.utils.helpers import normalize_str
from tc_spec.utils.errors import ExcelValidationError

LIST_CODE_TEMPLATE = "LST-SKU-{code}"

def is_sku_sheet(sheet_name: str) -> bool:
    """
    Détecte si une feuille correspond à une feuille SKU.
    Exemples valides :
    - V70 SKU
    - V80 SKU
    """
    return (
        sheet_name.startswith("V")
        and sheet_name.endswith("SKU")
        and sheet_name.split()[0][1:].isdigit()
    )
def map_skus_to_lists(
    sheets: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Mappe les feuilles SKU Excel vers une DataFrame LISTS machine-first.
    """
    sku_sheets = {
        name: df
        for name, df in sheets.items()
        if is_sku_sheet(name)
    }

    if not sku_sheets:
        raise ExcelValidationError(
            "No SKU sheets found (expected sheets like 'V70 SKU')"
        )
    rows: List[dict] = []

    for sheet_name, df in sku_sheets.items():
        # Exemple: "V70 SKU" → V70
        sku_code = sheet_name.split()[0]
        list_code = LIST_CODE_TEMPLATE.format(code=sku_code)
        if df.empty:
            continue

        # Colonnes candidates (on s’adapte au réel)
        possible_code_cols = ["SKU", "Code", "SKU Code"]
        possible_label_cols = ["Label", "Name", "Description"]

        code_col = next(
            (c for c in possible_code_cols if c in df.columns),
            None
        )
        label_col = next(
            (c for c in possible_label_cols if c in df.columns),
            None
        )

        if not code_col or not label_col:
            raise ExcelValidationError(
                f"SKU sheet '{sheet_name}' must contain a code and label column"
            )
        order = 1

        for _, row in df.iterrows():
            value = normalize_str(row.get(code_col))
            label = normalize_str(row.get(label_col))

            if not value or not label:
                continue  # lignes vides ignorées proprement

            rows.append({
                "list_code": list_code,
                "value": value,
                "order": order,
                "lang_SYS": label,
                "parent": None,
            })

            order += 1
    lists_df = pd.DataFrame(rows)

    if lists_df.empty:
        raise ExcelValidationError(
            "SKU mapping produced an empty LISTS DataFrame"
        )

    # Unicité (list_code, value)
    if lists_df.duplicated(subset=["list_code", "value"]).any():
        raise ExcelValidationError(
            "Duplicate SKU values detected in LISTS"
        )

    return lists_df
