"""
eaps_ml_pipeline.py
====================
EAPS — Employee Attrition Prediction System
Full ML Training Pipeline — Supports IBM HR CSV + Custom CSVs

Trains 4 models on your datasets:
  1. Logistic Regression
  2. SVM (RBF kernel)
  3. Random Forest    (class_weight='balanced' + isotonic calibration)
  4. XGBoost          (scale_pos_weight + isotonic calibration)

Also saves:
  models/label_encoders.pkl   — for decoding at inference time
  models/feature_names.pkl    — exact column order
  models/best_model_name.pkl  — fastest model lookup in app
  models/threshold.pkl        — per-model optimal thresholds (Youden's J)
  models/class_ratio.pkl      — training class imbalance ratio

Usage:
    python eaps_ml_pipeline.py

Outputs:
    models/*.pkl      (8 model/meta files)
    results/*.png     (7 plot files)
"""

import os, sys, warnings, joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, roc_auc_score, f1_score,
    precision_score, recall_score, roc_curve, confusion_matrix,
    classification_report
)

warnings.filterwarnings('ignore')

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
MODEL_DIR   = os.path.join(BASE_DIR, 'models')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 65)
print("  EAPS ML Pipeline - Employee Attrition Prediction System")
print("  [Debiased Version: class_weight + calibration + threshold]")
print("=" * 65)

# ── 1. Column name normalisation map ─────────────────────────────────────────
# Maps custom CSV column names → IBM-style column names
COLUMN_RENAME_MAP = {
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
    'Average_Hours_Worked_Per_Week': 'MonthlyRate',
    'Project_Count':               'StockOptionLevel',
    'Absenteeism':                 'PercentSalaryHike',
}

TARGET_CANDIDATES = ['Attrition', 'attrition', 'ATTRITION']

DROP_COLS = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber',
             'Employee_ID', 'DailyRate', 'Overtime']

# Final 25 features used across both CSV formats
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

    df.rename(columns=COLUMN_RENAME_MAP, inplace=True)

    if 'Overtime' in df.columns and 'OverTime' not in df.columns:
        df.rename(columns={'Overtime': 'OverTime'}, inplace=True)

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

    target_col = None
    for cand in TARGET_CANDIDATES:
        if cand in df.columns:
            target_col = cand
            break
    if target_col is None:
        print(f"    [WARN] No Attrition column found - skipping")
        return None

    df['Attrition'] = df[target_col].map(
        lambda x: 1 if str(x).strip().lower() in ['yes', '1', 'true'] else 0
    )
    if target_col != 'Attrition':
        df.drop(columns=[target_col], inplace=True)

    yes_count = df['Attrition'].sum()
    no_count  = (df['Attrition'] == 0).sum()
    print(f"    Attrition: Yes={yes_count}, No={no_count}  "
          f"(ratio {no_count/max(yes_count,1):.1f}:1)")
    return df


print("\n>> Loading datasets...")
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
    sys.exit(1)

df = pd.concat(frames, ignore_index=True)
print(f"\n[OK] Combined dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")

total_yes = df['Attrition'].sum()
total_no  = (df['Attrition'] == 0).sum()
class_ratio = total_no / max(total_yes, 1)
print(f"   Overall class ratio  No:Yes = {total_no}:{total_yes} = {class_ratio:.2f}:1")

# ── 3. Preprocess ─────────────────────────────────────────────────────────────
print("\n>> Preprocessing...")

for col in DROP_COLS:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

available = [f for f in FINAL_FEATURES if f in df.columns]
missing   = [f for f in FINAL_FEATURES if f not in df.columns]
if missing:
    print(f"   [WARN] Missing features (will use defaults): {missing}")
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

# Label-encode all object columns — save encoders for consistent inference
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

# Save class ratio for scale_pos_weight
joblib.dump(class_ratio, os.path.join(MODEL_DIR, 'class_ratio.pkl'))
print(f"   Saved → models/class_ratio.pkl  (ratio={class_ratio:.2f})")

# ── 4. Stratified Train/Test split ────────────────────────────────────────────
X = df[FINAL_FEATURES]
y = df['Attrition']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n   Train: {len(X_train):,}  |  Test: {len(X_test):,}")
train_dist = dict(zip(*np.unique(y_train, return_counts=True)))
print(f"   Class balance (train — before balancing): {train_dist}")
print(f"   No:Yes ratio = {train_dist.get(0,0)}:{train_dist.get(1,0)}")

# ── 5. Scale for LR & SVM ───────────────────────────────────────────────────
print("\n>> Fitting scaler on raw (unbalanced) train data...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
print("   Saved → models/scaler.pkl")

# ── 6. Class balance plot (no SMOTE — using class weights instead) ───────────
fig, ax = plt.subplots(figsize=(6, 4))
counts = y_train.value_counts().sort_index()
ax.bar(['No (Stay)', 'Yes (Leave)'], counts.values,
       color=['#4f46e5', '#dc2626'], alpha=0.85, edgecolor='white')
ax.set_title('Training Class Distribution (class_weight handles imbalance)',
             fontsize=12, fontweight='bold')
ax.set_ylabel('Count')
for i, v in enumerate(counts.values):
    ax.text(i, v + 5, str(v), ha='center', fontweight='600')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'smote_class_balance.png'), dpi=150)
