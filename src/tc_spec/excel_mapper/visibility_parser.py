"""
Parser for visibility rules from Excel to spec format.

Supports various syntax patterns:
- e-or, e-and: element in list (or/and)
- =-or, =-and: equals (or/and)
- !-or, !-and: not equals (or/and)
- Simple operators: =, !, <, >, <=, >=, e
- Logical operators: and, or
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def parse_visibility_rule(rule: str) -> Optional[List[Dict[str, Any]]]:
    """
    Parse a visibility rule string into spec format.
    
    Args:
        rule: Visibility rule string from Excel
        
    Returns:
        List of visibility conditions in spec format, or None if empty/invalid
    """
    if not rule or not isinstance(rule, str):
        return None
    
    rule = rule.strip()
    if not rule or rule.lower() == 'nan':
        return None
    
    try:
        # Handle top-level 'or' separator
        if ' or ' in rule:
            result = _parse_or_conditions(rule)
            return _flatten_conditions(result)
        
        # Handle top-level 'and' separator
        if ' and ' in rule:
            result = _parse_and_conditions(rule)
            return _flatten_conditions(result)
        
        # Single condition
        condition = _parse_single_condition(rule)
        if not condition:
            return None
        
        # Check if needs flattening
        if isinstance(condition, dict) and "_flatten" in condition:
            return condition["_flatten"]
        
        return [condition]
    
    except Exception as e:
        logger.warning(f"Failed to parse visibility rule: {rule}. Error: {e}")
        return None


def _parse_or_conditions(rule: str) -> List[Dict[str, Any]]:
    """Parse conditions separated by 'or'."""
    parts = rule.split(' or ')
    conditions = []
    
    for part in parts:
        part = part.strip()
        condition = _parse_single_condition(part)
        if condition:
            conditions.append(condition)
    
    if not conditions:
        return []
    
    # Wrap in 'or' structure
    return [{"or": conditions}]


def _parse_and_conditions(rule: str) -> List[Dict[str, Any]]:
    """Parse conditions separated by 'and'."""
    parts = rule.split(' and ')
    conditions = []
    
    for part in parts:
        part = part.strip()
        condition = _parse_single_condition(part)
        if condition:
            conditions.append(condition)
    
    return conditions


def _parse_single_condition(condition: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single condition.
    
    Patterns:
    - Q-10 e-or ["V1", "V2"]
    - Q-10 e-and ["V1", "V2"]
    - Q-10 =-or ["V1", "V2"]
    - Q-10 =-and ["V1", "V2"]
    - Q-10 !-or ["V1", "V2"]
    - Q-10 !-and ["V1", "V2"]
    - Q-10 e ["V1"]
    - Q-10 = "V1"
    - Q-10 ! "V1"
    - Q-10 > 100
    - Q-10 < 100
    - Q-10 >= 100
    - Q-10 <= 100
    - Q-10 = Yes
    - Q-10 = No
    """
    condition = condition.strip()
    
    # Pattern: Q-10 OPERATOR-LOGIC ["V1", "V2", ...]
    # e.g., W-10 e-or ["WCU-1", "WCU-2"]
    match = re.match(r'^([A-Z]+-\d+)\s+([!=e])-(\w+)\s+\[(.+)\]$', condition)
    if match:
        question_id = match.group(1)
        operator = match.group(2)
        logic = match.group(3)  # 'or' or 'and'
        values_str = match.group(4)
        
        # Parse values array
        values = _parse_array_values(values_str)
        
        if logic == 'or':
            # Create or structure
            or_conditions = []
            for value in values:
                or_conditions.append({
                    "r": question_id,
                    "o": operator,
                    "v": value
                })
            return {"or": or_conditions}
        else:  # 'and'
            # For -and patterns, return a special marker that will be flattened
            return {
                "_flatten": [
                    {
                        "r": question_id,
                        "o": operator,
                        "v": value
                    }
                    for value in values
                ]
            }
    
    # Pattern: Q-10 e ["V1"]
    # Single value in array
    match = re.match(r'^([A-Z]+-\d+)\s+([!=e])\s+\[(.+)\]$', condition)
    if match:
        question_id = match.group(1)
        operator = match.group(2)
        values_str = match.group(3)
        
        values = _parse_array_values(values_str)
        if len(values) == 1:
            return {
                "r": question_id,
                "o": operator,
                "v": values[0]
            }
        else:
            # Multiple values without -or/-and, treat as 'or'
            or_conditions = []
            for value in values:
                or_conditions.append({
                    "r": question_id,
                    "o": operator,
                    "v": value
                })
            return {"or": or_conditions}
    
    # Pattern: Q-10 OPERATOR "VALUE" or Q-10 OPERATOR VALUE
    # e.g., I-40 = "CO-1", I-60 > 1000, I-80 = Yes
    match = re.match(r'^([A-Z]+-\d+)\s*([!=<>]+)\s*(.+)$', condition)
    if match:
        question_id = match.group(1)
        operator = match.group(2)
        value_str = match.group(3).strip()
        
        # Parse value (remove quotes if present)
        value = _parse_value(value_str)
        
        return {
            "r": question_id,
            "o": operator,
            "v": value
        }
    
    # If it's just a number or simple value, skip it silently (likely invalid)
    if condition.isdigit() or len(condition) < 3:
        return None
    
    # Only log warning for conditions that look like they should be valid
    if re.match(r'^[A-Z]+-\d+', condition):
        logger.warning(f"Could not parse condition: {condition}")
    
    return None


def _parse_array_values(values_str: str) -> List[Any]:
    """
    Parse array values from string.
    
    Examples:
    - '"V1", "V2", "V3"' -> ["V1", "V2", "V3"]
    - "'V1', 'V2'" -> ["V1", "V2"]
    """
    values = []
    
    # Split by comma
    parts = values_str.split(',')
    
    for part in parts:
        part = part.strip()
        # Remove quotes
        part = part.strip('"').strip("'")
        if part:
            values.append(part)
    
    return values


def _parse_value(value_str: str) -> Any:
    """
    Parse a single value, handling quotes and type conversion.
    
    Examples:
    - '"CO-1"' -> "CO-1"
    - '1000' -> 1000
    - 'Yes' -> "Yes"
    - 'No' -> "No"
    """
    value_str = value_str.strip()
    
    # Remove quotes if present
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # Try to convert to number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        # Return as string
        return value_str


def _flatten_conditions(conditions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Flatten conditions that have _flatten marker.
    
    This is used for e-and and =-and patterns where multiple conditions
    should be at the same level.
    """
    flattened = []
    
    for condition in conditions:
        if isinstance(condition, dict) and "_flatten" in condition:
            # Expand flattened conditions
            flattened.extend(condition["_flatten"])
        else:
            flattened.append(condition)
    
    return flattened
