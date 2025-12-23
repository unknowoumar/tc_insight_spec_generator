"""
TC Insight – Modèle métier (Spec V2)

Ce module contient l'ensemble des entités métier utilisées pour
construire un Spec TC Insight conforme au JSON Schema V2.
"""

from tc_spec.model.spec import Spec
from tc_spec.model.section import Section
from tc_spec.model.question import Question
from tc_spec.model.rule import Rule, Condition
from tc_spec.model.anomaly import Anomaly
from tc_spec.model.list import SpecList, ListItem

__all__ = [
    "Spec",
    "Section",
    "Question",
    "Rule",
    "Condition",
    "Anomaly",
    "SpecList",
    "ListItem",
]
