"""
bias_diagnosis.py
==================
EAPS — Employee Attrition Prediction System
Standalone Bias Diagnosis & Before/After Comparison Tool

Run BEFORE and AFTER retraining to compare prediction distributions.

Usage:
    python bias_diagnosis.py

Outputs:
    results/bias_diagnosis_*.png   — distribution plots
    prints classification reports and distribution stats
"""

import os, sys, warnings, joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, classification_report, confusion_matrix, roc_curve
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR   = os.path.join(BASE_DIR, 'models')
DATA_DIR    = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

FINAL_FEATURES = [
    'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
    'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'WorkLifeBalance', 'JobSatisfaction',
    'PerformanceRating', 'TrainingTimesLastYear', 'EnvironmentSatisfaction',
    'RelationshipSatisfaction', 'JobInvolvement', 'DistanceFromHome',
    'NumCompaniesWorked', 'Gender', 'OverTime',
    'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
]

COLUMN_RENAME_MAP = {
    'Employee_ID': 'EmployeeNumber', 'Marital_Status': 'MaritalStatus',
    'Job_Role': 'JobRole', 'Job_Level': 'JobLevel',
    'Monthly_Income': 'MonthlyIncome', 'Hourly_Rate': 'HourlyRate',
    'Years_at_Company': 'YearsAtCompany', 'Years_in_Current_Role': 'YearsInCurrentRole',
    'Years_Since_Last_Promotion': 'YearsSinceLastPromotion',
    'Work_Life_Balance': 'WorkLifeBalance', 'Job_Satisfaction': 'JobSatisfaction',
    'Performance_Rating': 'PerformanceRating',
    'Training_Hours_Last_Year': 'TrainingTimesLastYear',
    'Work_Environment_Satisfaction': 'EnvironmentSatisfaction',
    'Relationship_with_Manager': 'RelationshipSatisfaction',
    'Job_Involvement': 'JobInvolvement', 'Distance_From_Home': 'DistanceFromHome',
    'Number_of_Companies_Worked': 'NumCompaniesWorked',
    'Average_Hours_Worked_Per_Week': 'MonthlyRate',
    'Project_Count': 'StockOptionLevel', 'Absenteeism': 'PercentSalaryHike',
}

MODEL_FILES = {
    'Random Forest':       'random_forest.pkl',
    'XGBoost':             'xgboost.pkl',
    'Logistic Regression': 'logistic_regression.pkl',
    'SVM':                 'svm.pkl',
}
SCALED_MODELS = {'Logistic Regression', 'SVM'}

# ──────────────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  EAPS Bias Diagnosis Tool")
print("=" * 65)

# ── 1. Check models exist ─────────────────────────────────────────────────────
missing_models = [f for f in MODEL_FILES.values()
                  if not os.path.exists(os.path.join(MODEL_DIR, f))]
if missing_models:
    print(f"\n❌ Models not found: {missing_models}")
    print("   Run: python eaps_ml_pipeline.py  first.")
    sys.exit(1)

# ── 2. Load models and metadata ───────────────────────────────────────────────
print("\n📦 Loading models...")
models = {name: joblib.load(os.path.join(MODEL_DIR, fname))
          for name, fname in MODEL_FILES.items()}

scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl')) \
         if os.path.exists(os.path.join(MODEL_DIR, 'scaler.pkl')) else None

label_encoders = joblib.load(os.path.join(MODEL_DIR, 'label_encoders.pkl')) \
                 if os.path.exists(os.path.join(MODEL_DIR, 'label_encoders.pkl')) else {}

thresholds_all = joblib.load(os.path.join(MODEL_DIR, 'threshold.pkl')) \
                 if os.path.exists(os.path.join(MODEL_DIR, 'threshold.pkl')) else {}

feature_names = joblib.load(os.path.join(MODEL_DIR, 'feature_names.pkl')) \
                if os.path.exists(os.path.join(MODEL_DIR, 'feature_names.pkl')) else FINAL_FEATURES

print(f"   Loaded {len(models)} models")
print(f"   Saved thresholds: {thresholds_all}")

# ── 3. Rebuild test set (must mirror pipeline encoding) ───────────────────────
print("\n📂 Rebuilding test set...")
TARGET_CANDIDATES = ['Attrition', 'attrition', 'ATTRITION']
DROP_COLS = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber',
             'Employee_ID', 'DailyRate', 'Overtime']

frames = []
for fname in ['WA_Fn-UseC_-HR-Employee-Attrition.csv',
              'employee_attrition_dataset.csv',
              'employee_attrition_dataset_10000.csv']:
    path = os.path.join(DATA_DIR, fname)
    if not os.path.exists(path):
        continue
    df_raw = pd.read_csv(path)
    df_raw.rename(columns=COLUMN_RENAME_MAP, inplace=True)
    if 'Overtime' in df_raw.columns and 'OverTime' not in df_raw.columns:
        df_raw.rename(columns={'Overtime': 'OverTime'}, inplace=True)

    defaults = {'BusinessTravel': 'Travel_Rarely', 'StockOptionLevel': 0,
                'PercentSalaryHike': 14, 'MonthlyRate': 14000}
    for col, val in defaults.items():
        if col not in df_raw.columns:
            df_raw[col] = val

    target_col = next((c for c in TARGET_CANDIDATES if c in df_raw.columns), None)
    if target_col is None:
        continue
    df_raw['Attrition'] = df_raw[target_col].map(
        lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0)
    if target_col != 'Attrition':
        df_raw.drop(columns=[target_col], inplace=True)
    frames.append(df_raw)

