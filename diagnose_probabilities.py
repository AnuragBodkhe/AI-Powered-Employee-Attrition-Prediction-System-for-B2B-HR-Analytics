"""
diagnose_probabilities.py
==========================
Compare raw XGBoost vs Platt-calibrated probabilities.
Find the probability compression problem and fix it.
"""
import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np, pandas as pd, joblib
from utils.model_loader import load_model, load_scaler, load_feature_names, _reset_cache
from utils.preprocess   import preprocess_uploaded_csv

_reset_cache()
clf    = load_model()
scaler = load_scaler()
feats  = load_feature_names()
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'data', 'WA_Fn-UseC_-HR-Employee-Attrition.csv')
df = pd.read_csv(DATA)
y  = (df['Attrition'] == 'Yes').astype(int).values

df_proc = preprocess_uploaded_csv(df.copy())
X_sc    = pd.DataFrame(scaler.transform(df_proc.values), columns=df_proc.columns)

# ── Compare raw vs calibrated ──────────────────────────────────────────────
raw_probs = clf.base.predict_proba(df_proc.values)[:, 1]
cal_probs = clf.predict_proba(X_sc)[:, 1]

print("=" * 60)
print("  PROBABILITY ANALYSIS — Raw XGBoost vs Platt Calibrated")
print("=" * 60)

for label, probs in [('RAW XGBoost (before Platt)', raw_probs),
                     ('PLATT calibrated (current)',  cal_probs)]:
    leavers = probs[y == 1]
    stayers = probs[y == 0]
    sep = leavers.mean() - stayers.mean()
    print(f"\n  {label}")
    print(f"    Leavers  avg={leavers.mean():.3f}  min={leavers.min():.3f}  max={leavers.max():.3f}")
    print(f"    Stayers  avg={stayers.mean():.3f}  min={stayers.min():.3f}  max={stayers.max():.3f}")
    print(f"    Separation gap : {sep:.3f}")

# ── Fix: strip Platt, use raw XGBoost probabilities directly ──────────────
# Raw XGBoost is well-calibrated enough (trained with scale_pos_weight + SMOTE)
# Platt scaling was compressing probabilities toward center (0.10–0.63 range)
print("\n" + "=" * 60)
print("  FIX: Remove Platt scaling — use raw XGBoost probabilities")
print("=" * 60)

# Verify the fix on real leavers
raw_leave = raw_probs[y == 1]
raw_stay  = raw_probs[y == 0]
print(f"\n  Raw XGBoost on IBM HR (1470 employees):")
print(f"    Leavers  avg={raw_leave.mean():.3f}  max={raw_leave.max():.3f}")
print(f"    Stayers  avg={raw_stay.mean():.3f}   max={raw_stay.max():.3f}")
print(f"    Separation: {raw_leave.mean()-raw_stay.mean():.3f}")

# Apply 0.50 threshold to raw probs
raw_preds = (raw_probs >= 0.50).astype(int)
tp = int(((raw_preds==1) & (y==1)).sum())
fp = int(((raw_preds==1) & (y==0)).sum())
fn = int(((raw_preds==0) & (y==1)).sum())
prec = tp/(tp+fp) if (tp+fp)>0 else 0
rec  = tp/(tp+fn) if (tp+fn)>0 else 0
f1   = 2*prec*rec/(prec+rec) if (prec+rec)>0 else 0
print(f"\n  Raw XGBoost at 0.50 threshold:")
print(f"    TP={tp}  FP={fp}  FN={fn}")
print(f"    Precision={prec:.2%}  Recall={rec:.2%}  F1={f1:.3f}")
print(f"    Predicted Leave rate: {raw_preds.mean():.1%}")

# ── Patch CalibratedXGB to skip Platt ─────────────────────────────────────
print("\n  Patching model: disabling Platt scaling...")

# Override predict_proba to use raw XGBoost directly
import types

def predict_proba_raw(self, X):
    """Use raw XGBoost probability — no Platt compression."""
    import numpy as np
    p1 = self.base.predict_proba(X)[:, 1]
    return np.column_stack([1 - p1, p1])

clf.predict_proba = types.MethodType(predict_proba_raw, clf)

# Verify after patch
new_probs = clf.predict_proba(df_proc.values)[:, 1]
new_leave = new_probs[y == 1]
new_stay  = new_probs[y == 0]
print(f"\n  After patch (raw, no Platt):")
print(f"    Leavers  avg={new_leave.mean():.3f}  max={new_leave.max():.3f}")
print(f"    Stayers  avg={new_stay.mean():.3f}   max={new_stay.max():.3f}")
print(f"    Separation: {new_leave.mean()-new_stay.mean():.3f}")

# ── Save patched model ─────────────────────────────────────────────────────
joblib.dump(clf, os.path.join(MODEL_DIR, 'eaps_xgboost_v3.pkl'))
print("\n  Saved patched model to eaps_xgboost_v3.pkl")
print("  Done. Restart Flask to apply.")
