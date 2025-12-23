from typing import Dict, List, Optional, Any

from tc_spec.model.rule import Rule
from tc_spec.utils.errors import SpecError

class Question:
    """
    Représente une question TC Insight conforme au JSON Schema V2.
    """

    def __init__(
        self,
        ref: str,
        label: str,
        texts: Dict[str, str],
        qtype: Dict[str, Any],
        roles: Optional[List[str]] = None,
        visibility: Optional[List[Rule]] = None,
        matrix: Optional[dict] = None,
    ):
        self.ref = ref                  # ex: "V-50"
        self.label = label              # ex: "V-50 Categories"
        self.texts = texts              # multilingue
        self.qtype = qtype              # dict UNIQUE (1 type)
        self.roles = roles or []        # ["e", "b"]
        self.visibility = visibility or []
        self.matrix = matrix            # futur (matrices)

        self._validate_internal()

class Question:
    """
    Représente une question TC Insight conforme au JSON Schema V2.
    """

    def __init__(
        self,
        ref: str,
        label: str,
        texts: Dict[str, str],
        qtype: Dict[str, Any],
        roles: Optional[List[str]] = None,
        visibility: Optional[List[Rule]] = None,
        matrix: Optional[dict] = None,
    ):
        self.ref = ref                  # ex: "V-50"
        self.label = label              # ex: "V-50 Categories"
        self.texts = texts              # multilingue
        self.qtype = qtype              # dict UNIQUE (1 type)
        self.roles = roles or []        # ["e", "b"]
        self.visibility = visibility or []
        self.matrix = matrix            # futur (matrices)

        self._validate_internal()

    def _validate_internal(self):
        if not self.ref or not isinstance(self.ref, str):
            raise SpecError("Question ref must be a non-empty string")

        if not self.label:
            raise SpecError(f"Question {self.ref}: label is required")

        if not self.texts or not isinstance(self.texts, dict):
            raise SpecError(f"Question {self.ref}: texts must be a dict")

        if len(self.qtype.keys()) == 0:
            raise SpecError(f"Question {self.ref}: qtype is required")

        if not isinstance(self.qtype, dict):
            raise SpecError(f"Question {self.ref}: qtype must be a dict")

        if self.roles:
            for r in self.roles:
                if r not in {"e", "b", "u", "h"}:
                    raise SpecError(
                        f"Question {self.ref}: invalid role '{r}'"
                    )
                    
    def to_dict(self) -> dict:
        """
        Retourne une représentation dict conforme au JSON Schema.
        """

        question_dict = {
            "n": self.texts,
            "label": self.label,
            "t": [self.qtype],
        }

        if self.roles:
            question_dict["o"] = self.roles

        if self.visibility:
            question_dict["v"] = [
                rule.to_dict() for rule in self.visibility
            ]

        if self.matrix:
            question_dict["r"] = self.matrix

        return question_dict
