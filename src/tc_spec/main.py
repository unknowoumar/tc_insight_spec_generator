from pathlib import Path
from typing import Optional

from tc_spec.pipeline import map_excel_to_machine_first

from tc_spec.excel import load_and_validate_excel, load_excel_all
from tc_spec.builder import (
    build_rules,
    build_questions,
    build_sections,
    build_lists,
    build_anomalies,
)
from tc_spec.model.spec import Spec
from tc_spec.validation import (
    validate_excel,
    validate_spec_schema,
)
from tc_spec.exporter import export_spec_to_json
from tc_spec.utils.errors import SpecError

def generate_spec(
    excel_path: str | Path,
    output_path: str | Path,
    schema_path: str | Path,
    excel_mode: str = "metier",  # "metier" | "machine"
    validate_only: bool = False,
) -> Optional[dict]:
    """
    Génère un Spec TC Insight à partir d'un fichier Excel.

    :param excel_path: chemin du fichier Excel
    :param output_path: chemin du JSON de sortie
    :param schema_path: chemin du JSON Schema
    :param validate_only: si True, ne génère pas le fichier
    :return: spec sérialisé (dict) si validate_only=True
    """

    try:
        if excel_mode == "metier":
            raw_sheets = load_excel_all(excel_path)
            sheets = map_excel_to_machine_first(raw_sheets)
        elif excel_mode == "machine":
            sheets = load_and_validate_excel(excel_path)
        else:
            raise SpecError(
                f"Invalid excel_mode '{excel_mode}' (expected 'metier' or 'machine')"
            )

        validate_excel(sheets)
        rules = build_rules(sheets["VISIBILITY_RULES"])

        questions = build_questions(
            sheets["QUESTIONS"],
            sheets["QUESTION_TYPES"],
            rules,
        )

        sections = build_sections(
            sheets["SECTIONS"],
            questions,
            rules,
        )

        lists = build_lists(sheets["LISTS"])

        anomalies = {}
        if "ANOMALIES" in sheets and not sheets["ANOMALIES"].empty:
            anomalies = build_anomalies(
                sheets["ANOMALIES"],
                rules,
            )
        spec = Spec(
            name="TC Insight Spec",
            version="2.0.0",
            sections=sections,
            lists=lists,
            anomalies=anomalies,
        )
        if validate_only:
            return spec.to_dict()

        export_spec_to_json(
            spec,
            output_path,
        )

        return None
    except SpecError:
        # on relance tel quel (déjà métier)
        raise
    except Exception as e:
        raise SpecError(
            f"Unexpected error during spec generation: {e}"
        ) from e
