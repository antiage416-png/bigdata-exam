"""
BigData Exam Simulator - Grader Engine
작업형 1, 2, 3유형에 대한 자동 채점, 정답 판정, 오차 허용범위 계산 및 상세 피드백 생성
"""

import os
import re
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, mean_squared_error
from .code_runner import run_user_code, ExecutionResult


def extract_numeric_value(text: str) -> Optional[float]:
    """텍스트에서 가장 마지막으로 등장하는 유효 수치값을 파싱합니다."""
    if not text:
        return None
    # Match integers, floats, scientific notation
    matches = re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", str(text))
    if matches:
        try:
            return float(matches[-1])
        except ValueError:
            return None
    return None


def grade_type1(question: Dict[str, Any], user_code: str = None, direct_input: str = None) -> Dict[str, Any]:
    """
    작업형 1유형 채점
    - 코드 실행 결과(stdout의 마지막 줄) 또는 직접 입력된 값과 정답 비교
    """
    stdout = ""
    stderr = ""
    exec_success = True
    candidate_answer = direct_input.strip() if direct_input else None

    if user_code and user_code.strip():
        exec_res = run_user_code(user_code)
        stdout = exec_res.stdout
        stderr = exec_res.stderr
        exec_success = exec_res.success
        if exec_res.last_output and not candidate_answer:
            candidate_answer = exec_res.last_output

    expected = question["expected"]
    tolerance = question.get("tolerance", 0.001)
    ans_type = question.get("answer_type", "float")
    max_score = question.get("points", 10)

    is_correct = False
    feedback = ""
    parsed_val = None

    if not candidate_answer:
        feedback = "출력 또는 입력된 정답이 없습니다. 코드를 실행하거나 직접 답안을 입력하세요."
        return {
            "is_correct": False,
            "score": 0,
            "max_score": max_score,
            "user_answer": "None",
            "expected_answer": expected,
            "stdout": stdout,
            "stderr": stderr,
            "feedback": feedback
        }

    if ans_type in ["float", "int"]:
        parsed_val = extract_numeric_value(candidate_answer)
        if parsed_val is not None:
            diff = abs(parsed_val - float(expected))
            if diff <= tolerance:
                is_correct = True
                score = max_score
                feedback = f"정답입니다! (제출값: {parsed_val}, 정답: {expected}, 오차: {diff:.4f} <= 허용치: {tolerance})"
            else:
                score = 0
                feedback = f"오답입니다. (제출값: {parsed_val}, 정답: {expected}, 오차: {diff:.4f})"
        else:
            score = 0
            feedback = f"수치형 값을 파싱할 수 없습니다: '{candidate_answer}'"
    else:  # string type
        user_str = str(candidate_answer).strip().lower()
        exp_str = str(expected).strip().lower()
        if user_str == exp_str or exp_str in user_str:
            is_correct = True
            score = max_score
            feedback = f"정답입니다! (제출값: '{candidate_answer}')"
        else:
            score = 0
            feedback = f"오답입니다. (제출값: '{candidate_answer}', 정답: '{expected}')"

    return {
        "is_correct": is_correct,
        "score": score,
        "max_score": max_score,
        "user_answer": candidate_answer,
        "expected_answer": expected,
        "stdout": stdout,
        "stderr": stderr,
        "feedback": feedback
    }


