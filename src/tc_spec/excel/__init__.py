
"""
TC Insight – Excel interface

Ce module gère le chargement et la validation des fichiers Excel
machine-first utilisés pour générer des Specs TC Insight (V2).
"""

from pathlib import Path
from typing import Dict

import pandas as pd

from tc_spec.excel.loader import load_excel, load_excel_all
from tc_spec.excel.validators import validate_excel_structure

def load_and_validate_excel(path: str | Path) -> Dict[str, pd.DataFrame]:
    """
    Charge un fichier Excel et valide sa structure.

    Toute incohérence ou ambiguïté provoque une exception bloquante.
    """
    sheets = load_excel(path)
    validate_excel_structure(sheets)
    return sheets

__all__ = [
    "load_and_validate_excel",
    "load_excel_all",
]
