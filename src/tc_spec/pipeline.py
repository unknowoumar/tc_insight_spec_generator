"""
Excel Mapping Pipeline

Assemble les différents mappers pour transformer
un Excel métier en Excel machine-first contractuel.
"""

from typing import Dict
import pandas as pd

from tc_spec.excel_mapper import (
    map_lists,
    map_questions,
    map_visibility_rules,
)
from tc_spec.utils.errors import ExcelValidationError

def map_excel_to_machine_first(
    sheets: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Transforme un Excel métier en Excel machine-first.

    :param sheets: dictionnaire {sheet_name: DataFrame}
    :return: dictionnaire normalisé prêt pour le générateur
    """

    lists_df = map_lists(sheets)

    if lists_df.empty:
        raise ExcelValidationError(
            "Mapping failed: LISTS is empty"
        )
    questions_df = map_questions(sheets)

    if questions_df.empty:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS is empty"
        )
    rules_df = map_visibility_rules(sheets)

    if "type" not in questions_df.columns:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS must contain a 'type' column to build QUESTION_TYPES"
        )

    question_types_df = questions_df[["section", "q_num", "type"]].copy()

    if "section" not in questions_df.columns:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS must contain a 'section' column to build SECTIONS"
        )

    sections_df = (
        questions_df[["section"]]
        .drop_duplicates()
        .sort_values("section")
        .reset_index(drop=True)
    )
    sections_df = sections_df.rename(
        columns={"section": "section_code"}
    )
    sections_df["section_label"] = sections_df["section_code"]
    sections_df["order"] = range(1, len(sections_df) + 1)

    anomalies_df = pd.DataFrame(columns=["anomaly_code", "weight"])

    return {
        "QUESTIONS": questions_df.reset_index(drop=True),
        "QUESTION_TYPES": question_types_df.reset_index(drop=True),
        "SECTIONS": sections_df.reset_index(drop=True),
        "LISTS": lists_df.reset_index(drop=True),
        "VISIBILITY_RULES": rules_df.reset_index(drop=True),
        "ANOMALIES": anomalies_df,
    }
