"""
utils/preprocess.py
===================
Preprocessing helpers for user input → model-ready features (XGBoost v3).

Key changes for v3:
  - Loads label_encoders_v3.pkl and feature_names_v3.pkl
  - Computes composite features: SatisfactionIndex, TenureRatio, CompensationGap
  - TotalWorkingYears added to IBM_FEATURES (required by v3 model)
  - Risk labels aligned to model threshold (dynamic, not fixed 40/70)
"""

import os
import pandas as pd
import numpy as np

# ── v3 Base features (26 raw — excludes the 3 composite which are computed) ──
IBM_FEATURES_RAW = [
    'Age', 'MaritalStatus', 'Department', 'JobRole', 'JobLevel',
    'MonthlyIncome', 'HourlyRate', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'TotalWorkingYears', 'WorkLifeBalance',
    'JobSatisfaction', 'PerformanceRating', 'TrainingTimesLastYear',
    'EnvironmentSatisfaction', 'RelationshipSatisfaction', 'JobInvolvement',
    'DistanceFromHome', 'NumCompaniesWorked', 'Gender', 'OverTime',
    'MonthlyRate', 'StockOptionLevel', 'PercentSalaryHike', 'BusinessTravel',
]

# Full v3 feature list (raw + composite) — must match feature_names_v3.pkl order
V3_FEATURES = IBM_FEATURES_RAW + ['SatisfactionIndex', 'TenureRatio', 'CompensationGap']

# Fallback encoding maps (must match sklearn LabelEncoder alphabetical sort)
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
    'Overtime':                  'OverTime',
    'overtime':                  'OverTime',
    'over_time':                 'OverTime',
    'Marital_Status':            'MaritalStatus',
    'marital_status':            'MaritalStatus',
    'Job_Role':                  'JobRole',
    'job_role':                  'JobRole',
    'Monthly_Income':            'MonthlyIncome',
    'monthly_income':            'MonthlyIncome',
    'Work_Life_Balance':         'WorkLifeBalance',
    'work_life_balance':         'WorkLifeBalance',
    'Job_Satisfaction':          'JobSatisfaction',
    'job_satisfaction':          'JobSatisfaction',
    'Employee_ID':               'EmployeeNumber',
    'Total_Working_Years':       'TotalWorkingYears',
    'Years_At_Company':          'YearsAtCompany',
    'Years_at_Company':          'YearsAtCompany',
    'Years_In_Current_Role':     'YearsInCurrentRole',
    'Years_in_Current_Role':     'YearsInCurrentRole',
    'Years_Since_Last_Promotion':'YearsSinceLastPromotion',
    'Years_With_Curr_Manager':   'YearsWithCurrManager',
    'Distance_From_Home':        'DistanceFromHome',
    'Num_Companies_Worked':      'NumCompaniesWorked',
    'Number_of_Companies_Worked':'NumCompaniesWorked',
    'Percent_Salary_Hike':       'PercentSalaryHike',
    'Performance_Rating':        'PerformanceRating',
    'Relationship_Satisfaction': 'RelationshipSatisfaction',
    'Relationship_with_Manager': 'RelationshipSatisfaction',
    'Stock_Option_Level':        'StockOptionLevel',
    'Training_Times_Last_Year':  'TrainingTimesLastYear',
    'Training_Hours_Last_Year':  'TrainingTimesLastYear',
    'Environment_Satisfaction':  'EnvironmentSatisfaction',
    'Work_Environment_Satisfaction': 'EnvironmentSatisfaction',
    'Education_Field':           'EducationField',
    'Business_Travel':           'BusinessTravel',
    'Hourly_Rate':               'HourlyRate',
    'Monthly_Rate':              'MonthlyRate',
    'Daily_Rate':                'DailyRate',
    'Job_Level':                 'JobLevel',
    'Job_Involvement':           'JobInvolvement',
}


def _compute_composite(df: pd.DataFrame) -> pd.DataFrame:
    """Add the 3 composite features used by XGBoost v3 training."""
    df = df.copy()
    sat_cols = ['JobSatisfaction', 'EnvironmentSatisfaction',
                'RelationshipSatisfaction', 'WorkLifeBalance']
    existing = [c for c in sat_cols if c in df.columns]
    df['SatisfactionIndex'] = df[existing].mean(axis=1) if existing else 2.5

    yac = df['YearsAtCompany'].fillna(0) if 'YearsAtCompany' in df.columns else 0
    twy = df['TotalWorkingYears'].fillna(0) if 'TotalWorkingYears' in df.columns else 10
    df['TenureRatio'] = yac / (twy + 1)

    inc = df['MonthlyIncome'].fillna(5000) if 'MonthlyIncome' in df.columns else 5000
    jl  = df['JobLevel'].fillna(2) if 'JobLevel' in df.columns else 2
    df['CompensationGap'] = inc / (jl * 1000).clip(lower=1000)

    return df