plt.close()

# ── 7. Train all models ───────────────────────────────────────────────────────
print("\n>> Training models (with bias mitigations)...\n")

# XGBoost scale_pos_weight automatically handles imbalance
xgb_spw = min(class_ratio, 10.0)  # cap at 10 to avoid over-correction

MODEL_CONFIGS = {
    'Logistic Regression': (
        LogisticRegression(max_iter=2000, random_state=42, C=1.0,
                           class_weight='balanced'),
        X_train_scaled, X_test_scaled, X_train, 'logistic_regression.pkl'
    ),
    'SVM': (
        SVC(kernel='rbf', C=1.0, gamma='scale', probability=True,
            random_state=42, class_weight='balanced'),
        X_train_scaled, X_test_scaled, X_train, 'svm.pkl'
    ),
    'Random Forest': (
        RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=4,
            min_samples_split=10,
            class_weight='balanced_subsample',
            random_state=42,
            n_jobs=-1,
        ),
        X_train, X_test, X_train, 'random_forest.pkl'
    ),
    'XGBoost': (
        XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=xgb_spw,
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1,
            verbosity=0,
        ),
        X_train, X_test, X_train, 'xgboost.pkl'
    ),
}

RESULTS  = {}
trained  = {}
thresholds = {}

for name, (clf, Xtr, Xte, Xtr_raw, fname) in MODEL_CONFIGS.items():
    print(f"  ▶ Training {name}...")

    # Train base model
    clf.fit(Xtr, y_train)

    # ── Isotonic probability calibration (tree/SVM) ────────────────────────
    # Skip calibration for LR — it's already well-calibrated via logistic link
    if name in ('Random Forest', 'XGBoost'):
        print(f"    Calibrating probabilities (isotonic)...")
        calibrated = CalibratedClassifierCV(clf, method='isotonic', cv=3)
        calibrated.fit(Xtr, y_train)
        clf_final = calibrated
    else:
        clf_final = clf

    # Predict probabilities on test set
    y_proba = clf_final.predict_proba(Xte)[:, 1]

    # ── Find optimal threshold via Youden's J ─────────────────────────────
    fpr, tpr, thresh_vals = roc_curve(y_test, y_proba)
    j_scores = tpr - fpr
    best_idx  = np.argmax(j_scores)
    opt_thresh = float(thresh_vals[best_idx])
    opt_thresh = round(max(0.20, min(0.65, opt_thresh)), 4)  # clamp to sane range
    thresholds[name] = opt_thresh

    # Use optimal threshold for predictions
    y_pred = (y_proba >= opt_thresh).astype(int)

    RESULTS[name] = {
        'Accuracy':   round(accuracy_score(y_test, y_pred), 4),
        'AUC-ROC':    round(roc_auc_score(y_test, y_proba), 4),
        'F1':         round(f1_score(y_test, y_pred, zero_division=0), 4),
        'Precision':  round(precision_score(y_test, y_pred, zero_division=0), 4),
        'Recall':     round(recall_score(y_test, y_pred, zero_division=0), 4),
        'Threshold':  opt_thresh,
    }
    trained[name] = (clf_final, Xte, y_proba)
    joblib.dump(clf_final, os.path.join(MODEL_DIR, fname))

    r = RESULTS[name]
    print(f"    Threshold={opt_thresh}  Acc={r['Accuracy']}  AUC={r['AUC-ROC']}  "
          f"F1={r['F1']}  Prec={r['Precision']}  Rec={r['Recall']}")

    # ── Bias check ────────────────────────────────────────────────────────
    n_leave = int(y_pred.sum())
    n_stay  = len(y_pred) - n_leave
    pct_leave = 100 * n_leave / max(len(y_pred), 1)
    print(f"    Prediction dist → Stay={n_stay}  Leave={n_leave}  "
          f"({pct_leave:.1f}% Leave)")
    if pct_leave > 85:
        print(f"    [WARN] Model still heavily biased ({pct_leave:.1f}% Leave)!")
    elif pct_leave < 5:
        print(f"    [WARN] Model predicts almost no leavers ({pct_leave:.1f}%)!")
    else:
        print(f"    [OK]  Prediction distribution looks healthy")

    print(f"    Saved → models/{fname}")

# Save thresholds and best model name
joblib.dump(thresholds, os.path.join(MODEL_DIR, 'threshold.pkl'))
print(f"\n   Saved → models/threshold.pkl  {thresholds}")

best_model = max(RESULTS, key=lambda m: RESULTS[m]['AUC-ROC'])
joblib.dump(best_model, os.path.join(MODEL_DIR, 'best_model_name.pkl'))

