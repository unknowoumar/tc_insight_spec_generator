from typing import Dict, List, Any

import pandas as pd

from tc_spec.model.question import Question
from tc_spec.model.rule import Rule, Condition
from tc_spec.utils.errors import ExcelValidationError

QUESTIONS_REQUIRED_COLS = {
    "section", "q_num", "label", "lang_SYS"
}

QUESTION_TYPES_REQUIRED_COLS = {
    "section", "q_num", "type"
}

def _validate_columns(df: pd.DataFrame, required: set, sheet: str):
    missing = required - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"{sheet} missing columns: {missing}"
        )

def _build_qtype(row: pd.Series) -> dict:
    qtype = {"t": row["type"]}

    if pd.notna(row.get("min")):
        qtype["-"] = row["min"]

    if pd.notna(row.get("max")):
        qtype["+"] = row["max"]

    if pd.notna(row.get("default")):
        qtype["d"] = row["default"]

    if pd.notna(row.get("regex")):
        qtype["regex"] = row["regex"]

    if pd.notna(row.get("list_code")):
        qtype["o"] = row["list_code"]

    if pd.notna(row.get("choice_limit")):
        qtype["c"] = int(row["choice_limit"])

    if pd.notna(row.get("auto_code")):
        qtype["i"] = row["auto_code"]

    return qtype


def _convert_visibility_rules(parsed_rules: List[Dict[str, Any]]) -> List[Rule]:
    """
    Convert parsed visibility rules (dicts) to Rule objects.
    
    Parsed rules format:
    - Simple condition: {"r": "Q-10", "o": "=", "v": "value"}
    - OR conditions: {"or": [{"r": "Q-10", "o": "=", "v": "v1"}, ...]}
    """
    rules = []
    
    for rule_dict in parsed_rules:
        if "or" in rule_dict:
            # OR rule with multiple conditions
            conditions = []
            for cond_dict in rule_dict["or"]:
                condition = Condition(
                    ref=cond_dict["r"],
                    operator=cond_dict["o"],
                    value_type="v",  # Default to "v" (value)
                    value=cond_dict["v"]
                )
                conditions.append(condition)
            
            rule = Rule(or_conditions=conditions)
            rules.append(rule)
        else:
            # Simple condition
            condition = Condition(
                ref=rule_dict["r"],
                operator=rule_dict["o"],
                value_type="v",  # Default to "v" (value)
                value=rule_dict["v"]
            )
            rule = Rule(condition=condition)
            rules.append(rule)
    
    return rules

def build_questions(
    questions_df: pd.DataFrame,
    question_types_df: pd.DataFrame,
    rules_by_target: Dict[str, list],
) -> Dict[str, Question]:
    """
    Construit toutes les questions du spec.

    Retour :
      {
        "V-50": Question,
        "I-01": Question
      }
    """
    _validate_columns(questions_df, QUESTIONS_REQUIRED_COLS, "QUESTIONS")
    _validate_columns(question_types_df, QUESTION_TYPES_REQUIRED_COLS, "QUESTION_TYPES")

    type_index = {}

    for _, row in question_types_df.iterrows():
        ref = f"{row['section']}-{row['q_num']}"
        if ref in type_index:
            raise ExcelValidationError(
                f"Multiple types defined for question {ref}"
            )
        type_index[ref] = _build_qtype(row)


    questions: Dict[str, Question] = {}

    for _, row in questions_df.iterrows():
        ref = f"{row['section']}-{row['q_num']}"

        if ref not in type_index:
            raise ExcelValidationError(
                f"Missing question type for {ref}"
            )

        texts = {
            k.replace("lang_", ""): v
            for k, v in row.items()
            if k.startswith("lang_") and pd.notna(v)
        }

        roles = []
        if pd.notna(row.get("roles")):
            roles = [r.strip() for r in str(row["roles"]).split(",")]

        # Get visibility rules from VISIBILITY_RULES DataFrame (old system)
        visibility = rules_by_target.get(f"question:{ref}", [])
        
        # Also get visibility rules from question's visibility column (new system)
        if pd.notna(row.get("visibility")) and row.get("visibility"):
            # visibility column contains parsed rules as list of dicts
            # Convert them to Rule objects
            parsed_rules = row.get("visibility")
            if isinstance(parsed_rules, list):
                visibility = _convert_visibility_rules(parsed_rules)

        question = Question(
            ref=ref,
            label=row["label"],
            texts=texts,
            qtype=type_index[ref],
            roles=roles,
            visibility=visibility,
        )

        questions[ref] = question

    return questions