# ── Lazy-load v3 label encoders ───────────────────────────────────────────────
_label_encoders = None
_le_load_attempted = False


def _get_label_encoders():
    """Lazy-load v3 training label encoders for consistent inference encoding."""
    global _label_encoders, _le_load_attempted
    if _le_load_attempted:
        return _label_encoders
    _le_load_attempted = True
    try:
        import joblib
        # Prefer v3 encoders, fall back to legacy
        for fname in ['label_encoders_v3.pkl', 'label_encoders.pkl']:
            le_path = os.path.join(os.path.dirname(__file__), '..', 'models', fname)
            if os.path.exists(le_path):
                _label_encoders = joblib.load(le_path)
                break
    except Exception:
        _label_encoders = None
    return _label_encoders


def _get_feature_names():
    """Load v3 feature names (29 features including composite)."""
    try:
        import joblib
        for fname in ['feature_names_v3.pkl', 'feature_names.pkl']:
            path = os.path.join(os.path.dirname(__file__), '..', 'models', fname)
            if os.path.exists(path):
                names = joblib.load(path)
                # Only use if it includes the composite features
                if 'SatisfactionIndex' in names:
                    return names
    except Exception:
        pass
    return V3_FEATURES


def _encode_categorical_value(col: str, val) -> int:
    """Encode a single categorical value using training LabelEncoder."""
    le_dict = _get_label_encoders()
    if le_dict and col in le_dict:
        le = le_dict[col]
        val_str = str(val)
        if val_str in le.classes_:
            return int(le.transform([val_str])[0])
        return 0
    if col in CATEGORICAL_MAPS:
        return CATEGORICAL_MAPS[col].get(str(val), 0)
    return 0


def encode_input(user_input: dict) -> pd.DataFrame:
    """
    Takes a raw user input dict (from the Flask form) and returns a DataFrame
    with the exact 29 features expected by XGBoost v3 (including composites).
    """
    row = {}
    le_dict = _get_label_encoders()

    # Fill raw features
    for col in IBM_FEATURES_RAW:
        val = user_input.get(col, 0)
        is_cat = col in CATEGORICAL_MAPS or (le_dict and col in le_dict)
        if is_cat:
            row[col] = _encode_categorical_value(col, val)
        else:
            try:
                row[col] = float(val)
            except (ValueError, TypeError):
                row[col] = 0.0

    df = pd.DataFrame([row])

    # Compute composite features
    df = _compute_composite(df)

    # Ensure correct column order
    feature_names = _get_feature_names()
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0.0

    return df[feature_names]


def preprocess_uploaded_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess a user-uploaded CSV for batch prediction.
    Handles both IBM-style and custom-style columns.
    Computes composite features required by XGBoost v3.
    """
    df = df.copy()

    # Normalise column aliases
    df.rename(columns=COLUMN_ALIASES, inplace=True)

    # Drop target if present
    for col in ['Attrition', 'attrition', 'ATTRITION']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Drop irrelevant ID/constant columns
    for col in ['EmployeeCount', 'Over18', 'StandardHours',
                'EmployeeNumber', 'Employee_ID', 'DailyRate']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    le_dict = _get_label_encoders()

    # Apply training LabelEncoders (for known categorical cols)
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

    # Encode any remaining object columns
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

    # Add TotalWorkingYears if missing (estimate from Age)
    if 'TotalWorkingYears' not in df.columns:
        age = df['Age'] if 'Age' in df.columns else 30
        df['TotalWorkingYears'] = (age - 18).clip(lower=0)

    # Compute composite features
    df = _compute_composite(df)

    # Load v3 feature names
    feature_names = _get_feature_names()

    # Add any missing feature columns (fill zero)
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0.0

    # Return in correct order
    available = [c for c in feature_names if c in df.columns]
    if len(available) == len(feature_names):
        return df[feature_names]

    return df[available] if available else df.select_dtypes(include=[np.number])
