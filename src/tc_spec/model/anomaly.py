from typing import List

from tc_spec.model.rule import Rule
from tc_spec.utils.errors import SpecError

class Anomaly:
    """
    Représente une anomalie TC Insight conforme au JSON Schema V2.
    """

    def __init__(
        self,
        code: str,
        weight: int,
        rules: List[Rule],
    ):
        self.code = code          # ex: "ANO-A1"
        self.weight = weight     # ex: 10
        self.rules = rules       # AND implicite

        self._validate_internal()

    def _validate_internal(self):
        if not self.code or not isinstance(self.code, str):
            raise SpecError("Anomaly code must be a non-empty string")

        if not isinstance(self.weight, int):
            raise SpecError(
                f"Anomaly '{self.code}': weight must be an integer"
            )

        if self.weight <= 0:
            raise SpecError(
                f"Anomaly '{self.code}': weight must be greater than 0"
            )

        if not isinstance(self.rules, list) or not self.rules:
            raise SpecError(
                f"Anomaly '{self.code}': must contain at least one rule"
            )

        for rule in self.rules:
            if not isinstance(rule, Rule):
                raise SpecError(
                    f"Anomaly '{self.code}': rules must be Rule objects"
                )

    def to_dict(self) -> dict:
        """
        Retourne une représentation dict conforme au JSON Schema.
        """

        return {
            "w": self.weight,
            "r": [rule.to_dict() for rule in self.rules],
        }
