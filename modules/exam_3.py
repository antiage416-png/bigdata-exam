"""
BigData Exam Simulator - Module: Type 3 Exam
작업형 제3유형 통계적 가설검정 실습 및 검증기 (t-test, ANOVA, Chi-Square, 회귀분석)
"""

import os
import streamlit as st
import pandas as pd
from utils.storage import load_question_bank
from utils.grader import grade_type3_total, grade_type3_subquestion
from utils.code_runner import run_user_code


def render_exam_3():
    st.markdown("## 📐 작업형 제3유형 실습실 (통계적 가설검정 및 추론)")
    st.caption("배점: 대문항당 15점 (소문항 3개 각 5점) | 목표: 검정통계량, p-value 계산 및 유의수준 0.05 기준 가설 기각 판정")

    bank = load_question_bank()
    questions = bank.get("type3", [])

    if not questions:
        st.warning("등록된 작업형 3유형 문제가 없습니다.")
        return

    # Question Selection
    q_titles = [f"[{q['id']}] {q['title']} ({q['points']}점)" for q in questions]
    selected_idx = st.selectbox("🎯 실습할 가설검정 문제를 선택하세요:", range(len(q_titles)), format_func=lambda i: q_titles[i])
    q = questions[selected_idx]

    st.divider()

    # Question Description
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.subheader(f"📝 {q['title']}")
        st.info(q["description"])
    with col_h2:
        st.metric(label="총 배점", value=f"{q['points']}점")
        st.metric(label="유의수준 (alpha)", value="0.05")

    # Dataset Preview Section
    dataset_path = os.path.join(os.path.dirname(__file__), "..", q["dataset"])
    if os.path.exists(dataset_path):
        with st.expander("📂 통계 검정 대상 데이터셋 미리보기", expanded=False):
            df = pd.read_csv(dataset_path)
            st.write(f"데이터셋 크기: `{df.shape[0]}행 x {df.shape[1]}열`")
            st.dataframe(df.head(6), use_container_width=True)
            st.dataframe(df.describe(), use_container_width=True)

    # Sub-questions input and Code runner side-by-side or tabs
    tab_inspect, tab_code = st.tabs(["📝 소문항 답안 작성 및 채점", "💻 scipy/statsmodels 파이썬 계산기"])

    with tab_code:
        st.markdown("##### 🧪 통계 분석 코드 실행기")
        st.caption("아래에서 `scipy.stats` 또는 `statsmodels` 코드를 실행하여 검정통계량과 p-value를 계산해보세요.")
        
        calc_code_key = f"t3_code_{q['id']}"
        if calc_code_key not in st.session_state:
            st.session_state[calc_code_key] = q.get("solution_code", "")

        user_calc_code = st.text_area(
            "통계 계산 코드:",
            value=st.session_state[calc_code_key],
            height=180,
            key=f"t3_editor_{q['id']}"
        )
        st.session_state[calc_code_key] = user_calc_code

        if st.button("⚡ 통계 계산 실행 (Run)", key=f"t3_run_{q['id']}"):
            with st.spinner("통계량을 계산 중입니다..."):
                exec_res = run_user_code(user_calc_code)
                st.markdown("**🖥️ 계산 결과 (Console Output):**")
                if exec_res.stdout:
                    st.code(exec_res.stdout, language="text")
                if exec_res.stderr:
                    st.error(exec_res.stderr)

    with tab_inspect:
        st.markdown("##### ✏️ 소문항 답안 입력")
        user_answers = {}

        for idx, sub_q in enumerate(q.get("sub_questions", []), 1):
            sub_id = sub_q["id"]
            st.markdown(f"**소문항 {idx}. {sub_q['question']}** (배점: {sub_q.get('points', 5)}점)")

            if sub_q.get("type") == "choice":
                opts = sub_q.get("options", [])
                ans = st.radio(
                    f"소문항 {idx} 선택:",
                    opts,
                    key=f"ans_{q['id']}_{sub_id}",
                    label_visibility="collapsed"
                )
                user_answers[sub_id] = ans
            else:
                placeholder_txt = "예: 11.1772 또는 0.0021" if sub_q.get("type") == "float" else "정수 입력"
                ans = st.text_input(
                    f"소문항 {idx} 수치 입력:",
                    placeholder=placeholder_txt,
                    key=f"ans_{q['id']}_{sub_id}",
                    label_visibility="collapsed"
                )
                user_answers[sub_id] = ans

        st.markdown("<br>", unsafe_allow_html=True)
        grade_btn = st.button("🎯 제3유형 소문항 전체 채점하기", type="primary", use_container_width=True, key=f"grade_all_{q['id']}")

        t3_res_key = f"t3_result_{q['id']}"
        if grade_btn:
            res = grade_type3_total(q, user_answers)
            st.session_state[t3_res_key] = res

        if t3_res_key in st.session_state:
            res = st.session_state[t3_res_key]
            st.markdown("---")
            st.markdown("### 🏆 제3유형 채점 결과 리포트")
            
            score_col1, score_col2 = st.columns([1, 2])
            with score_col1:
                st.metric("총 획득 점수", f"{res['total_score']} / {res['max_score']} 점")
            with score_col2:
                if res["all_correct"]:
                    st.success("🎉 모든 소문항을 완벽하게 맞히셨습니다! (만점)")
                elif res["total_score"] > 0:
                    st.warning(f"일부 문항이 오답입니다. ({res['total_score']}점 획득)")
                else:
                    st.error("모든 문항이 오답입니다. 아래 해설을 확인하세요.")

            # Breakdown
            st.markdown("##### 📋 소문항별 세부 판정:")
            for sub_q in q.get("sub_questions", []):
                sub_id = sub_q["id"]
                sub_r = res["sub_results"].get(sub_id, {})
                icon = "✅" if sub_r.get("is_correct") else "❌"
                
                with st.expander(f"{icon} {sub_q['question']} [{sub_r.get('score', 0)}/{sub_r.get('max_score', 5)}점]", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"**제출한 답:** `{sub_r.get('user_answer')}`")
                    c2.write(f"**기대 정답:** `{sub_r.get('expected_answer')}`")
                    c3.write(f"**판정:** `{sub_r.get('feedback')}`")

    # Study Reference Tabs
    st.markdown("---")
    tab_sol, tab_guide = st.tabs(["📖 모범 풀이 코드", "📚 통계 검정 가설 및 판정 가이드"])
    with tab_sol:
        st.code(q.get("solution_code", "# 풀이 코드가 없습니다."), language="python")
    with tab_guide:
        st.markdown(r"""
        - **유의확률($p$-value) 판정 원칙**:
          - $p$-value $< 0.05$: **귀무가설 기각 ($H_0$ 기각)** -> 두 집단 간 평균 차이(또는 관련성)가 통계적으로 유의미함.
          - $p$-value $\ge 0.05$: **귀무가설 기각 실패 (채택)** -> 통계적으로 유의미한 차이가 있다고 볼 수 없음.
        - **자주 나오는 검정 유형 함수 매핑**:
          - 대응표본 t-검정: `scipy.stats.ttest_rel(a, b)`
          - 독립표본 t-검정: `scipy.stats.ttest_ind(a, b, equal_var=...)`
          - 등분산 검정: `scipy.stats.levene(a, b)`
          - 일원배치 분산분석: `scipy.stats.f_oneway(a, b, c)`
          - 카이제곱 독립성 검정: `scipy.stats.chi2_contingency(pd.crosstab(df['col1'], df['col2']))`
        """)
