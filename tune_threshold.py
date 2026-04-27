"""
tune_threshold.py
=================
Scans thresholds on the full IBM HR dataset to find the one whose
predicted attrition rate best matches the true ~20% base rate.
Then updates threshold_v3.pkl and the saved model object in-place.
"""

import sys, os, joblib, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_model, load_scaler, load_feature_names, _reset_cache
from utils.preprocess   import _compute_composite, _get_label_encoders, CATEGORICAL_MAPS

MODEL_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
TARGET_RATE = 0.20   # true IBM HR attrition base rate

# ── 1. Load model artifacts ────────────────────────────────────────────────
clf    = load_model()
scaler = load_scaler()
feats  = load_feature_names()
print(f"Current threshold in model : {clf.threshold:.4f}")

# ── 2. Load raw IBM HR dataset ────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for candidate in [
    os.path.join(BASE_DIR, 'data', 'WA_Fn-UseC_-HR-Employee-Attrition.csv'),
    os.path.join(BASE_DIR, 'WA_Fn-UseC_-HR-Employee-Attrition.csv'),
    os.path.join(BASE_DIR, 'data', 'HR_Employee_Attrition.csv'),
    os.path.join(BASE_DIR, 'HR_Employee_Attrition.csv'),
]:
    if os.path.exists(candidate):
        DATA_PATH = candidate
        break
else:
    raise FileNotFoundError("Cannot find the IBM HR dataset CSV.")

df = pd.read_csv(DATA_PATH)
print(f"Dataset: {len(df)} rows  from  {os.path.basename(DATA_PATH)}")

# Encode target
if df['Attrition'].dtype == object:
    df['Attrition'] = df['Attrition'].map({'Yes': 1, 'No': 0})
y         = df['Attrition'].values
true_rate = y.mean()
print(f"True attrition rate        : {true_rate:.1%}\n")

# ── 3. Encode features (same as training pipeline) ────────────────────────
# Drop non-feature columns
for col in ['Attrition', 'EmployeeCount', 'Over18', 'StandardHours',
            'EmployeeNumber', 'Employee_ID', 'DailyRate']:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# LabelEncode categoricals
le_dict = _get_label_encoders()
if le_dict:
    for col, le in le_dict.items():
        if col in df.columns:
            known = set(le.classes_)
            df[col] = df[col].astype(str).apply(
                lambda x: int(le.transform([x])[0]) if x in known else 0
            )
else:
    for col, mapping in CATEGORICAL_MAPS.items():
        if col in df.columns:
            df[col] = df[col].astype(str).map(mapping).fillna(0).astype(int)

# Add TotalWorkingYears if missing
if 'TotalWorkingYears' not in df.columns:
    df['TotalWorkingYears'] = (df.get('Age', 30) - 18).clip(lower=0)

# Compute composite features
df = _compute_composite(df)

# Convert remaining object cols
for col in df.select_dtypes(include='object').columns:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# Build feature matrix
X    = pd.DataFrame({c: df[c] if c in df.columns else 0.0 for c in feats})
X_sc = pd.DataFrame(scaler.transform(X.values), columns=feats)
probs = clf.predict_proba(X_sc)[:, 1]

print(f"{'Threshold':>10} | {'Pred Rate':>9} | {'Recall':>7} | {'Precision':>9} | {'F1':>6} | {'TP':>4} | {'FP':>4} | {'FN':>4}")
print("-" * 75)

best_thresh = 0.20
best_diff   = 1.0
all_rows    = []

for t in np.arange(0.10, 0.65, 0.01):
    preds = (probs >= t).astype(int)
    rate  = preds.mean()
    tp = int(((preds==1) & (y==1)).sum())
    fp = int(((preds==1) & (y==0)).sum())
    fn = int(((preds==0) & (y==1)).sum())
    prec = tp/(tp+fp) if (tp+fp) > 0 else 0.0
    rec  = tp/(tp+fn) if (tp+fn) > 0 else 0.0
    f1   = 2*prec*rec/(prec+rec) if (prec+rec) > 0 else 0.0
    diff = abs(rate - TARGET_RATE)
    all_rows.append((t, rate, rec, prec, f1, tp, fp, fn, diff))
    if diff < best_diff:
        best_diff   = diff
        best_thresh = t

# Print every 0.05 step
for t, rate, rec, prec, f1, tp, fp, fn, diff in all_rows:
    if round(t * 100) % 5 == 0:
        marker = " <-- SELECTED" if abs(t - best_thresh) < 0.005 else ""
        print(f"  {t:.2f}     | {rate:>8.1%}  | {rec:>6.1%} | {prec:>8.1%}  | {f1:.3f} | {tp:>4} | {fp:>4} | {fn:>4}{marker}")

preds_best = (probs >= best_thresh).astype(int)
print(f"\nSelected threshold : {best_thresh:.4f}")
print(f"Predicted Leave    : {preds_best.mean():.1%}  (target {TARGET_RATE:.0%})")
print(f"Actual Leave       : {true_rate:.1%}")

# ── 4. Save updated threshold ──────────────────────────────────────────────
thresh_path = os.path.join(MODEL_DIR, 'threshold_v3.pkl')
joblib.dump({'XGBoost_v3': float(best_thresh)}, thresh_path)
print(f"\nSaved threshold_v3.pkl  → {best_thresh:.4f}")

# Patch model object threshold and re-save
clf.threshold = float(best_thresh)
model_path = os.path.join(MODEL_DIR, 'eaps_xgboost_v3.pkl')
joblib.dump(clf, model_path)
print(f"Updated eaps_xgboost_v3.pkl  threshold = {best_thresh:.4f}")

_reset_cache()
print("\nDone. Restart Flask to apply the new threshold.")
