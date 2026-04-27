"""
train_xgboost_v3.py  —  EAPS XGBoost v3
========================================
Fixes over v2:
  1. Composite features: SatisfactionIndex, TenureRatio, CompensationGap
  2. SMOTE on training set only
  3. Platt Scaling (manual sigmoid calibration on val set)
  4. Threshold chosen by Youden's J (maximises recall+specificity)
  5. 5-fold stratified cross-validation
  6. IBM HR dataset only (clean, well-labelled)

Run:  python train_xgboost_v3.py
"""

import os, sys, io, warnings, joblib
import numpy as np
import pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Windows-safe UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Add project root to path so utils/ is importable
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.calibrated_xgb import CalibratedXGB

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing   import LabelEncoder, StandardScaler
from sklearn.linear_model    import LogisticRegression
from sklearn.metrics import (accuracy_score, roc_auc_score, f1_score,
                              precision_score, recall_score, confusion_matrix,
                              classification_report, roc_curve)
from imblearn.over_sampling  import SMOTE
from xgboost                 import XGBClassifier

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, 'data')
MODEL_DIR   = os.path.join(BASE_DIR, 'models')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
os.makedirs(MODEL_DIR,   exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

print("=" * 65)
print("  EAPS XGBoost v3  [SMOTE + Platt + Youden-J threshold]")
print("=" * 65)

# ── 1. Load datasets ─────────────────────────────────────────────────────────
COL_RENAME = {
    'Employee_ID':'EmployeeNumber','Marital_Status':'MaritalStatus',
    'Job_Role':'JobRole','Job_Level':'JobLevel','Monthly_Income':'MonthlyIncome',
    'Hourly_Rate':'HourlyRate','Years_at_Company':'YearsAtCompany',
    'Years_in_Current_Role':'YearsInCurrentRole',
    'Years_Since_Last_Promotion':'YearsSinceLastPromotion',
    'Work_Life_Balance':'WorkLifeBalance','Job_Satisfaction':'JobSatisfaction',
    'Performance_Rating':'PerformanceRating',
    'Training_Hours_Last_Year':'TrainingTimesLastYear',
    'Work_Environment_Satisfaction':'EnvironmentSatisfaction',
    'Relationship_with_Manager':'RelationshipSatisfaction',
    'Job_Involvement':'JobInvolvement','Distance_From_Home':'DistanceFromHome',
    'Number_of_Companies_Worked':'NumCompaniesWorked',
    'Average_Hours_Worked_Per_Week':'MonthlyRate',
    'Project_Count':'StockOptionLevel','Absenteeism':'PercentSalaryHike',
}

def load_csv(path):
    if not os.path.exists(path): return None
    d = pd.read_csv(path).rename(columns=COL_RENAME)
    if 'Overtime' in d.columns and 'OverTime' not in d.columns:
        d.rename(columns={'Overtime':'OverTime'}, inplace=True)
    for col,val in [('BusinessTravel','Travel_Rarely'),('StockOptionLevel',0),
                    ('PercentSalaryHike',14),('MonthlyRate',14000),
                    ('TotalWorkingYears',10),('NumCompaniesWorked',3)]:
        if col not in d.columns: d[col] = val
    for cand in ['Attrition','attrition','ATTRITION']:
        if cand in d.columns:
            d['Attrition'] = d[cand].map(
                lambda x: 1 if str(x).strip().lower() in ['yes','1','true'] else 0)
            if cand != 'Attrition': d.drop(columns=[cand], inplace=True)
            break
    return d if 'Attrition' in d.columns else None

frames = []
for fn in ['WA_Fn-UseC_-HR-Employee-Attrition.csv']:
    d = load_csv(os.path.join(DATA_DIR, fn))
    if d is not None:
        frames.append(d)
        print(f"   Loaded {fn}: {d.shape}  Yes={d['Attrition'].sum()}")

if not frames: print("ERROR: no datasets found"); sys.exit(1)
df = pd.concat(frames, ignore_index=True)
print(f"\n>> Dataset: {df.shape[0]} rows, Yes={df['Attrition'].sum()}, No={(df['Attrition']==0).sum()}")

# Drop irrelevant columns
for col in ['EmployeeNumber','Over18','StandardHours','EmployeeCount',
            'Employee_ID','DailyRate']:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# ── 3. Composite features (before split) ─────────────────────────────────────
print("\n>> Engineering composite features...")
for c in ['JobSatisfaction','EnvironmentSatisfaction',
          'RelationshipSatisfaction','WorkLifeBalance',
          'YearsAtCompany','TotalWorkingYears','MonthlyIncome','JobLevel']:
    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

df['SatisfactionIndex'] = df[['JobSatisfaction','EnvironmentSatisfaction',
                               'RelationshipSatisfaction','WorkLifeBalance']].mean(axis=1)
df['TenureRatio']       = df['YearsAtCompany'] / (df['TotalWorkingYears'] + 1)
df['CompensationGap']   = df['MonthlyIncome']  / (df['JobLevel'] * 1000 + 1e-9)
print("   Created: SatisfactionIndex, TenureRatio, CompensationGap")

# ── 4. Feature list ───────────────────────────────────────────────────────────
FEATURES = [
    'Age','MaritalStatus','Department','JobRole','JobLevel',
    'MonthlyIncome','HourlyRate','YearsAtCompany','YearsInCurrentRole',
    'YearsSinceLastPromotion','TotalWorkingYears','WorkLifeBalance',
    'JobSatisfaction','PerformanceRating','TrainingTimesLastYear',
    'EnvironmentSatisfaction','RelationshipSatisfaction','JobInvolvement',
    'DistanceFromHome','NumCompaniesWorked','Gender','OverTime',
    'MonthlyRate','StockOptionLevel','PercentSalaryHike','BusinessTravel',
    'SatisfactionIndex','TenureRatio','CompensationGap',
]
for f in FEATURES:
    if f not in df.columns:
        df[f] = 0

df = df[FEATURES + ['Attrition']].copy()
df.ffill(inplace=True); df.fillna(0, inplace=True)
print(f"   Final features: {len(FEATURES)}, rows: {len(df)}")

# ── 5. Label-encode categoricals ─────────────────────────────────────────────
print("\n>> Encoding categoricals...")
label_encoders = {}
for col in df.select_dtypes(include='object').columns:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le
joblib.dump(label_encoders, os.path.join(MODEL_DIR, 'label_encoders_v3.pkl'))
print(f"   Encoded {len(label_encoders)} columns")

# ── 6. Split: 70% train | 15% val | 15% test ─────────────────────────────────
X = df[FEATURES].values
y = df['Attrition'].values

X_tv, X_test, y_tv, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42, stratify=y)
X_train, X_val, y_train, y_val = train_test_split(
    X_tv, y_tv, test_size=0.176, random_state=42, stratify=y_tv)

