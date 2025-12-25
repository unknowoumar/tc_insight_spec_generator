"""
Constants/Lists Mapper

Extracts lists from C&C Lists and I&M Lists sheets.
"""

from typing import Dict, List
import logging
import re
import pandas as pd

from tc_spec.utils.helpers import normalize_str
from tc_spec.utils.errors import ExcelValidationError

logger = logging.getLogger(__name__)


def map_constants_lists(sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Extract lists from C&C Lists and I&M Lists sheets.
    
    Returns a DataFrame with columns: list_code, value, order, lang_SYS, parent
    """
    rows: List[dict] = []
    
    # Parse C&C Lists
    cc_lists = sheets.get('C&C Lists')
    if cc_lists is not None:
        logger.info("Constants: parsing C&C Lists sheet")
        rows.extend(_parse_cc_lists(cc_lists))
    
    # Parse I&M Lists (similar structure but may have different format)
    im_lists = sheets.get('I&M Lists')
    if im_lists is not None:
        logger.info("Constants: parsing I&M Lists sheet")
        rows.extend(_parse_im_lists(im_lists))
    
    if not rows:
        logger.warning("Constants: no lists found in C&C Lists or I&M Lists")
        return pd.DataFrame(columns=['list_code', 'value', 'order', 'lang_SYS', 'parent'])
    
    df = pd.DataFrame(rows)
    logger.info("Constants: generated %d list items from %d unique lists", 
                len(df), df['list_code'].nunique())
    
    return df


def build_list_name_to_code_index(sheets: Dict[str, pd.DataFrame]) -> Dict[str, str]:
    """
    Build an index mapping list names (from ANSWER OPTIONS) to list codes.
    
    Returns a dict mapping normalized list names to list codes.
    Example: {"gender": "LST-VFUQ-10", "age group": "LST-VFUQ-20", "interviewee roles": "LST-I-20"}
    """
    index = {}
    
    # Parse C&C Lists to extract list names
    cc_lists = sheets.get('C&C Lists')
    if cc_lists is not None:
        for idx, row in cc_lists.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ''
            col1 = str(row[1]).strip() if pd.notna(row[1]) else ''
            
            # New list starts when col0 looks like a question code
            if col0 and re.match(r'^[A-Z]+-\d+$', col0):
                list_name = col1.strip()
                list_name_normalized = list_name.lower().strip()
                list_code = f"LST-{col0}"
                
                if list_name_normalized:
                    # Map name to question-code-based list code
                    # If duplicate names exist, last one wins (acceptable for now)
                    index[list_name_normalized] = list_code
                    logger.debug("Constants index: %s -> %s", list_name_normalized, list_code)
    
    # Parse I&M Lists to extract list names
    im_lists = sheets.get('I&M Lists')
    if im_lists is not None:
        for idx, row in im_lists.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ''
            col1 = str(row[1]).strip() if pd.notna(row[1]) else ''
            col2 = str(row[2]).strip() if pd.notna(row[2]) and len(row) > 2 else ''
            col4 = str(row[4]).strip() if pd.notna(row[4]) and len(row) > 4 else ''
            
            # Skip header and items rows
            if col1 == 'Question' or col2 == 'Code' or col0.startswith('{ "v":'):
                continue
            
            # New list starts when col1 looks like a question code
            if col1 and re.match(r'^[A-Z]+-?\d*$', col1):
                list_name = col4 if col4 else ''
                list_name_normalized = list_name.lower().strip()
                
                # Generate list_code from col4 by slugifying
                list_name_slug = re.sub(r'[^a-z0-9]+', '-', list_name.lower()).strip('-').upper()
                list_code = f"LST-{list_name_slug}"
                
                if list_name_normalized:
                    # Map name to slugified list code
                    index[list_name_normalized] = list_code
                    logger.debug("Constants index (I&M): %s -> %s", list_name_normalized, list_code)
    
    logger.info("Constants: built index with %d list name mappings", len(index))
    return index


def _parse_cc_lists(raw_df: pd.DataFrame) -> List[dict]:
    """
    Parse C&C Lists sheet format:
    
    IFUQ-10    Channel Type
    1          On-Trade
    2          Off-Trade
    ...
    
    Note: Same question code may appear multiple times with different lists.
    We use a global counter per list_code to avoid value collisions.
    """
    rows = []
    current_list_code = None
    current_question_code = None
    current_list_name = None
    # Track global order counter per list_code to avoid duplicates
    list_code_counters = {}
    
    for idx, row in raw_df.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ''
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ''
        
        # Skip empty rows
        if not col0 and not col1:
            continue
        
        # New list starts when col0 looks like a question code (e.g., IFUQ-10)
        if col0 and re.match(r'^[A-Z]+-\d+$', col0):
            # Use question code for list_code
            current_question_code = col0
            current_list_code = f"LST-{col0}"
            current_list_name = col1.strip()
            
            # Initialize counter if first time seeing this list_code
            if current_list_code not in list_code_counters:
                list_code_counters[current_list_code] = 0
            
            logger.debug("Constants: found list %s (%s)", current_list_code, current_list_name)
        elif col0.isdigit() and current_list_code and col1:
            # This is a list item - use global counter for this list_code
            list_code_counters[current_list_code] += 1
            global_order = list_code_counters[current_list_code]
            value_code = f"{current_question_code}-{global_order}"
            rows.append({
                'list_code': current_list_code,
                'value': value_code,
                'order': global_order,
                'lang_SYS': col1,
                'parent': None,
            })
    
    return rows


def _parse_im_lists(raw_df: pd.DataFrame) -> List[dict]:
    """
    Parse I&M Lists sheet format:
    
    The sheet has a header row at index 0:
    Question | Code | ... | Question Wording ENGLISH
    
    Then each list section starts with a header row:
    NaN | I-20 | IR | ... | Interviewee Roles
    
    Followed by item rows:
    { "v": " | 1 | IR-1 | ... | Manager
    { "v": " | 2 | IR-2 | ... | Owner
    
    We generate list_code from col4 (list name) by slugifying it.
    """
    rows = []
    current_list_code = None
    current_list_name = None
    order = 1
    
    for idx, row in raw_df.iterrows():
        col0 = str(row[0]).strip() if pd.notna(row[0]) else ''
        col1 = str(row[1]).strip() if pd.notna(row[1]) else ''
        col2 = str(row[2]).strip() if pd.notna(row[2]) and len(row) > 2 else ''
        col4 = str(row[4]).strip() if pd.notna(row[4]) and len(row) > 4 else ''
        
        # Skip header row and empty rows
        if col1 == 'Question' or col2 == 'Code' or (not col1 and not col2):
            continue
        
        # New list starts when col1 looks like a question code (e.g., I-20, W-250, PT)
        # This can happen with or without { "v": " in col0
        if col1 and re.match(r'^[A-Z]+-?\d*$', col1):
            # Generate list_code from col4 (list name) by slugifying
            # e.g., "Interviewee Roles" -> "LST-INTERVIEWEE-ROLES"
            list_name = col4 if col4 else col2
            list_name_slug = re.sub(r'[^a-z0-9]+', '-', list_name.lower()).strip('-').upper()
            current_list_code = f"LST-{list_name_slug}"
            current_list_name = list_name
            order = 1
            logger.debug("Constants: found I&M list %s (%s)", current_list_code, current_list_name)
        elif col0.startswith('{ "v":') and current_list_code and col2 and col1.isdigit():
            # This is a list item
            # col1 is the order number
            # col2 contains the value code (e.g., IR-1, SUS-1)
            # col4 contains the label text
            value_code = col2
            value_text = col4 if col4 else col2
            
            if value_code and value_text:
                rows.append({
                    'list_code': current_list_code,
                    'value': value_code,
                    'order': order,
                    'lang_SYS': value_text,
                    'parent': None,
                })
                order += 1
    
    return rows
