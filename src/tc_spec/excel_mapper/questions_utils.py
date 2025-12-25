from __future__ import annotations

from typing import List, Optional

import pandas as pd

from tc_spec.utils.helpers import normalize_str


def normalize_header_value(value: object) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def detect_header_row(raw_df: pd.DataFrame) -> Optional[int]:
    # Heuristic for metier files: look for a row that contains a known header label.
    needles = {"Question #", "Question / Action Detail", "ID"}
    max_rows = min(30, len(raw_df))
    for i in range(max_rows):
        row = raw_df.iloc[i]
        normalized = {
            normalize_header_value(v)
            for v in row.tolist()
        }
        normalized.discard(None)
        if needles.intersection(normalized):
            return i
    return None


def with_detected_header(raw_df: pd.DataFrame) -> pd.DataFrame:
    header_row = detect_header_row(raw_df)
    if header_row is None:
        return pd.DataFrame()

    header_values = [
        normalize_header_value(v)
        for v in raw_df.iloc[header_row].tolist()
    ]
    header_values = [h if h is not None else f"col_{i}" for i, h in enumerate(header_values)]

    df = raw_df.iloc[header_row + 1 :].copy()
    df.columns = header_values

    # Drop columns that are fully empty
    df = df.dropna(axis=1, how="all")
    return df


def parse_question_refs(value: object) -> List[tuple[str, str]]:
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


def map_metier_type_to_code(raw_type: object) -> str:
    t = normalize_str(raw_type)
    if not t:
        return "T"

    t_upper = t.upper()

    if "NOTE" in t_upper:
        return "-"
    if "NUMER" in t_upper:
        return "N"
    if "SINGLE" in t_upper:
        return "O"
    if "MULTIPLE" in t_upper:
        return "C"
    if "GPS" in t_upper:
        return "T"
    if "TEXT" in t_upper:
        return "T"

    return "T"


def is_removed_by_priority(priority_value: object) -> bool:
    if priority_value is None or pd.isna(priority_value):
        return False

    if isinstance(priority_value, (int, float)):
        try:
            return int(priority_value) == -1
        except Exception:
            return False

    s = normalize_str(priority_value)
    if not s:
        return False

    try:
        return int(float(s)) == -1
    except Exception:
        return False


def is_yes(value: object) -> bool:
    s = normalize_str(value)
    if not s:
        return False
    return s.strip().upper() in {"Y", "YES"}
