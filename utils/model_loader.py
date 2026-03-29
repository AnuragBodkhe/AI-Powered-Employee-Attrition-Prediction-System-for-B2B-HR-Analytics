"""
utils/model_loader.py
Loads trained .pkl models and scaler from the models/ directory.
Handles both IBM HR feature set and custom CSV feature set.
Flask-compatible — NO Streamlit dependency.

Key fixes (debiased version):
  - Uses saved optimal threshold (threshold.pkl) instead of 0.5
  - Loads label_encoders.pkl to match training encoding exactly
  - predict_single / predict_batch use probability >= threshold
"""

import os
import joblib
import numpy as np

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

MODELS = {
    'Random Forest':       'random_forest.pkl',
    'XGBoost':             'xgboost.pkl',
    'Logistic Regression': 'logistic_regression.pkl',
    'SVM':                 'svm.pkl',
}
SCALER_FILE          = 'scaler.pkl'
FEATURE_NAMES_FILE   = 'feature_names.pkl'
BEST_MODEL_FILE      = 'best_model_name.pkl'
LABEL_ENCODERS_FILE  = 'label_encoders.pkl'
THRESHOLD_FILE       = 'threshold.pkl'
CLASS_RATIO_FILE     = 'class_ratio.pkl'

# Models that need scaled input
SCALED_MODELS = {'Logistic Regression', 'SVM'}

# Module-level cache (replaces @st.cache_resource)
_cache = {}


def _reset_cache():
    """Clear in-memory model cache (call after retraining)."""
    _cache.clear()


def load_all_models():
    """
    Load all trained models and the scaler. Cached after first call.
    Returns: (loaded_models_dict, scaler)
    """
    if 'models' in _cache:
        return _cache['models'], _cache['scaler']

    loaded = {}
    for name, fname in MODELS.items():
        path = os.path.join(MODEL_DIR, fname)
        if os.path.exists(path):
            loaded[name] = joblib.load(path)
        else:
            loaded[name] = None

    scaler_path = os.path.join(MODEL_DIR, SCALER_FILE)
    scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

    _cache['models'] = loaded
    _cache['scaler'] = scaler
    return loaded, scaler


def load_feature_names():
    """Load the exact feature names the models were trained on."""
    if 'feature_names' in _cache:
        return _cache['feature_names']

    path = os.path.join(MODEL_DIR, FEATURE_NAMES_FILE)
    if os.path.exists(path):
        names = joblib.load(path)
    else:
        # Fallback: 25-column FINAL_FEATURES from pipeline
        names = [
            'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
            'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
            'YearsSinceLastPromotion', 'WorkLifeBalance', 'JobSatisfaction',
            'PerformanceRating', 'TrainingTimesLastYear', 'EnvironmentSatisfaction',
            'RelationshipSatisfaction', 'JobInvolvement', 'DistanceFromHome',
            'NumCompaniesWorked', 'Gender', 'OverTime',
            'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
        ]

    _cache['feature_names'] = names
    return names


def load_label_encoders():
    """Load the LabelEncoders saved during training for consistent encoding."""
    if 'label_encoders' in _cache:
        return _cache['label_encoders']

    path = os.path.join(MODEL_DIR, LABEL_ENCODERS_FILE)
    le = joblib.load(path) if os.path.exists(path) else {}
    _cache['label_encoders'] = le
    return le


def load_thresholds():
    """Load per-model optimal thresholds (Youden's J) from training."""
    if 'thresholds' in _cache:
        return _cache['thresholds']

    path = os.path.join(MODEL_DIR, THRESHOLD_FILE)
    thresholds = joblib.load(path) if os.path.exists(path) else {}
    _cache['thresholds'] = thresholds
    return thresholds


def load_best_model_name():
    """Return the name of the best-performing model from training."""
    path = os.path.join(MODEL_DIR, BEST_MODEL_FILE)
    if os.path.exists(path):
        return joblib.load(path)
    return 'Random Forest'


def models_exist() -> bool:
    """Check if at least the Random Forest model file exists."""
    return os.path.exists(os.path.join(MODEL_DIR, 'random_forest.pkl'))


def _risk_label(prob: float) -> str:
    """Convert raw probability to Low / Medium / High risk label."""
    if prob >= 0.70:
        return 'HIGH'
    elif prob >= 0.40:
        return 'MEDIUM'
    return 'LOW'


def predict_single(employee_dict: dict, model_name: str = 'Random Forest') -> dict:
    """
    Predict attrition for one employee.
    employee_dict should already be numerically encoded (via encode_input).
    Returns: { prediction, probability, risk_level, threshold_used }
    """
    import pandas as pd

    models, scaler = load_all_models()
    model = models.get(model_name)

    if model is None:
        return {'error': f'Model "{model_name}" not found. Run eaps_ml_pipeline.py first.'}

    feature_names = load_feature_names()
    thresholds    = load_thresholds()
    threshold     = thresholds.get(model_name, 0.5)

    # Build DataFrame with correct column order, filling missing columns with 0
    row = {col: employee_dict.get(col, 0) for col in feature_names}
    df  = pd.DataFrame([row])

    if model_name in SCALED_MODELS and scaler:
        df = pd.DataFrame(scaler.transform(df), columns=df.columns)

    # Use probability >= threshold (NOT model.predict directly, avoids threshold mismatch)
    prob  = float(model.predict_proba(df)[0][1])
    pred  = 1 if prob >= threshold else 0

    return {
        'prediction':      'Leave' if pred == 1 else 'Stay',
        'probability':     round(prob, 4),
        'risk_level':      _risk_label(prob),
        'threshold_used':  threshold,
    }


def predict_batch(df_input, model_name: str = 'Random Forest'):
    """
    Predict attrition for a DataFrame of employees.
    Returns df_input with added columns:
        Prediction, Probability, Risk_Level, Threshold_Used
    """
    import pandas as pd

    models, scaler = load_all_models()
    model = models.get(model_name)

    if model is None:
        raise ValueError(f'Model "{model_name}" not found. Run eaps_ml_pipeline.py first.')

    feature_names = load_feature_names()
    thresholds    = load_thresholds()
    threshold     = thresholds.get(model_name, 0.5)

    # Align columns: keep only known features, fill missing with 0
    df = df_input.copy()
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    X = df[feature_names]

    if model_name in SCALED_MODELS and scaler:
        X = pd.DataFrame(scaler.transform(X), columns=X.columns)

    probs  = model.predict_proba(X)[:, 1]
    preds  = (probs >= threshold).astype(int)

    df_out = df_input.copy()
    df_out['Prediction']     = ['Leave' if p == 1 else 'Stay' for p in preds]
    df_out['Probability']    = np.round(probs, 4)
    df_out['Risk_Level']     = [_risk_label(p) for p in probs]
    df_out['Threshold_Used'] = threshold
    return df_out
