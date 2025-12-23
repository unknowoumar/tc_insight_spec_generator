from typing import Dict, Set, Tuple

import pandas as pd

from tc_spec.utils.errors import ExcelValidationError

_ALLOW_EMPTY_SHEETS = {
    "VISIBILITY_RULES",
    "ANOMALIES",
}

def _validate_non_empty(sheets: Dict[str, pd.DataFrame]):
    for name, df in sheets.items():
        if name in _ALLOW_EMPTY_SHEETS:
            continue
        if df.empty:
            raise ExcelValidationError(
                f"Sheet '{name}' must not be empty"
            )

QUESTIONS_REQUIRED_COLS = {
    "section",
    "q_num",
    "label",
}

def _validate_questions(df: pd.DataFrame):
    missing = QUESTIONS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"QUESTIONS missing columns: {missing}"
        )

    seen: Set[Tuple[str, str]] = set()

    for idx, row in df.iterrows():
        key = (str(row["section"]), str(row["q_num"]))

        if key in seen:
            raise ExcelValidationError(
                f"Duplicate question {key} in QUESTIONS (row {idx})"
            )
        seen.add(key)

        # au moins une langue
        lang_cols = [c for c in df.columns if c.startswith("lang_")]
        if not lang_cols:
            raise ExcelValidationError(
                "QUESTIONS must define at least one lang_* column"
            )

        if all(pd.isna(row[c]) for c in lang_cols):
            raise ExcelValidationError(
                f"Question {key} has no label in any language (row {idx})"
            )

QUESTION_TYPES_REQUIRED_COLS = {
    "section",
    "q_num",
    "type",
}

ALLOWED_TYPES = {"O", "T", "TM", "N", "C", "I", "A", "-"}

def _validate_question_types(df: pd.DataFrame):
    missing = QUESTION_TYPES_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"QUESTION_TYPES missing columns: {missing}"
        )

    seen: Set[Tuple[str, str]] = set()

    for idx, row in df.iterrows():
        key = (str(row["section"]), str(row["q_num"]))

        if key in seen:
            raise ExcelValidationError(
                f"Multiple types defined for question {key} (row {idx})"
            )
        seen.add(key)

        if row["type"] not in ALLOWED_TYPES:
            raise ExcelValidationError(
                f"Invalid question type '{row['type']}' for {key}"
            )

def _validate_questions_have_types(
    questions_df: pd.DataFrame,
    types_df: pd.DataFrame,
):
    q_keys = {
        (str(r["section"]), str(r["q_num"]))
        for _, r in questions_df.iterrows()
    }
    t_keys = {
        (str(r["section"]), str(r["q_num"]))
        for _, r in types_df.iterrows()
    }

    missing = q_keys - t_keys
    if missing:
        raise ExcelValidationError(
            f"Questions without types: {missing}"
        )

SECTIONS_REQUIRED_COLS = {
    "section_code",
    "section_label",
    "order",
}

def _validate_sections(df: pd.DataFrame, questions_df: pd.DataFrame):
    missing = SECTIONS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"SECTIONS missing columns: {missing}"
        )

    if df["section_code"].duplicated().any():
        raise ExcelValidationError(
            "Duplicate section_code in SECTIONS"
        )

    if df["order"].duplicated().any():
        raise ExcelValidationError(
            "Duplicate order in SECTIONS"
        )

    question_sections = set(questions_df["section"].astype(str))
    declared_sections = set(df["section_code"].astype(str))

    orphan = question_sections - declared_sections
    if orphan:
        raise ExcelValidationError(
            f"Questions reference undefined sections: {orphan}"
        )

LISTS_REQUIRED_COLS = {
    "list_code",
    "value",
}

def _validate_lists(df: pd.DataFrame):
    missing = LISTS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"LISTS missing columns: {missing}"
        )

    duplicated = df.duplicated(subset=["list_code", "value"])
    if duplicated.any():
        raise ExcelValidationError(
            "Duplicate (list_code, value) in LISTS"
        )

VISIBILITY_REQUIRED_COLS = {
    "target_type",
    "target_ref",
    "r_ref",
    "operator",
    "value_type",
    "value",
}

ALLOWED_TARGETS = {"question", "section", "anomaly"}
ALLOWED_OPERATORS = {"=", "!", ">", "<", ">=", "<=", "e", "!e"}
ALLOWED_VALUE_TYPES = {"v", "a"}

def _validate_visibility_rules(df: pd.DataFrame):
    missing = VISIBILITY_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"VISIBILITY_RULES missing columns: {missing}"
        )

    for idx, row in df.iterrows():
        if row["target_type"] not in ALLOWED_TARGETS:
            raise ExcelValidationError(
                f"Invalid target_type '{row['target_type']}' (row {idx})"
            )

        if row["operator"] not in ALLOWED_OPERATORS:
            raise ExcelValidationError(
                f"Invalid operator '{row['operator']}' (row {idx})"
            )

        if row["value_type"] not in ALLOWED_VALUE_TYPES:
            raise ExcelValidationError(
                f"Invalid value_type '{row['value_type']}' (row {idx})"
            )

ANOMALIES_REQUIRED_COLS = {
    "anomaly_code",
    "weight",
}

def _validate_anomalies(df: pd.DataFrame):
    missing = ANOMALIES_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"ANOMALIES missing columns: {missing}"
        )

    if df["anomaly_code"].duplicated().any():
        raise ExcelValidationError(
            "Duplicate anomaly_code in ANOMALIES"
        )

    for idx, w in df["weight"].items():
        try:
            if int(w) <= 0:
                raise ValueError
        except Exception:
            raise ExcelValidationError(
                f"Invalid weight at row {idx}: must be > 0"
            )

def validate_excel_structure(sheets: Dict[str, pd.DataFrame]) -> None:
    """
    Validation complète de la structure Excel (machine-first).
    """
    _validate_non_empty(sheets)

    _validate_questions(sheets["QUESTIONS"])
    _validate_question_types(sheets["QUESTION_TYPES"])
    _validate_questions_have_types(
        sheets["QUESTIONS"],
        sheets["QUESTION_TYPES"],
    )
    _validate_sections(
        sheets["SECTIONS"],
        sheets["QUESTIONS"],
    )
    _validate_lists(sheets["LISTS"])
    _validate_visibility_rules(sheets["VISIBILITY_RULES"])
    _validate_anomalies(sheets["ANOMALIES"])
