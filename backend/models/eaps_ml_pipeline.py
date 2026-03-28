"""
============================================================
 Employee Attrition Prediction System (EAPS)
 AI-Powered B2B HR Analytics — ML Pipeline
============================================================
 Author  : Anurag Bodkhe et al., MIT School of Computing
 Models  : Logistic Regression | SVM | Random Forest | XGBoost
 Dataset : IBM HR Analytics (primary) + custom datasets
 Features: SMOTE balancing, SHAP explainability, model export
============================================================

REQUIREMENTS (install once):
    pip install scikit-learn xgboost shap imbalanced-learn
    pip install pandas numpy matplotlib seaborn joblib

USAGE:
    python eaps_ml_pipeline.py
    # Trained models saved to ./models/
    # Results printed to console + saved to ./results/
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, roc_auc_score, f1_score,
                             precision_score, recall_score,
                             classification_report, confusion_matrix,
                             RocCurveDisplay)
import xgboost as xgb
from imblearn.over_sampling import SMOTE
import shap

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────
# 0. PATHS — edit these to point to your dataset files
# ─────────────────────────────────────────────────────────────────
IBM_PATH   = 'WA_Fn-UseC_-HR-Employee-Attrition.csv'
DS1_PATH   = 'employee_attrition_dataset.csv'       # 1000-row custom set
DS2_PATH   = 'employee_attrition_dataset_10000.csv' # 10000-row custom set

OUT_DIR    = './results'
MODEL_DIR  = './models'
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

RANDOM_STATE = 42

# ─────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────────────────────────
def load_ibm(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Drop constant/useless columns
    df.drop(columns=['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber'],
            inplace=True, errors='ignore')
    return df


def load_custom(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.drop(columns=['Employee_ID'], inplace=True, errors='ignore')
    return df


# ─────────────────────────────────────────────────────────────────
# 2. PREPROCESS
# ─────────────────────────────────────────────────────────────────
def preprocess(df: pd.DataFrame, target_col: str = 'Attrition') -> tuple:
    """
    Encode categoricals, map target to 0/1.
    Returns (X, y, feature_names, scaler).
    """
    df = df.copy()

    # Map target
    if df[target_col].dtype == object:
        df[target_col] = df[target_col].map({'Yes': 1, 'No': 0,
                                              'yes': 1, 'no': 0,
                                              '1': 1, '0': 0})
    df[target_col] = df[target_col].astype(int)

    # Encode all remaining object columns
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    le = LabelEncoder()
    for col in cat_cols:
        df[col] = le.fit_transform(df[col].astype(str))

    X = df.drop(columns=[target_col])
    y = df[target_col]
    feature_names = X.columns.tolist()

    return X, y, feature_names


# ─────────────────────────────────────────────────────────────────
# 3. SMOTE CLASS BALANCING
# ─────────────────────────────────────────────────────────────────
def apply_smote(X, y, random_state=RANDOM_STATE):
    sm = SMOTE(random_state=random_state)
    X_res, y_res = sm.fit_resample(X, y)
    print(f"  After SMOTE → class counts: {dict(pd.Series(y_res).value_counts())}")
    return X_res, y_res


# ─────────────────────────────────────────────────────────────────
# 4. BUILD MODELS
# ─────────────────────────────────────────────────────────────────
def build_models():
    return {
        'Logistic Regression': LogisticRegression(
            max_iter=1000, C=1.0, solver='lbfgs', random_state=RANDOM_STATE),

        'SVM': SVC(
            kernel='rbf', C=1.0, gamma='scale',
            probability=True, random_state=RANDOM_STATE),

        'Random Forest': RandomForestClassifier(
            n_estimators=200, max_depth=None,
            min_samples_split=2, random_state=RANDOM_STATE, n_jobs=-1),

        'XGBoost': xgb.XGBClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=5,
            subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric='logloss',
            random_state=RANDOM_STATE, n_jobs=-1)
    }


# ─────────────────────────────────────────────────────────────────
# 5. TRAIN & EVALUATE
# ─────────────────────────────────────────────────────────────────
def train_evaluate(models: dict, X_train, X_test, y_train, y_test,
                   scaler: StandardScaler = None) -> dict:
    """
    Train each model, evaluate on test set.
    Logistic Regression and SVM use scaled features automatically.
    Returns dict of results.
    """
    results = {}
    SCALED_MODELS = {'Logistic Regression', 'SVM'}

    print(f"\n{'Model':<22} {'Acc':>6} {'AUC':>6} {'F1':>6} {'Prec':>6} {'Rec':>6}")
    print("─" * 65)

    for name, model in models.items():
        if scaler and name in SCALED_MODELS:
            Xtr = scaler.transform(X_train)
            Xte = scaler.transform(X_test)
        else:
            Xtr, Xte = X_train, X_test

        model.fit(Xtr, y_train)
        y_pred = model.predict(Xte)
        y_prob = model.predict_proba(Xte)[:, 1]

        acc  = accuracy_score(y_test, y_pred)
        auc  = roc_auc_score(y_test, y_prob)
        f1   = f1_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec  = recall_score(y_test, y_pred)

        results[name] = dict(model=model, acc=acc, auc=auc,
                             f1=f1, prec=prec, rec=rec,
                             y_pred=y_pred, y_prob=y_prob)

        print(f"{name:<22} {acc:>6.4f} {auc:>6.4f} {f1:>6.4f} "
              f"{prec:>6.4f} {rec:>6.4f}")

    print("─" * 65)
    return results


# ─────────────────────────────────────────────────────────────────
# 6. SHAP EXPLAINABILITY
# ─────────────────────────────────────────────────────────────────
def explain_shap(model, X_test, feature_names: list, model_name: str):
    """Generate SHAP summary plot for tree-based models."""
    print(f"\n[SHAP] Computing SHAP values for {model_name} ...")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test)
        # For binary classification, shap_values may be a list
        sv = shap_values[1] if isinstance(shap_values, list) else shap_values

        plt.figure(figsize=(10, 6))
        shap.summary_plot(sv, X_test, feature_names=feature_names,
                          show=False, plot_type='bar')
        plt.title(f'SHAP Feature Importance — {model_name}', fontsize=13)
        plt.tight_layout()
        path = f'{OUT_DIR}/shap_{model_name.replace(" ", "_").lower()}.png'
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"  SHAP plot saved → {path}")
    except Exception as e:
        print(f"  SHAP skipped: {e}")


# ─────────────────────────────────────────────────────────────────
# 7. PLOTS
# ─────────────────────────────────────────────────────────────────
def plot_confusion(results: dict, y_test):
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    if n == 1:
        axes = [axes]
    for ax, (name, res) in zip(axes, results.items()):
        cm = confusion_matrix(y_test, res['y_pred'])
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=['Stay', 'Leave'],
                    yticklabels=['Stay', 'Leave'])
        ax.set_title(f'{name}\nAcc={res["acc"]:.3f}')
        ax.set_ylabel('Actual')
        ax.set_xlabel('Predicted')
    plt.tight_layout()
    path = f'{OUT_DIR}/confusion_matrices.png'
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n[Plot] Confusion matrices saved → {path}")


def plot_roc(results: dict, X_test, y_test, scaler=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    SCALED_MODELS = {'Logistic Regression', 'SVM'}
    for name, res in results.items():
        Xte = scaler.transform(X_test) if (scaler and name in SCALED_MODELS) else X_test
        RocCurveDisplay.from_estimator(res['model'], Xte, y_test,
                                       name=f"{name} (AUC={res['auc']:.3f})", ax=ax)
    ax.plot([0, 1], [0, 1], 'k--', lw=1)
    ax.set_title('ROC Curves — All Models', fontsize=13)
    plt.tight_layout()
    path = f'{OUT_DIR}/roc_curves.png'
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"[Plot] ROC curves saved → {path}")


def plot_bar_comparison(results: dict):
    metrics = ['acc', 'auc', 'f1', 'prec', 'rec']
    labels  = ['Accuracy', 'AUC-ROC', 'F1', 'Precision', 'Recall']
    df_res = pd.DataFrame(
        {name: [res[m] for m in metrics] for name, res in results.items()},
        index=labels)
    ax = df_res.T.plot(kind='bar', figsize=(10, 5), rot=15, edgecolor='black')
    ax.set_ylim(0.5, 1.02)
    ax.set_ylabel('Score')
    ax.set_title('Model Comparison — All Metrics', fontsize=13)
    ax.legend(loc='lower right')
    plt.tight_layout()
    path = f'{OUT_DIR}/model_comparison.png'
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"[Plot] Bar comparison saved → {path}")


def plot_feature_importance(model, feature_names: list, model_name: str, top_n=15):
    if hasattr(model, 'feature_importances_'):
        imp = pd.Series(model.feature_importances_, index=feature_names)\
                .sort_values(ascending=True).tail(top_n)
        fig, ax = plt.subplots(figsize=(8, 6))
        imp.plot(kind='barh', ax=ax, color='steelblue', edgecolor='black')
        ax.set_title(f'Feature Importance — {model_name}', fontsize=13)
        ax.set_xlabel('Importance Score')
        plt.tight_layout()
        path = f'{OUT_DIR}/feature_importance_{model_name.replace(" ","_").lower()}.png'
        plt.savefig(path, dpi=150)
        plt.close()
        print(f"[Plot] Feature importance saved → {path}")


# ─────────────────────────────────────────────────────────────────
# 8. SAVE MODELS
# ─────────────────────────────────────────────────────────────────
def save_models(results: dict, scaler: StandardScaler = None):
    for name, res in results.items():
        fname = name.replace(' ', '_').lower()
        joblib.dump(res['model'], f'{MODEL_DIR}/{fname}.pkl')
    if scaler:
        joblib.dump(scaler, f'{MODEL_DIR}/scaler.pkl')
    print(f"\n[Save] All models saved to {MODEL_DIR}/")


# ─────────────────────────────────────────────────────────────────
# 9. INFERENCE FUNCTION (use after loading saved model)
# ─────────────────────────────────────────────────────────────────
def predict_attrition(employee_data: dict, model_path: str,
                      scaler_path: str = None) -> dict:
    """
    Predict attrition for a single employee.
    employee_data: dict of feature_name → value (same as training features)
    Returns: {'prediction': 'Leave'/'Stay', 'probability': float}
    """
    model = joblib.load(model_path)
    df = pd.DataFrame([employee_data])

    if scaler_path:
        scaler = joblib.load(scaler_path)
        df = pd.DataFrame(scaler.transform(df), columns=df.columns)

    pred  = model.predict(df)[0]
    prob  = model.predict_proba(df)[0][1]
    label = 'Leave' if pred == 1 else 'Stay'
    return {'prediction': label, 'probability': round(float(prob), 4),
            'risk_level': 'HIGH' if prob > 0.7 else ('MEDIUM' if prob > 0.4 else 'LOW')}


# ─────────────────────────────────────────────────────────────────
# 10. MAIN PIPELINE
# ─────────────────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  EAPS — Employee Attrition Prediction System")
    print("  MIT School of Computing | B2B HR Analytics")
    print("=" * 65)

    # ── Load & Preprocess
    print("\n[1] Loading IBM HR Analytics dataset ...")
    ibm_raw = load_ibm(IBM_PATH)
    X, y, feature_names = preprocess(ibm_raw)
    print(f"    Features: {len(feature_names)}  |  Samples: {len(y)}")
    print(f"    Class distribution: {dict(y.value_counts())}")

    # ── SMOTE
    print("\n[2] Applying SMOTE oversampling ...")
    X_res, y_res = apply_smote(X.values, y.values)

    # ── Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=RANDOM_STATE, stratify=y_res)
    print(f"    Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")

    # ── Scale (for LR & SVM)
    scaler = StandardScaler()
    scaler.fit(X_train)

    # ── Train
    print("\n[3] Training models ...")
    models = build_models()
    results = train_evaluate(models, X_train, X_test, y_train, y_test, scaler)

    # ── Best model details
    best_name = max(results, key=lambda k: results[k]['auc'])
    best_res  = results[best_name]
    print(f"\n[4] Best Model: {best_name}  (AUC-ROC = {best_res['auc']:.4f})")
    print(classification_report(y_test, best_res['y_pred'],
                                target_names=['Stay (0)', 'Leave (1)']))

    # ── Plots
    print("[5] Generating plots ...")
    X_test_df = pd.DataFrame(X_test, columns=feature_names)
    plot_confusion(results, y_test)
    plot_roc(results, X_test, y_test, scaler)
    plot_bar_comparison(results)
    plot_feature_importance(results['Random Forest']['model'],
                            feature_names, 'Random Forest')
    plot_feature_importance(results['XGBoost']['model'],
                            feature_names, 'XGBoost')

    # ── SHAP
    print("[6] SHAP Explainability ...")
    for name in ['Random Forest', 'XGBoost']:
        explain_shap(results[name]['model'], X_test_df, feature_names, name)

    # ── Save models
    print("[7] Saving trained models ...")
    save_models(results, scaler)

    # ── Cross-validation summary
    print("\n[8] 5-Fold Cross-Validation (on full balanced data) ...")
    X_full_df = pd.DataFrame(X_res, columns=feature_names)
    for name in ['Random Forest', 'XGBoost']:
        cv_scores = cross_val_score(results[name]['model'], X_full_df, y_res,
                                    cv=StratifiedKFold(n_splits=5, shuffle=True,
                                                       random_state=RANDOM_STATE),
                                    scoring='roc_auc', n_jobs=-1)
        print(f"  {name}: AUC = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    print("\n[Done] EAPS pipeline complete.")
    print(f"  Results → {OUT_DIR}/")
    print(f"  Models  → {MODEL_DIR}/")
    print("=" * 65)


if __name__ == '__main__':
    main()
