"""
utils/preprocess.py
Preprocessing helpers for user input → model-ready features.
Mirrors the exact encoding used during training on IBM HR dataset.
"""

import pandas as pd
import numpy as np

# Exact 25 features the models were trained on (verified from feature_names.pkl)
IBM_FEATURES = [
    'Age', 'BusinessTravel', 'Department', 'DistanceFromHome',
    'EnvironmentSatisfaction', 'Gender', 'HourlyRate',
    'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction',
    'MaritalStatus', 'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
    'OverTime', 'PercentSalaryHike', 'PerformanceRating',
    'RelationshipSatisfaction', 'StockOptionLevel',
    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany',
    'YearsInCurrentRole', 'YearsSinceLastPromotion'
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


def encode_input(user_input: dict) -> pd.DataFrame:
    """
    Takes a raw user input dict (from the Flask form) and returns
    a DataFrame with the exact 30 features expected by the model.
    Categorical values are mapped using the same encoding as training.
    """
    row = {}
    for col in IBM_FEATURES:
        val = user_input.get(col, 0)
        if col in CATEGORICAL_MAPS:
            # Use exact training-time mapping; default to 0 for unknown values
            row[col] = CATEGORICAL_MAPS[col].get(str(val), 0)
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
    Uses the exact same CATEGORICAL_MAPS as training (not generic LabelEncoder).
    """
    df = df.copy()

    # Normalise column aliases
    df.rename(columns=COLUMN_ALIASES, inplace=True)

    # Drop target if present
    for col in ['Attrition', 'attrition', 'ATTRITION']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Drop constants / ID columns
    for col in ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber', 'Employee_ID']:
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # Apply consistent categorical encoding (same as training)
    for col, mapping in CATEGORICAL_MAPS.items():
        if col in df.columns:
            # Map string values; unknown → 0
            df[col] = df[col].astype(str).map(mapping).fillna(0).astype(int)

    # Encode any remaining object columns with a consistent fallback
    for col in df.select_dtypes(include='object').columns:
        # Try numeric conversion first
        converted = pd.to_numeric(df[col], errors='coerce')
        if converted.notna().mean() > 0.5:
            df[col] = converted.fillna(0)
        else:
            # Alphabetical label encoding as a last resort
            cats = sorted(df[col].dropna().unique())
            mapping = {c: i for i, c in enumerate(cats)}
            df[col] = df[col].map(mapping).fillna(0).astype(int)

    # Convert all remaining columns to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Keep only known features if all are present
    available = [c for c in IBM_FEATURES if c in df.columns]
    if len(available) == len(IBM_FEATURES):
        return df[IBM_FEATURES]

    # Otherwise return all numeric columns (partial match)
    return df[available] if available else df.select_dtypes(include=[np.number])
