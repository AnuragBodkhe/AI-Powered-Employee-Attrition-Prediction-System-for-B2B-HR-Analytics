"""
eaps_ml_pipeline.py
====================
EAPS — Employee Attrition Prediction System
Full ML Training Pipeline — Supports IBM HR CSV + Custom CSVs

Trains 4 models on your datasets:
  1. Logistic Regression
  2. SVM (RBF kernel)
  3. Random Forest
  4. XGBoost

Also saves:
  models/label_encoders.pkl   — for decoding
  models/feature_names.pkl    — exact column order
  models/best_model_name.pkl  — fastest model lookup in app

Usage:
    python eaps_ml_pipeline.py

Outputs:
    models/*.pkl      (5 model files + 3 meta files)
    results/*.png     (6 plot files)
"""

import os, sys, warnings, joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, roc_auc_score, f1_score,
    precision_score, recall_score, roc_curve, confusion_matrix
)
from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
MODEL_DIR   = os.path.join(BASE_DIR, 'models')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 65)
print("  EAPS ML Pipeline — Employee Attrition Prediction System")
print("=" * 65)

# ── 1. Column name normalisation map ─────────────────────────────────────────
# Maps custom CSV column names → IBM-style column names
COLUMN_RENAME_MAP = {
    # Custom CSV → IBM standard
    'Employee_ID':                 'EmployeeNumber',
    'Marital_Status':              'MaritalStatus',
    'Job_Role':                    'JobRole',
    'Job_Level':                   'JobLevel',
    'Monthly_Income':              'MonthlyIncome',
    'Hourly_Rate':                 'HourlyRate',
    'Years_at_Company':            'YearsAtCompany',
    'Years_in_Current_Role':       'YearsInCurrentRole',
    'Years_Since_Last_Promotion':  'YearsSinceLastPromotion',
    'Work_Life_Balance':           'WorkLifeBalance',
    'Job_Satisfaction':            'JobSatisfaction',
    'Performance_Rating':          'PerformanceRating',
    'Training_Hours_Last_Year':    'TrainingTimesLastYear',
    'Work_Environment_Satisfaction': 'EnvironmentSatisfaction',
    'Relationship_with_Manager':   'RelationshipSatisfaction',
    'Job_Involvement':             'JobInvolvement',
    'Distance_From_Home':          'DistanceFromHome',
    'Number_of_Companies_Worked':  'NumCompaniesWorked',
    'Average_Hours_Worked_Per_Week': 'MonthlyRate',   # best proxy
    'Project_Count':               'StockOptionLevel', # best proxy
    'Absenteeism':                 'PercentSalaryHike', # best proxy
}

# Target columns to try (case-insensitive)
TARGET_CANDIDATES = ['Attrition', 'attrition', 'ATTRITION']

# Columns to always drop
DROP_COLS = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber',
             'Employee_ID', 'DailyRate', 'Overtime']  # 'Overtime' = duplicate of 'OverTime'

# Final 25 features we'll use (works across both CSV formats)
FINAL_FEATURES = [
    'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
    'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'WorkLifeBalance', 'JobSatisfaction',
    'PerformanceRating', 'TrainingTimesLastYear', 'EnvironmentSatisfaction',
    'RelationshipSatisfaction', 'JobInvolvement', 'DistanceFromHome',
    'NumCompaniesWorked', 'Gender', 'OverTime',
    'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
]


