"""
utils/preprocess.py
Preprocessing helpers for user input → model-ready features.

KEY FIX: Now loads and uses the same label_encoders.pkl saved during
training, ensuring inference encoding exactly matches training encoding.
Falls back to hardcoded CATEGORICAL_MAPS if pkl not available.
"""

import os
import pandas as pd
import numpy as np

# Exact 25 features the models were trained on (verified from feature_names.pkl)
IBM_FEATURES = [
    'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
    'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'WorkLifeBalance', 'JobSatisfaction',
    'PerformanceRating', 'TrainingTimesLastYear', 'EnvironmentSatisfaction',
    'RelationshipSatisfaction', 'JobInvolvement', 'DistanceFromHome',
    'NumCompaniesWorked', 'Gender', 'OverTime',
    'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
]

# Fallback encoding maps (used if label_encoders.pkl is missing)
# These MUST match sklearn LabelEncoder alphabetical sort order.
CATEGORICAL_MAPS = {
    'BusinessTravel':  {'Non-Travel': 0, 'Travel_Frequently': 1, 'Travel_Rarely': 2},
    'Department':      {'Human Resources': 0, 'Research & Development': 1, 'Sales': 2},
    'Gender':          {'Female': 0, 'Male': 1},
    'JobRole':         {'Healthcare Representative': 0, 'Human Resources': 1,
                        'Laboratory Technician': 2, 'Manager': 3,
                        'Manufacturing Director': 4, 'Research Director': 5,
                        'Research Scientist': 6, 'Sales Executive': 7,
                        'Sales Representative': 8},
    'MaritalStatus':   {'Divorced': 0, 'Married': 1, 'Single': 2},
    'OverTime':        {'No': 0, 'Yes': 1},
}

# Column aliasing: map non-standard names → IBM HR names
COLUMN_ALIASES = {
    'Overtime':      'OverTime',
    'overtime':      'OverTime',
    'over_time':     'OverTime',
    'Marital_Status':  'MaritalStatus',
    'marital_status':  'MaritalStatus',
    'Job_Role':        'JobRole',
    'job_role':        'JobRole',
    'Monthly_Income':  'MonthlyIncome',
    'monthly_income':  'MonthlyIncome',
    'Work_Life_Balance': 'WorkLifeBalance',
    'work_life_balance': 'WorkLifeBalance',
    'Job_Satisfaction':  'JobSatisfaction',
    'job_satisfaction':  'JobSatisfaction',
    'Employee_ID':       'EmployeeNumber',
    'Total_Working_Years': 'TotalWorkingYears',
    'Years_At_Company':   'YearsAtCompany',
    'Years_In_Current_Role': 'YearsInCurrentRole',
    'Years_Since_Last_Promotion': 'YearsSinceLastPromotion',
    'Years_With_Curr_Manager': 'YearsWithCurrManager',
    'Distance_From_Home': 'DistanceFromHome',
    'Num_Companies_Worked': 'NumCompaniesWorked',
    'Percent_Salary_Hike': 'PercentSalaryHike',
    'Performance_Rating': 'PerformanceRating',
    'Relationship_Satisfaction': 'RelationshipSatisfaction',
    'Stock_Option_Level': 'StockOptionLevel',
    'Training_Times_Last_Year': 'TrainingTimesLastYear',
    'Environment_Satisfaction': 'EnvironmentSatisfaction',
    'Education_Field': 'EducationField',
    'Business_Travel': 'BusinessTravel',
    'Hourly_Rate': 'HourlyRate',
    'Monthly_Rate': 'MonthlyRate',
    'Daily_Rate': 'DailyRate',
    'Job_Level': 'JobLevel',
    'Job_Involvement': 'JobInvolvement',
}

# ── Load label encoders from training artifact ────────────────────────────────
_label_encoders = None
_le_load_attempted = False

def _get_label_encoders():
    """Lazy-load training label encoders for consistent inference encoding."""
    global _label_encoders, _le_load_attempted
    if _le_load_attempted:
        return _label_encoders
    _le_load_attempted = True
    try:
        import joblib
        le_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'label_encoders.pkl')
        if os.path.exists(le_path):
            _label_encoders = joblib.load(le_path)
    except Exception:
        _label_encoders = None
    return _label_encoders


def _encode_categorical_value(col: str, val) -> int:
    """
    Encode a single categorical value using training LabelEncoder if available,
    otherwise fall back to CATEGORICAL_MAPS.
    """
    le_dict = _get_label_encoders()

    # Try training LabelEncoder first (most accurate)
    if le_dict and col in le_dict:
        le = le_dict[col]
        val_str = str(val)
        if val_str in le.classes_:
            return int(le.transform([val_str])[0])
        # Unknown value → return 0 (safe fallback)
        return 0

    # Fall back to hardcoded map
    if col in CATEGORICAL_MAPS:
        return CATEGORICAL_MAPS[col].get(str(val), 0)

    return 0


def encode_input(user_input: dict) -> pd.DataFrame:
    """
    Takes a raw user input dict (from the Flask form) and returns
    a DataFrame with the exact 25 features expected by the model.
    Categorical values are encoded using the same LabelEncoder as training.
    """
    row = {}
    for col in IBM_FEATURES:
        val = user_input.get(col, 0)
        if col in CATEGORICAL_MAPS or (_get_label_encoders() and col in _get_label_encoders()):
            row[col] = _encode_categorical_value(col, val)
        else:
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = 0
    return pd.DataFrame([row])


def preprocess_uploaded_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess a user-uploaded CSV for batch prediction.
    Handles both IBM-style and custom-style columns.
    Uses the exact same LabelEncoders as training (loaded from label_encoders.pkl).
    """
    df = df.copy()

    # Normalise column aliases
    df.rename(columns=COLUMN_ALIASES, inplace=True)

    # Drop target if present
    for col in ['Attrition', 'attrition', 'ATTRITION']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Drop constants / ID columns
    for col in ['EmployeeCount', 'Over18', 'StandardHours',
                'EmployeeNumber', 'Employee_ID', 'DailyRate']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    le_dict = _get_label_encoders()

    # Apply training LabelEncoders first (for known categorical cols)
    if le_dict:
        for col, le in le_dict.items():
            if col in df.columns:
                known = set(le.classes_)
                df[col] = df[col].astype(str).apply(
                    lambda x: int(le.transform([x])[0]) if x in known else 0
                )
    else:
        # Fallback: use hardcoded CATEGORICAL_MAPS
        for col, mapping in CATEGORICAL_MAPS.items():
            if col in df.columns:
                df[col] = df[col].astype(str).map(mapping).fillna(0).astype(int)

    # Encode any remaining object columns with consistent alphabetical LabelEncoder
    for col in df.select_dtypes(include='object').columns:
        converted = pd.to_numeric(df[col], errors='coerce')
        if converted.notna().mean() > 0.5:
            df[col] = converted.fillna(0)
        else:
            cats = sorted(df[col].dropna().unique())
            mapping = {c: i for i, c in enumerate(cats)}
            df[col] = df[col].map(mapping).fillna(0).astype(int)

    # Convert all remaining columns to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Load feature names from pkl if available, fall back to IBM_FEATURES
    try:
        import joblib
        fn_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'feature_names.pkl')
        feature_names = joblib.load(fn_path) if os.path.exists(fn_path) else IBM_FEATURES
    except Exception:
        feature_names = IBM_FEATURES

    # Add missing feature columns (fill zero)
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0

    # Keep only known features if all are present
    available = [c for c in feature_names if c in df.columns]
    if len(available) == len(feature_names):
        return df[feature_names]

    return df[available] if available else df.select_dtypes(include=[np.number])
