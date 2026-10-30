"""
BigData Exam Simulator - Module: Type 2 Exam
작업형 제2유형 머신러닝 파이프라인 실습 및 검증기 (40점 만점)
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
from utils.storage import load_question_bank
from utils.grader import grade_type2
from utils.code_runner import run_user_code


def render_exam_2():
    st.markdown("## 🤖 작업형 제2유형 실습실 (머신러닝 파이프라인)")
    st.caption("배점: 40점 | 목표: 전처리 -> 모델 학습 -> 예측 -> `result.csv` 제출 및 ROC-AUC 고득점 달성")

    bank = load_question_bank()
    questions = bank.get("type2", [])

    if not questions:
        st.warning("등록된 작업형 2유형 문제가 없습니다.")
        return

    q = questions[0]  # Standard Type 2 Problem

    # Problem Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.subheader(f"📝 {q['title']}")
        st.info(q["description"])
    with col_h2:
        st.metric(label="배점", value=f"{q['points']}점 만점")
        st.metric(label="평가 지표", value=q["metric"].upper())

    # Dataset Preview Section
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    train_path = os.path.join(base_dir, q["train_dataset"])
    test_path = os.path.join(base_dir, q["test_dataset"])

    if os.path.exists(train_path) and os.path.exists(test_path):
        with st.expander("📂 X_train, y_train 및 X_test 데이터셋 미리보기", expanded=False):
            df_train = pd.read_csv(train_path)
            df_test = pd.read_csv(test_path)

            col_tr, col_te = st.columns(2)
            with col_tr:
                st.write(f"**훈련 데이터 (Train Data):** `{df_train.shape[0]}행 x {df_train.shape[1]}열`")
                st.write(f"타깃 변수: `{q['target_col']}` (클래스 비율: {df_train[q['target_col']].value_counts(normalize=True).to_dict()})")
                st.dataframe(df_train.head(5), use_container_width=True)
            with col_te:
                st.write(f"**테스트 데이터 (Test Data):** `{df_test.shape[0]}행 x {df_test.shape[1]}열`")
                st.write("※ 테스트 데이터에는 타깃 레이블(Churn)이 없습니다.")
                st.dataframe(df_test.head(5), use_container_width=True)

    # Submission Requirements Alert
    st.markdown("""
    > [!IMPORTANT]
    > **시험장 필수 규정 준수 체크리스트:**
    > 1. 최종 예측 결과는 반드시 프로젝트 루트의 **`result.csv`** 파일로 저장되어야 합니다.
    > 2. `result.csv`에는 테스트 데이터와 동일한 행 수(600행) 및 예측값 컬럼(`pred`)이 포함되어야 합니다.
    > 3. 파일 저장 시 반드시 **`index=False`** 옵션을 지정해야 인덱스 컬럼 불일치로 인한 감점을 방지할 수 있습니다.
    """)

    # Code Editor Section
    st.subheader("💻 머신러닝 파이프라인 코드 작성 및 제출")
    
    code_key = f"t2_code_{q['id']}"
    if code_key not in st.session_state:
        st.session_state[code_key] = q.get("starter_code", "")

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    with col_btn2:
        if st.button("🔄 기본 템플릿 리셋", key="t2_reset"):
            st.session_state[code_key] = q.get("starter_code", "")
            st.rerun()
    with col_btn3:
        if st.button("💡 만점 모범 답안 코드", key="t2_load_sol"):
            st.session_state[code_key] = q.get("solution_code", "")
            st.rerun()

    user_code = st.text_area(
        "아래 에디터에서 전처리, 모델링, 예측 및 result.csv 저장 코드를 작성하세요:",
        value=st.session_state[code_key],
        height=320,
        key="t2_editor"
    )
    st.session_state[code_key] = user_code

    col_sub1, col_sub2 = st.columns([1, 1])
    with col_sub1:
        submit_pressed = st.button("🚀 모델 파이프라인 실행 및 최종 채점 (Submit)", use_container_width=True, type="primary")

    t2_res_key = f"t2_result_{q['id']}"

    if submit_pressed:
        with st.spinner("파이프라인 실행 중... (전처리 -> 모델 훈련 -> result.csv 검증 -> 평가 지표 채점)"):
            res = grade_type2(q, user_code=user_code, working_dir=base_dir)
            st.session_state[t2_res_key] = res

    # Display Grading Results
    if t2_res_key in st.session_state:
        res = st.session_state[t2_res_key]
        st.markdown("### 🏆 작업형 제2유형 채점 리포트")
        
        if res["is_valid_format"]:
            st.success(f"✅ **[제출 성공]** {res['feedback']}")
        else:
            st.error(f"❌ **[제출 실패 / 실격]** {res['feedback']}")

        # Score Metric Cards
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("최종 획득 점수", f"{res['score']} / {res['max_score']} 점")
        col_m2.metric(f"검증 {res.get('metric_name', 'ROC-AUC')}", f"{res.get('metric_value', 0.0):.4f}")
        col_m3.metric("제출 파일 행 수", f"{res.get('row_count', 0)} / 600 행")
        format_badge = "통과 (PASS)" if res["is_valid_format"] else "실격 (FAIL)"
        col_m4.metric("파일 무결성", format_badge)

        # Rubric Table
        with st.expander("📊 ROC-AUC 평가 점수 배점 기준표 (Rubric)", expanded=False):
            st.table(pd.DataFrame({
                "ROC-AUC 구간": [">= 0.78 (우수)", "0.74 ~ 0.78 (양호)", "0.70 ~ 0.74 (보통)", "0.65 ~ 0.70 (기본)", "0.60 ~ 0.65", "< 0.60"],
                "부여 점수": ["40점 만점", "36점", "32점", "28점", "24점", "15점"]
            }))

        # If result.csv exists, preview submitted predictions
        result_csv_path = os.path.join(base_dir, "result.csv")
        if os.path.exists(result_csv_path):
            with st.expander("📄 생성된 result.csv 미리보기 (상위 10행)", expanded=True):
                sub_df = pd.read_csv(result_csv_path)
                st.dataframe(sub_df.head(10), use_container_width=True)

        if res["stdout"]:
            with st.expander("출력 로그 확인 (stdout)"):
                st.code(res["stdout"])
        if res["stderr"]:
            with st.expander("에러 로그 확인 (stderr)"):
                st.code(res["stderr"])

    # Educational Tabs
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["💡 머신러닝 5단계 표준 템플릿", "⚠️ 시험장 단골 감점 요인", "📖 만점 모범 답안"])
    with tab1:
        st.markdown("""
        ```python
        # 1단계: 라이브러리 및 데이터 로드
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier
        train = pd.read_csv('data/cust_churn_train.csv')
        test = pd.read_csv('data/cust_churn_test.csv')

        # 2단계: 피처(X)와 타깃(y) 분리
        X_train = train.drop(columns=['CustomerID', 'Churn'])
        y_train = train['Churn']
        X_test = test.drop(columns=['CustomerID'])

        # 3단계: 원-핫 인코딩 및 컬럼 정렬 (Data Leakage 주의)
        X_train = pd.get_dummies(X_train)
        X_test = pd.get_dummies(X_test)
        X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

        # 4단계: 모델 학습 및 예측
        model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_test)[:, 1]

        # 5단계: 제출 파일 저장 (index=False 필수!)
        output = pd.DataFrame({'CustomerID': test['CustomerID'], 'pred': preds})
        output.to_csv('result.csv', index=False)
        ```
        """)
    with tab2:
        st.markdown("""
        1. **`index=False` 누락**: CSV에 인덱스 번호가 추가되어 2열이어야 할 파일이 3열이 되거나 채점 파서 에러로 0점 처리될 수 있습니다.
        2. **테스트 데이터 누수 (Data Leakage)**: `StandardScaler`나 인코딩을 적용할 때 `fit`은 오직 `train`에만 수행하고, `test`에는 `transform`만 적용해야 합니다.
        3. **분류 문제 확률 vs 클래스**: ROC-AUC는 확률값(`predict_proba`)을 제출해야 점수가 훨씬 높게 나옵니다.
        4. **과도한 튜닝 지양**: 빅분기 실기 환경은 GPU가 없으며 CPU 실행 시간이 제한되므로 `RandomForestClassifier`의 `n_estimators=100`, `max_depth=5~8` 정도의 베이스라인 모델로 안정성을 확보하는 것이 최선입니다.
        """)
    with tab3:
        st.code(q.get("solution_code", ""), language="python")
