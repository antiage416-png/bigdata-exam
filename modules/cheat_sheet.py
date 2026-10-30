"""
BigData Exam Simulator - Module: Cheat Sheet
빅데이터 분석기사 실기 시험장 필수 암기 코드 및 문법 치트시트
"""

import streamlit as st


def render_cheat_sheet():
    st.markdown("## 📚 빅데이터 분석기사 실기 핵심 치트시트 (Cheat Sheet)")
    st.caption("시험장에서 인터넷 검색이 불가능할 때 합격을 결정짓는 필수 파이썬 문법과 라이브러리 공식")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 1. dir() & help() 내장 도움말",
        "🐼 2. Pandas 전처리 핵심 문법",
        "🤖 3. Scikit-learn 머신러닝 파이프라인",
        "📐 4. Scipy & Statsmodels 가설검정 총정리"
    ])

    with tab1:
        st.markdown("""
        ### 🔍 시험장 치트키: `dir()`과 `help()` 활용법
        실제 시험장에서는 구글 검색이나 공식 문서 웹사이트 접근이 차단됩니다. 패키지의 함수명이나 매개변수가 기억나지 않을 때는 파이썬 내장 명령어를 적극 활용해야 합니다.

        ```python
        # 1. 모듈 내 사용 가능한 함수/클래스 목록 확인
        import scipy.stats
        print(dir(scipy.stats))

        # 특정 단어가 포함된 함수만 필터링
        print([item for item in dir(scipy.stats) if 'test' in item])
        # 출력: ['f_oneway', 'ttest_1samp', 'ttest_ind', 'ttest_rel', ...]

        # 2. 함수의 공식 설명서와 파라미터 확인 (help)
        from sklearn.ensemble import RandomForestClassifier
        help(RandomForestClassifier)

        # 3. 데이터프레임 전체 컬럼 및 행 생략 없이 출력하기
        import pandas as pd
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', 100)
        ```
        """)

    with tab2:
        st.markdown("""
        ### 🐼 Pandas 데이터 전처리 빈출 문법 10선
        
        #### 1. 결측치 탐지 및 대체
        ```python
        df.isnull().sum()  # 컬럼별 결측치 개수
        df['Age'] = df['Age'].fillna(df['Age'].median())  # 중앙값 대체
        df = df.dropna(subset=['Embarked'])  # 특정 컬럼 결측치 행 제거
        ```

        #### 2. 이상치(IQR) 탐지
        ```python
        q1 = df['CRIM'].quantile(0.25)
        q3 = df['CRIM'].quantile(0.75)
        iqr = q3 - q1
        outliers = df[(df['CRIM'] < q1 - 1.5 * iqr) | (df['CRIM'] > q3 + 1.5 * iqr)]
        ```

        #### 3. 날짜형 변환 및 파생변수 추출
        ```python
        df['Date'] = pd.to_datetime(df['Date'])
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['DayOfWeek'] = df['Date'].dt.day_name()
        ```

        #### 4. 복합 조건 필터링 및 정렬
        ```python
        cond = (df['Fare'] >= 100) & (df['Sex'] == 'female')
        top5 = df[cond].sort_values(by='Age', ascending=False).head(5)
        ```

        #### 5. 그룹별 집계 (groupby)
        ```python
        df.groupby('Category')['TotalAmount'].agg(['sum', 'mean', 'count'])
        ```
        """)

    with tab3:
        st.markdown("""
        ### 🤖 Scikit-learn 머신러닝 파이프라인 뼈대 코드
        제2유형(40점)은 이 템플릿 하나만 확실히 외우면 무조건 35점 이상 확보 가능합니다.

        ```python
        import pandas as pd
        from sklearn.ensemble import RandomForestClassifier  # 회귀: RandomForestRegressor
        from sklearn.metrics import roc_auc_score

        # 1. 데이터 로드
        train = pd.read_csv('data/cust_churn_train.csv')
        test = pd.read_csv('data/cust_churn_test.csv')

        # 2. X, y 분리
        X_train = train.drop(columns=['CustomerID', 'Churn'])
        y_train = train['Churn']
        X_test = test.drop(columns=['CustomerID'])

        # 3. 원-핫 인코딩 & 컬럼 맞춤 (Data Leakage 방지)
        X_train = pd.get_dummies(X_train)
        X_test = pd.get_dummies(X_test)
        X_train, X_test = X_train.align(X_test, join='left', axis=1, fill_value=0)

        # 4. 결측치 중앙값 채우기 (필요 시)
        X_train = X_train.fillna(X_train.median())
        X_test = X_test.fillna(X_train.median())

        # 5. 모델 생성 및 학습
        model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        model.fit(X_train, y_train)

        # 6. 예측 (분류 ROC-AUC는 predict_proba[:, 1], 분류 클래스는 predict, 회귀는 predict)
        preds = model.predict_proba(X_test)[:, 1]

        # 7. 제출 CSV 저장 (index=False 필수!)
        output = pd.DataFrame({'CustomerID': test['CustomerID'], 'pred': preds})
        output.to_csv('result.csv', index=False)
        ```
        """)

    with tab4:
        st.markdown("""
        ### 📐 Scipy & Statsmodels 가설검정 총정리표

        | 검정 유형 | 대상 데이터 및 목적 | 파이썬 함수 | 반환값 |
        | :--- | :--- | :--- | :--- |
        | **단일표본 t-검정** | 한 집단의 평균이 특정 기준값과 같은지 검정 | `scipy.stats.ttest_1samp(a, popmean)` | `statistic, pvalue` |
        | **대응표본 t-검정** | 동일 집단의 사전/사후 평균 차이 검정 | `scipy.stats.ttest_rel(before, after)` | `statistic, pvalue` |
        | **독립표본 t-검정** | 서로 다른 두 집단의 평균 차이 검정 | `scipy.stats.ttest_ind(a, b, equal_var=True/False)` | `statistic, pvalue` |
        | **등분산 검정** | 두 집단의 분산이 동일한지 검정 | `scipy.stats.levene(a, b)` | `statistic, pvalue` |
        | **일원 분산분석 (ANOVA)** | 3개 이상 집단의 평균 차이 검정 | `scipy.stats.f_oneway(g1, g2, g3)` | `statistic, pvalue` |
        | **카이제곱 독립성 검정** | 두 범주형 변수 간의 관련성/독립성 검정 | `scipy.stats.chi2_contingency(pd.crosstab(c1, c2))` | `chi2, p, dof, expected` |
        | **다중선형회귀분석** | 연속형 종속변수에 대한 회귀모델 적합 | `import statsmodels.api as sm`<br>`model = sm.OLS(y, sm.add_constant(X)).fit()` | `model.summary()`, `model.pvalues`, `model.params`, `model.rsquared` |
        | **로지스틱 회귀분석** | 범주형 종속변수에 대한 승산비(OR) 및 검정 | `model = sm.Logit(y, sm.add_constant(X)).fit()` | `np.exp(model.params)` (오즈비) |
        """)