df = pd.concat(frames, ignore_index=True)
for col in DROP_COLS:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)
for f in feature_names:
    if f not in df.columns:
        df[f] = 0
df = df[feature_names + ['Attrition']].copy()
df.dropna(subset=['Attrition'], inplace=True)
df.fillna(0, inplace=True)

# Apply same label encoders
for col, le in label_encoders.items():
    if col in df.columns:
        known = set(le.classes_)
        df[col] = df[col].astype(str).apply(
            lambda x: le.transform([x])[0] if x in known else 0)

X = df[feature_names]
y = df['Attrition']
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2,
                                         random_state=42, stratify=y)

if scaler:
    X_test_scaled = pd.DataFrame(scaler.transform(X_test), columns=X_test.columns)
else:
    X_test_scaled = X_test

print(f"   Test set: {len(X_test):,} rows  "
      f"(Stay={int((y_test==0).sum())}, Leave={int((y_test==1).sum())})")

# ── 4. Per-model diagnosis ─────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  BIAS DIAGNOSIS — All Models")
print("=" * 65)

all_results = {}
for name, clf in models.items():
    Xte = X_test_scaled if name in SCALED_MODELS else X_test
    y_proba = clf.predict_proba(Xte)[:, 1]

    # Default threshold (0.5) — "biased" mode
    y_pred_default  = (y_proba >= 0.5).astype(int)
    # Optimal threshold
    opt_thresh = thresholds_all.get(name, 0.5)
    y_pred_optimal  = (y_proba >= opt_thresh).astype(int)

    def stats(y_p):
        n_leave = int(y_p.sum())
        n_stay  = len(y_p) - n_leave
        pct     = 100 * n_leave / max(len(y_p), 1)
        return n_stay, n_leave, pct

    s0, l0, p0 = stats(y_pred_default)
    s1, l1, p1 = stats(y_pred_optimal)

    acc0  = accuracy_score(y_test, y_pred_default)
    f1_0  = f1_score(y_test, y_pred_default, zero_division=0)
    rec0  = recall_score(y_test, y_pred_default, zero_division=0)

    acc1  = accuracy_score(y_test, y_pred_optimal)
    f1_1  = f1_score(y_test, y_pred_optimal, zero_division=0)
    rec1  = recall_score(y_test, y_pred_optimal, zero_division=0)
    auc   = roc_auc_score(y_test, y_proba)

    all_results[name] = {
        'y_proba': y_proba, 'y_pred_default': y_pred_default,
        'y_pred_optimal': y_pred_optimal, 'opt_thresh': opt_thresh,
        'leave_pct_default': p0, 'leave_pct_optimal': p1,
        'acc_default': acc0, 'f1_default': f1_0, 'rec_default': rec0,
        'acc_optimal': acc1, 'f1_optimal': f1_1, 'rec_optimal': rec1,
        'auc': auc,
    }

    bias_flag = "🔴 BIASED" if p0 > 85 else ("🟡 OK" if p0 > 60 else "🟢 GOOD")

    print(f"\n  ┌── {name} ──────────────────────────────────────────")
    print(f"  │  AUC-ROC:       {auc:.4f}")
    print(f"  │  Avg Proba:     {y_proba.mean():.4f}  "
          f"(med={np.median(y_proba):.4f}  std={y_proba.std():.4f})")
    print(f"  │")
    print(f"  │  DEFAULT (thresh=0.50) {bias_flag}")
    print(f"  │    Stay={s0:,}  Leave={l0:,}  → {p0:.1f}% Leave")
    print(f"  │    Acc={acc0:.4f}  F1={f1_0:.4f}  Recall={rec0:.4f}")
    print(f"  │")
    print(f"  │  OPTIMAL (thresh={opt_thresh:.4f}) {'✅' if abs(p1-16)<20 else '⚠️'}")
    print(f"  │    Stay={s1:,}  Leave={l1:,}  → {p1:.1f}% Leave")
    print(f"  └─  Acc={acc1:.4f}  F1={f1_1:.4f}  Recall={rec1:.4f}")

    print(f"\n  Classification Report [{name}] (optimal threshold):")
    print(classification_report(y_test, y_pred_optimal,
                                 target_names=['Stay', 'Leave'],
                                 zero_division=0))

