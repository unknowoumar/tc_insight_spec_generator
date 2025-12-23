from typing import Dict, List

import pandas as pd

from tc_spec.model.section import Section
from tc_spec.model.question import Question
from tc_spec.model.rule import Rule
from tc_spec.utils.errors import ExcelValidationError

SECTIONS_REQUIRED_COLS = {
    "section_code",
    "section_label",
    "order",
}

def _validate_columns(df: pd.DataFrame):
    missing = SECTIONS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"SECTIONS missing columns: {missing}"
        )

def build_sections(
    sections_df: pd.DataFrame,
    questions: Dict[str, Question],
    rules_by_target: Dict[str, List[Rule]],
) -> Dict[str, Section]:
    """
    Construit les sections du spec.

    Retour :
      {
        "I": Section,
        "V": Section
      }
    """
    _validate_columns(sections_df)
    questions_by_section: Dict[str, List[Question]] = {}

    for ref, question in questions.items():
        section_code = ref.split("-")[0]
        questions_by_section.setdefault(section_code, []).append(question)
    sections: Dict[str, Section] = {}

    ordered_rows = sections_df.sort_values("order")
    for _, row in ordered_rows.iterrows():
        code = str(row["section_code"]).strip()

        if code not in questions_by_section:
            raise ExcelValidationError(
                f"Section '{code}' has no questions"
            )

        visibility = rules_by_target.get(f"section:{code}", [])
        section = Section(
            code=code,
            name=row["section_label"],
            questions=questions_by_section[code],
            visibility=visibility,
        )

        sections[code] = section
    return sections
