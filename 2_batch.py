"""
pages/2_📂_Batch.py
Batch CSV upload → predict attrition for all employees → download results.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import io
from utils.model_loader import predict_batch, MODELS
from utils.preprocess import preprocess_uploaded_csv

st.set_page_config(page_title="Batch Predict | EAPS", page_icon="📂", layout="wide")
st.title("📂 Batch Employee Attrition Prediction")
st.markdown("Upload a CSV of employees and get attrition predictions for all of them at once.")
st.markdown("---")

# ── Settings ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])
with col1:
    model_name = st.selectbox("Model to use", list(MODELS.keys()), index=0)
with col2:
    threshold = st.slider("Risk threshold (%)", 30, 80, 50,
                          help="Employees above this probability are flagged HIGH risk")

# ── File upload ───────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload Employee CSV",
    type=["csv"],
    help="CSV should have the same columns as the IBM HR dataset (Attrition column optional)"
)

if uploaded:
    df_raw = pd.read_csv(uploaded)
    st.success(f"Loaded {len(df_raw):,} employees with {df_raw.shape[1]} columns.")

    with st.expander("Preview uploaded data (first 5 rows)"):
        st.dataframe(df_raw.head())

    if st.button("🚀 Run Batch Prediction", use_container_width=True):
        with st.spinner("Predicting..."):
            try:
                df_features = preprocess_uploaded_csv(df_raw)
                df_results  = predict_batch(df_features, model_name)

                # Attach results back to original for readability
                df_out = df_raw.copy()
                df_out['Prediction']  = df_results['Prediction'].values
                df_out['Probability'] = df_results['Probability'].values
                # Re-apply custom threshold
                df_out['Risk_Level'] = df_out['Probability'].apply(
                    lambda p: 'HIGH' if p >= threshold/100 else ('MEDIUM' if p >= 0.4 else 'LOW'))

                # ── Summary metrics
                st.markdown("---")
                st.markdown("## Results Summary")

                total    = len(df_out)
                leavers  = (df_out['Prediction'] == 'Leave').sum()
                high_r   = (df_out['Risk_Level'] == 'HIGH').sum()
                avg_prob = df_out['Probability'].mean() * 100

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Employees", f"{total:,}")
                m2.metric("Predicted to Leave", f"{leavers:,}", f"{leavers/total*100:.1f}%")
                m3.metric("High Risk", f"{high_r:,}", f"{high_r/total*100:.1f}%")
                m4.metric("Avg Attrition Prob", f"{avg_prob:.1f}%")

                # ── Risk distribution
                st.markdown("### Risk Distribution")
                risk_counts = df_out['Risk_Level'].value_counts()
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"""
                <div style='background:#fef2f2;border-radius:12px;padding:16px;text-align:center'>
                  <div style='font-size:2rem;color:#dc2626;font-weight:700'>{risk_counts.get('HIGH', 0)}</div>
                  <div style='color:#991b1b'>HIGH Risk</div>
                </div>""", unsafe_allow_html=True)
                c2.markdown(f"""
                <div style='background:#fffbeb;border-radius:12px;padding:16px;text-align:center'>
                  <div style='font-size:2rem;color:#d97706;font-weight:700'>{risk_counts.get('MEDIUM', 0)}</div>
                  <div style='color:#92400e'>MEDIUM Risk</div>
                </div>""", unsafe_allow_html=True)
                c3.markdown(f"""
                <div style='background:#f0fdf4;border-radius:12px;padding:16px;text-align:center'>
                  <div style='font-size:2rem;color:#16a34a;font-weight:700'>{risk_counts.get('LOW', 0)}</div>
                  <div style='color:#166534'>LOW Risk</div>
                </div>""", unsafe_allow_html=True)

                # ── High risk employees table
                st.markdown("### 🔴 High Risk Employees")
                df_high = df_out[df_out['Risk_Level'] == 'HIGH'].sort_values(
                    'Probability', ascending=False)

                display_cols = ['Prediction', 'Probability', 'Risk_Level']
                for col in ['Age', 'Department', 'JobRole', 'MonthlyIncome', 'OverTime']:
                    if col in df_high.columns:
                        display_cols.insert(0, col)

                st.dataframe(
                    df_high[display_cols].style.background_gradient(
                        subset=['Probability'], cmap='RdYlGn_r'),
                    use_container_width=True
                )

                # ── Full results table
                with st.expander("View full results table"):
                    st.dataframe(df_out, use_container_width=True)

                # ── Download button
                csv_buffer = io.BytesIO()
                df_out.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="⬇️ Download Full Results as CSV",
                    data=csv_buffer.getvalue(),
                    file_name="eaps_batch_predictions.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.info("Make sure models are trained first by running `python eaps_ml_pipeline.py`")
else:
    # Show sample template
    st.info("No file uploaded yet. Download the template below to get started.")
    sample_cols = ['Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
                   'Education', 'EducationField', 'EnvironmentSatisfaction', 'Gender',
                   'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
                   'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
                   'OverTime', 'PercentSalaryHike', 'PerformanceRating',
                   'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
                   'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
                   'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager']
    sample_data = {c: [''] for c in sample_cols}
    df_template = pd.DataFrame(sample_data)
    csv_buf = io.BytesIO()
    df_template.to_csv(csv_buf, index=False)
    st.download_button("⬇️ Download CSV Template", data=csv_buf.getvalue(),
                       file_name="eaps_template.csv", mime="text/csv")
