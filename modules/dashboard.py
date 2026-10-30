"""
BigData Exam Simulator - Module: Dashboard
수험자의 응시 이력, 합격률 통계 및 유형별 취약점 분석 대시보드
"""

import streamlit as st
import pandas as pd
from utils.storage import load_exam_history, clear_history


def render_dashboard():
    st.markdown("## 📈 나의 모의고사 응시 이력 및 취약점 분석")
    st.caption("실전 모의고사 풀이 기록을 바탕으로 합격 가능성과 유형별 취약 영역을 진단합니다.")

    history = load_exam_history()

    if not history:
        st.info("아직 응시한 모의고사 기록이 없습니다. **'⏱️ 실전 모의고사'** 메뉴에서 시험을 응시해보세요!")
        return

    # Overview Metrics
    total_exams = len(history)
    pass_count = sum(1 for h in history if h.get("passed"))
    pass_rate = (pass_count / total_exams) * 100
    scores = [h.get("total_score", 0) for h in history]
    avg_score = sum(scores) / total_exams
    max_score = max(scores)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 응시 횟수", f"{total_exams} 회")
    col2.metric("평균 점수", f"{avg_score:.1f} 점")
    col3.metric("최고 점수", f"{max_score:.1f} 점")
    col4.metric("합격률", f"{pass_rate:.1f} %", delta=f"{pass_count}회 합격")

    st.divider()

    # Score Progression Chart
    st.subheader("📊 회차별 점수 추이 및 60점 합격선")
    chart_data = []
    for idx, h in enumerate(history, 1):
        chart_data.append({
            "회차": f"{idx}회 ({h.get('timestamp', '')[5:16]})",
            "총점": h.get("total_score", 0),
            "1유형 (30)": h.get("type1_score", 0),
            "2유형 (40)": h.get("type2_score", 0),
            "3유형 (30)": h.get("type3_score", 0)
        })
    df_chart = pd.DataFrame(chart_data)
    st.line_chart(df_chart.set_index("회차")[["총점", "1유형 (30)", "2유형 (40)", "3유형 (30)"]])

    # Vulnerability Breakdown
    st.subheader("🎯 유형별 평균 득점률 분석")
    avg_t1 = sum(h.get("type1_score", 0) for h in history) / total_exams
    avg_t2 = sum(h.get("type2_score", 0) for h in history) / total_exams
    avg_t3 = sum(h.get("type3_score", 0) for h in history) / total_exams

    col_v1, col_v2, col_v3 = st.columns(3)
    col_v1.metric("작업형 1유형 평균", f"{avg_t1:.1f} / 30 점", f"득점률 {avg_t1/30*100:.1f}%")
    col_v2.metric("작업형 2유형 평균", f"{avg_t2:.1f} / 40 점", f"득점률 {avg_t2/40*100:.1f}%")
    col_v3.metric("작업형 3유형 평균", f"{avg_t3:.1f} / 30 점", f"득점률 {avg_t3/30*100:.1f}%")

    # Diagnosis Message
    st.markdown("##### 💡 수석 강사의 맞춤 학습 처방전:")
    if avg_t2 < 30:
        st.warning("⚠️ **작업형 2유형(머신러닝) 보완 필요**: 40점 배점 중 30점 미만입니다. `result.csv` 인덱스 누락 방지, 원-핫 인코딩 `align`, `predict_proba` 적용을 반복 숙달하세요.")
    elif avg_t1 < 20:
        st.warning("⚠️ **작업형 1유형(전처리) 보완 필요**: 판다스 결측치 중앙값 대체, IQR 이상치 필터링 문법을 치트시트에서 다시 점검하세요.")
    elif avg_t3 < 20:
        st.warning("⚠️ **작업형 3유형(가설검정) 보완 필요**: t-검정, 분산분석, 카이제곱 p-value 산출 공식과 $p < 0.05$ 귀무가설 기각 판정을 집중 훈련하세요.")
    else:
        st.success("🎉 **전 영역 우수**: 전 유형에서 고른 고득점을 기록 중입니다! 실전 시험에서도 충분히 합격할 수 있습니다.")

    # Exam History Table
    st.subheader("📋 상세 응시 기록표")
    history_table = []
    for idx, h in enumerate(reversed(history), 1):
        history_table.append({
            "응시 일시": h.get("timestamp"),
            "시험명": h.get("exam_name"),
            "총점": f"{h.get('total_score')}점",
            "1유형": f"{h.get('type1_score')}점",
            "2유형": f"{h.get('type2_score')}점",
            "3유형": f"{h.get('type3_score')}점",
            "소요 시간": f"{h.get('time_spent_minutes', 0)}분",
            "합격 여부": "✅ 합격" if h.get("passed") else "❌ 불합격"
        })
    st.dataframe(pd.DataFrame(history_table), use_container_width=True)

    # Clear History Action
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ 모든 응시 기록 초기화", type="secondary"):
        clear_history()
        st.toast("모든 응시 기록이 초기화되었습니다.")
        st.rerun()
