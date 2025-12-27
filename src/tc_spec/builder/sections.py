from typing import Dict, List, Any

import pandas as pd

from tc_spec.model.section import Section
from tc_spec.model.question import Question
from tc_spec.model.rule import Rule, Condition
from tc_spec.utils.errors import ExcelValidationError

SECTIONS_REQUIRED_COLS = {
    "section_code",
    "section_label",
    "order",
}

def _validate_columns(df: pd.DataFrame):
    missing = SECTIONS_REQUIRED_COLS - set(df.columns)
    if missing:
        raise ExcelValidationError(
            f"SECTIONS missing columns: {missing}"
        )


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

def build_sections(
    sections_df: pd.DataFrame,
    questions: Dict[str, Question],
    rules_by_target: Dict[str, List[Rule]],
) -> Dict[str, Section]:
    """
    Construit les sections du spec.

    Retour :
      {
        "I": Section,
        "V": Section
      }
    """
    _validate_columns(sections_df)
    questions_by_section: Dict[str, List[Question]] = {}

    for ref, question in questions.items():
        section_code = ref.split("-")[0]
        questions_by_section.setdefault(section_code, []).append(question)
    sections: Dict[str, Section] = {}
    
    # Extract section visibility rules from DataFrame attributes
    section_visibility_rules = sections_df.attrs.get('section_visibility_rules', {})

    ordered_rows = sections_df.sort_values("order")
    for _, row in ordered_rows.iterrows():
        code = str(row["section_code"]).strip()

        if code not in questions_by_section:
            raise ExcelValidationError(
                f"Section '{code}' has no questions"
            )

        # Get visibility rules from VISIBILITY_RULES DataFrame (old system)
        visibility = rules_by_target.get(f"section:{code}", [])
        
        # Also get visibility rules from section_visibility_rules (new system)
        if code in section_visibility_rules:
            parsed_rules = section_visibility_rules[code]
            if isinstance(parsed_rules, list):
                visibility = _convert_visibility_rules(parsed_rules)
        
        section = Section(
            code=code,
            name=row["section_label"],
            questions=questions_by_section[code],
            visibility=visibility,
        )

        sections[code] = section
    return sections
