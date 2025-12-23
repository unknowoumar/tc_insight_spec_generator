from typing import Dict, List

import pandas as pd

from tc_spec.model.anomaly import Anomaly
from tc_spec.model.rule import Rule
from tc_spec.utils.errors import ExcelValidationError

ANOMALIES_REQUIRED_COLS = {
    "anomaly_code",
    "weight",
}

def _validate_columns(df: pd.DataFrame):
    missing = ANOMALIES_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"ANOMALIES missing columns: {missing}"
        )

def build_anomalies(
    anomalies_df: pd.DataFrame,
    rules_by_target: Dict[str, List[Rule]],
) -> Dict[str, Anomaly]:
    """
    Construit les anomalies du spec.

    Retour :
      {
        "ANO-A1": Anomaly,
        "ANO-A2": Anomaly
      }
    """
    _validate_columns(anomalies_df)
    anomalies: Dict[str, Anomaly] = {}

    for _, row in anomalies_df.iterrows():
        code = str(row["anomaly_code"]).strip()

        if code in anomalies:
            raise ExcelValidationError(
                f"Duplicate anomaly code '{code}'"
            )

        rules = rules_by_target.get(f"anomaly:{code}", [])

        if not rules:
            raise ExcelValidationError(
                f"Anomaly '{code}' has no rules defined"
            )
        try:
            weight = int(row["weight"])
        except Exception:
            raise ExcelValidationError(
                f"Anomaly '{code}': weight must be an integer"
            )
        anomaly = Anomaly(
            code=code,
            weight=weight,
            rules=rules,
        )

        anomalies[code] = anomaly
    return anomalies