"""
Questions Mapper

Transforme les feuilles questions Excel en DataFrame QUESTIONS
machine-first.
"""

from typing import Dict, List, Optional
import pandas as pd

from tc_spec.utils.helpers import normalize_str, parse_csv
from tc_spec.utils.errors import ExcelValidationError

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
QUESTION_TYPE_COLS = ["Type", "Q_TYPE"]
QUESTION_LIST_COLS = ["List", "ListCode", "LIST_CODE"]
QUESTION_ROLES_COLS = ["Roles", "ROLE"]
QUESTION_MANDATORY_COLS = ["Mandatory", "Required"]

def is_question_sheet(sheet_name: str) -> bool:
    """
    Détermine si une feuille est une feuille de questions.
    """
    return sheet_name not in QUESTION_SHEETS_EXCLUDE

def _has_any_column(df: pd.DataFrame, candidates: List[str]) -> bool:
    return any(c in df.columns for c in candidates)


def _normalize_header_value(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def _detect_header_row(raw_df: pd.DataFrame) -> Optional[int]:
    # Heuristic for metier files: look for a row that contains a known header label.
    needles = {"Question #", "Question / Action Detail", "ID"}
    max_rows = min(30, len(raw_df))
    for i in range(max_rows):
        row = raw_df.iloc[i]
        normalized = {
            _normalize_header_value(v)
            for v in row.tolist()
        }
        normalized.discard(None)
        if needles.intersection(normalized):
            return i
    return None


def _with_detected_header(raw_df: pd.DataFrame) -> pd.DataFrame:
    header_row = _detect_header_row(raw_df)
    if header_row is None:
        return pd.DataFrame()

    header_values = [
        _normalize_header_value(v)
        for v in raw_df.iloc[header_row].tolist()
    ]
    header_values = [h if h is not None else f"col_{i}" for i, h in enumerate(header_values)]

    df = raw_df.iloc[header_row + 1 :].copy()
    df.columns = header_values

    # Drop columns that are fully empty
    df = df.dropna(axis=1, how="all")
    return df


def _parse_question_refs(value: object) -> List[tuple[str, str]]:
    """Parse a metier question reference cell.

    Examples:
    - "A-10" -> [("A", "10")]
    - "A-10,20,30" -> [("A", "10"), ("A", "20"), ("A", "30")]
    """
    raw = normalize_str(value)
    if not raw:
        return []

    parts = [p.strip() for p in str(raw).split(",") if p.strip()]
    if not parts:
        return []

    refs: List[tuple[str, str]] = []
    current_section: Optional[str] = None

    for part in parts:
        if "-" in part:
            sec, num = part.split("-", 1)
            sec = normalize_str(sec)
            num = normalize_str(num)
            if not sec or not num:
                continue
            sec_code = sec.upper()
            current_section = sec_code
            refs.append((sec_code, num))
        else:
            num = normalize_str(part)
            if not current_section or not num:
                continue
            refs.append((current_section, num))

    return refs

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

    rows: List[dict] = []
    seen_keys: set[tuple[str, str]] = set()

    for sheet_name, df in question_sheets.items():
        if df.empty:
            continue

        # Metier sheets are loaded with header=None. Detect real header row first.
        if all(isinstance(c, int) for c in df.columns):
            df = _with_detected_header(df)

        # Skip sheets that clearly aren't question sheets (e.g. Profile)
        if df.empty or not _has_any_column(df, QUESTION_CODE_COLS) or not _has_any_column(df, QUESTION_LABEL_COLS):
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
        roles_col = next(
            (c for c in QUESTION_ROLES_COLS if c in df.columns),
            None
        )
        mandatory_col = next(
            (c for c in QUESTION_MANDATORY_COLS if c in df.columns),
            None
        )
        for _, row in df.iterrows():
            refs = _parse_question_refs(row.get(code_col))
            text = normalize_str(row.get(label_col))

            if not refs or not text:
                continue

            q_type = normalize_str(row.get(type_col)) if type_col else "T"
            list_code = normalize_str(row.get(list_col)) if list_col else None

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
