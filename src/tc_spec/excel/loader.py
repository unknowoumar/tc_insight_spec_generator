from pathlib import Path
from typing import Dict

import pandas as pd

from tc_spec.utils.errors import ExcelValidationError

REQUIRED_SHEETS = {
    "QUESTIONS",
    "QUESTION_TYPES",
    "SECTIONS",
    "LISTS",
    "VISIBILITY_RULES",
    "ANOMALIES",
}

def load_excel(path: str | Path) -> Dict[str, pd.DataFrame]:
    """
    Charge un fichier Excel et retourne les feuilles requises
    sous forme de DataFrames.

    Aucune validation métier n'est effectuée ici.
    """

    excel_path = Path(path)

    if not excel_path.exists():
        raise ExcelValidationError(
            f"Excel file not found: {excel_path}"
        )

    try:
        xls = pd.ExcelFile(excel_path)
    except Exception as e:
        raise ExcelValidationError(
            f"Unable to open Excel file '{excel_path}': {e}"
        ) from e

    available_sheets = {name.strip() for name in xls.sheet_names}
    missing_sheets = REQUIRED_SHEETS - available_sheets

    if missing_sheets:
        raise ExcelValidationError(
            f"Missing required sheets: {sorted(missing_sheets)}"
        )
    sheets: Dict[str, pd.DataFrame] = {}

    for sheet_name in REQUIRED_SHEETS:
        try:
            df = pd.read_excel(
                xls,
                sheet_name=sheet_name,
                dtype=object
            )
        except Exception as e:
            raise ExcelValidationError(
                f"Failed to load sheet '{sheet_name}': {e}"
            ) from e

        sheets[sheet_name] = df

    return sheets


def load_excel_all(path: str | Path) -> Dict[str, pd.DataFrame]:
    excel_path = Path(path)

    if not excel_path.exists():
        raise ExcelValidationError(
            f"Excel file not found: {excel_path}"
        )

    try:
        xls = pd.ExcelFile(excel_path)
    except Exception as e:
        raise ExcelValidationError(
            f"Unable to open Excel file '{excel_path}': {e}"
        ) from e

    sheets: Dict[str, pd.DataFrame] = {}
    for sheet_name in xls.sheet_names:
        name = str(sheet_name).strip()
        try:
            sheets[name] = pd.read_excel(
                xls,
                sheet_name=sheet_name,
                dtype=object,
                header=None,
            )
        except Exception as e:
            raise ExcelValidationError(
                f"Failed to load sheet '{name}': {e}"
            ) from e

    return sheets