# ── 8. Results summary ────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  FINAL RESULTS SUMMARY")
print("=" * 65)

df_results = pd.DataFrame(RESULTS).T
print(df_results.to_string())
print(f"\n[BEST] Best model: {best_model} (AUC-ROC={RESULTS[best_model]['AUC-ROC']})")

# ── 9. Classification reports ─────────────────────────────────────────────────
print("\n>> Classification Reports (with optimal thresholds):\n")
for name, (clf_final, Xte, y_proba) in trained.items():
    thresh = thresholds[name]
    y_pred = (y_proba >= thresh).astype(int)
    print(f"  [{name}]  threshold={thresh}")
    print(classification_report(y_test, y_pred,
                                 target_names=['Stay (0)', 'Leave (1)'],
                                 zero_division=0))

# ── 10. ROC curves ────────────────────────────────────────────────────────────
print("\n>> Generating plots...")
colors_map = {
    'Logistic Regression': '#4f46e5',
    'SVM':                 '#0891b2',
    'Random Forest':       '#16a34a',
    'XGBoost':             '#dc2626',
}

fig, ax = plt.subplots(figsize=(8, 6))
for name, (clf_final, Xte, y_proba) in trained.items():
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

# ── 11. Confusion matrices ────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 4, figsize=(18, 4))
for ax, (name, (clf_final, Xte, y_proba)) in zip(axes, trained.items()):
    thresh = thresholds[name]
    y_pred = (y_proba >= thresh).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Stay', 'Leave'], yticklabels=['Stay', 'Leave'],
                annot_kws={'size': 13})
    ax.set_title(f'{name}\n(thresh={thresh})', fontsize=10, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
plt.suptitle('Confusion Matrices — Optimal Thresholds', fontsize=13,
             fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrices.png'),
            dpi=150, bbox_inches='tight')
plt.close()
print("   Saved → results/confusion_matrices.png")

# ── 12. Model comparison bar chart ───────────────────────────────────────────
df_bar   = pd.DataFrame(RESULTS).T.reset_index().rename(columns={'index': 'Model'})
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
ax.set_title('Model Comparison — All Metrics (Debiased)', fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 2)
ax.set_xticklabels(model_names, fontsize=11)
ax.set_ylim(0.4, 1.08)
ax.legend(fontsize=10, loc='lower right')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'model_comparison.png'), dpi=150)
plt.close()
print("   Saved → results/model_comparison.png")

# ── 13. Probability distribution plot ────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()
for idx, (name, (clf_final, Xte, y_proba)) in enumerate(trained.items()):
    thresh = thresholds[name]
    ax = axes[idx]
    ax.hist(y_proba[y_test == 0], bins=40, alpha=0.7, color='#4f46e5',
            label='Actual Stay', density=True)
    ax.hist(y_proba[y_test == 1], bins=40, alpha=0.7, color='#dc2626',
            label='Actual Leave', density=True)
    ax.axvline(thresh, color='black', linestyle='--', lw=2,
               label=f'Threshold={thresh}')
    ax.set_title(f'{name}', fontsize=11, fontweight='bold')
    ax.set_xlabel('Predicted Probability')
    ax.set_ylabel('Density')
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
plt.suptitle('Probability Distributions — Stay vs Leave', fontsize=13,
             fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'probability_distributions.png'), dpi=150)
plt.close()
print("   Saved → results/probability_distributions.png")

# ── 14. Feature importance plots ─────────────────────────────────────────────
for mname, fsuffix in [('Random Forest', 'random_forest'), ('XGBoost', 'xgboost')]:
    clf_final = trained[mname][0]
    # CalibratedClassifierCV wraps the base estimator
    base_clf = clf_final.estimator if hasattr(clf_final, 'estimator') else clf_final
    if hasattr(base_clf, 'calibrated_classifiers_'):
        # Get importances from the first fold's base estimator
        base_clf = base_clf.calibrated_classifiers_[0].estimator

    if not hasattr(base_clf, 'feature_importances_'):
        print(f"   [WARN] {mname}: feature importances not available after calibration")
        continue

    imp = pd.Series(base_clf.feature_importances_, index=FINAL_FEATURES)
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
print("  [DONE] Pipeline complete!")
print(f"  [BEST] Best model: {best_model} (AUC={RESULTS[best_model]['AUC-ROC']})")
print("\n  Files saved:")
print("  models/ -> random_forest.pkl  xgboost.pkl  logistic_regression.pkl")
print("            svm.pkl  scaler.pkl  label_encoders.pkl")
print("            feature_names.pkl  best_model_name.pkl")
print("            threshold.pkl  class_ratio.pkl")
print("  results/ -> roc_curves.png  confusion_matrices.png")
print("             model_comparison.png  feature_importance_*.png")
print("             probability_distributions.png")
print("             smote_class_balance.png")
print("\n  Launch the app:")
print("    python flask_app/server.py")
print("=" * 65)
