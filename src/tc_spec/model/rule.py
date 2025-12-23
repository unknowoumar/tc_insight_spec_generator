from typing import Any, List, Optional

from tc_spec.utils.errors import SpecError

class Condition:
    """
    Condition atomique d'une règle TC Insight.
    Conforme au JSON Schema V2.
    """

    ALLOWED_OPERATORS = {"=", "!", ">", "<", ">=", "<=", "e", "!e"}
    ALLOWED_VALUE_TYPES = {"v", "a"}

    def __init__(
        self,
        ref: str,
        operator: str,
        value_type: str,
        value: Any,
    ):
        self.ref = ref
        self.operator = operator
        self.value_type = value_type
        self.value = value

        self._validate_internal()

    def _validate_internal(self):
        if not self.ref or not isinstance(self.ref, str):
            raise SpecError("Rule condition: 'ref' must be a non-empty string")

        if self.operator not in self.ALLOWED_OPERATORS:
            raise SpecError(
                f"Rule condition '{self.ref}': invalid operator '{self.operator}'"
            )

        if self.value_type not in self.ALLOWED_VALUE_TYPES:
            raise SpecError(
                f"Rule condition '{self.ref}': invalid value type '{self.value_type}'"
            )

    def to_dict(self) -> dict:
        return {
            "r": self.ref,
            "o": self.operator,
            "t": self.value_type,
            "v": self.value,
        }

class Rule:
    """
    Représente une règle logique TC Insight.
    Peut être :
    - une condition simple
    - un OR de conditions
    """

    def __init__(
        self,
        condition: Optional[Condition] = None,
        or_conditions: Optional[List[Condition]] = None,
    ):
        self.condition = condition
        self.or_conditions = or_conditions

        self._validate_internal()

    def _validate_internal(self):
        if self.condition and self.or_conditions:
            raise SpecError(
                "Rule cannot have both 'condition' and 'or_conditions'"
            )

        if not self.condition and not self.or_conditions:
            raise SpecError(
                "Rule must have either 'condition' or 'or_conditions'"
            )

        if self.or_conditions:
            if not isinstance(self.or_conditions, list) or not self.or_conditions:
                raise SpecError("OR rule must contain at least one condition")

            for cond in self.or_conditions:
                if not isinstance(cond, Condition):
                    raise SpecError("OR rule must contain Condition objects only")
                    
    def to_dict(self) -> dict:
        if self.condition:
            return self.condition.to_dict()

        return {
            "or": [cond.to_dict() for cond in self.or_conditions]
        }
