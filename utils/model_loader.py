"""
utils/model_loader.py
=====================
Loads the XGBoost v3 model and supporting artifacts.
Single-model pipeline — only eaps_xgboost_v3.pkl is used.
"""

import os
import joblib
import numpy as np
from utils.calibrated_xgb import CalibratedXGB  # noqa: F401 — needed for joblib unpickling

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

# v3 artifact filenames
MODEL_FILE         = 'eaps_xgboost_v3.pkl'
SCALER_FILE        = 'scaler_v3.pkl'
FEATURE_NAMES_FILE = 'feature_names_v3.pkl'
LABEL_ENCODERS_FILE= 'label_encoders_v3.pkl'
THRESHOLD_FILE     = 'threshold_v3.pkl'

# Models that need scaled input — all use scaler_v3
SCALED_MODELS = {'XGBoost'}

# Module-level cache
_cache = {}


def _reset_cache():
    """Clear in-memory model cache (call after retraining)."""
    _cache.clear()


def load_model():
    """Load the XGBoost v3 calibrated model. Cached after first call."""
    if 'model' in _cache:
        return _cache['model']
    path = os.path.join(MODEL_DIR, MODEL_FILE)
    if not os.path.exists(path):
        return None
    m = joblib.load(path)
    _cache['model'] = m
    return m


def load_scaler():
    """Load the v3 StandardScaler. Cached after first call."""
    if 'scaler' in _cache:
        return _cache['scaler']
    path = os.path.join(MODEL_DIR, SCALER_FILE)
    s = joblib.load(path) if os.path.exists(path) else None
    _cache['scaler'] = s
    return s


def load_all_models():
    """
    Backward-compatible wrapper so existing server.py routes still work.
    Returns: (models_dict, scaler)
    models_dict always has 'XGBoost' key pointing to the v3 model.
    """
    model  = load_model()
    scaler = load_scaler()
    models = {'XGBoost': model}
    return models, scaler


def load_feature_names():
    """Load the exact feature names the v3 model was trained on."""
    if 'feature_names' in _cache:
        return _cache['feature_names']
    path = os.path.join(MODEL_DIR, FEATURE_NAMES_FILE)
    if os.path.exists(path):
        names = joblib.load(path)
    else:
        # Fallback — v3 feature list including composite features
        names = [
            'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
            'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
            'YearsSinceLastPromotion', 'TotalWorkingYears', 'WorkLifeBalance',
            'JobSatisfaction', 'PerformanceRating', 'TrainingTimesLastYear',
            'EnvironmentSatisfaction', 'RelationshipSatisfaction', 'JobInvolvement',
            'DistanceFromHome', 'NumCompaniesWorked', 'Gender', 'OverTime',
            'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
            'SatisfactionIndex', 'TenureRatio', 'CompensationGap',
        ]
    _cache['feature_names'] = names
    return names


def load_label_encoders():
    """Load the v3 LabelEncoders for consistent categorical encoding."""
    if 'label_encoders' in _cache:
        return _cache['label_encoders']
    path = os.path.join(MODEL_DIR, LABEL_ENCODERS_FILE)
    le = joblib.load(path) if os.path.exists(path) else {}
    _cache['label_encoders'] = le
    return le


def load_thresholds():
    """Load the v3 optimal threshold."""
    if 'thresholds' in _cache:
        return _cache['thresholds']
    path = os.path.join(MODEL_DIR, THRESHOLD_FILE)
    if os.path.exists(path):
        raw = joblib.load(path)
        # threshold_v3.pkl stores {'XGBoost_v3': value}
        # Normalise to {'XGBoost': value} for compatibility
        if isinstance(raw, dict):
            thresholds = {k.replace('_v3', ''): v for k, v in raw.items()}
        else:
            thresholds = {'XGBoost': float(raw)}
    else:
        thresholds = {'XGBoost': 0.50}
    _cache['thresholds'] = thresholds
    return thresholds


def load_best_model_name():
    """Always returns 'XGBoost' — only one model in v3 pipeline."""
    return 'XGBoost'


def models_exist() -> bool:
    """Check if the v3 XGBoost model file exists."""
    return os.path.exists(os.path.join(MODEL_DIR, MODEL_FILE))


def _risk_label(prob: float, threshold: float = 0.50) -> str:
    """
    Convert raw probability to LOW / MEDIUM / HIGH risk label.
      - prob >= 0.60  -> HIGH   (high confidence attrition)
      - prob >= 0.40  -> MEDIUM (borderline / watch closely)
      - prob <  0.40  -> LOW    (low concern)
    """
    if prob >= 0.60:
        return 'HIGH'
    elif prob >= 0.40:
        return 'MEDIUM'
    return 'LOW'


def predict_single(employee_dict: dict, model_name: str = 'XGBoost') -> dict:
    """
    Predict attrition for one employee.
    employee_dict should already be numerically encoded (via encode_input).
    Returns: { prediction, probability, risk_level, threshold_used }
    """
    import pandas as pd

    model  = load_model()
    scaler = load_scaler()

    if model is None:
        return {'error': 'XGBoost v3 model not found. Run train_xgboost_v3.py first.'}

    feature_names = load_feature_names()
    thresholds    = load_thresholds()
    threshold     = thresholds.get('XGBoost', 0.50)

    # Build DataFrame with correct column order, filling missing with 0
    row = {col: employee_dict.get(col, 0) for col in feature_names}
    df  = pd.DataFrame([row])

    # Scale input
    if scaler:
        df = pd.DataFrame(scaler.transform(df), columns=df.columns)

    prob = float(model.predict_proba(df)[0][1])
    pred = 1 if prob >= threshold else 0

    return {
        'prediction':     'Leave' if pred == 1 else 'Stay',
        'probability':    round(prob, 4),
        'risk_level':     _risk_label(prob, threshold),
        'threshold_used': threshold,
    }


def predict_batch(df_input, model_name: str = 'XGBoost'):
    """
    Predict attrition for a DataFrame of employees.
    Returns df_input with added columns: Prediction, Probability, Risk_Level, Threshold_Used
    """
    import pandas as pd

    model  = load_model()
    scaler = load_scaler()

    if model is None:
        raise ValueError('XGBoost v3 model not found. Run train_xgboost_v3.py first.')

    feature_names = load_feature_names()
    thresholds    = load_thresholds()
    threshold     = thresholds.get('XGBoost', 0.50)

    df = df_input.copy()
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    X = df[feature_names]

    if scaler:
        X = pd.DataFrame(scaler.transform(X), columns=X.columns)

    probs = model.predict_proba(X)[:, 1]
    preds = (probs >= threshold).astype(int)

    df_out = df_input.copy()
    df_out['Prediction']     = ['Leave' if p == 1 else 'Stay' for p in preds]
    df_out['Probability']    = np.round(probs, 4)
    df_out['Risk_Level']     = [_risk_label(p, threshold) for p in probs]
    df_out['Threshold_Used'] = threshold
    return df_out
