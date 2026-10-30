"""
BigData Exam Simulator - Main Application
빅데이터 분석기사 실기시험 인터랙티브 웹 시뮬레이터
"""

import os
import streamlit as st
from datetime import datetime

# Import Custom Modules
from utils.data_generator import generate_all_datasets
from utils.storage import load_question_bank
from modules.exam_1 import render_exam_1
from modules.exam_2 import render_exam_2
from modules.exam_3 import render_exam_3
from modules.exam_mock import render_mock_exam
from modules.cheat_sheet import render_cheat_sheet
from modules.dashboard import render_dashboard

# Ensure datasets are generated on startup
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
generate_all_datasets(data_dir)

# Page Configuration
st.set_page_config(
    page_title="BigData Exam Simulator - 빅분기 실기 합격 시뮬레이터",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #1E88E5;
    }
    .badge-pass {
        background-color: #2E7D32;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def render_home():
    st.markdown('<div class="main-header">🎓 BigData Exam Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">한국데이터산업진흥원(K-Data) 빅데이터 분석기사 실기 시험 완벽 대비 인터랙티브 플랫폼</div>', unsafe_allow_html=True)

    # Key Statistics Overview
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info("⏱️ **시험 시간: 180분**\n실전 3시간 타임어택 훈련")
    with col2:
        st.success("🎯 **합격 기준: 60점 이상**\n총 100점 만점 중 60점 패스")
    with col3:
        st.warning("⚡ **실시간 자동 채점**\n오차 허용 및 ROC-AUC 채점")
    with col4:
        st.info("📚 **기출/변형 100% 반영**\n타이타닉, 주택, 고객이탈 실습")

    st.divider()

    # Strategy Section
    st.markdown("### 🏆 수석 강사가 추천하는 '초단기 70점+ 안정권 합격 전략'")
    
    col_strat1, col_strat2, col_strat3 = st.columns(3)
    with col_strat1:
        st.markdown("""
        #### 1️⃣ 작업형 1유형 (30점 만점)
        - **목표 점수:** 20 ~ 30점 (2문항 이상 적중)
        - **핵심:** 결측치 중앙값/평균 대체, 사분위수(IQR) 이상치 탐지, `to_datetime` 날짜 파싱.
        - **주의:** 소수점 반올림 요구사항 및 `print()` 단일값 출력.
        """)
    with col_strat2:
        st.markdown("""
        #### 2️⃣ 작업형 2유형 (40점 만점)
        - **목표 점수:** 32 ~ 40점 (**합격의 당락 결정**)
        - **핵심:** `RandomForestClassifier` 베이스라인 템플릿 암기.
        - **주의:** `result.csv` 인덱스 제외(`index=False`), `predict_proba` 확률값 제출.
        """)
    with col_strat3:
        st.markdown("""
        #### 3️⃣ 작업형 3유형 (30점 만점)
        - **목표 점수:** 20 ~ 25점
        - **핵심:** t-검정, 분산분석(ANOVA), 카이제곱 검정 3대장 마스터.
        - **주의:** $p$-value와 유의수준 0.05 비교 -> 귀무가설 기각 판정.
        """)

    st.divider()

    # Quick Start Navigation Buttons
    st.markdown("### 🚀 실습 모드 바로가기")
    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
    with c_btn1:
        if st.button("⏱️ 실전 모의고사 풀코스", use_container_width=True, type="primary"):
            st.session_state["nav_selection"] = "⏱️ 실전 모의고사 풀코스"
            st.rerun()
    with c_btn2:
        if st.button("📊 작업형 제1유형 실습실", use_container_width=True):
            st.session_state["nav_selection"] = "📊 작업형 제1유형 실습실"
            st.rerun()
    with c_btn3:
        if st.button("🤖 작업형 제2유형 실습실", use_container_width=True):
            st.session_state["nav_selection"] = "🤖 작업형 제2유형 실습실"
            st.rerun()
    with c_btn4:
        if st.button("📐 작업형 제3유형 실습실", use_container_width=True):
            st.session_state["nav_selection"] = "📐 작업형 제3유형 실습실"
            st.rerun()

    st.markdown("---")
    st.markdown("##### 📌 실기 시험 정보 요약")
    exam_summary_df = {
        "구분": ["작업형 1유형", "작업형 2유형", "작업형 3유형", "합계"],
        "문항 수": ["3문항", "1문항", "2대문항 (4~6소문항)", "총 6문항"],
        "배점": ["30점 (각 10점)", "40점", "30점 (각 15점)", "100점 만점"],
        "답안 제출 형태": ["단답형 수치/문자열 print", "result.csv 파일 생성", "소문항별 수치 및 기각 판정", "60점 이상 합격"]
    }
    st.table(exam_summary_df)


def main():
    # Sidebar Navigation
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=70)
    st.sidebar.title("빅분기 실기 시뮬레이터")
    st.sidebar.caption("BigData Exam Simulator v1.0")

    menu_options = [
        "🏠 홈 & 합격 전략 가이드",
        "⏱️ 실전 모의고사 풀코스",
        "📊 작업형 제1유형 실습실",
        "🤖 작업형 제2유형 실습실",
        "📐 작업형 제3유형 실습실",
        "📚 시험장 핵심 치트시트",
        "📈 내 성적 및 취약점 분석"
    ]

    # Handle navigation state
    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = menu_options[0]

    current_idx = menu_options.index(st.session_state["nav_selection"]) if st.session_state["nav_selection"] in menu_options else 0
    selection = st.sidebar.radio("📋 학습 메뉴 선택", menu_options, index=current_idx)
    st.session_state["nav_selection"] = selection

    st.sidebar.divider()
    st.sidebar.markdown(f"**📅 현재 일시:** `{datetime.now().strftime('%Y-%m-%d %H:%M')}`")
    st.sidebar.markdown("**🎯 합격 목표 점수:** `75점 / 100점`")
    st.sidebar.caption("💡 팁: 실제 시험에서는 인터넷 검색이 불가능하므로 치트시트의 문법을 미리 암기하세요.")

    # Page Dispatcher
    if selection == "🏠 홈 & 합격 전략 가이드":
        render_home()
    elif selection == "⏱️ 실전 모의고사 풀코스":
        render_mock_exam()
    elif selection == "📊 작업형 제1유형 실습실":
        render_exam_1()
    elif selection == "🤖 작업형 제2유형 실습실":
        render_exam_2()
    elif selection == "📐 작업형 제3유형 실습실":
        render_exam_3()
    elif selection == "📚 시험장 핵심 치트시트":
        render_cheat_sheet()
    elif selection == "📈 내 성적 및 취약점 분석":
        render_dashboard()


if __name__ == "__main__":
    main()
