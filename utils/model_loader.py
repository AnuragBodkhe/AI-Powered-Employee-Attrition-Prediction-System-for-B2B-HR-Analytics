"""
utils/model_loader.py
Loads trained .pkl models and scaler from the models/ directory.
Handles both IBM HR feature set and custom CSV feature set.
"""

import os
import joblib
import streamlit as st

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

# Models that need scaled input
SCALED_MODELS = {'Logistic Regression', 'SVM'}


@st.cache_resource(show_spinner="Loading models...")
def load_all_models():
    """
    Load all trained models and the scaler. Cached after first call.
    Returns: (loaded_models_dict, scaler)
    """
    loaded = {}
    for name, fname in MODELS.items():
        path = os.path.join(MODEL_DIR, fname)
        if os.path.exists(path):
            loaded[name] = joblib.load(path)
        else:
            loaded[name] = None  # Not yet trained

    scaler_path = os.path.join(MODEL_DIR, SCALER_FILE)
    scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

    return loaded, scaler


@st.cache_resource(show_spinner=False)
def load_feature_names():
    """Load the exact feature names the models were trained on."""
    path = os.path.join(MODEL_DIR, FEATURE_NAMES_FILE)
    if os.path.exists(path):
        return joblib.load(path)
    # Fallback: IBM HR features
    return [
        'Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
        'Education', 'EducationField', 'EnvironmentSatisfaction', 'Gender',
        'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
        'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
        'OverTime', 'PercentSalaryHike', 'PerformanceRating',
        'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
        'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
        'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager'
    ]


@st.cache_resource(show_spinner=False)
def load_best_model_name():
    """Return the name of the best-performing model from training."""
    path = os.path.join(MODEL_DIR, BEST_MODEL_FILE)
    if os.path.exists(path):
        return joblib.load(path)
    return 'Random Forest'


def models_exist() -> bool:
    """Check if at least the Random Forest model file exists."""
    return os.path.exists(os.path.join(MODEL_DIR, 'random_forest.pkl'))


def predict_single(employee_dict: dict, model_name: str = 'Random Forest') -> dict:
    """
    Predict attrition for one employee.
    employee_dict should be already numerically encoded.
    Returns: { prediction, probability, risk_level }
    """
    import pandas as pd
    models, scaler = load_all_models()
    model = models.get(model_name)

    if model is None:
        return {'error': f'Model "{model_name}" not found. Run eaps_ml_pipeline.py first.'}

    feature_names = load_feature_names()

    # Build DataFrame with correct column order, filling missing columns with 0
    row = {col: employee_dict.get(col, 0) for col in feature_names}
    df = pd.DataFrame([row])

    if model_name in SCALED_MODELS and scaler:
        df = pd.DataFrame(scaler.transform(df), columns=df.columns)

    pred = int(model.predict(df)[0])
    prob = float(model.predict_proba(df)[0][1])

    if prob >= 0.70:
        risk = 'HIGH'
    elif prob >= 0.40:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'

    return {
        'prediction': 'Leave' if pred == 1 else 'Stay',
        'probability': round(prob, 4),
        'risk_level': risk,
    }


def predict_batch(df_input, model_name: str = 'Random Forest'):
    """
    Predict attrition for a DataFrame of employees.
    Returns df_input with added columns: Prediction, Probability, Risk_Level.
    """
    import pandas as pd
    import numpy as np
    models, scaler = load_all_models()
    model = models.get(model_name)

    if model is None:
        raise ValueError(f'Model "{model_name}" not found. Run eaps_ml_pipeline.py first.')

    feature_names = load_feature_names()

    # Align columns: keep only known features, fill missing with 0
    df = df_input.copy()
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0
    X = df[feature_names]

    if model_name in SCALED_MODELS and scaler:
        X = pd.DataFrame(scaler.transform(X), columns=X.columns)

    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]

    df_out = df_input.copy()
    df_out['Prediction']  = ['Leave' if p == 1 else 'Stay' for p in preds]
    df_out['Probability'] = np.round(probs, 4)
    df_out['Risk_Level']  = ['HIGH' if p >= 0.7 else ('MEDIUM' if p >= 0.4 else 'LOW')
                              for p in probs]
    return df_out