# ── 2. Load & normalise data ──────────────────────────────────────────────────
def load_and_normalise(filepath: str) -> pd.DataFrame | None:
    """Load a CSV and normalise its columns to IBM-style names."""
    if not os.path.exists(filepath):
        return None
    df = pd.read_csv(filepath)
    print(f"  Loaded {filepath.split(os.sep)[-1]}: {df.shape}")

    # Rename custom columns → IBM standard
    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)

    # Fix OverTime capitalisation (custom CSV uses 'Overtime')
    if 'Overtime' in df.columns and 'OverTime' not in df.columns:
        df.rename(columns={'Overtime': 'OverTime'}, inplace=True)

    # Add missing columns with sensible defaults
    defaults = {
        'BusinessTravel': 'Travel_Rarely',
        'DailyRate': 800,
        'Education': 3,
        'EducationField': 'Other',
        'StockOptionLevel': 0,
        'PercentSalaryHike': 14,
        'MonthlyRate': 14000,
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val

    # Find and standardise target
    target_col = None
    for cand in TARGET_CANDIDATES:
        if cand in df.columns:
            target_col = cand
            break
    if target_col is None:
        print(f"    ⚠️  No Attrition column found — skipping")
        return None

    df['Attrition'] = df[target_col].map(
        lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0
    )
    if target_col != 'Attrition':
        df.drop(columns=[target_col], inplace=True)

    print(f"    Attrition: Yes={df['Attrition'].sum()}, No={(df['Attrition']==0).sum()}")
    return df


print("\n📂 Loading datasets...")
frames = []
for fname in [
    'WA_Fn-UseC_-HR-Employee-Attrition.csv',
    'employee_attrition_dataset.csv',
    'employee_attrition_dataset_10000.csv',
]:
    df_loaded = load_and_normalise(os.path.join(DATA_DIR, fname))
    if df_loaded is not None:
        frames.append(df_loaded)

if not frames:
    print("\n❌ No datasets found in data/ folder!")
    print("   Place at least one CSV in data/ and re-run.")
    sys.exit(1)

df = pd.concat(frames, ignore_index=True)
print(f"\n✅ Combined dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ── 3. Preprocess ─────────────────────────────────────────────────────────────
print("\n🔧 Preprocessing...")

# Drop unwanted columns
for col in DROP_COLS:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# Keep only available final features
available = [f for f in FINAL_FEATURES if f in df.columns]
missing   = [f for f in FINAL_FEATURES if f not in df.columns]
if missing:
    print(f"   ⚠️  Missing features (will use defaults): {missing}")
    for m in missing:
        df[m] = 0

df = df[FINAL_FEATURES + ['Attrition']].copy()
df.dropna(subset=['Attrition'], inplace=True)
df.fillna(method='ffill', inplace=True)
df.fillna(0, inplace=True)

print(f"   Features used: {len(FINAL_FEATURES)}")
print(f"   Final shape:   {df.shape}")

# Save feature names for app use
joblib.dump(FINAL_FEATURES, os.path.join(MODEL_DIR, 'feature_names.pkl'))
print("   Saved → models/feature_names.pkl")

# Label-encode all object columns
label_encoders = {}
categorical_cols = df.select_dtypes(include='object').columns.tolist()
categorical_cols = [c for c in categorical_cols if c != 'Attrition']

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

joblib.dump(label_encoders, os.path.join(MODEL_DIR, 'label_encoders.pkl'))
print(f"   Encoded {len(categorical_cols)} categorical columns")
print("   Saved → models/label_encoders.pkl")

# ── 4. Train/test split ───────────────────────────────────────────────────────
X = df[FINAL_FEATURES]
y = df['Attrition']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n   Train: {len(X_train):,}  |  Test: {len(X_test):,}")
print(f"   Class balance (train): {dict(zip(*np.unique(y_train, return_counts=True)))}")

# ── 5. SMOTE balancing ────────────────────────────────────────────────────────
print("\n⚖️  Applying SMOTE...")
smote = SMOTE(random_state=42)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(f"   After SMOTE: {dict(zip(*np.unique(y_train_sm, return_counts=True)))}")

# Plot class balance
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, data, title in zip(axes,
    [y_train, pd.Series(y_train_sm)],
    ['Before SMOTE', 'After SMOTE']):
    counts = data.value_counts().sort_index()
    ax.bar(['No (Stay)', 'Yes (Leave)'], counts.values,
           color=['#4f46e5', '#dc2626'], alpha=0.85, edgecolor='white')
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_ylabel('Count')
    for i, v in enumerate(counts.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='600')
plt.suptitle('SMOTE Class Balancing', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'smote_class_balance.png'), dpi=150)
plt.close()

# ── 6. Scale for LR & SVM ────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_sm)
X_test_scaled  = scaler.transform(X_test)
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
print("\n   Saved → models/scaler.pkl")

# ── 7. Train all models ───────────────────────────────────────────────────────
print("\n🤖 Training models...\n")

MODEL_CONFIGS = {
    'Logistic Regression': (
        LogisticRegression(max_iter=2000, random_state=42, C=1.0),
        X_train_scaled, X_test_scaled, 'logistic_regression.pkl'
    ),
    'SVM': (
        SVC(kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42),
        X_train_scaled, X_test_scaled, 'svm.pkl'
    ),
    'Random Forest': (
        RandomForestClassifier(n_estimators=200, max_depth=None,
                               min_samples_leaf=2, random_state=42, n_jobs=-1),
        X_train_sm, X_test, 'random_forest.pkl'
    ),
    'XGBoost': (
        XGBClassifier(n_estimators=200, learning_rate=0.1, max_depth=6,
                      use_label_encoder=False, eval_metric='logloss',
                      random_state=42, n_jobs=-1, verbosity=0),
        X_train_sm, X_test, 'xgboost.pkl'
    ),
}

RESULTS     = {}
trained     = {}

for name, (clf, Xtr, Xte, fname) in MODEL_CONFIGS.items():
    print(f"  ▶ Training {name}...")
    clf.fit(Xtr, y_train_sm)
    y_pred  = clf.predict(Xte)
    y_proba = clf.predict_proba(Xte)[:, 1]

    RESULTS[name] = {
        'Accuracy':  round(accuracy_score(y_test, y_pred), 4),
        'AUC-ROC':   round(roc_auc_score(y_test, y_proba), 4),
        'F1':        round(f1_score(y_test, y_pred), 4),
        'Precision': round(precision_score(y_test, y_pred), 4),
        'Recall':    round(recall_score(y_test, y_pred), 4),
    }
    trained[name] = (clf, Xte, y_proba)
    joblib.dump(clf, os.path.join(MODEL_DIR, fname))
    r = RESULTS[name]
    print(f"    Acc={r['Accuracy']}  AUC={r['AUC-ROC']}  "
          f"F1={r['F1']}  Prec={r['Precision']}  Rec={r['Recall']}")
    print(f"    Saved → models/{fname}")

# Save best model name for fast app lookup
best_model = max(RESULTS, key=lambda m: RESULTS[m]['AUC-ROC'])
joblib.dump(best_model, os.path.join(MODEL_DIR, 'best_model_name.pkl'))

# ── 8. Results summary ────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  FINAL RESULTS SUMMARY")
print("=" * 65)
df_results = pd.DataFrame(RESULTS).T
print(df_results.to_string())
print(f"\n🏆 Best model: {best_model} (AUC-ROC={RESULTS[best_model]['AUC-ROC']})")

# ── 9. ROC curves ─────────────────────────────────────────────────────────────
print("\n📊 Generating plots...")
colors_map = {
    'Logistic Regression': '#4f46e5',
    'SVM':                 '#0891b2',
    'Random Forest':       '#16a34a',
    'XGBoost':             '#dc2626',
}

fig, ax = plt.subplots(figsize=(8, 6))
for name, (clf, Xte, y_proba) in trained.items():
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = RESULTS[name]['AUC-ROC']
    ax.plot(fpr, tpr, color=colors_map[name], lw=2.5,
            label=f'{name} (AUC={auc})')
ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curves — All Models', fontsize=14, fontweight='bold')
ax.legend(loc='lower right', fontsize=10, framealpha=0.9)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'roc_curves.png'), dpi=150)
plt.close()
print("   Saved → results/roc_curves.png")