print(f"\n   Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
print(f"   Train class dist: {dict(zip(*np.unique(y_train, return_counts=True)))}")

# ── 7. Scale ──────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_val_sc   = scaler.transform(X_val)
X_test_sc  = scaler.transform(X_test)
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler_v3.pkl'))
joblib.dump(FEATURES, os.path.join(MODEL_DIR, 'feature_names_v3.pkl'))

# ── 8. SMOTE (training only) ──────────────────────────────────────────────────
print("\n>> Applying SMOTE to training set only...")
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X_train_sc, y_train)
print(f"   Before: {dict(zip(*np.unique(y_train, return_counts=True)))}")
print(f"   After : {dict(zip(*np.unique(y_res, return_counts=True)))}")

# Plot
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
for ax, counts, title in zip(axes,
        [dict(zip(*np.unique(y_train, return_counts=True))),
         dict(zip(*np.unique(y_res, return_counts=True)))],
        ['Before SMOTE', 'After SMOTE']):
    ax.bar(['Stay','Leave'], [counts.get(0,0), counts.get(1,0)],
           color=['#4f46e5','#dc2626'], alpha=0.85)
    ax.set_title(title, fontweight='bold')
    ax.set_ylabel('Count')
plt.suptitle('SMOTE Class Balancing', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'smote_class_balance_v3.png'), dpi=150)
plt.close()

