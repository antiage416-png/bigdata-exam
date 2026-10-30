"""
BigData Exam Simulator - Storage Manager
문제 뱅크(JSON) 및 응시/채점 이력(history/exam_history.json)을 로드하고 영구 보관합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


def get_base_dir() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_questions_path() -> str:
    return os.path.join(get_base_dir(), "data", "questions.json")


def get_history_path() -> str:
    return os.path.join(get_base_dir(), "history", "exam_history.json")


def load_question_bank() -> Dict[str, Any]:
    path = get_questions_path()
    if not os.path.exists(path):
        return {"type1": [], "type2": [], "type3": [], "mock_exams": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_question_by_id(qid: str) -> Optional[Dict[str, Any]]:
    bank = load_question_bank()
    for cat in ["type1", "type2", "type3"]:
        for q in bank.get(cat, []):
            if q["id"] == qid:
                return q
    return None


def get_mock_exams() -> List[Dict[str, Any]]:
    bank = load_question_bank()
    return bank.get("mock_exams", [])


def load_exam_history() -> List[Dict[str, Any]]:
    path = get_history_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_exam_result(
    exam_name: str,
    total_score: float,
    max_score: float,
    type1_score: float,
    type2_score: float,
    type3_score: float,
    time_spent_seconds: int,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    history = load_exam_history()
    
    passed = total_score >= 60.0
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exam_name": exam_name,
        "total_score": round(total_score, 1),
        "max_score": round(max_score, 1),
        "type1_score": round(type1_score, 1),
        "type2_score": round(type2_score, 1),
        "type3_score": round(type3_score, 1),
        "time_spent_minutes": round(time_spent_seconds / 60, 1),
        "passed": passed,
        "details": details
    }
    history.append(record)
    
    path = get_history_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
        
    return record


def clear_history():
    path = get_history_path()
    if os.path.exists(path):
        os.remove(path)
