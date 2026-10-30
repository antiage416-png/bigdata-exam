"""
BigData Exam Simulator - Module: Mock Exam (Full Course)
실전 모의고사 100점 통합 풀코스 (1유형 30점 + 2유형 40점 + 3유형 30점 = 총 100점)
"""

import os
import time
import streamlit as st
import pandas as pd
from utils.storage import load_question_bank, get_question_by_id, save_exam_result
from utils.grader import grade_type1, grade_type2, grade_type3_total


def render_mock_exam():
    st.markdown("## ⏱️ 실전 모의고사 100점 통합 풀코스")
    st.caption("실제 빅데이터 분석기사 실기 시험과 동일한 조건: 3시간(180분) / 총 100점 / 60점 이상 합격")

    bank = load_question_bank()
    mock_exams = bank.get("mock_exams", [])

    if not mock_exams:
        st.warning("등록된 실전 모의고사가 없습니다.")
        return

    # Select Mock Exam
    exam_names = [f"[{m['id']}] {m['name']}" for m in mock_exams]
    selected_idx = st.selectbox("📝 응시할 모의고사 회차를 선택하세요:", range(len(mock_exams)), format_func=lambda i: exam_names[i])
    mock = mock_exams[selected_idx]

    # Timer Session State
    timer_key = f"mock_timer_{mock['id']}"
    if timer_key not in st.session_state:
        st.session_state[timer_key] = {
            "start_time": None,
            "duration": mock.get("duration_minutes", 180) * 60,
            "running": False,
            "elapsed": 0
        }

    # Timer Bar
    render_timer_bar(timer_key)

    st.divider()

    # Tabs for the Exam Sections
    tab_intro, tab_t1, tab_t2, tab_t3, tab_submit = st.tabs([
        "📋 수험자 유의사항",
        "1️⃣ 작업형 1유형 (30점)",
        "2️⃣ 작업형 2유형 (40점)",
        "3️⃣ 작업형 3유형 (30점)",
        "🏁 최종 제출 및 성적표"
    ])

    with tab_intro:
        st.markdown(f"""
        ### 📌 {mock['name']} 수험자 가이드
        - **총 배점:** 100점 만점 (합격 기준: 60점 이상)
        - **제한 시간:** 180분 (3시간)
        - **문항 구성**:
          - **작업형 제1유형:** 데이터 처리 및 연산 3문항 (각 10점, 총 30점)
          - **작업형 제2유형:** 고객 이탈 분류 예측 머신러닝 파이프라인 (총 40점)
          - **작업형 제3유형:** 통계 가설검정 및 추론 2대문항 (각 15점, 총 30점)
        - **주의사항**:
          - 제2유형의 경우 최종 예측 결과를 `result.csv` 파일로 정상 생성해야 채점됩니다.
          - 모든 작성이 끝나면 상단의 **'🏁 최종 제출 및 성적표'** 탭으로 이동하여 [최종 답안 제출 및 성적표 발급] 버튼을 눌러주세요.
        """)

    # 1. Type 1 Section
    with tab_t1:
        st.markdown("### 📊 작업형 제1유형 (각 10점 / 총 30점)")
        st.caption("각 문제의 지시사항에 따라 코드를 작성하고 정답을 출력하세요.")

        t1_questions = [get_question_by_id(qid) for qid in mock.get("type1_ids", []) if get_question_by_id(qid)]
        for idx, q1 in enumerate(t1_questions, 1):
            with st.expander(f"문항 {idx}. {q1['title']} (배점: {q1['points']}점)", expanded=True):
                st.write(q1["description"])
                code_k = f"mock_{mock['id']}_code_{q1['id']}"
                if code_k not in st.session_state:
                    st.session_state[code_k] = q1.get("starter_code", "")

                st.session_state[code_k] = st.text_area(
                    f"문항 {idx} 코드 에디터:",
                    value=st.session_state[code_k],
                    height=160,
                    key=f"mock_editor_{mock['id']}_{q1['id']}"
                )

    # 2. Type 2 Section
    with tab_t2:
        st.markdown("### 🤖 작업형 제2유형 (총 40점)")
        t2_id = mock.get("type2_ids", ["T2-1"])[0]
        q2 = get_question_by_id(t2_id)
        if q2:
            st.info(q2["description"])
            code_k2 = f"mock_{mock['id']}_code_{q2['id']}"
            if code_k2 not in st.session_state:
                st.session_state[code_k2] = q2.get("starter_code", "")

            st.session_state[code_k2] = st.text_area(
                "머신러닝 파이프라인 코드 (반드시 result.csv 생성 필요):",
                value=st.session_state[code_k2],
                height=280,
                key=f"mock_editor_{mock['id']}_{q2['id']}"
            )

    # 3. Type 3 Section
    with tab_t3:
        st.markdown("### 📐 작업형 제3유형 (각 15점 / 총 30점)")
        t3_questions = [get_question_by_id(qid) for qid in mock.get("type3_ids", []) if get_question_by_id(qid)]
        for idx, q3 in enumerate(t3_questions, 1):
            with st.expander(f"대문항 {idx}. {q3['title']} (배점: {q3['points']}점)", expanded=True):
                st.write(q3["description"])
                for sub_q in q3.get("sub_questions", []):
                    sub_id = sub_q["id"]
                    sub_key = f"mock_ans_{mock['id']}_{q3['id']}_{sub_id}"
                    st.markdown(f"**- {sub_q['question']}** ({sub_q.get('points', 5)}점)")
                    if sub_q.get("type") == "choice":
                        st.radio(
                            "선택:",
                            sub_q.get("options", []),
                            key=sub_key,
                            label_visibility="collapsed"
                        )
                    else:
                        st.text_input(
                            "수치 입력:",
                            key=sub_key,
                            label_visibility="collapsed"
                        )

    # 4. Final Submit & Scorecard
    with tab_submit:
        st.markdown("### 🏁 실전 모의고사 최종 제출 및 채점")
        st.write("작성한 모든 답안을 종합 채점 엔진에 전달하고 최종 성적표를 발급합니다.")

        final_submit_btn = st.button("🏆 최종 답안 제출 및 성적표 발급 (Grade Exam)", type="primary", use_container_width=True)

        mock_res_key = f"mock_result_{mock['id']}"

        if final_submit_btn:
            with st.spinner("모든 유형의 답안을 정밀 채점 중입니다... (1유형 -> 2유형 ML 평가 -> 3유형 통계검정)"):
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                
                # Grade Type 1
                t1_scores = []
                t1_details = []
                for q1 in t1_questions:
                    code_val = st.session_state.get(f"mock_{mock['id']}_code_{q1['id']}", "")
                    g1 = grade_type1(q1, user_code=code_val)
                    t1_scores.append(g1["score"])
                    t1_details.append(g1)

                # Grade Type 2
                t2_code_val = st.session_state.get(f"mock_{mock['id']}_code_{q2['id']}", "")
                g2 = grade_type2(q2, user_code=t2_code_val, working_dir=base_dir)

                # Grade Type 3
                t3_scores = []
                t3_details = []
                for q3 in t3_questions:
                    sub_answers = {}
                    for sub_q in q3.get("sub_questions", []):
                        sub_id = sub_q["id"]
                        sub_answers[sub_id] = st.session_state.get(f"mock_ans_{mock['id']}_{q3['id']}_{sub_id}")
                    g3 = grade_type3_total(q3, sub_answers)
                    t3_scores.append(g3["total_score"])
                    t3_details.append(g3)

                t1_total = sum(t1_scores)
                t2_total = g2["score"]
                t3_total = sum(t3_scores)
                total_score = t1_total + t2_total + t3_total

                time_spent = st.session_state[timer_key].get("elapsed", 0)

                record = save_exam_result(
                    exam_name=mock["name"],
                    total_score=total_score,
                    max_score=100.0,
                    type1_score=t1_total,
                    type2_score=t2_total,
                    type3_score=t3_total,
                    time_spent_seconds=time_spent,
                    details={
                        "t1": t1_details,
                        "t2": g2,
                        "t3": t3_details
                    }
                )

                st.session_state[mock_res_key] = record

        if mock_res_key in st.session_state:
            record = st.session_state[mock_res_key]
            render_scorecard(record)