# ── 9. Hyperparameter-tuned XGBoost ─────────────────────────────────────────
print("\n>> Tuning XGBoost v3 (RandomizedSearchCV, 40 iterations)...")
param_dist = {
    'n_estimators':     [200, 300, 400, 500],
    'max_depth':        [3, 4, 5, 6],
    'learning_rate':    [0.01, 0.03, 0.05, 0.07, 0.1],
    'subsample':        [0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.6, 0.7, 0.8, 0.9],
    'min_child_weight': [1, 3, 5, 7],
    'gamma':            [0, 0.1, 0.2, 0.5],
    'reg_alpha':        [0, 0.01, 0.1, 0.5],
    'reg_lambda':       [1, 1.5, 2, 3],
}
base_xgb = XGBClassifier(
    scale_pos_weight=1, eval_metric='logloss',
    random_state=42, n_jobs=-1, verbosity=0)
cv_inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
search = RandomizedSearchCV(
    base_xgb, param_dist, n_iter=40, cv=cv_inner,
    scoring='f1', n_jobs=-1, random_state=42, verbose=0)
search.fit(X_res, y_res)
model = search.best_estimator_
print(f"   Best CV F1 (inner 3-fold): {search.best_score_:.3f}")
print(f"   Best params: {search.best_params_}")

# ── 10. Platt Scaling on validation set ───────────────────────────────────────
print("\n>> Platt Scaling calibration (val set)...")
raw_val = model.predict_proba(X_val_sc)[:, 1].reshape(-1, 1)
platt   = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
platt.fit(raw_val, y_val)

def calibrated_proba(X_scaled):
    raw = model.predict_proba(X_scaled)[:, 1].reshape(-1, 1)
    return platt.predict_proba(raw)[:, 1]

print("   Calibration done.")

# ── 11. Threshold via Youden's J on validation set ────────────────────────────
val_probs = calibrated_proba(X_val_sc)
fpr_v, tpr_v, thresh_v = roc_curve(y_val, val_probs)
j_scores  = tpr_v - fpr_v
best_idx  = np.argmax(j_scores)
JOUDEN_T  = float(thresh_v[best_idx])

# Also find threshold that gives recall >= 0.75 on val set with best F1
best_f1, RECALL_T = 0.0, JOUDEN_T
for t in np.arange(0.05, 0.50, 0.005):
    vp = (val_probs >= t).astype(int)
    r  = recall_score(y_val, vp, zero_division=0)
    f  = f1_score(y_val, vp, zero_division=0)
    if r >= 0.75 and f > best_f1:
        best_f1, RECALL_T = f, t

# Prefer recall-optimised threshold; fall back to Youden-J clamped
if best_f1 > 0:
    THRESHOLD = float(RECALL_T)
    print(f"\n   Recall-priority threshold  = {THRESHOLD:.4f}  (val recall>0.75, F1={best_f1:.3f})")
else:
    THRESHOLD = float(np.clip(JOUDEN_T, 0.12, 0.35))
    print(f"\n   Youden-J threshold (clamped) = {THRESHOLD:.4f}")

# ── 12. Evaluate on test set ──────────────────────────────────────────────────
probs  = calibrated_proba(X_test_sc)
y_pred = (probs >= THRESHOLD).astype(int)

acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, zero_division=0)
rec  = recall_score(y_test, y_pred, zero_division=0)
f1   = f1_score(y_test, y_pred, zero_division=0)
auc  = roc_auc_score(y_test, probs)
cm   = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

unique_p   = len(np.unique(np.round(probs, 4)))
hi_risk_tp = int(np.sum((probs >= 0.5) & (y_test == 1)))
n_leave    = int(y_test.sum())

