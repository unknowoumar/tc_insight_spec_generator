"""
TC Insight – Builder

Ce module contient l'ensemble des builders responsables de la
transformation des données Excel en modèle métier (Spec V2).
"""

from tc_spec.builder.rules import build_rules
from tc_spec.builder.questions import build_questions
from tc_spec.builder.sections import build_sections
from tc_spec.builder.lists import build_lists
from tc_spec.builder.anomalies import build_anomalies

__all__ = [
    "build_rules",
    "build_questions",
    "build_sections",
    "build_lists",
    "build_anomalies",
]

from tc_spec.builder import (
    build_rules,
    build_questions,
    build_sections,
    build_lists,
    build_anomalies,
)
