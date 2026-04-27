"""
fix_probabilities.py
====================
Rebuild CalibratedXGB from scratch using the intact base XGBoost model,
refit the Platt scaler with OOF cross-validated scores for better spread,
and save a clean new pkl.
"""
import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np, pandas as pd, joblib
from sklearn.linear_model    import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from xgboost                 import XGBClassifier
from utils.calibrated_xgb   import CalibratedXGB
from utils.model_loader      import load_scaler, load_feature_names, _reset_cache
from utils.preprocess        import preprocess_uploaded_csv

_reset_cache()
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

# ── Load base XGBoost from training pkl (bypasses the corrupted wrapper) ──
# Try to load just the base model that was saved separately
import pickle

# Try loading the broken pkl with a fallback
broken_path = os.path.join(MODEL_DIR, 'eaps_xgboost_v3.pkl')
try:
    import joblib as jl
    obj = jl.load(broken_path)
    base_xgb = obj.base
    print("Loaded base XGB from existing pkl")
except Exception as e:
    print(f"PKL broken ({e}), trying backup...")
    # Re-instantiate from training script params
    base_xgb = None

if base_xgb is None:
    print("ERROR: Cannot load base model. Please run train_xgboost_v3.py first.")
    sys.exit(1)

scaler = load_scaler()
feats  = load_feature_names()

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    'data', 'WA_Fn-UseC_-HR-Employee-Attrition.csv')
df = pd.read_csv(DATA)
y  = (df['Attrition'] == 'Yes').astype(int).values
df_proc = preprocess_uploaded_csv(df.copy())
X_arr = df_proc.values

print(f"Dataset: {len(y)} employees  |  Leavers: {y.sum()} ({y.mean():.1%})\n")

# ── Step 1: Refit Platt using OOF cross-validated scores ─────────────────
print("Generating OOF raw scores (5-fold CV)...")
oof_raw = np.zeros(len(y))
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

for fold, (tr_idx, val_idx) in enumerate(skf.split(X_arr, y)):
    xgb_fold = XGBClassifier(**base_xgb.get_params())
    xgb_fold.fit(X_arr[tr_idx], y[tr_idx],
                 eval_set=[(X_arr[val_idx], y[val_idx])],
                 verbose=False)
    oof_raw[val_idx] = xgb_fold.predict_proba(X_arr[val_idx])[:, 1]
    lv = oof_raw[val_idx][y[val_idx]==1]
    st = oof_raw[val_idx][y[val_idx]==0]
    print(f"  Fold {fold+1}: leavers avg={lv.mean():.3f}  stayers avg={st.mean():.3f}")

print(f"\nOOF summary:")
print(f"  Leavers  avg={oof_raw[y==1].mean():.3f}  max={oof_raw[y==1].max():.3f}")
print(f"  Stayers  avg={oof_raw[y==0].mean():.3f}  max={oof_raw[y==0].max():.3f}")
print(f"  Separation: {oof_raw[y==1].mean()-oof_raw[y==0].mean():.3f}")

# ── Step 2: Fit new Platt on OOF ─────────────────────────────────────────
new_platt = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
new_platt.fit(oof_raw.reshape(-1, 1), y)

# ── Step 3: Apply to full dataset and verify ──────────────────────────────
full_raw_scores = base_xgb.predict_proba(X_arr)[:, 1].reshape(-1, 1)
new_cal_probs   = new_platt.predict_proba(full_raw_scores)[:, 1]

nl = new_cal_probs[y==1]
ns = new_cal_probs[y==0]
print(f"\nNew calibrated probabilities:")
print(f"  Leavers  avg={nl.mean():.3f}  min={nl.min():.3f}  max={nl.max():.3f}")
print(f"  Stayers  avg={ns.mean():.3f}   min={ns.min():.3f}  max={ns.max():.3f}")
print(f"  Separation: {nl.mean()-ns.mean():.3f}")

# Metrics at 0.50
preds = (new_cal_probs >= 0.50).astype(int)
tp = int(((preds==1)&(y==1)).sum())
fp = int(((preds==1)&(y==0)).sum())
fn = int(((preds==0)&(y==1)).sum())
prec = tp/(tp+fp) if (tp+fp)>0 else 0
rec  = tp/(tp+fn) if (tp+fn)>0 else 0
f1   = 2*prec*rec/(prec+rec) if (prec+rec)>0 else 0
print(f"\nAt 0.50 threshold:")
print(f"  TP={tp}  FP={fp}  FN={fn}")
print(f"  Precision={prec:.2%}  Recall={rec:.2%}  F1={f1:.3f}")
print(f"  Predicted Leave rate: {preds.mean():.1%}  (target ~20%)")

# ── Step 4: Save clean new pkl ────────────────────────────────────────────
new_clf = CalibratedXGB(base=base_xgb, platt=new_platt, threshold=0.50)
joblib.dump(new_clf, os.path.join(MODEL_DIR, 'eaps_xgboost_v3.pkl'))
print(f"\nSaved clean eaps_xgboost_v3.pkl  (threshold=0.50)")
print("Restart Flask to apply.")