def render_timer_bar(timer_key: str):
    col_t1, col_t2, col_t3, col_t4 = st.columns([2, 1, 1, 1])
    timer_data = st.session_state[timer_key]
    
    with col_t1:
        st.markdown("⏱️ **실제 시험 시간 (180분 제한):**")
        remaining = max(0, timer_data["duration"] - timer_data["elapsed"])
        rem_min = remaining // 60
        rem_sec = remaining % 60
        st.markdown(f"### `{rem_min:02d}:{rem_sec:02d}` 남음")

    with col_t2:
        if st.button("▶️ 시험 시작", key=f"start_{timer_key}", use_container_width=True):
            timer_data["running"] = True
            st.rerun()

    with col_t3:
        if st.button("⏸️ 일시 정지", key=f"pause_{timer_key}", use_container_width=True):
            timer_data["running"] = False
            st.rerun()

    with col_t4:
        if st.button("🔄 리셋", key=f"reset_{timer_key}", use_container_width=True):
            timer_data["elapsed"] = 0
            timer_data["running"] = False
            st.rerun()


def render_scorecard(record: dict):
    st.markdown("---")
    st.markdown("## 🎓 빅데이터 분석기사 실기 최종 성적표")
    
    total = record["total_score"]
    passed = record["passed"]
    
    if passed:
        st.balloons()
        st.success(f"### 🎉 축하합니다! [최종 합격] (총점: {total} / 100점)")
    else:
        st.error(f"### 😢 아쉽습니다. [불합격] (총점: {total} / 100점 - 기준: 60점 이상)")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총점", f"{total} 점", delta="합격" if passed else "과락")
    col2.metric("작업형 1유형", f"{record['type1_score']} / 30 점")
    col3.metric("작업형 2유형", f"{record['type2_score']} / 40 점")
    col4.metric("작업형 3유형", f"{record['type3_score']} / 30 점")

    # Score breakdown chart
    score_df = pd.DataFrame({
        "유형": ["작업형 1유형 (30점)", "작업형 2유형 (40점)", "작업형 3유형 (30점)"],
        "획득 점수": [record["type1_score"], record["type2_score"], record["type3_score"]],
        "만점": [30, 40, 30]
    })
    st.bar_chart(score_df.set_index("유형"))

    with st.expander("🔍 유형별 상세 채점 내역 확인", expanded=True):
        details = record.get("details", {})
        st.write("#### 1유형 상세 결과")
        for i, d in enumerate(details.get("t1", []), 1):
            st.write(f"- 문항 {i}: {d.get('score')}점 / {d.get('max_score')}점 - {d.get('feedback')}")
        
        st.write("#### 2유형 상세 결과")
        d2 = details.get("t2", {})
        st.write(f"- 획득 점수: {d2.get('score')}점 / {d2.get('max_score')}점")
        st.write(f"- 검증 지표({d2.get('metric_name')}): {d2.get('metric_value')}")
        st.write(f"- 피드백: {d2.get('feedback')}")

        st.write("#### 3유형 상세 결과")
        for i, d3 in enumerate(details.get("t3", []), 1):
            st.write(f"- 대문항 {i}: {d3.get('total_score')}점 / {d3.get('max_score')}점")