# ── 13. Cross-validation (base model, full dataset) ───────────────────────────
print("\n>> 5-fold stratified cross-validation (recall)...")
X_all_sc = scaler.transform(X)
cv       = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_rec   = cross_val_score(model, X_all_sc, y, cv=cv, scoring='recall')
cv_f1    = cross_val_score(model, X_all_sc, y, cv=cv, scoring='f1')
print(f"   CV Recall : {np.round(cv_rec,3)}  mean={cv_rec.mean():.3f}")
print(f"   CV F1     : {np.round(cv_f1,3)}  mean={cv_f1.mean():.3f}")

# ── 14. Dashboard validation ──────────────────────────────────────────────────
print("\n>> Dashboard Validation...")
df_test = df.iloc[
    np.where(np.isin(np.arange(len(df)),
             np.where(np.isin(np.arange(len(df)),
                      np.arange(len(df))[-(len(X_test)+len(X_val)):]
             ))[0][-len(X_test):]
    ))[0]
].copy() if False else pd.DataFrame()

# Simpler: reconstruct via index tracking
idx_tv, idx_test = train_test_split(
    np.arange(len(df)), test_size=0.15, random_state=42,
    stratify=df['Attrition'].values)
idx_train, idx_val = train_test_split(
    idx_tv, test_size=0.176, random_state=42,
    stratify=df['Attrition'].values[idx_tv])

df_test_view = df.iloc[idx_test].copy()
df_test_view['PredAttrition'] = y_pred
df_test_view['Probability']   = probs

total_pred_leave = int(y_pred.sum())
attr_rate_pct    = 100.0 * total_pred_leave / len(y_pred)

# Decode dept / role
dept_enc = label_encoders.get('Department')
role_enc = label_encoders.get('JobRole')

dept_rates = df_test_view.groupby('Department')['PredAttrition'].mean() * 100
if dept_enc is not None:
    dept_rates.index = dept_enc.inverse_transform(dept_rates.index.astype(int))
print("\n   Department Attrition Rates (predicted):")
for d, r in dept_rates.sort_values(ascending=False).items():
    print(f"     {d:<30} {r:.1f}%")

role_avg = df_test_view.groupby('JobRole')['Probability'].mean()
if role_enc is not None:
    role_avg.index = role_enc.inverse_transform(role_avg.index.astype(int))
print(f"\n   Top risk role: {role_avg.idxmax()}")

inc_leave  = df_test_view[df_test_view['PredAttrition']==1]['MonthlyIncome'].mean()
inc_stay   = df_test_view[df_test_view['PredAttrition']==0]['MonthlyIncome'].mean()
print(f"   Avg Income Leavers={inc_leave:,.0f}  Stayers={inc_stay:,.0f}")
print(f"   {'[OK] Leavers earn less' if inc_leave < inc_stay else '[WARN] Leavers earn more'}")

# ── 15. Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  EAPS XGBoost v3 -- Results")
print("=" * 60)
print(f"  Accuracy  : {acc*100:.1f}%")
print(f"  Precision : {prec*100:.1f}%")
print(f"  Recall    : {rec*100:.1f}%   <- target > 75%")
print(f"  F1 Score  : {f1*100:.1f}%   <- target > 72%")
print(f"  ROC-AUC   : {auc*100:.1f}%")
print(f"  Threshold : {THRESHOLD:.4f} (Youden-J)")
print(f"  Unique Probabilities : {unique_p} (out of {len(y_test)})")
print(f"  High-Risk Detected   : {hi_risk_tp} / {n_leave}")
print(f"\n  Confusion Matrix:")
print(f"                    Predicted Stay   Predicted Leave")
print(f"  Actual Stay       {tn:<16} {fp}")
print(f"  Actual Leave      {fn:<16} {tp}")
print("=" * 60)
print(f"  Total Predicted Leave   : {total_pred_leave}")
print(f"  Predicted Attrition Rate: {attr_rate_pct:.1f}%")
print(f"  Mean CV Recall (5-fold) : {cv_rec.mean()*100:.1f}%")
print(f"  Mean CV F1     (5-fold) : {cv_f1.mean()*100:.1f}%")
print("=" * 60)

