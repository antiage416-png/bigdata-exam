"""
BigData Exam Simulator - Module: Type 1 Exam
작업형 제1유형 실습 및 검증기 (Pandas 데이터 전처리 및 수치 연산)
"""

import os
import streamlit as st
import pandas as pd
from utils.storage import load_question_bank
from utils.grader import grade_type1
from utils.code_runner import run_user_code


def render_exam_1():
    st.markdown("## 📊 작업형 제1유형 실습실 (데이터 전처리 및 연산)")
    st.caption("배점: 문항당 10점 | 목표: 정확한 단일 수치/문자열 단답형 출력")

    bank = load_question_bank()
    questions = bank.get("type1", [])

    if not questions:
        st.warning("등록된 작업형 1유형 문제가 없습니다.")
        return

    # Question Selection
    q_titles = [f"[{q['id']}] {q['title']} ({q['points']}점)" for q in questions]
    selected_idx = st.selectbox("🎯 실습할 문제를 선택하세요:", range(len(q_titles)), format_func=lambda i: q_titles[i])
    q = questions[selected_idx]

    st.divider()

    # Question Card
    col_q1, col_q2 = st.columns([3, 1])
    with col_q1:
        st.subheader(f"📝 {q['title']}")
        st.info(q["description"])
    with col_q2:
        st.metric(label="배점", value=f"{q['points']}점")
        st.metric(label="데이터셋", value=os.path.basename(q["dataset"]))

    # Dataset Preview Section
    dataset_path = os.path.join(os.path.dirname(__file__), "..", q["dataset"])
    if os.path.exists(dataset_path):
        with st.expander("📂 데이터셋 미리보기 및 컬럼 정보 확인", expanded=False):
            df = pd.read_csv(dataset_path)
            col_d1, col_d2, col_d3 = st.columns(3)
            col_d1.write(f"**행 수 (Rows):** `{len(df):,}`")
            col_d2.write(f"**열 수 (Columns):** `{len(df.columns)}`")
            missing_count = df.isnull().sum().sum()
            col_d3.write(f"**총 결측치 수:** `{missing_count:,}`")
            
            st.dataframe(df.head(6), use_container_width=True)
            
            tab_info1, tab_info2 = st.tabs(["컬럼 명세 및 결측치 현황", "수치형 요약 통계"])
            with tab_info1:
                meta_df = pd.DataFrame({
                    "컬럼명": df.columns,
                    "데이터 타입": df.dtypes.astype(str),
                    "결측치 수": df.isnull().sum(),
                    "고유값 수": df.nunique()
                })
                st.dataframe(meta_df, use_container_width=True)
            with tab_info2:
                st.dataframe(df.describe(), use_container_width=True)

    # Coding & Input Area
    st.subheader("💻 파이썬 코드 작성 및 실행")
    
    # State key management for code
    code_key = f"t1_code_{q['id']}"
    if code_key not in st.session_state:
        st.session_state[code_key] = q.get("starter_code", "")

    c_btn1, c_btn2, c_btn3 = st.columns([2, 1, 1])
    with c_btn2:
        if st.button("🔄 초기 코드로 리셋", key=f"reset_{q['id']}"):
            st.session_state[code_key] = q.get("starter_code", "")
            st.rerun()
    with c_btn3:
        if st.button("💡 모범 코드 불러오기", key=f"load_sol_{q['id']}"):
            st.session_state[code_key] = q.get("solution_code", "")
            st.rerun()

    user_code = st.text_area(
        "아래 에디터에 파이썬 코드를 작성하세요. 최종 정답은 반드시 `print(...)`로 출력되어야 합니다:",
        value=st.session_state[code_key],
        height=220,
        key=f"editor_{q['id']}"
    )
    st.session_state[code_key] = user_code

    # Optional manual input
    with st.expander("✍️ 코드 대신 직접 수치/답안 입력으로 채점하기", expanded=False):
        direct_input = st.text_input("직접 계산한 최종 답안을 입력하세요:", key=f"direct_{q['id']}")

    # Run & Grade Button
    col_run, col_grade = st.columns([1, 1])
    
    grade_trigger = False
    with col_run:
        run_pressed = st.button("⚡ 코드 실행 (Run)", use_container_width=True, type="secondary", key=f"run_{q['id']}")
    with col_grade:
        grade_pressed = st.button("🎯 실행 및 자동 채점 (Grade)", use_container_width=True, type="primary", key=f"grade_{q['id']}")

    res_key = f"t1_result_{q['id']}"

    if run_pressed:
        with st.spinner("코드를 실행 중입니다..."):
            exec_res = run_user_code(user_code)
            st.session_state[f"run_out_{q['id']}"] = exec_res

    if grade_pressed:
        with st.spinner("채점 엔진이 정답과 오차를 검증 중입니다..."):
            inp = direct_input if direct_input else None
            grade_res = grade_type1(q, user_code=user_code, direct_input=inp)
            st.session_state[res_key] = grade_res

    # Display Execution Output
    if f"run_out_{q['id']}" in st.session_state and not grade_pressed:
        exec_res = st.session_state[f"run_out_{q['id']}"]
        st.markdown("#### 🖥️ 표준 출력 (Console Output)")
        if exec_res.stdout:
            st.code(exec_res.stdout, language="text")
        if exec_res.stderr:
            st.error(f"오류 발생:\n{exec_res.stderr}")
        if exec_res.last_output:
            st.success(f"감지된 최종 출력값: `{exec_res.last_output}`")

    # Display Grading Results
    if res_key in st.session_state:
        res = st.session_state[res_key]
        st.markdown("### 🏆 채점 결과 리포트")
        if res["is_correct"]:
            st.success(f"🎉 **[정답]** {res['feedback']}")
        else:
            st.error(f"❌ **[오답]** {res['feedback']}")

        col_sc1, col_sc2, col_sc3 = st.columns(3)
        col_sc1.metric("획득 점수", f"{res['score']} / {res['max_score']} 점")
        col_sc2.metric("제출한 값", str(res["user_answer"]))
        col_sc3.metric("기대 정답", str(res["expected_answer"]))

        if res["stdout"]:
            with st.expander("출력 로그 확인 (stdout)"):
                st.code(res["stdout"])
        if res["stderr"]:
            with st.expander("에러 로그 확인 (stderr)"):
                st.code(res["stderr"])

    # Learning Materials Tabs
    st.markdown("---")
    tab_hint, tab_sol, tab_tips = st.tabs(["💡 문제 해결 힌트", "📖 모범 풀이 코드", "📌 시험장 꿀팁"])
    with tab_hint:
        st.markdown(q.get("hint", "제공된 힌트가 없습니다."))
    with tab_sol:
        st.code(q.get("solution_code", "# 모범 답안이 없습니다."), language="python")
    with tab_tips:
        st.markdown("""
        - **빅분기 1유형 감점 방지 팁**:
          1. 문제에서 요구한 자릿수(예: 소수점 둘째 자리)를 반드시 `round(ans, 2)` 등으로 처리하세요.
          2. 결측치 대체 시 원본 보존 여부에 주의하고, 결측치 대체 전/후 표준편차 계산 시 `ddof=1`(판다스 기본값)이 적용됩니다.
          3. `print(...)` 구문으로 답안만 깔끔하게 단일 출력하는 것이 채점 안정성에 좋습니다.
        """)
