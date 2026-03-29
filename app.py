"""
EAPS — Employee Attrition Prediction System
Main Streamlit App Entry Point
"""

import streamlit as st

st.set_page_config(
    page_title="EAPS — Employee Attrition Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #1e2130; }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .metric-card {
        background: #f8f9fa; border-radius: 12px;
        padding: 16px 20px; border-left: 4px solid #4f46e5;
        margin-bottom: 12px;
    }
    .risk-high   { color: #dc2626; font-weight: 700; font-size: 1.1rem; }
    .risk-medium { color: #d97706; font-weight: 700; font-size: 1.1rem; }
    .risk-low    { color: #16a34a; font-weight: 700; font-size: 1.1rem; }
    .stButton > button {
        background: #4f46e5; color: white;
        border-radius: 8px; border: none;
        padding: 8px 24px; font-weight: 600;
    }
    .stButton > button:hover { background: #4338ca; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/4f46e5/ffffff?text=EAPS", width=200)
    st.markdown("---")
    st.markdown("### Navigation")
    st.markdown("""
    | Page | Description |
    |------|-------------|
    | 🎯 Predict | Single employee |
    | 📂 Batch   | CSV upload |
    | 📊 Dashboard | Analytics |
    | 🔬 Compare | Model metrics |
    """)
    st.markdown("---")
    st.markdown("**MIT School of Computing**")
    st.markdown("B2B HR Analytics — EAPS v1.0")
    st.markdown("*Anurag Bodkhe et al.*")

# ── Home page ─────────────────────────────────────────────────────────────────
st.title("📊 Employee Attrition Prediction System")
st.markdown("#### AI-Powered B2B HR Analytics | MIT School of Computing")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Models Trained", "4", "LR · SVM · RF · XGBoost")
with col2:
    st.metric("Best AUC-ROC", "0.9979", "Random Forest")
with col3:
    st.metric("Dataset Size", "11,470", "rows across 3 datasets")
with col4:
    st.metric("Features", "30", "IBM HR Analytics")

st.markdown("---")

c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🚀 What this system does")
    st.markdown("""
    - **Predict** whether an employee will leave (attrition risk)
    - **Explain** which factors drive that prediction (SHAP)
    - **Batch analyse** entire HR CSV files at once
    - **Compare** all 4 ML model performances side-by-side
    - **Visualise** attrition patterns across departments, age, salary
    """)
with c2:
    st.markdown("### 📂 Navigate using the sidebar →")
    st.markdown("""
    | | |
    |---|---|
    | **🎯 Predict** | Fill in employee details, get instant risk |
    | **📂 Batch** | Upload CSV, predict all employees at once |
    | **📊 Dashboard** | Analytics charts & attrition heatmaps |
    | **🔬 Compare** | Model accuracy, AUC, F1 comparison |
    """)

st.info("👈 Use the sidebar to navigate between pages", icon="ℹ️")
