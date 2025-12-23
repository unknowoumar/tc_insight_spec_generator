from typing import Dict, List, Optional

from tc_spec.model.section import Section
from tc_spec.model.anomaly import Anomaly
from tc_spec.utils.errors import SpecError

class Spec:
    """
    Représente un Spec TC Insight V2 conforme au JSON Schema officiel.
    """

    def __init__(
        self,
        name: str,
        version: str,
        sections: Dict[str, Section],
        lists: Optional[dict] = None,
        anomalies: Optional[Dict[str, Anomaly]] = None,
        notes: Optional[List[str]] = None,
    ):
        self.name = name
        self.version = version
        self.sections = sections
        self.lists = lists or {}
        self.anomalies = anomalies or {}
        self.notes = notes or []

        self._validate_internal()

    def _validate_internal(self):
        if not self.name or not isinstance(self.name, str):
            raise SpecError("Spec name must be a non-empty string")

        if not self.version or not isinstance(self.version, str):
            raise SpecError("Spec version must be a string")

        if not self.sections:
            raise SpecError("Spec must contain at least one section")

        for code, section in self.sections.items():
            if code != section.code:
                raise SpecError(
                    f"Section code mismatch: key '{code}' != section.code '{section.code}'"
                )
                
    def to_dict(self) -> dict:
        """
        Retourne une représentation dict strictement conforme
        au JSON Schema spec_v2.schema.json
        """

        spec_dict = {
            "n": self.name,
            "v": self.version,
            "s": {
                code: section.to_dict()
                for code, section in self.sections.items()
            }
        }

        if self.notes:
            spec_dict["notes"] = self.notes

        if self.lists:
            spec_dict["l"] = {
                code: (
                    lst.to_list()
                    if hasattr(lst, "to_list")
                    else lst
                )
                for code, lst in self.lists.items()
            }

        if self.anomalies:
            spec_dict["a"] = {
                code: anomaly.to_dict()
                for code, anomaly in self.anomalies.items()
            }

        return spec_dict

    def validate_against_schema(self, schema: dict):
        """
        Valide le spec courant contre un JSON Schema donné.
        """
        from jsonschema import validate, ValidationError

        try:
            validate(instance=self.to_dict(), schema=schema)
        except ValidationError as e:
            raise SpecError(f"Schema validation failed: {e.message}") from e
