from __future__ import annotations

import re
from typing import Optional

import pandas as pd


QUESTION_SHEET_HEADER_NEEDLES = {"Question #", "Question / Action Detail", "ID"}

ANSWER_OPTIONS_COLS = [
    "ANSWER OPTIONS",
    "Answer Options",
    "Answer options",
    "answer options",
]

_SHEET_CELL_RE = re.compile(
    r"^(?P<sheet>.+?)!\s*(?P<cell>\$?[A-Z]+\$?\d+)(?:\s*:\s*(?P<cell2>\$?[A-Z]+\$?\d+))?$"
)


def normalize_sheet_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    if raw_df.empty:
        return pd.DataFrame()

    if not all(isinstance(c, int) for c in raw_df.columns):
        return raw_df

    max_rows = min(30, len(raw_df))
    header_row = None

    for i in range(max_rows):
        row_values = {
            str(v).strip() for v in raw_df.iloc[i].tolist() if pd.notna(v)
        }
        if QUESTION_SHEET_HEADER_NEEDLES.intersection(row_values):
            header_row = i
            break

    if header_row is None:
        return pd.DataFrame()

    header_values = [
        (str(v).strip() if pd.notna(v) and str(v).strip() else f"col_{i}")
        for i, v in enumerate(raw_df.iloc[header_row].tolist())
    ]

    df = raw_df.iloc[header_row + 1 :].copy()
    df.columns = header_values
    return df.dropna(axis=1, how="all")


def answer_options_is_yes_no(value: object) -> bool:
    if value is None or pd.isna(value):
        return False
    s = str(value).strip().lower()
    s = re.sub(r"\s+", "", s)
    return s in {"yes/no", "yesno"}


def parse_sheet_cell_ref(value: object) -> Optional[tuple[str, int, int]]:
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    m = _SHEET_CELL_RE.match(s)
    if not m:
        return None

    sheet_name = m.group("sheet").strip()
    if sheet_name.startswith("'") and sheet_name.endswith("'") and len(sheet_name) >= 2:
        sheet_name = sheet_name[1:-1]

    cell = m.group("cell").strip().upper().replace("$", "")
    col_letters = "".join(ch for ch in cell if ch.isalpha())
    row_digits = "".join(ch for ch in cell if ch.isdigit())
    if not col_letters or not row_digits:
        return None
    row_1_based = int(row_digits)

    col_idx = 0
    for ch in col_letters:
        col_idx = col_idx * 26 + (ord(ch) - ord("A") + 1)

    col_0_based = col_idx - 1
    row_0_based = row_1_based - 1

    if row_0_based < 0 or col_0_based < 0:
        return None

    return sheet_name, row_0_based, col_0_based


def slugify_list_code(sheet_name: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "-", sheet_name.strip().upper()).strip("-")
    base = base or "LIST"
    return f"LST-{base}-DYN"
