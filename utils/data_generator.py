"""
BigData Exam Simulator - Dataset Generator
실기 시험에 필요한 기출 및 표준 스타일의 다양한 데이터셋을 자동 생성합니다.
"""

import os
import numpy as np
import pandas as pd


def generate_all_datasets(data_dir: str):
    os.makedirs(data_dir, exist_ok=True)
    np.random.seed(42)

    # 1. Titanic Dataset (Type 1 전처리/결측치/통계)
    titanic_path = os.path.join(data_dir, "titanic.csv")
    if not os.path.exists(titanic_path):
        n = 891
        pclass = np.random.choice([1, 2, 3], size=n, p=[0.24, 0.21, 0.55])
        sex = np.random.choice(["male", "female"], size=n, p=[0.65, 0.35])
        
        # Survived probability based on sex and pclass
        surv_prob = np.where(sex == "female", 0.74, 0.19) * np.where(pclass == 1, 1.2, np.where(pclass == 2, 1.0, 0.7))
        surv_prob = np.clip(surv_prob, 0.05, 0.95)
        survived = (np.random.rand(n) < surv_prob).astype(int)
        
        # Age with missing values
        age = np.random.normal(loc=29.7, scale=14.5, size=n)
        age = np.clip(age, 0.5, 80.0)
        missing_age_mask = np.random.rand(n) < 0.20  # ~20% missing
        age[missing_age_mask] = np.nan
        
        # Fare with outliers
        base_fare = np.where(pclass == 1, 84.0, np.where(pclass == 2, 20.6, 13.6))
        fare = base_fare * np.random.exponential(scale=1.0, size=n)
        fare = np.round(np.clip(fare, 0.0, 512.3), 4)
        
        embarked = np.random.choice(["S", "C", "Q"], size=n, p=[0.72, 0.19, 0.09])
        # A couple of missing values in embarked
        embarked_series = pd.Series(embarked)
        embarked_series.iloc[[61, 829]] = np.nan

        sibsp = np.random.choice([0, 1, 2, 3, 4], size=n, p=[0.68, 0.23, 0.05, 0.02, 0.02])
        parch = np.random.choice([0, 1, 2, 3], size=n, p=[0.76, 0.13, 0.09, 0.02])

        df_titanic = pd.DataFrame({
            "PassengerId": np.arange(1, n + 1),
            "Survived": survived,
            "Pclass": pclass,
            "Name": [f"Passenger_{i}" for i in range(1, n + 1)],
            "Sex": sex,
            "Age": np.round(age, 1),
            "SibSp": sibsp,
            "Parch": parch,
            "Fare": fare,
            "Embarked": embarked_series
        })
        df_titanic.to_csv(titanic_path, index=False)

    # 2. Boston Housing Dataset (Type 1 이상치/IQR/상관계수)
    boston_path = os.path.join(data_dir, "boston_housing.csv")
    if not os.path.exists(boston_path):
        n = 506
        crim = np.random.exponential(scale=3.6, size=n)
        zn = np.random.choice([0.0, 12.5, 20.0, 25.0, 80.0], size=n, p=[0.73, 0.08, 0.08, 0.06, 0.05])
        indus = np.random.uniform(1.0, 27.7, size=n)
        chas = np.random.choice([0, 1], size=n, p=[0.93, 0.07])
        nox = np.random.uniform(0.38, 0.87, size=n)
        rm = np.random.normal(loc=6.28, scale=0.7, size=n)
        age = np.random.uniform(2.9, 100.0, size=n)
        dis = np.random.exponential(scale=3.8, size=n) + 1.1
        rad = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8, 24], size=n)
        tax = np.random.choice([198, 222, 270, 307, 403, 666], size=n)
        ptratio = np.random.uniform(12.6, 22.0, size=n)
        medv = 30 + 5 * rm - 0.5 * crim - 0.4 * lstat_approx(rm, crim) + np.random.normal(0, 3, size=n)
        medv = np.clip(medv, 5.0, 50.0)

        df_boston = pd.DataFrame({
            "CRIM": np.round(crim, 5),
            "ZN": zn,
            "INDUS": np.round(indus, 2),
            "CHAS": chas,
            "NOX": np.round(nox, 4),
            "RM": np.round(rm, 3),
            "AGE": np.round(age, 1),
            "DIS": np.round(dis, 4),
            "RAD": rad,
            "TAX": tax,
            "PTRATIO": np.round(ptratio, 1),
            "MEDV": np.round(medv, 1)
        })
        df_boston.to_csv(boston_path, index=False)

    # 3. Customer Shopping Transactions (Type 1 시계열/날짜 파싱/그룹화)
    shopping_path = os.path.join(data_dir, "customer_shopping.csv")
    if not os.path.exists(shopping_path):
        n = 1000
        dates = pd.date_range("2023-01-01", "2023-12-31", periods=n)
        date_list = [d.strftime("%Y-%m-%d") for d in dates]
        np.random.shuffle(date_list)
        categories = ["Clothing", "Cosmetics", "Food & Beverage", "Books", "Electronics", "Shoes"]
        payment_methods = ["Credit Card", "Cash", "Debit Card"]
        cities = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"]
        
        df_shopping = pd.DataFrame({
            "InvoiceNo": [f"INV{10000 + i}" for i in range(n)],
            "CustomerID": np.random.randint(1001, 1300, size=n),
            "Category": np.random.choice(categories, size=n),
            "Quantity": np.random.randint(1, 6, size=n),
            "UnitPrice": np.round(np.random.uniform(10.0, 500.0, size=n), 2),
            "InvoiceDate": date_list,
            "PaymentMethod": np.random.choice(payment_methods, size=n),
            "City": np.random.choice(cities, size=n)
        })
        df_shopping["TotalAmount"] = np.round(df_shopping["Quantity"] * df_shopping["UnitPrice"], 2)
        df_shopping.to_csv(shopping_path, index=False)

    # 4. Type 2 Customer Churn (Machine Learning Classification)
    churn_train_path = os.path.join(data_dir, "cust_churn_train.csv")
    churn_test_path = os.path.join(data_dir, "cust_churn_test.csv")
    churn_gt_path = os.path.join(data_dir, "cust_churn_ground_truth.csv")
    
    if not (os.path.exists(churn_train_path) and os.path.exists(churn_test_path) and os.path.exists(churn_gt_path)):
        total_cust = 2000
        cust_id = np.arange(10001, 10001 + total_cust)
        age = np.random.randint(18, 75, size=total_cust)
        gender = np.random.choice(["Male", "Female"], size=total_cust)
        tenure = np.random.randint(1, 72, size=total_cust)
        contract = np.random.choice(["Month-to-month", "One year", "Two year"], size=total_cust, p=[0.55, 0.25, 0.20])
        tech_support = np.random.choice(["Yes", "No"], size=total_cust, p=[0.4, 0.6])
        online_security = np.random.choice(["Yes", "No"], size=total_cust, p=[0.35, 0.65])
        monthly_charges = np.round(np.random.uniform(20.0, 118.0, size=total_cust), 2)
        total_charges = np.round(monthly_charges * tenure + np.random.normal(0, 50, size=total_cust), 2)
        total_charges = np.maximum(total_charges, monthly_charges)

        # Churn score
        churn_logits = (
            0.02 * (age - 40)
            - 0.04 * tenure
            + 0.015 * monthly_charges
            + np.where(contract == "Month-to-month", 1.2, -0.8)
            + np.where(tech_support == "No", 0.6, -0.4)
            - 0.5
        )
        churn_prob = 1 / (1 + np.exp(-churn_logits))
        churn = (np.random.rand(total_cust) < churn_prob).astype(int)

        full_df = pd.DataFrame({
            "CustomerID": cust_id,
            "Age": age,
            "Gender": gender,
            "Tenure": tenure,
            "Contract": contract,
            "TechSupport": tech_support,
            "OnlineSecurity": online_security,
            "MonthlyCharges": monthly_charges,
            "TotalCharges": total_charges,
            "Churn": churn
        })

        # Split into train (1400) and test (600)
        train_df = full_df.iloc[:1400].copy()
        test_df = full_df.iloc[1400:].copy()

        ground_truth_df = test_df[["CustomerID", "Churn"]].copy()
        test_features_df = test_df.drop(columns=["Churn"]).copy()

        train_df.to_csv(churn_train_path, index=False)
        test_features_df.to_csv(churn_test_path, index=False)
        ground_truth_df.to_csv(churn_gt_path, index=False)

    # 5. Type 3 Medical Treatment (Paired t-test)
    med_path = os.path.join(data_dir, "medical_treatment.csv")
    if not os.path.exists(med_path):
        n = 60
        before = np.random.normal(loc=142.0, scale=12.0, size=n)
        # Treatment effect: average reduction of 6.5 mmHg
        effect = np.random.normal(loc=6.5, scale=4.0, size=n)
        after = before - effect
        
        df_med = pd.DataFrame({
            "PatientID": [f"PT_{100 + i}" for i in range(1, n + 1)],
            "Age": np.random.randint(35, 75, size=n),
            "Gender": np.random.choice(["M", "F"], size=n),
            "BloodPressure_Before": np.round(before, 2),
            "BloodPressure_After": np.round(after, 2)
        })
        df_med.to_csv(med_path, index=False)

    # 6. Type 3 Marketing AB Testing (Independent t-test & Levene test)
    mkt_path = os.path.join(data_dir, "marketing_ab.csv")
    if not os.path.exists(mkt_path):
        n_a, n_b = 60, 60
        spent_a = np.random.normal(loc=48.5, scale=12.0, size=n_a)
        spent_b = np.random.normal(loc=54.2, scale=11.5, size=n_b)
        
        users_a = [f"USR_A_{i}" for i in range(1, n_a + 1)]
        users_b = [f"USR_B_{i}" for i in range(1, n_b + 1)]
        
        df_mkt = pd.DataFrame({
            "UserID": users_a + users_b,
            "Group": ["A"] * n_a + ["B"] * n_b,
            "SpentAmount": np.round(np.concatenate([spent_a, spent_b]), 2),
            "VisitCount": np.random.randint(1, 15, size=n_a + n_b)
        })
        df_mkt.to_csv(mkt_path, index=False)

    # 7. Type 3 Store ANOVA (One-way ANOVA)
    anova_path = os.path.join(data_dir, "store_anova.csv")
    if not os.path.exists(anova_path):
        n_per_group = 35
        # 3 groups with different sales means
        sales_east = np.random.normal(loc=310.0, scale=35.0, size=n_per_group)
        sales_west = np.random.normal(loc=335.0, scale=32.0, size=n_per_group)
        sales_south = np.random.normal(loc=290.0, scale=38.0, size=n_per_group)

        df_anova = pd.DataFrame({
            "StoreID": [f"STR_{i:03d}" for i in range(1, n_per_group * 3 + 1)],
            "Region": ["East"] * n_per_group + ["West"] * n_per_group + ["South"] * n_per_group,
            "DailySales": np.round(np.concatenate([sales_east, sales_west, sales_south]), 2),
            "Promotion": np.random.choice(["Standard", "Discount", "VIP"], size=n_per_group * 3)
        })
        df_anova.to_csv(anova_path, index=False)

    # 8. Type 3 Survey Chi-Square (Independence test)
    chi2_path = os.path.join(data_dir, "survey_chi2.csv")
    if not os.path.exists(chi2_path):
        n = 300
        age_groups = ["20s", "30s", "40s", "50s"]
        brands = ["Brand_Alpha", "Brand_Beta", "Brand_Gamma"]
        # Probabilities that vary by age group
        p_matrix = [
            [0.55, 0.30, 0.15],  # 20s
            [0.40, 0.40, 0.20],  # 30s
            [0.25, 0.45, 0.30],  # 40s
            [0.15, 0.35, 0.50]   # 50s
        ]
        sampled_age = np.random.choice(age_groups, size=n, p=[0.25, 0.30, 0.25, 0.20])
        sampled_brand = []
        for ag in sampled_age:
            idx = age_groups.index(ag)
            b = np.random.choice(brands, p=p_matrix[idx])
            sampled_brand.append(b)

        df_survey = pd.DataFrame({
            "RespondentID": [f"RESP_{i:04d}" for i in range(1, n + 1)],
            "AgeGroup": sampled_age,
            "BrandPreference": sampled_brand,
            "SatisfactionScore": np.random.randint(1, 11, size=n)
        })
        df_survey.to_csv(chi2_path, index=False)


def lstat_approx(rm, crim):
    return np.clip(35 - 3 * rm + 0.5 * crim, 1.0, 40.0)


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_data_dir = os.path.abspath(os.path.join(current_dir, "..", "data"))
    generate_all_datasets(target_data_dir)
    print(f"All datasets generated in: {target_data_dir}")