print("\n>> Full Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=['Stay (0)', 'Leave (1)'], zero_division=0))

# ── 16. Plots ─────────────────────────────────────────────────────────────────
# Probability distribution
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(probs[y_test==0], bins=40, alpha=0.7, color='#4f46e5',
        label='Actual Stay', density=True)
ax.hist(probs[y_test==1], bins=40, alpha=0.7, color='#dc2626',
        label='Actual Leave', density=True)
ax.axvline(THRESHOLD, color='black', lw=2, linestyle='--',
           label=f'Threshold = {THRESHOLD:.3f}')
ax.axvline(0.5, color='orange', lw=1.5, linestyle=':',
           label='High-Risk = 0.5')
ax.set_title('XGBoost v3 -- Calibrated Probability Distribution',
             fontsize=13, fontweight='bold')
ax.set_xlabel('P(Leave)')
ax.set_ylabel('Density')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'prob_distribution_v3.png'), dpi=150)
plt.close()

# Feature importance
feat_imp = pd.Series(model.feature_importances_, index=FEATURES)
top10    = feat_imp.nlargest(10).sort_values()
fig, ax  = plt.subplots(figsize=(9, 6))
colors   = ['#dc2626' if v > top10.median() else '#4f46e5' for v in top10.values]
ax.barh(top10.index, top10.values, color=colors, alpha=0.85)
ax.set_xlabel('Importance', fontsize=12)
ax.set_title('Top 10 Feature Importances -- XGBoost v3',
             fontsize=13, fontweight='bold')
ax.axvline(top10.median(), color='gray', linestyle='--', lw=1, alpha=0.6)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'feature_importance_v3.png'), dpi=150)
plt.close()

print("\n>> Top 10 Feature Importances:")
for feat, val in feat_imp.nlargest(10).items():
    print(f"   {feat:<32} {val:.4f}")

# Confusion matrix
fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
            xticklabels=['Stay','Leave'], yticklabels=['Stay','Leave'],
            annot_kws={'size': 14})
ax.set_title(f'XGBoost v3 Confusion Matrix (t={THRESHOLD:.3f})',
             fontsize=11, fontweight='bold')
ax.set_xlabel('Predicted'); ax.set_ylabel('Actual')
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'confusion_matrix_v3.png'), dpi=150)
plt.close()

# ROC curve
fpr_t, tpr_t, _ = roc_curve(y_test, probs)
fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(fpr_t, tpr_t, color='#dc2626', lw=2.5,
        label=f'XGBoost v3 (AUC={auc:.3f})')
ax.plot([0,1],[0,1], 'k--', lw=1, alpha=0.5)
ax.set_xlabel('False Positive Rate', fontsize=12)
ax.set_ylabel('True Positive Rate', fontsize=12)
ax.set_title('ROC Curve -- XGBoost v3', fontsize=13, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(RESULTS_DIR, 'roc_curve_v3.png'), dpi=150)
plt.close()

# ── 17. Save model & artifacts ────────────────────────────────────────────────
print("\n>> Saving model artifacts...")

wrapped = CalibratedXGB(model, platt, THRESHOLD)
joblib.dump(wrapped, os.path.join(MODEL_DIR, 'eaps_xgboost_v3.pkl'))
joblib.dump({'XGBoost_v3': THRESHOLD}, os.path.join(MODEL_DIR, 'threshold_v3.pkl'))

print("   Saved -> models/eaps_xgboost_v3.pkl")
print("   Saved -> models/threshold_v3.pkl")
print("   Saved -> models/scaler_v3.pkl")
print("   Saved -> models/label_encoders_v3.pkl")
print("   Saved -> models/feature_names_v3.pkl")
print("   Saved -> results/prob_distribution_v3.png")
print("   Saved -> results/feature_importance_v3.png")
print("   Saved -> results/confusion_matrix_v3.png")
print("   Saved -> results/roc_curve_v3.png")
print("   Saved -> results/smote_class_balance_v3.png")

print("\n" + "=" * 65)
print("  [DONE] XGBoost v3 complete!")
print(f"  Recall  = {rec*100:.1f}%  (target > 75%)")
print(f"  F1      = {f1*100:.1f}%  (target > 72%)")
print(f"  AUC-ROC = {auc*100:.1f}%")
print("=" * 65)
