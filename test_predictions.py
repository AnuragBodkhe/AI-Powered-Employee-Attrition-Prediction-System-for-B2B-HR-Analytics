"""
test_predictions.py
===================
Generate 100 realistic employees, run full prediction pipeline,
verify correctness, and report any issues.
"""

import sys, os, random, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader  import load_model, load_scaler, load_feature_names, load_thresholds, _risk_label, _reset_cache
from utils.preprocess    import preprocess_uploaded_csv

random.seed(42)
np.random.seed(42)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE 100 REALISTIC EMPLOYEES
# ─────────────────────────────────────────────────────────────────────────────
def generate_employees(n=100):
    depts    = ['Sales', 'Research & Development', 'Human Resources']
    roles    = {
        'Sales':                   ['Sales Executive', 'Sales Representative', 'Manager'],
        'Research & Development':  ['Research Scientist', 'Laboratory Technician',
                                    'Manufacturing Director', 'Healthcare Representative',
                                    'Research Director'],
        'Human Resources':         ['Human Resources', 'Manager'],
    }
    travel   = ['Non-Travel', 'Travel_Rarely', 'Travel_Frequently']
    genders  = ['Male', 'Female']
    marital  = ['Single', 'Married', 'Divorced']

    # We'll create ~20 high-risk profiles (should be Leave at 0.50 threshold)
    # and ~80 low-risk profiles (should be Stay)
    rows = []
    for i in range(n):
        is_high_risk = i < 20   # first 20 = high risk

        dept = random.choice(depts)
        role = random.choice(roles[dept])
        age  = random.randint(22, 35) if is_high_risk else random.randint(30, 58)

        row = {
            'EmployeeNumber':         i + 1001,
            'Age':                    age,
            'Gender':                 random.choice(genders),
            'MaritalStatus':          'Single' if is_high_risk else random.choice(marital),
            'Department':             dept,
            'JobRole':                role,
            'JobLevel':               random.randint(1, 2) if is_high_risk else random.randint(2, 5),
            'MonthlyIncome':          random.randint(1500, 3500) if is_high_risk else random.randint(4000, 18000),
            'HourlyRate':             random.randint(30, 55)  if is_high_risk else random.randint(50, 100),
            'MonthlyRate':            random.randint(2000, 8000) if is_high_risk else random.randint(8000, 27000),
            'PercentSalaryHike':      random.randint(11, 13) if is_high_risk else random.randint(13, 25),
            'StockOptionLevel':       0 if is_high_risk else random.randint(0, 3),
            'OverTime':               'Yes' if is_high_risk else random.choice(['No', 'No', 'No', 'Yes']),
            'BusinessTravel':         'Travel_Frequently' if is_high_risk else random.choice(travel),
            'JobSatisfaction':        random.randint(1, 2) if is_high_risk else random.randint(2, 4),
            'JobInvolvement':         random.randint(1, 2) if is_high_risk else random.randint(2, 4),
            'EnvironmentSatisfaction':random.randint(1, 2) if is_high_risk else random.randint(2, 4),
            'WorkLifeBalance':        random.randint(1, 2) if is_high_risk else random.randint(2, 4),
            'RelationshipSatisfaction':random.randint(1,2) if is_high_risk else random.randint(2, 4),
            'PerformanceRating':      random.randint(3, 4),
            'TrainingTimesLastYear':  random.randint(0, 2) if is_high_risk else random.randint(2, 6),
            'DistanceFromHome':       random.randint(15, 30) if is_high_risk else random.randint(1, 15),
            'NumCompaniesWorked':     random.randint(5, 9) if is_high_risk else random.randint(0, 4),
            'YearsAtCompany':         random.randint(0, 2)  if is_high_risk else random.randint(3, 30),
            'YearsInCurrentRole':     random.randint(0, 1)  if is_high_risk else random.randint(1, 12),
            'YearsSinceLastPromotion':random.randint(4, 12) if is_high_risk else random.randint(0, 5),
            'TotalWorkingYears':      random.randint(1, 5)  if is_high_risk else random.randint(5, 35),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    df['_profile'] = ['HighRisk' if i < 20 else 'LowRisk' for i in range(n)]
    return df

print("=" * 65)
print("  EAPS MODEL VERIFICATION — 100 Employee Test")
print("=" * 65)

df_raw = generate_employees(100)
print(f"\n[1] Generated {len(df_raw)} employees  |  High-risk profiles: 20  |  Low-risk: 80")

# ─────────────────────────────────────────────────────────────────────────────
# 2. RUN FULL PREDICTION PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
_reset_cache()
clf    = load_model()
scaler = load_scaler()
feats  = load_feature_names()
thresh = load_thresholds().get('XGBoost', 0.50)

print(f"\n[2] Model loaded  |  Threshold = {thresh:.2f}")

# Preprocess exactly as the batch route does
profiles = df_raw['_profile'].copy()
df_input = df_raw.drop(columns=['_profile'])

df_proc = preprocess_uploaded_csv(df_input.copy())
X_sc    = pd.DataFrame(scaler.transform(df_proc.values), columns=df_proc.columns)
probs   = clf.predict_proba(X_sc)[:, 1]
preds   = ['Leave' if p >= thresh else 'Stay' for p in probs]
risks   = [_risk_label(p) for p in probs]

# ─────────────────────────────────────────────────────────────────────────────
# 3. RESULTS SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
df_results = df_input[['EmployeeNumber', 'Age', 'JobLevel', 'MonthlyIncome', 'OverTime',
                        'JobSatisfaction', 'StockOptionLevel']].copy()
df_results['Profile']     = profiles.values
df_results['Probability'] = np.round(probs, 4)
df_results['Prediction']  = preds
df_results['Risk_Level']  = risks

leave_df = df_results[df_results['Prediction'] == 'Leave']
stay_df  = df_results[df_results['Prediction'] == 'Stay']
high_df  = df_results[df_results['Risk_Level'] == 'HIGH']
med_df   = df_results[df_results['Risk_Level'] == 'MEDIUM']

print(f"\n[3] PREDICTION DISTRIBUTION")
print(f"    Leave predicted   : {len(leave_df):3d} / 100  ({len(leave_df):.0f}%)")
print(f"    Stay predicted    : {len(stay_df):3d} / 100  ({len(stay_df):.0f}%)")
print(f"    HIGH risk         : {len(high_df):3d}")
print(f"    MEDIUM risk       : {len(med_df):3d}")
print(f"    LOW risk          : {100 - len(high_df) - len(med_df):3d}")
print(f"    Avg probability   : {probs.mean()*100:.1f}%")
print(f"    Min / Max prob    : {probs.min()*100:.1f}% / {probs.max()*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 4. SANITY CHECKS — correctness by profile
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[4] SANITY CHECK (by designed profile)")
hr_df   = df_results[df_results['Profile'] == 'HighRisk']
lr_df   = df_results[df_results['Profile'] == 'LowRisk']

hr_leave = (hr_df['Prediction'] == 'Leave').sum()
lr_stay  = (lr_df['Prediction'] == 'Stay').sum()

print(f"    High-risk  -> predicted Leave : {hr_leave}/20  ({hr_leave/20*100:.0f}%)")
print(f"    Low-risk   -> predicted Stay  : {lr_stay}/80  ({lr_stay/80*100:.0f}%)")

print(f"\n    High-risk avg prob : {hr_df['Probability'].mean()*100:.1f}%")
print(f"    Low-risk  avg prob : {lr_df['Probability'].mean()*100:.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# 5. SHOW SAMPLE PREDICTIONS
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[5] SAMPLE — Top 10 highest-risk employees")
top10 = df_results.nlargest(10, 'Probability')[
    ['EmployeeNumber','Profile','Probability','Prediction','Risk_Level',
     'Age','MonthlyIncome','OverTime','JobSatisfaction']]
print(top10.to_string(index=False))

print(f"\n[6] SAMPLE — 5 lowest-risk employees")
bot5 = df_results.nsmallest(5, 'Probability')[
    ['EmployeeNumber','Profile','Probability','Prediction','Risk_Level',
     'Age','MonthlyIncome','OverTime','JobSatisfaction']]
print(bot5.to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# 6. PROBLEM DETECTION
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n[7] PROBLEM DETECTION")
issues = []

leave_rate = len(leave_df) / 100
if leave_rate > 0.35:
    issues.append(f"OVER-PREDICTION: {leave_rate:.0%} predicted Leave (target ~20%)")
if leave_rate < 0.05:
    issues.append(f"UNDER-PREDICTION: only {leave_rate:.0%} predicted Leave")

if hr_leave < 10:
    issues.append(f"LOW RECALL: only {hr_leave}/20 high-risk employees correctly identified as Leave")

if probs.max() < 0.51:
    issues.append("NO EMPLOYEE exceeds 0.50 threshold — threshold may be too high for this model")

prob_range = probs.max() - probs.min()
if prob_range < 0.15:
    issues.append(f"NARROW PROBABILITY RANGE: {prob_range:.3f} — model may lack discrimination")

if not issues:
    print("    No issues detected — model is working correctly!")
else:
    for i, issue in enumerate(issues, 1):
        print(f"    ISSUE {i}: {issue}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. SAVE TEST RESULTS CSV
# ─────────────────────────────────────────────────────────────────────────────
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_100_employees_results.csv')
df_full = df_raw.drop(columns=['_profile']).copy()
df_full['Profile']     = profiles.values
df_full['Probability'] = np.round(probs, 4)
df_full['Prediction']  = preds
df_full['Risk_Level']  = risks
df_full.to_csv(out_path, index=False)
print(f"\n[8] Full results saved to: test_100_employees_results.csv")
print(f"\n{'='*65}")
print("  VERIFICATION COMPLETE")
print(f"{'='*65}")
