from typing import Dict, List

from tc_spec.utils.errors import SpecError

class ListItem:
    """
    Représente un élément d'une liste TC Insight.
    """

    def __init__(self, value: str, labels: Dict[str, str]):
        self.value = value      # ex: "SEG1"
        self.labels = labels    # multilingue

        self._validate_internal()

    def _validate_internal(self):
        if not self.value or not isinstance(self.value, str):
            raise SpecError("ListItem value must be a non-empty string")

        if not isinstance(self.labels, dict) or not self.labels:
            raise SpecError(
                f"ListItem '{self.value}': labels must be a non-empty dict"
            )

        for lang, text in self.labels.items():
            if not isinstance(lang, str) or not isinstance(text, str):
                raise SpecError(
                    f"ListItem '{self.value}': invalid label format"
                )

    def to_dict(self) -> dict:
        return {
            "v": self.value,
            "n": self.labels
        }

class SpecList:
    """
    Représente une liste TC Insight conforme au JSON Schema V2.
    """

    def __init__(self, code: str, items: List[ListItem]):
        self.code = code        # ex: "LST-SEGMENT"
        self.items = items

        self._validate_internal()

    def _validate_internal(self):
        if not self.code or not isinstance(self.code, str):
            raise SpecError("List code must be a non-empty string")

        if not self.code.startswith("LST-"):
            raise SpecError(
                f"List '{self.code}': code must start with 'LST-'"
            )

        if not isinstance(self.items, list) or not self.items:
            raise SpecError(
                f"List '{self.code}': must contain at least one item"
            )

        seen_values = set()
        for item in self.items:
            if not isinstance(item, ListItem):
                raise SpecError(
                    f"List '{self.code}': items must be ListItem objects"
                )

            if item.value in seen_values:
                raise SpecError(
                    f"List '{self.code}': duplicate value '{item.value}'"
                )

            seen_values.add(item.value)
            
    def to_list(self) -> list:
        """
        Retourne la liste d'items conforme au JSON Schema.
        """
        return [item.to_dict() for item in self.items]