# ── 5. Before / After Summary Table ──────────────────────────────────────────
print("\n" + "=" * 65)
print("  BEFORE vs AFTER COMPARISON")
print("=" * 65)
print(f"\n  {'Model':<22} {'Before':>30}   {'After':>30}")
print(f"  {'':22} {'(thresh=0.50)':>30}   {'(optimal thresh)':>30}")
print("  " + "-" * 90)
for name, r in all_results.items():
    before = (f"Leave={r['leave_pct_default']:.0f}%  "
              f"Acc={r['acc_default']:.3f}  F1={r['f1_default']:.3f}")
    after  = (f"Leave={r['leave_pct_optimal']:.0f}%  "
              f"Acc={r['acc_optimal']:.3f}  F1={r['f1_optimal']:.3f}")
    print(f"  {name:<22} {before:>30}   {after:>30}")

# ── 6. Visualisation ──────────────────────────────────────────────────────────
print("\n📊 Generating diagnosis plots...")

# 6a. Probability histograms per model
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
axes = axes.flatten()
for idx, (name, r) in enumerate(all_results.items()):
    ax  = axes[idx]
    yp  = r['y_proba']
    thresh = r['opt_thresh']
    ax.hist(yp[y_test == 0], bins=40, alpha=0.65, color='#4f46e5',
            label='Actual Stay', density=True)
    ax.hist(yp[y_test == 1], bins=40, alpha=0.65, color='#dc2626',
            label='Actual Leave', density=True)
    ax.axvline(0.5, color='#6b7280', linestyle=':', lw=1.5, label='Default (0.5)')
    ax.axvline(thresh, color='#000000', linestyle='--', lw=2,
               label=f'Optimal ({thresh})')

    bias_pct = r['leave_pct_default']
    color_title = '#dc2626' if bias_pct > 85 else ('#d97706' if bias_pct > 60 else '#16a34a')
    ax.set_title(f'{name}\nDefault → {bias_pct:.0f}% Leave  |  Optimal → {r["leave_pct_optimal"]:.0f}% Leave',
                 fontsize=10, fontweight='bold', color=color_title)
    ax.set_xlabel('Predicted Probability', fontsize=10)
    ax.set_ylabel('Density', fontsize=10)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

plt.suptitle('Probability Distributions — Bias Diagnosis\n'
             'Red = was biased, Green = healthy distribution',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'bias_diagnosis_proba.png'), dpi=150)
plt.close()
print("   Saved → results/bias_diagnosis_proba.png")

# 6b. Confusion matrices (default vs optimal) for best model
best_name = max(all_results, key=lambda n: all_results[n]['auc'])
r = all_results[best_name]
fig, axes = plt.subplots(1, 2, figsize=(10, 4))

for ax, y_pred, label in [
    (axes[0], r['y_pred_default'], 'Default (0.5)'),
    (axes[1], r['y_pred_optimal'], f'Optimal ({r["opt_thresh"]})'),
]:
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Stay', 'Leave'], yticklabels=['Stay', 'Leave'],
                annot_kws={'size': 14})
    n_leave = int(y_pred.sum())
    pct = 100 * n_leave / max(len(y_pred), 1)
    acc = accuracy_score(y_test, y_pred)
    f1  = f1_score(y_test, y_pred, zero_division=0)
    ax.set_title(f'{best_name} [{label}]\n'
                 f'{pct:.0f}% Leave  Acc={acc:.3f}  F1={f1:.3f}',
                 fontsize=10, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')

plt.suptitle(f'Before vs After Threshold Fix — {best_name}',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'bias_diagnosis_confusion.png'), dpi=150)
plt.close()
print("   Saved → results/bias_diagnosis_confusion.png")

# 6c. Bar chart: before vs after Leave % per model
fig, ax = plt.subplots(figsize=(10, 5))
names  = list(all_results.keys())
before = [all_results[n]['leave_pct_default'] for n in names]
after  = [all_results[n]['leave_pct_optimal'] for n in names]
x = np.arange(len(names))
w = 0.35
b1 = ax.bar(x - w/2, before, w, label='Default (thresh=0.5)',
            color='#dc2626', alpha=0.8)
b2 = ax.bar(x + w/2, after,  w, label='Optimal Threshold',
            color='#16a34a', alpha=0.8)
ax.axhline(16, color='#000', linestyle='--', lw=1.5, alpha=0.7,
           label='IBM Real-World Attrition (~16%)')
ax.axhspan(10, 30, alpha=0.07, color='#16a34a', label='Healthy Range (10–30%)')
for bar in list(b1) + list(b2):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height():.0f}%', ha='center', va='bottom',
            fontsize=9, fontweight='600')
ax.set_xticks(x)
ax.set_xticklabels(names, fontsize=11)
ax.set_ylabel('% Predicted as Leave', fontsize=12)
ax.set_title('Before vs After — % Predicted Leave per Model',
             fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.set_ylim(0, max(max(before), max(after)) * 1.15)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'bias_diagnosis_before_after.png'), dpi=150)
plt.close()
print("   Saved → results/bias_diagnosis_before_after.png")

# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  ✅  Bias Diagnosis Complete!")
print("  Check results/ folder for plots.")
print("=" * 65)
