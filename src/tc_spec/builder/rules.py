from collections import defaultdict
from typing import Dict, List

import pandas as pd

from tc_spec.model.rule import Rule, Condition
from tc_spec.utils.errors import ExcelValidationError

REQUIRED_COLUMNS = {
    "target_type",
    "target_ref",
    "r_ref",
    "operator",
    "value_type",
    "value",
}

def _validate_columns(df: pd.DataFrame):
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"VISIBILITY_RULES missing columns: {missing}"
        )

def _build_condition(row: pd.Series) -> Condition:
    try:
        return Condition(
            ref=str(row["r_ref"]).strip(),
            operator=str(row["operator"]).strip(),
            value_type=str(row["value_type"]).strip(),
            value=row["value"],
        )
    except Exception as e:
        raise ExcelValidationError(
            f"Invalid rule condition on row {row.name}: {e}"
        ) from e

def build_rules(df: pd.DataFrame) -> Dict[str, List[Rule]]:
    """
    Construit des règles à partir d'un DataFrame Excel.

    Retour :
      {
        "question:V-50": [Rule, Rule],
        "section:W": [Rule],
        "anomaly:ANO-A1": [Rule]
      }
    """

    _validate_columns(df)

    rules_by_target: Dict[str, List[Rule]] = defaultdict(list)

    # On groupe par cible logique
    grouped = df.groupby(["target_type", "target_ref"])

    for (target_type, target_ref), group in grouped:
        key = f"{target_type}:{target_ref}"

        # Sous-groupement OR (si présent)
        if "or_group" in group.columns:
            or_groups = group.groupby(group["or_group"].fillna("__AND__"))
        else:
            or_groups = [(None, group)]

        for or_key, or_group in or_groups:
            conditions = [
                _build_condition(row)
                for _, row in or_group.iterrows()
            ]

            if or_key == "__AND__":
                # AND implicite → une règle par condition
                for cond in conditions:
                    rules_by_target[key].append(
                        Rule(condition=cond)
                    )
            else:
                # OR explicite
                rules_by_target[key].append(
                    Rule(or_conditions=conditions)
                )
    return rules_by_target