def grade_type2(question: Dict[str, Any], user_code: str, working_dir: str = None) -> Dict[str, Any]:
    """
    작업형 2유형 채점
    - 머신러닝 파이프라인 코드 실행
    - 생성된 'result.csv' 파일 형식 및 무결성 검증
    - 숨겨진 평가 데이터셋과 ROC-AUC / 평가 지표 계산
    - 점수 구간표(Rubric)에 따른 최종 득점(40점 만점) 산출
    """
    max_score = question.get("points", 40)
    
    if working_dir is None:
        working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
    result_csv_path = os.path.join(working_dir, "result.csv")
    # Clean previous result.csv if exists to prevent caching old results
    if os.path.exists(result_csv_path):
        try:
            os.remove(result_csv_path)
        except Exception:
            pass

    # 1. Run user code
    exec_res = run_user_code(user_code, working_dir=working_dir, timeout_seconds=30)
    stdout = exec_res.stdout
    stderr = exec_res.stderr

    if not exec_res.success:
        return {
            "is_valid_format": False,
            "metric_name": question.get("metric", "roc_auc"),
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": f"코드 실행 중 오류가 발생했습니다.\n{stderr}",
            "stdout": stdout,
            "stderr": stderr
        }

    # 2. Check result.csv existence
    if not os.path.exists(result_csv_path):
        return {
            "is_valid_format": False,
            "metric_name": question.get("metric", "roc_auc"),
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": "제출 파일 'result.csv'가 생성되지 않았습니다. 코드가 result.csv로 저장하는지 확인하세요.",
            "stdout": stdout,
            "stderr": stderr
        }

    # 3. Validate CSV Integrity
    try:
        user_pred_df = pd.read_csv(result_csv_path)
    except Exception as e:
        return {
            "is_valid_format": False,
            "metric_name": question.get("metric", "roc_auc"),
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": f"result.csv 파일을 읽는 중 오류가 발생했습니다: {e}",
            "stdout": stdout,
            "stderr": stderr
        }

    gt_path = os.path.join(working_dir, question["ground_truth"])
    gt_df = pd.read_csv(gt_path)
    expected_rows = len(gt_df)

    if len(user_pred_df) != expected_rows:
        return {
            "is_valid_format": False,
            "metric_name": question.get("metric", "roc_auc"),
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": f"제출 파일 행 수 불일치! (제출: {len(user_pred_df)}행, 요구: {expected_rows}행)",
            "stdout": stdout,
            "stderr": stderr
        }

    # Identify prediction column
    pred_col = None
    target_col = question.get("target_col", "Churn")
    candidate_cols = ["pred", "prediction", "predict", "proba", "probability", "Churn", target_col]
    
    for c in candidate_cols:
        if c in user_pred_df.columns:
            pred_col = c
            break

    if pred_col is None:
        # If 2 columns, take the second column; if 1 column, take it
        if len(user_pred_df.columns) == 2:
            pred_col = user_pred_df.columns[1]
        elif len(user_pred_df.columns) == 1:
            pred_col = user_pred_df.columns[0]
        else:
            return {
                "is_valid_format": False,
                "metric_name": question.get("metric", "roc_auc"),
                "metric_value": 0.0,
                "score": 0,
                "max_score": max_score,
                "feedback": f"예측값 컬럼('pred' 등)을 찾을 수 없습니다. 컬럼 목록: {list(user_pred_df.columns)}",
                "stdout": stdout,
                "stderr": stderr
            }

    y_pred = user_pred_df[pred_col]

    # Check for NaN / Inf
    if y_pred.isnull().any() or np.isinf(y_pred).any():
        return {
            "is_valid_format": False,
            "metric_name": question.get("metric", "roc_auc"),
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": "예측값에 결측치(NaN) 또는 무한대(Inf)가 포함되어 있어 실격 처리되었습니다.",
            "stdout": stdout,
            "stderr": stderr
        }

    # 4. Compute Evaluation Metric
    y_true = gt_df[target_col]
    metric_type = question.get("metric", "roc_auc")
    metric_val = 0.0

    try:
        if metric_type == "roc_auc":
            metric_val = roc_auc_score(y_true, y_pred)
        elif metric_type == "f1":
            binary_pred = (y_pred >= 0.5).astype(int)
            metric_val = f1_score(y_true, binary_pred, average="macro")
        elif metric_type == "accuracy":
            binary_pred = (y_pred >= 0.5).astype(int)
            metric_val = accuracy_score(y_true, binary_pred)
        elif metric_type == "rmse":
            metric_val = np.sqrt(mean_squared_error(y_true, y_pred))
    except Exception as e:
        return {
            "is_valid_format": False,
            "metric_name": metric_type,
            "metric_value": 0.0,
            "score": 0,
            "max_score": max_score,
            "feedback": f"평가 지표 계산 중 오류 발생: {e}",
            "stdout": stdout,
            "stderr": stderr
        }

    # 5. Rubric Score Mapping
    rubric = question.get("rubric", {})
    score = 10  # Minimum default if valid file
    sorted_thresholds = sorted([float(k) for k in rubric.keys()], reverse=True)

    for th in sorted_thresholds:
        if metric_val >= th:
            score = rubric[str(th)]
            break

    feedback = f"검증 완료! {metric_type.upper()} = {metric_val:.4f} -> 획득 점수: {score}/{max_score}점"

    return {
        "is_valid_format": True,
        "metric_name": metric_type.upper(),
        "metric_value": round(metric_val, 4),
        "score": score,
        "max_score": max_score,
        "row_count": len(user_pred_df),
        "feedback": feedback,
        "stdout": stdout,
        "stderr": stderr
    }