# ── 10. Confusion matrices ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(18, 4))
for ax, (name, (clf, Xte, y_proba)) in zip(axes, trained.items()):
    y_pred = clf.predict(Xte)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Stay', 'Leave'], yticklabels=['Stay', 'Leave'],
                annot_kws={'size': 13})
    ax.set_title(name, fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
plt.suptitle('Confusion Matrices — All Models', fontsize=13,
             fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrices.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("   Saved → results/confusion_matrices.png")

# ── 11. Model comparison bar chart ───────────────────────────────────────────
df_bar   = pd.DataFrame(RESULTS).T.reset_index().rename(columns={'index': 'Model'})
df_melt  = df_bar.melt(id_vars='Model', var_name='Metric', value_name='Score')
metrics  = ['Accuracy', 'AUC-ROC', 'F1', 'Precision', 'Recall']
m_colors = ['#4f46e5', '#0891b2', '#16a34a', '#dc2626', '#d97706']

fig, ax = plt.subplots(figsize=(13, 5))
model_names = list(RESULTS.keys())
x = np.arange(len(model_names))
width = 0.15

for i, (metric, color) in enumerate(zip(metrics, m_colors)):
    vals = [RESULTS[m][metric] for m in model_names]
    bars = ax.bar(x + i * width, vals, width, label=metric,
                  color=color, alpha=0.85, edgecolor='white')
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                f'{bar.get_height():.3f}', ha='center', va='bottom',
                fontsize=7, fontweight='600')

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Model Comparison — All Metrics', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 2)
ax.set_xticklabels(model_names, fontsize=11)
ax.set_ylim(0.5, 1.08)
ax.legend(fontsize=10, loc='lower right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'model_comparison.png'), dpi=150)
plt.close()
print("   Saved → results/model_comparison.png")

# ── 12. Feature importance plots ─────────────────────────────────────────────
for mname, fsuffix in [('Random Forest', 'random_forest'), ('XGBoost', 'xgboost')]:
    clf = trained[mname][0]
    imp = pd.Series(clf.feature_importances_, index=FINAL_FEATURES)
    imp = imp.sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    colors_feat = ['#dc2626' if v > imp.median() else '#4f46e5' for v in imp.values]
    ax.barh(imp.index, imp.values, color=colors_feat, edgecolor='none', alpha=0.85)
    ax.set_xlabel('Feature Importance', fontsize=12)
    ax.set_title(f'{mname} — Feature Importances ({len(FINAL_FEATURES)} features)',
                 fontsize=13, fontweight='bold')
    ax.axvline(imp.median(), color='gray', linestyle='--', lw=1, alpha=0.7,
               label='Median')
    ax.legend(fontsize=10)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, f'feature_importance_{fsuffix}.png'), dpi=150)
    plt.close()
    print(f"   Saved → results/feature_importance_{fsuffix}.png")

# ── Done ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  ✅  Pipeline complete!")
print(f"  🏆  Best model: {best_model} (AUC={RESULTS[best_model]['AUC-ROC']})")
print("\n  Files saved:")
print("  models/ → random_forest.pkl  xgboost.pkl  logistic_regression.pkl")
print("            svm.pkl  scaler.pkl  label_encoders.pkl")
print("            feature_names.pkl   best_model_name.pkl")
print("  results/ → roc_curves.png  confusion_matrices.png")
print("             model_comparison.png  feature_importance_*.png")
print("             smote_class_balance.png")
print("\n  Launch the app:")
print("    streamlit run app.py")
print("=" * 65)
