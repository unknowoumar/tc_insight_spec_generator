"""
TC Insight – Constantes globales

Ce module centralise toutes les constantes utilisées dans le
générateur de Specs TC Insight (V2).
Aucune logique ne doit apparaître ici.
"""

EXCEL_SHEETS = {
    "QUESTIONS",
    "QUESTION_TYPES",
    "SECTIONS",
    "LISTS",
    "VISIBILITY_RULES",
    "ANOMALIES",
}

DEFAULT_LANGUAGE = "SYS"

LANGUAGE_PREFIX = "lang_"

QUESTION_TYPES = {
    "O",    # One choice
    "T",    # Text
    "TM",   # Text multi-line
    "N",    # Numeric
    "C",    # Multiple choice
    "I",    # Integer
    "A",    # Auto
    "-",    # Note / separator
}

ROLES = {
    "e",  # enumerator
    "b",  # backoffice
    "u",  # user
    "h",  # hidden
}

RULE_TARGET_TYPES = {
    "question",
    "section",
    "anomaly",
}

RULE_OPERATORS = {
    "=",   # equals
    "!",   # not equals
    ">",   # greater than
    "<",   # less than
    ">=",  # greater or equal
    "<=",  # less or equal
    "e",   # exists
    "!e",  # not exists
}

RULE_VALUE_TYPES = {
    "v",  # value
    "a",  # answer
}

SECTION_CODE_PATTERN = r"^[A-Z]+$"

LIST_CODE_PREFIX = "LST-"

ANOMALY_CODE_PREFIX = "ANO-"

SPEC_VERSION_PATTERN = r"^\d+\.\d+\.\d+$"
