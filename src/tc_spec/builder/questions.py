from typing import Dict

import pandas as pd

from tc_spec.model.question import Question
from tc_spec.model.rule import Rule
from tc_spec.utils.errors import ExcelValidationError

QUESTIONS_REQUIRED_COLS = {
    "section", "q_num", "label", "lang_SYS"
}

QUESTION_TYPES_REQUIRED_COLS = {
    "section", "q_num", "type"
}

def _validate_columns(df: pd.DataFrame, required: set, sheet: str):
    missing = required - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"{sheet} missing columns: {missing}"
        )

def _build_qtype(row: pd.Series) -> dict:
    qtype = {"t": row["type"]}

    if pd.notna(row.get("min")):
        qtype["-"] = row["min"]

    if pd.notna(row.get("max")):
        qtype["+"] = row["max"]

    if pd.notna(row.get("default")):
        qtype["d"] = row["default"]

    if pd.notna(row.get("regex")):
        qtype["regex"] = row["regex"]

    if pd.notna(row.get("list_code")):
        qtype["o"] = row["list_code"]

    if pd.notna(row.get("choice_limit")):
        qtype["c"] = int(row["choice_limit"])

    if pd.notna(row.get("auto_code")):
        qtype["i"] = row["auto_code"]

    return qtype

def build_questions(
    questions_df: pd.DataFrame,
    question_types_df: pd.DataFrame,
    rules_by_target: Dict[str, list],
) -> Dict[str, Question]:
    """
    Construit toutes les questions du spec.

    Retour :
      {
        "V-50": Question,
        "I-01": Question
      }
    """
    _validate_columns(questions_df, QUESTIONS_REQUIRED_COLS, "QUESTIONS")
    _validate_columns(question_types_df, QUESTION_TYPES_REQUIRED_COLS, "QUESTION_TYPES")

    type_index = {}

    for _, row in question_types_df.iterrows():
        ref = f"{row['section']}-{row['q_num']}"
        if ref in type_index:
            raise ExcelValidationError(
                f"Multiple types defined for question {ref}"
            )
        type_index[ref] = _build_qtype(row)


    questions: Dict[str, Question] = {}

    for _, row in questions_df.iterrows():
        ref = f"{row['section']}-{row['q_num']}"

        if ref not in type_index:
            raise ExcelValidationError(
                f"Missing question type for {ref}"
            )

        texts = {
            k.replace("lang_", ""): v
            for k, v in row.items()
            if k.startswith("lang_") and pd.notna(v)
        }

        roles = []
        if pd.notna(row.get("roles")):
            roles = [r.strip() for r in str(row["roles"]).split(",")]

        visibility = rules_by_target.get(f"question:{ref}", [])

        question = Question(
            ref=ref,
            label=row["label"],
            texts=texts,
            qtype=type_index[ref],
            roles=roles,
            visibility=visibility,
        )

        questions[ref] = question

    return questions
