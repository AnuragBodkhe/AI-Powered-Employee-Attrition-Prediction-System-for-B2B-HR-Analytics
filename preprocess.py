"""
utils/preprocess.py
Preprocessing helpers for user input → model-ready features.
Mirrors the exact encoding used during training on IBM HR dataset.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

# IBM HR Analytics feature columns (after dropping constants)
IBM_FEATURES = [
    'Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
    'Education', 'EducationField', 'EnvironmentSatisfaction', 'Gender',
    'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
    'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
    'OverTime', 'PercentSalaryHike', 'PerformanceRating',
    'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
    'YearsInCurrentRole', 'YearsSinceLastPromotion', 'YearsWithCurrManager'
]

# Categorical columns and their label-encoding maps (fitted on IBM training data)
CATEGORICAL_MAPS = {
    'BusinessTravel':  {'Non-Travel': 0, 'Travel_Frequently': 1, 'Travel_Rarely': 2},
    'Department':      {'Human Resources': 0, 'Research & Development': 1, 'Sales': 2},
    'EducationField':  {'Human Resources': 0, 'Life Sciences': 1, 'Marketing': 2,
                        'Medical': 3, 'Other': 4, 'Technical Degree': 5},
    'Gender':          {'Female': 0, 'Male': 1},
    'JobRole':         {'Healthcare Representative': 0, 'Human Resources': 1,
                        'Laboratory Technician': 2, 'Manager': 3,
                        'Manufacturing Director': 4, 'Research Director': 5,
                        'Research Scientist': 6, 'Sales Executive': 7,
                        'Sales Representative': 8},
    'MaritalStatus':   {'Divorced': 0, 'Married': 1, 'Single': 2},
    'OverTime':        {'No': 0, 'Yes': 1},
}


def encode_input(user_input: dict) -> pd.DataFrame:
    """
    Takes a raw user input dict (from Streamlit form) and returns
    a DataFrame with the exact 30 features expected by the model.
    """
    row = {}
    for col in IBM_FEATURES:
        val = user_input.get(col, 0)
        if col in CATEGORICAL_MAPS:
            row[col] = CATEGORICAL_MAPS[col].get(val, 0)
        else:
            row[col] = val
    return pd.DataFrame([row])


def preprocess_uploaded_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess a user-uploaded CSV for batch prediction.
    Handles both IBM-style and custom-style columns.
    Drops the Attrition column if present (it's the target).
    """
    df = df.copy()

    # Drop target if present
    for col in ['Attrition', 'attrition']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Drop constants
    for col in ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber', 'Employee_ID']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Encode all remaining object columns
    le = LabelEncoder()
    for col in df.select_dtypes(include='object').columns:
        df[col] = le.fit_transform(df[col].astype(str))

    # Keep only known features if possible
    known = [c for c in IBM_FEATURES if c in df.columns]
    if len(known) == len(IBM_FEATURES):
        return df[IBM_FEATURES]

    # Otherwise use all numeric columns
    return df.select_dtypes(include=[np.number])
