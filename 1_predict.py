"""
pages/1_🎯_Predict.py
Single Employee Attrition Prediction — fill a form, get instant risk score.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from utils.model_loader import predict_single, load_all_models, MODELS
from utils.preprocess import encode_input, CATEGORICAL_MAPS
from utils.shap_explain import shap_waterfall

st.set_page_config(page_title="Predict | EAPS", page_icon="🎯", layout="wide")
st.title("🎯 Single Employee Attrition Predictor")
st.markdown("Fill in the employee details below and click **Predict** to get the attrition risk.")
st.markdown("---")

# ── Model selector ────────────────────────────────────────────────────────────
model_name = st.selectbox("Choose prediction model",
                           list(MODELS.keys()), index=0,
                           help="Random Forest and XGBoost give the best accuracy.")

st.markdown("### Employee Information")

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("predict_form"):
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Personal**")
        age              = st.slider("Age", 18, 60, 35)
        gender           = st.selectbox("Gender", ["Male", "Female"])
        marital_status   = st.selectbox("Marital Status", ["Single", "Married", "Divorced"])
        distance         = st.slider("Distance From Home (km)", 1, 30, 10)

    with c2:
        st.markdown("**Job Details**")
        department       = st.selectbox("Department", ["Sales", "Research & Development", "Human Resources"])
        job_role         = st.selectbox("Job Role", [
            "Sales Executive", "Research Scientist", "Laboratory Technician",
            "Manufacturing Director", "Healthcare Representative", "Manager",
            "Sales Representative", "Research Director", "Human Resources"])
        job_level        = st.slider("Job Level", 1, 5, 2)
        job_involvement  = st.slider("Job Involvement (1–4)", 1, 4, 3)
        job_satisfaction = st.slider("Job Satisfaction (1–4)", 1, 4, 3)
        over_time        = st.selectbox("OverTime", ["No", "Yes"])

    with c3:
        st.markdown("**Compensation & Experience**")
        monthly_income   = st.number_input("Monthly Income ($)", 1000, 20000, 5000, step=500)
        percent_hike     = st.slider("Percent Salary Hike", 11, 25, 14)
        stock_option     = st.slider("Stock Option Level (0–3)", 0, 3, 1)
        total_years      = st.slider("Total Working Years", 0, 40, 10)
        years_company    = st.slider("Years at Company", 0, 40, 5)
        years_role       = st.slider("Years in Current Role", 0, 18, 3)
        years_promoted   = st.slider("Years Since Last Promotion", 0, 15, 1)
        years_manager    = st.slider("Years with Current Manager", 0, 17, 3)

    st.markdown("---")
    c4, c5 = st.columns(2)

    with c4:
        st.markdown("**Education & Travel**")
        education        = st.slider("Education Level (1–5)", 1, 5, 3)
        education_field  = st.selectbox("Education Field", [
            "Life Sciences", "Medical", "Marketing", "Technical Degree",
            "Human Resources", "Other"])
        business_travel  = st.selectbox("Business Travel", [
            "Non-Travel", "Travel_Rarely", "Travel_Frequently"])
        num_companies    = st.slider("Num Companies Worked", 0, 9, 2)
        training_times   = st.slider("Training Times Last Year", 0, 6, 3)

    with c5:
        st.markdown("**Work Environment**")
        env_satisfaction = st.slider("Environment Satisfaction (1–4)", 1, 4, 3)
        work_life        = st.slider("Work-Life Balance (1–4)", 1, 4, 3)
        relationship_sat = st.slider("Relationship Satisfaction (1–4)", 1, 4, 3)
        performance      = st.slider("Performance Rating (1–4)", 1, 4, 3)
        daily_rate       = st.number_input("Daily Rate", 100, 1500, 800, step=50)
        hourly_rate      = st.number_input("Hourly Rate", 30, 100, 65, step=5)
        monthly_rate     = st.number_input("Monthly Rate", 2000, 27000, 14000, step=500)

    submitted = st.form_submit_button("🔍 Predict Attrition Risk", use_container_width=True)

# ── Prediction ────────────────────────────────────────────────────────────────
if submitted:
    employee = {
        'Age': age, 'BusinessTravel': business_travel, 'DailyRate': daily_rate,
        'Department': department, 'DistanceFromHome': distance,
        'Education': education, 'EducationField': education_field,
        'EnvironmentSatisfaction': env_satisfaction, 'Gender': gender,
        'HourlyRate': hourly_rate, 'JobInvolvement': job_involvement,
        'JobLevel': job_level, 'JobRole': job_role,
        'JobSatisfaction': job_satisfaction, 'MaritalStatus': marital_status,
        'MonthlyIncome': monthly_income, 'MonthlyRate': monthly_rate,
        'NumCompaniesWorked': num_companies, 'OverTime': over_time,
        'PercentSalaryHike': percent_hike, 'PerformanceRating': performance,
        'RelationshipSatisfaction': relationship_sat,
        'StockOptionLevel': stock_option, 'TotalWorkingYears': total_years,
        'TrainingTimesLastYear': training_times, 'WorkLifeBalance': work_life,
        'YearsAtCompany': years_company, 'YearsInCurrentRole': years_role,
        'YearsSinceLastPromotion': years_promoted,
        'YearsWithCurrManager': years_manager,
    }

    # Encode and predict
    X_enc = encode_input(employee)
    result = predict_single(X_enc.iloc[0].to_dict(), model_name)

    if 'error' in result:
        st.error(result['error'])
        st.info("Run `python eaps_ml_pipeline.py` first to train and save models.")
    else:
        st.markdown("---")
        st.markdown("## Prediction Result")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            color = "🔴" if result['prediction'] == 'Leave' else "🟢"
            st.metric(f"{color} Prediction", result['prediction'])
        with col_b:
            st.metric("Attrition Probability", f"{result['probability']*100:.1f}%")
        with col_c:
            risk_color = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
            st.metric(f"{risk_color[result['risk_level']]} Risk Level", result['risk_level'])

        # Risk bar
        prob_pct = result['probability'] * 100
        bar_color = "#dc2626" if prob_pct >= 70 else ("#d97706" if prob_pct >= 40 else "#16a34a")
        st.markdown(f"""
        <div style='background:#f1f5f9;border-radius:8px;height:24px;margin:12px 0;overflow:hidden'>
          <div style='background:{bar_color};height:100%;width:{prob_pct:.1f}%;
                      transition:width 0.5s;display:flex;align-items:center;
                      padding-left:8px;color:white;font-size:13px;font-weight:600'>
            {prob_pct:.1f}%
          </div>
        </div>
        """, unsafe_allow_html=True)

        # SHAP explanation
        st.markdown("### What's driving this prediction?")
        try:
            models, scaler = load_all_models()
            model = models[model_name]
            from utils.preprocess import IBM_FEATURES
            fig = shap_waterfall(model, X_enc, IBM_FEATURES)
            if fig:
                st.pyplot(fig)
        except Exception as e:
            st.warning(f"SHAP explanation unavailable: {e}")

        # HR Recommendations
        st.markdown("### 💡 HR Recommendations")
        recs = []
        if over_time == "Yes":
            recs.append("⚠️ **Overtime detected** — consider redistributing workload or offering compensation")
        if job_satisfaction <= 2:
            recs.append("⚠️ **Low job satisfaction** — schedule 1:1 feedback session")
        if work_life <= 2:
            recs.append("⚠️ **Poor work-life balance** — review schedule flexibility")
        if years_promoted >= 5:
            recs.append("⚠️ **Not promoted in 5+ years** — discuss career growth path")
        if monthly_income < 3000:
            recs.append("⚠️ **Below-average compensation** — benchmark against market rates")
        if not recs:
            recs = ["✅ No immediate red flags — maintain current engagement level"]
        for r in recs:
            st.markdown(r)
