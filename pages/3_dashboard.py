"""
pages/3_📊_Dashboard.py
Analytics dashboard — attrition patterns across department, age, salary, etc.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard | EAPS", page_icon="📊", layout="wide")
st.title("📊 HR Attrition Analytics Dashboard")
st.markdown("Explore attrition patterns across your dataset.")
st.markdown("---")

# ── Data loader ───────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

@st.cache_data
def load_data():
    ibm_path = os.path.join(DATA_DIR, 'WA_Fn-UseC_-HR-Employee-Attrition.csv')
    if os.path.exists(ibm_path):
        return pd.read_csv(ibm_path)
    return None

df = load_data()

if df is None:
    st.error("Dataset not found at `data/WA_Fn-UseC_-HR-Employee-Attrition.csv`")
    st.info("Place the IBM HR dataset in the `data/` folder.")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filters")
    dept_filter = st.multiselect("Department",
                                  df['Department'].unique().tolist(),
                                  default=df['Department'].unique().tolist())
    age_range = st.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()), (25, 50))
    gender_filter = st.multiselect("Gender",
                                    df['Gender'].unique().tolist(),
                                    default=df['Gender'].unique().tolist())

# Apply filters
dff = df[
    df['Department'].isin(dept_filter) &
    df['Gender'].isin(gender_filter) &
    df['Age'].between(*age_range)
].copy()

dff['Attrition_Num'] = dff['Attrition'].map({'Yes': 1, 'No': 0})

# ── KPI row ───────────────────────────────────────────────────────────────────
total     = len(dff)
attrited  = (dff['Attrition'] == 'Yes').sum()
rate      = attrited / total * 100 if total > 0 else 0
avg_inc   = dff['MonthlyIncome'].mean()
avg_age   = dff['Age'].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Employees",        f"{total:,}")
k2.metric("Attrition Count",  f"{attrited:,}")
k3.metric("Attrition Rate",   f"{rate:.1f}%")
k4.metric("Avg Monthly Income", f"${avg_inc:,.0f}")
k5.metric("Avg Age",          f"{avg_age:.1f} yrs")

st.markdown("---")

# ── Row 1: Department + JobRole ────────────────────────────────────────────────
c1, c2 = st.columns(2)
with c1:
    dept_att = dff.groupby('Department')['Attrition_Num'].mean().reset_index()
    dept_att.columns = ['Department', 'Attrition Rate']
    dept_att['Attrition Rate'] = (dept_att['Attrition Rate'] * 100).round(1)
    fig = px.bar(dept_att, x='Department', y='Attrition Rate',
                 color='Attrition Rate', color_continuous_scale='RdYlGn_r',
                 title='Attrition Rate by Department (%)',
                 text='Attrition Rate')
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(showlegend=False, height=350, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    role_att = dff.groupby('JobRole')['Attrition_Num'].mean().reset_index()
    role_att.columns = ['JobRole', 'Attrition Rate']
    role_att['Attrition Rate'] = (role_att['Attrition Rate'] * 100).round(1)
    role_att = role_att.sort_values('Attrition Rate', ascending=True)
    fig = px.bar(role_att, y='JobRole', x='Attrition Rate',
                 orientation='h', color='Attrition Rate',
                 color_continuous_scale='RdYlGn_r',
                 title='Attrition Rate by Job Role (%)')
    fig.update_layout(showlegend=False, height=350, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 2: Age distribution + Income boxplot ──────────────────────────────────
c3, c4 = st.columns(2)
with c3:
    fig = px.histogram(dff, x='Age', color='Attrition',
                       barmode='overlay', nbins=25,
                       color_discrete_map={'Yes': '#dc2626', 'No': '#4f46e5'},
                       title='Age Distribution by Attrition',
                       opacity=0.75)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    fig = px.box(dff, x='Attrition', y='MonthlyIncome',
                 color='Attrition',
                 color_discrete_map={'Yes': '#dc2626', 'No': '#4f46e5'},
                 title='Monthly Income vs Attrition',
                 points='outliers')
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 3: OverTime + WorkLifeBalance ─────────────────────────────────────────
c5, c6 = st.columns(2)
with c5:
    ot = dff.groupby(['OverTime', 'Attrition']).size().reset_index(name='Count')
    fig = px.bar(ot, x='OverTime', y='Count', color='Attrition',
                 barmode='group',
                 color_discrete_map={'Yes': '#dc2626', 'No': '#4f46e5'},
                 title='Overtime vs Attrition')
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    wlb = dff.groupby(['WorkLifeBalance', 'Attrition']).size().reset_index(name='Count')
    wlb['WorkLifeBalance'] = wlb['WorkLifeBalance'].map(
        {1: 'Bad', 2: 'Good', 3: 'Better', 4: 'Best'})
    fig = px.bar(wlb, x='WorkLifeBalance', y='Count', color='Attrition',
                 barmode='group',
                 color_discrete_map={'Yes': '#dc2626', 'No': '#4f46e5'},
                 title='Work-Life Balance vs Attrition',
                 category_orders={'WorkLifeBalance': ['Bad', 'Good', 'Better', 'Best']})
    fig.update_layout(height=320)
    st.plotly_chart(fig, use_container_width=True)

# ── Row 4: Heatmap ────────────────────────────────────────────────────────────
st.markdown("### Attrition Heatmap — Department × Job Satisfaction")
heat = dff.groupby(['Department', 'JobSatisfaction'])['Attrition_Num'].mean().unstack()
heat = (heat * 100).round(1)
heat.columns = [f'Satisfaction {c}' for c in heat.columns]
fig = px.imshow(heat, color_continuous_scale='RdYlGn_r',
                text_auto=True, aspect='auto',
                title='Attrition Rate (%) — Department × Job Satisfaction')
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# ── Scatter: Income vs TotalWorkingYears ──────────────────────────────────────
st.markdown("### Income vs Experience (coloured by attrition)")
fig = px.scatter(dff, x='TotalWorkingYears', y='MonthlyIncome',
                 color='Attrition', size='Age',
                 color_discrete_map={'Yes': '#dc2626', 'No': '#4f46e5'},
                 hover_data=['Department', 'JobRole'],
                 title='Monthly Income vs Total Working Years',
                 opacity=0.6)
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)
