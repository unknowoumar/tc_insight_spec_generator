import json
from pathlib import Path

from tc_spec.model.spec import Spec
from tc_spec.utils.errors import SpecError

def export_spec_to_json(
    spec: Spec,
    output_path: str | Path,
    pretty: bool = True,
) -> None:
    """
    Exporte un Spec TC Insight vers un fichier JSON.

    :param spec: objet Spec valide
    :param output_path: chemin du fichier de sortie
    :param pretty: JSON indenté si True
    """

    if not isinstance(spec, Spec):
        raise SpecError(
            "export_spec_to_json expects a Spec instance"
        )

    output_path = Path(output_path)

    if not output_path.parent.exists():
        raise SpecError(
            f"Output directory does not exist: {output_path.parent}"
        )
    try:
        data = spec.to_dict()
    except Exception as e:
        raise SpecError(
            f"Failed to serialize Spec: {e}"
        ) from e
    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2 if pretty else None,
            )
    except Exception as e:
        raise SpecError(
            f"Failed to write JSON file '{output_path}': {e}"
        ) from e