def grade_type3_subquestion(sub_q: Dict[str, Any], user_ans: Any) -> Dict[str, Any]:
    """작업형 3유형 소문항 채점"""
    q_type = sub_q.get("type", "float")
    expected = sub_q["expected"]
    points = sub_q.get("points", 5)

    if user_ans is None or str(user_ans).strip() == "":
        return {
            "is_correct": False,
            "score": 0,
            "max_score": points,
            "user_answer": "None",
            "expected_answer": expected,
            "feedback": "답안이 입력되지 않았습니다."
        }

    if q_type in ["float", "int"]:
        num_val = extract_numeric_value(str(user_ans))
        if num_val is None:
            return {
                "is_correct": False,
                "score": 0,
                "max_score": points,
                "user_answer": user_ans,
                "expected_answer": expected,
                "feedback": f"수치를 인식할 수 없습니다: '{user_ans}'"
            }
        tolerance = sub_q.get("tolerance", 0.001)
        diff = abs(num_val - float(expected))
        if diff <= tolerance:
            return {
                "is_correct": True,
                "score": points,
                "max_score": points,
                "user_answer": num_val,
                "expected_answer": expected,
                "feedback": f"정답입니다! (오차 {diff:.4f} <= {tolerance})"
            }
        else:
            return {
                "is_correct": False,
                "score": 0,
                "max_score": points,
                "user_answer": num_val,
                "expected_answer": expected,
                "feedback": f"오답입니다. (제출: {num_val}, 정답: {expected})"
            }
    else:  # choice / string
        user_str = str(user_ans).strip().lower()
        exp_str = str(expected).strip().lower()
        if user_str == exp_str or exp_str in user_str or user_str in exp_str:
            return {
                "is_correct": True,
                "score": points,
                "max_score": points,
                "user_answer": user_ans,
                "expected_answer": expected,
                "feedback": "정답입니다!"
            }
        else:
            return {
                "is_correct": False,
                "score": 0,
                "max_score": points,
                "user_answer": user_ans,
                "expected_answer": expected,
                "feedback": "오답입니다."
            }


def grade_type3_total(question: Dict[str, Any], user_answers: Dict[str, Any]) -> Dict[str, Any]:
    """작업형 3유형 대문항 종합 채점"""
    sub_results = {}
    total_score = 0
    max_score = question.get("points", 15)

    for sub_q in question.get("sub_questions", []):
        sub_id = sub_q["id"]
        u_ans = user_answers.get(sub_id)
        res = grade_type3_subquestion(sub_q, u_ans)
        sub_results[sub_id] = res
        total_score += res["score"]

    return {
        "question_id": question["id"],
        "total_score": total_score,
        "max_score": max_score,
        "sub_results": sub_results,
        "all_correct": total_score == max_score
    }
