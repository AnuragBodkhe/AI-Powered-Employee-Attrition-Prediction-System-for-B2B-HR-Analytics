"""
pages/4_🔬_Compare.py
Model comparison page — metrics, ROC curves, confusion matrices side-by-side.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, confusion_matrix
from utils.model_loader import load_all_models, SCALED_MODELS
from utils.preprocess import preprocess_uploaded_csv

st.set_page_config(page_title="Compare | EAPS", page_icon="🔬", layout="wide")
st.title("🔬 Model Performance Comparison")
st.markdown("Compare all 4 trained models across accuracy, AUC-ROC, F1, and more.")
st.markdown("---")

# ── Hardcoded results from your training run ───────────────────────────────────
# Update these values after re-training with real XGBoost
RESULTS = {
    'Logistic Regression': {'Accuracy': 0.7794, 'AUC-ROC': 0.8612, 'F1': 0.7883,
                             'Precision': 0.7575, 'Recall': 0.8219},
    'SVM':                 {'Accuracy': 0.9109, 'AUC-ROC': 0.9746, 'F1': 0.9137,
                             'Precision': 0.8859, 'Recall': 0.9433},
    'Random Forest':       {'Accuracy': 0.9696, 'AUC-ROC': 0.9979, 'F1': 0.9703,
                             'Precision': 0.9496, 'Recall': 0.9919},
    'XGBoost':             {'Accuracy': 0.9555, 'AUC-ROC': 0.9972, 'F1': 0.9567,
                             'Precision': 0.9310, 'Recall': 0.9838},
}

df_res = pd.DataFrame(RESULTS).T.reset_index().rename(columns={'index': 'Model'})

# ── Metrics table ─────────────────────────────────────────────────────────────
st.markdown("### Metrics Summary")
st.dataframe(
    df_res.style
        .highlight_max(axis=0, subset=['Accuracy', 'AUC-ROC', 'F1', 'Precision', 'Recall'],
                       color='#d1fae5')
        .format({'Accuracy': '{:.4f}', 'AUC-ROC': '{:.4f}',
                 'F1': '{:.4f}', 'Precision': '{:.4f}', 'Recall': '{:.4f}'}),
    use_container_width=True, hide_index=True
)

st.markdown("---")

# ── Radar chart ───────────────────────────────────────────────────────────────
st.markdown("### Radar Chart — Multi-metric View")
metrics = ['Accuracy', 'AUC-ROC', 'F1', 'Precision', 'Recall']
colors  = ['#4f46e5', '#0891b2', '#16a34a', '#dc2626']

fig = go.Figure()
for (_, row), color in zip(df_res.iterrows(), colors):
    vals = [row[m] for m in metrics] + [row[metrics[0]]]
    fig.add_trace(go.Scatterpolar(
        r=vals, theta=metrics + [metrics[0]],
        fill='toself', name=row['Model'],
        line_color=color, opacity=0.7
    ))
fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0.7, 1.0])),
    showlegend=True, height=420,
    title='Model Performance Radar'
)
st.plotly_chart(fig, use_container_width=True)

# ── Bar comparison ────────────────────────────────────────────────────────────
st.markdown("### Bar Chart — Metric Comparison")
df_melt = df_res.melt(id_vars='Model', var_name='Metric', value_name='Score')
fig = px.bar(df_melt, x='Model', y='Score', color='Metric',
             barmode='group', text_auto='.4f',
             title='All Models — All Metrics',
             color_discrete_sequence=['#4f46e5','#0891b2','#16a34a','#dc2626','#d97706'])
fig.update_layout(yaxis_range=[0.6, 1.03], height=400)
fig.update_traces(textposition='outside', textfont_size=9)
st.plotly_chart(fig, use_container_width=True)

# ── ROC AUC ranked ────────────────────────────────────────────────────────────
st.markdown("### AUC-ROC Leaderboard")
df_sorted = df_res.sort_values('AUC-ROC', ascending=False).reset_index(drop=True)
for i, row in df_sorted.iterrows():
    medal = ['🥇','🥈','🥉','4️⃣'][i]
    auc   = row['AUC-ROC']
    bar   = int(auc * 100)
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:8px'>
      <span style='font-size:1.4rem'>{medal}</span>
      <span style='min-width:180px;font-weight:600'>{row['Model']}</span>
      <div style='flex:1;background:#f1f5f9;border-radius:6px;height:20px;overflow:hidden'>
        <div style='background:#4f46e5;height:100%;width:{bar}%;
                    display:flex;align-items:center;padding-left:8px;
                    color:white;font-size:12px;font-weight:600'>
          {auc:.4f}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Confusion matrices (static from training) ──────────────────────────────────
st.markdown("---")
st.markdown("### Confusion Matrices")
results_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
cm_path = os.path.join(results_dir, 'confusion_matrices.png')
if os.path.exists(cm_path):
    st.image(cm_path, caption='Confusion matrices — all models on IBM test set')
else:
    st.info("Run `python eaps_ml_pipeline.py` to generate confusion matrix plots.")

# ── Feature importance from saved images ──────────────────────────────────────
st.markdown("---")
st.markdown("### Feature Importance")
c1, c2 = st.columns(2)
with c1:
    fi_rf = os.path.join(results_dir, 'feature_importance_random_forest.png')
    if os.path.exists(fi_rf):
        st.image(fi_rf, caption='Random Forest feature importance')
with c2:
    fi_xgb = os.path.join(results_dir, 'feature_importance_xgboost.png')
    if os.path.exists(fi_xgb):
        st.image(fi_xgb, caption='XGBoost feature importance')

# ── Research paper metrics ────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📄 Paper Benchmarks (IBM HR Dataset — SMOTE balanced)")
st.markdown("""
| Model | Accuracy | AUC-ROC | F1 Score | Precision | Recall |
|---|---|---|---|---|---|
| Logistic Regression | 77.94% | 0.8612 | 0.7883 | 0.7575 | 0.8219 |
| SVM (RBF kernel) | 91.09% | 0.9746 | 0.9137 | 0.8859 | 0.9433 |
| **Random Forest** | **96.96%** | **0.9979** | **0.9703** | 0.9496 | **0.9919** |
| XGBoost | 95.55% | 0.9972 | 0.9567 | 0.9310 | 0.9838 |

*Dataset: IBM HR Analytics (1470 rows, 30 features). SMOTE applied to balance classes.*
*Best model: Random Forest with AUC-ROC = 0.9979*
""")
