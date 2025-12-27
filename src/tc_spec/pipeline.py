"""
Excel Mapping Pipeline

Assemble les différents mappers pour transformer
un Excel métier en Excel machine-first contractuel.
"""

from typing import Dict
import pandas as pd

from tc_spec.excel_mapper import (
    map_lists,
    map_questions,
    map_visibility_rules,
)
from tc_spec.utils.errors import ExcelValidationError

def map_excel_to_machine_first(
    sheets: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Transforme un Excel métier en Excel machine-first.

    :param sheets: dictionnaire {sheet_name: DataFrame}
    :return: dictionnaire normalisé prêt pour le générateur
    """

    lists_df = map_lists(sheets)

    if lists_df.empty:
        raise ExcelValidationError(
            "Mapping failed: LISTS is empty"
        )
    questions_df = map_questions(sheets)

    if questions_df.empty:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS is empty"
        )
    rules_df = map_visibility_rules(sheets)

    if "type" not in questions_df.columns:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS must contain a 'type' column to build QUESTION_TYPES"
        )

    # Include list_code and other type-related columns for question types
    type_cols = ["section", "q_num", "type"]
    if "list_code" in questions_df.columns:
        type_cols.append("list_code")
    question_types_df = questions_df[type_cols].copy()

    if "section" not in questions_df.columns:
        raise ExcelValidationError(
            "Mapping failed: QUESTIONS must contain a 'section' column to build SECTIONS"
        )

    # Build sections with full sheet names and preserve Excel sheet order
    # First, get unique sections from questions
    unique_sections = questions_df["section"].unique()
    
    # Build a mapping from section codes to the sheets that generated them
    # by checking which sheets actually contain questions for each section
    from tc_spec.excel_mapper.questions_mapper import QUESTION_SHEETS_EXCLUDE
    from tc_spec.excel_mapper.metier_utils import normalize_sheet_df
    from tc_spec.excel_mapper.questions_utils import parse_question_refs
    
    section_to_sheet_name = {}
    section_to_order = {}
    
    # Get sheet names in order
    sheet_names_list = list(sheets.keys())
    
    # For each section, find which sheet generated its questions
    # by checking which sheet actually contains the question codes
    from tc_spec.excel_mapper.questions_utils import parse_question_refs
    
    for section_code in unique_sections:
        # Get sample questions from this section
        section_questions = questions_df[questions_df["section"] == section_code]
        
        if len(section_questions) == 0:
            section_to_sheet_name[section_code] = section_code
            section_to_order[section_code] = 9999
            continue
        
        # Get sample question codes to search for
        sample_codes = section_questions['label'].head(3).tolist()
        
        # Try to find which sheet contains these question codes in the ID/Code column
        found = False
        for idx, sheet_name in enumerate(sheet_names_list):
            if sheet_name in QUESTION_SHEETS_EXCLUDE:
                continue
            
            raw_df = sheets.get(sheet_name)
            if raw_df is None or raw_df.empty:
                continue
            
            # Normalize the sheet to find the ID/Code column
            df = normalize_sheet_df(raw_df)
            if df.empty:
                continue
            
            # Look for question codes in the ID/Code column specifically
            code_cols = ["Code", "Q_CODE", "QuestionCode", "Question", "Question #", "ID"]
            code_col = next((c for c in code_cols if c in df.columns), None)
            
            if code_col:
                # Check if this sheet contains any of the sample question codes in the code column
                col_data = df[code_col].astype(str)
                sheet_contains_codes = any(
                    col_data.str.contains(code, case=False, na=False, regex=False).any()
                    for code in sample_codes
                )
                
                if sheet_contains_codes:
                    section_to_sheet_name[section_code] = sheet_name
                    section_to_order[section_code] = idx
                    found = True
                    break
        
        if not found:
            # Fallback: use section_code as-is
            section_to_sheet_name[section_code] = section_code
            section_to_order[section_code] = 9999
    
    # Create sections dataframe with proper ordering
    sections_data = []
    for section_code in unique_sections:
        sections_data.append({
            'section_code': section_code,
            'section_label': section_to_sheet_name.get(section_code, section_code),
            'sheet_order': section_to_order.get(section_code, 9999)
        })
    
    sections_df = pd.DataFrame(sections_data)
    # Sort by sheet order to preserve Excel order
    sections_df = sections_df.sort_values('sheet_order').reset_index(drop=True)
    sections_df["order"] = range(1, len(sections_df) + 1)
    # Drop the temporary sheet_order column
    sections_df = sections_df.drop(columns=['sheet_order'])
    
    # Extract section visibility rules from questions_df attributes
    section_visibility_rules = questions_df.attrs.get('section_visibility_rules', {})
    
    # Map sheet names to section codes for visibility rules
    section_visibility_by_code = {}
    for sheet_name, vis_rules in section_visibility_rules.items():
        # Find the section code for this sheet
        for section_code in unique_sections:
            if section_to_sheet_name.get(section_code) == sheet_name:
                section_visibility_by_code[section_code] = vis_rules
                break
    
    # Store section visibility rules in sections_df attributes
    sections_df.attrs['section_visibility_rules'] = section_visibility_by_code

    anomalies_df = pd.DataFrame(columns=["anomaly_code", "weight"])

    return {
        "QUESTIONS": questions_df.reset_index(drop=True),
        "QUESTION_TYPES": question_types_df.reset_index(drop=True),
        "SECTIONS": sections_df.reset_index(drop=True),
        "LISTS": lists_df.reset_index(drop=True),
        "VISIBILITY_RULES": rules_df.reset_index(drop=True),
        "ANOMALIES": anomalies_df,
    }
