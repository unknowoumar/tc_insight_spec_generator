"""
Questions Mapper

Transforme les feuilles questions Excel en DataFrame QUESTIONS
machine-first.
"""

from typing import Dict, List

import logging
import pandas as pd

from tc_spec.excel_mapper.metier_utils import (
    ANSWER_OPTIONS_COLS,
    answer_options_is_yes_no,
    parse_sheet_cell_ref,
    slugify_list_code,
)
from tc_spec.excel_mapper.constants_mapper import build_list_name_to_code_index
from tc_spec.excel_mapper.questions_utils import (
    is_removed_by_priority,
    is_yes,
    map_metier_type_to_code,
    parse_question_refs,
    with_detected_header,
)
from tc_spec.utils.helpers import normalize_str, parse_csv
from tc_spec.utils.errors import ExcelValidationError


logger = logging.getLogger(__name__)


_ANSWER_OPTIONS_TO_LIST_CODE = {
    "region": "LST-AREA-LV1",
    "prefecture": "LST-AREA-LV2",
    "sub-prefecture/commune": "LST-AREA-LV3",
    "sub prefecture/commune": "LST-AREA-LV3",
    "sub-prefecture": "LST-AREA-LV3",
    "sub prefecture": "LST-AREA-LV3",
}

QUESTION_SHEETS_EXCLUDE = {
    "Instructions",
    "Constants",
    "Lists to Update",
}

QUESTION_CODE_COLS = [
    "Code",
    "Q_CODE",
    "QuestionCode",
    "Question",
    "Question #",
    "ID",
]
QUESTION_LABEL_COLS = [
    "Label",
    "Question Label",
    "Text",
    "Description",
    "Question / Action Detail",
    "QUESTION WORDING EN",
    "QUESTION WORDING FR",
]
QUESTION_TYPE_COLS = ["Type", "Q_TYPE", "ANSWER TYPE"]
QUESTION_LIST_COLS = ["List", "ListCode", "LIST_CODE"]
QUESTION_ROLES_COLS = ["Roles", "ROLE"]
QUESTION_VISIBLE_ENUMERATOR_COLS = [
    "Visible ENUMERATOR",
    "Visible Enumerator",
    "VISIBLE ENUMERATOR",
    "visible enumerator",
]
QUESTION_VISIBLE_BC_COLS = [
    "VISIBLE BC",
    "Visible BC",
    "Visible BackChecker",
    "visible bc",
]
QUESTION_PREFILLED_FOR_BC_COLS = [
    "PREFILLED FOR BC",
    "Prefilled for BC",
    "Prefield BC",
    "PREFIELD BC",
    "prefilled for bc",
]
QUESTION_MANDATORY_COLS = ["Mandatory", "Required"]

QUESTION_PRIORITY_COLS = [
    "Question Priority  1 Keep 0 Discuss -1 remove ?",
    "Question Priority 1 Keep 0 Discuss -1 remove ?",
    "Question Priority",
]

def is_question_sheet(sheet_name: str) -> bool:
    """
    Détermine si une feuille est une feuille de questions.
    """
    return sheet_name not in QUESTION_SHEETS_EXCLUDE

def _has_any_column(df: pd.DataFrame, candidates: List[str]) -> bool:
    return any(c in df.columns for c in candidates)

