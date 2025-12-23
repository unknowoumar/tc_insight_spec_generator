
"""
TC Insight – Exporter

Ce module gère l'export des Specs TC Insight vers différents formats.
Actuellement supporté :
- JSON (spec_v2)
"""

from tc_spec.exporter.json_exporter import export_spec_to_json

__all__ = [
    "export_spec_to_json",
]
