"""
utils/model_loader.py
Loads trained .pkl models and scaler from the models/ directory.
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
SCALER_FILE = 'scaler.pkl'

# Models that need scaled input
SCALED_MODELS = {'Logistic Regression', 'SVM'}


@st.cache_resource(show_spinner="Loading models...")
def load_all_models():
    """Load all trained models and the scaler. Cached after first call."""
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


def predict_single(employee_dict: dict, model_name: str = 'Random Forest') -> dict:
    """
    Predict attrition for one employee.
    Returns: { prediction, probability, risk_level }
    """
    import pandas as pd
    models, scaler = load_all_models()
    model = models.get(model_name)

    if model is None:
        return {'error': f'Model {model_name} not found. Run eaps_ml_pipeline.py first.'}

    df = pd.DataFrame([employee_dict])

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
        raise ValueError(f'Model {model_name} not found. Run eaps_ml_pipeline.py first.')

    df = df_input.copy()

    if model_name in SCALED_MODELS and scaler:
        X = pd.DataFrame(scaler.transform(df), columns=df.columns)
    else:
        X = df

    preds = model.predict(X)
    probs = model.predict_proba(X)[:, 1]

    df_input = df_input.copy()
    df_input['Prediction']  = ['Leave' if p == 1 else 'Stay' for p in preds]
    df_input['Probability'] = np.round(probs, 4)
    df_input['Risk_Level']  = ['HIGH' if p >= 0.7 else ('MEDIUM' if p >= 0.4 else 'LOW')
                                for p in probs]
    return df_input