def map_questions(
    sheets: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Mappe les feuilles questions Excel vers une DataFrame QUESTIONS machine-first.
    """

    question_sheets = {
        name: df
        for name, df in sheets.items()
        if is_question_sheet(name)
    }

    # Build index of list names to codes from C&C Lists
    list_name_index = build_list_name_to_code_index(sheets)

    rows: List[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for sheet_name, df in question_sheets.items():
        if df.empty:
            continue

        # Metier sheets are loaded with header=None. Detect real header row first.
        if all(isinstance(c, int) for c in df.columns):
            df = with_detected_header(df)

        # Skip sheets that clearly aren't question sheets (e.g. Profile)
        if df.empty or not _has_any_column(df, QUESTION_CODE_COLS) or not _has_any_column(df, QUESTION_LABEL_COLS):
            logger.debug("Questions: sheet '%s' ignored (not a question sheet or header not detected)", sheet_name)
            continue

        order = 1
        code_col = next(
            (c for c in QUESTION_CODE_COLS if c in df.columns),
            None
        )
        label_col = next(
            (c for c in QUESTION_LABEL_COLS if c in df.columns),
            None
        )

        if not code_col or not label_col:
            continue

        type_col = next(
            (c for c in QUESTION_TYPE_COLS if c in df.columns),
            None
        )
        list_col = next(
            (c for c in QUESTION_LIST_COLS if c in df.columns),
            None
        )
        answer_options_col = next(
            (c for c in ANSWER_OPTIONS_COLS if c in df.columns),
            None
        )
        if answer_options_col:
            logger.debug("Questions: sheet '%s' has ANSWER OPTIONS column '%s'", sheet_name, answer_options_col)
        roles_col = next(
            (c for c in QUESTION_ROLES_COLS if c in df.columns),
            None
        )
        visible_enum_col = next(
            (c for c in QUESTION_VISIBLE_ENUMERATOR_COLS if c in df.columns),
            None
        )
        visible_bc_col = next(
            (c for c in QUESTION_VISIBLE_BC_COLS if c in df.columns),
            None
        )
        prefilled_bc_col = next(
            (c for c in QUESTION_PREFILLED_FOR_BC_COLS if c in df.columns),
            None
        )
        mandatory_col = next(
            (c for c in QUESTION_MANDATORY_COLS if c in df.columns),
            None
        )

        priority_col = next(
            (c for c in QUESTION_PRIORITY_COLS if c in df.columns),
            None
        )
        for _, row in df.iterrows():
            if priority_col and is_removed_by_priority(row.get(priority_col)):
                continue

            refs = parse_question_refs(row.get(code_col))
            text = normalize_str(row.get(label_col))

            if not refs or not text:
                continue

            q_type = map_metier_type_to_code(row.get(type_col)) if type_col else "T"
            list_code = normalize_str(row.get(list_col)) if list_col else None

            if not list_code and answer_options_col:
                answer_value = row.get(answer_options_col)
                if answer_options_is_yes_no(answer_value):
                    list_code = "LST-YES-NO"
                    logger.debug(
                        "Questions: '%s' -> list_code '%s' (Yes/No)",
                        answer_value,
                        list_code,
                    )
                else:
                    normalized_answer = normalize_str(answer_value)
                    if normalized_answer:
                        # Try static AREA mappings first
                        mapped = _ANSWER_OPTIONS_TO_LIST_CODE.get(normalized_answer.lower())
                        if mapped:
                            list_code = mapped
                            logger.debug(
                                "Questions: '%s' -> list_code '%s' (named answer options)",
                                answer_value,
                                list_code,
                            )
                        else:
                            # Try dynamic list name index from C&C Lists
                            mapped = list_name_index.get(normalized_answer.lower())
                            if mapped:
                                list_code = mapped
                                logger.debug(
                                    "Questions: '%s' -> list_code '%s' (from C&C Lists index)",
                                    answer_value,
                                    list_code,
                                )

                    if not list_code:
                        parsed_ref = parse_sheet_cell_ref(answer_value)
                        if parsed_ref:
                            target_sheet, _, _ = parsed_ref
                            list_code = slugify_list_code(target_sheet)
                            logger.debug(
                                "Questions: '%s' -> list_code '%s' (ref to sheet '%s')",
                                answer_value,
                                list_code,
                                target_sheet,
                            )
                        elif answer_value is not None and not pd.isna(answer_value) and str(answer_value).strip() != "":
                            logger.debug(
                                "Questions: unable to parse ANSWER OPTIONS '%s' (no list_code inferred)",
                                answer_value,
                            )

            has_visibility_cols = any(
                c is not None
                for c in (visible_enum_col, visible_bc_col, prefilled_bc_col)
            )
            if has_visibility_cols:
                roles: List[str] = []
                if visible_enum_col and is_yes(row.get(visible_enum_col)):
                    roles.append("e")
                if visible_bc_col and is_yes(row.get(visible_bc_col)):
                    roles.append("b")
                if prefilled_bc_col and is_yes(row.get(prefilled_bc_col)):
                    roles.append("bp")
            else:
                roles = (
                    parse_csv(row.get(roles_col))
                    if roles_col else []
                )

            mandatory = (
                normalize_str(row.get(mandatory_col)) == "Y"
                if mandatory_col else False
            )
            for section, q_num in refs:
                key = (section, q_num)
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                ref = f"{section}-{q_num}"
                rows.append({
                    "section": section,
                    "q_num": q_num,
                    "label": ref,
                    "type": q_type,
                    "order": order,
                    "lang_SYS": text,
                    "list_code": list_code,
                    "roles": ",".join(roles) if roles else None,
                    "mandatory": "Y" if mandatory else "N",
                })

                order += 1
    questions_df = pd.DataFrame(rows)

    if questions_df.empty:
        raise ExcelValidationError(
            "QUESTIONS mapping produced an empty DataFrame"
        )

    return questions_df
