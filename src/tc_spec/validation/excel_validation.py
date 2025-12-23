"""
TC Insight – Validation Excel

Ce module expose une API officielle pour valider la structure
des fichiers Excel machine-first utilisés par le générateur.
"""

from typing import Dict

import pandas as pd

from tc_spec.excel.validators import validate_excel_structure
from tc_spec.utils.errors import ExcelValidationError

def validate_excel(sheets: Dict[str, pd.DataFrame]) -> None:
    """
    Valide la structure d'un Excel déjà chargé.

    :param sheets: dictionnaire {sheet_name: DataFrame}
    :raises ExcelValidationError: si l'Excel est invalide
    """

    try:
        validate_excel_structure(sheets)
    except ExcelValidationError:
        # on relance tel quel (déjà métier)
        raise
    except Exception as e:
        # sécurité : toute autre erreur devient métier
        raise ExcelValidationError(
            f"Unexpected error during Excel validation: {e}"
        ) from e
