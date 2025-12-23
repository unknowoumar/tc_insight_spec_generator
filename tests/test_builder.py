import pandas as pd
import pytest

from tc_spec.builder import (
    build_rules,
    build_questions,
    build_sections,
    build_lists,
    build_anomalies,
)
from tc_spec.utils.errors import ExcelValidationError
def make_base_dfs():
    questions = pd.DataFrame([
        {
            "section": "V",
            "q_num": "50",
            "label": "Q_V_50",
            "lang_SYS": "How many units?",
            "roles": "e",
        }
    ])

    question_types = pd.DataFrame([
        {
            "section": "V",
            "q_num": "50",
            "type": "N",
        }
    ])

    sections = pd.DataFrame([
        {
            "section_code": "V",
            "section_label": "Volume",
            "order": 1,
        }
    ])

    lists = pd.DataFrame([
        {
            "list_code": "LST-TEST",
            "value": "A",
            "lang_SYS": "Option A",
            "order": 1,
        }
    ])

    visibility_rules = pd.DataFrame([
        {
            "target_type": "question",
            "target_ref": "V-50",
            "r_ref": "I-10",
            "operator": "=",
            "value_type": "v",
            "value": "YES",
        }
    ])

    anomalies = pd.DataFrame([
        {
            "anomaly_code": "ANO-A1",
            "weight": 10,
        }
    ])

    return (
        questions,
        question_types,
        sections,
        lists,
        visibility_rules,
        anomalies,
    )

def test_build_rules():
    *_, visibility_rules, _ = make_base_dfs()

    rules = build_rules(visibility_rules)

    assert "question:V-50" in rules
    assert len(rules["question:V-50"]) == 1

def test_build_questions():
    questions_df, types_df, _, _, rules_df, _ = make_base_dfs()

    rules = build_rules(rules_df)
    questions = build_questions(questions_df, types_df, rules)

    assert "V-50" in questions
    q = questions["V-50"]

    assert q.ref == "V-50"
    assert q.qtype["t"] == "N"
    assert len(q.visibility) == 1

def test_build_questions():
    questions_df, types_df, _, _, rules_df, _ = make_base_dfs()

    rules = build_rules(rules_df)
    questions = build_questions(questions_df, types_df, rules)

    assert "V-50" in questions
    q = questions["V-50"]

    assert q.ref == "V-50"
    assert q.qtype["t"] == "N"
    assert len(q.visibility) == 1

def test_build_sections():
    questions_df, types_df, sections_df, _, rules_df, _ = make_base_dfs()

    rules = build_rules(rules_df)
    questions = build_questions(questions_df, types_df, rules)
    sections = build_sections(sections_df, questions, rules)

    assert "V" in sections
    section = sections["V"]

    assert section.code == "V"
    assert len(section.questions) == 1

def test_build_lists():
    *_, lists_df, _, _ = make_base_dfs()

    lists = build_lists(lists_df)

    assert "LST-TEST" in lists
    lst = lists["LST-TEST"]

    assert lst.code == "LST-TEST"
    assert len(lst.items) == 1

def test_build_anomalies():
    *_, rules_df, anomalies_df = make_base_dfs()

    rules = build_rules(rules_df)
    anomalies = build_anomalies(anomalies_df, rules)

    assert "ANO-A1" in anomalies
    ano = anomalies["ANO-A1"]

    assert ano.code == "ANO-A1"
    assert ano.weight == 10

def test_anomaly_without_rules_fails():
    *_, rules_df, anomalies_df = make_base_dfs()

    rules_df = rules_df.iloc[0:0]  # aucune règle

    rules = build_rules(rules_df)

    with pytest.raises(ExcelValidationError):
        build_anomalies(anomalies_df, rules)
