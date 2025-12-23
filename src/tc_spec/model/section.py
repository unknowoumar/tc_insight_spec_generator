from typing import List, Optional, Dict

from tc_spec.model.question import Question
from tc_spec.model.rule import Rule
from tc_spec.utils.errors import SpecError

class Section:
    """
    Représente une section TC Insight conforme au JSON Schema V2.
    """

    def __init__(
        self,
        code: str,
        name: str,
        questions: List[Question],
        visibility: Optional[List[Rule]] = None,
    ):
        self.code = code          # ex: "I"
        self.name = name          # ex: "Interview Start"
        self.questions = questions
        self.visibility = visibility or []

        self._validate_internal()

    def _validate_internal(self):
        if not self.code or not isinstance(self.code, str):
            raise SpecError("Section code must be a non-empty string")

        if not self.code.isupper():
            raise SpecError(
                f"Section code '{self.code}' must be uppercase"
            )

        if not self.name:
            raise SpecError(
                f"Section '{self.code}': name is required"
            )

        if not isinstance(self.questions, list) or not self.questions:
            raise SpecError(
                f"Section '{self.code}': must contain at least one question"
            )

        seen_refs = set()
        for q in self.questions:
            if q.ref in seen_refs:
                raise SpecError(
                    f"Duplicate question ref '{q.ref}' in section '{self.code}'"
                )
            seen_refs.add(q.ref)

    def to_dict(self) -> Dict:
        """
        Retourne une représentation dict conforme au JSON Schema.
        """

        section_dict = {
            "n": self.name,
            "p": []
        }

        if self.visibility:
            section_dict["v"] = [
                rule.to_dict() for rule in self.visibility
            ]

        for question in self.questions:
            section_dict["p"].append({
                question.ref.split("-")[-1]: question.to_dict()
            })

        return section_dict
