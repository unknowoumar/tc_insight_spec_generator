"""
TC Insight – Excel Mapper

Ce module transforme les fichiers Excel métier complexes
en Excel machine-first contractuel.
"""

from tc_spec.excel_mapper.skus_mapper import map_skus_to_lists
from tc_spec.excel_mapper.areas_mapper import map_areas_to_lists
from tc_spec.excel_mapper.lists_mapper import map_lists
from tc_spec.excel_mapper.questions_mapper import map_questions
from tc_spec.excel_mapper.visibility_rules_mapper import map_visibility_rules

__all__ = [
    "map_skus_to_lists",
    "map_areas_to_lists",
    "map_lists",
    "map_questions",
    "map_visibility_rules",
]
