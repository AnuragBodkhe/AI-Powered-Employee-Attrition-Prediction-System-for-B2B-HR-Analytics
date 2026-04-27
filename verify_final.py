import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np, pandas as pd
from utils.model_loader import (load_model, load_scaler, load_feature_names,
                                load_thresholds, _risk_label, _reset_cache, predict_single)
from utils.preprocess   import preprocess_uploaded_csv, encode_input

_reset_cache()
clf    = load_model()
scaler = load_scaler()
feats  = load_feature_names()
thresh = load_thresholds().get('XGBoost', 0.50)

DATA = os.path.join('data', 'WA_Fn-UseC_-HR-Employee-Attrition.csv')
df   = pd.read_csv(DATA)
y    = (df['Attrition'] == 'Yes').astype(int).values
proc = preprocess_uploaded_csv(df.copy())
X_sc = pd.DataFrame(scaler.transform(proc.values), columns=feats)
p    = clf.predict_proba(X_sc)[:, 1]

preds = (p >= thresh).astype(int)
tp = int(((preds==1) & (y==1)).sum())
fp = int(((preds==1) & (y==0)).sum())
fn = int(((preds==0) & (y==1)).sum())
prec = tp/(tp+fp) if (tp+fp) > 0 else 0
rec  = tp/(tp+fn) if (tp+fn) > 0 else 0
f1   = 2*prec*rec/(prec+rec) if (prec+rec) > 0 else 0

print('=== FINAL MODEL VERIFICATION ===')
print('Threshold         :', thresh)
print('Leavers avg prob  :', round(p[y==1].mean()*100, 1), '%  max:', round(p[y==1].max()*100, 1), '%')
print('Stayers avg prob  :', round(p[y==0].mean()*100, 1), '%  max:', round(p[y==0].max()*100, 1), '%')
print('Separation        :', round((p[y==1].mean()-p[y==0].mean())*100, 1), 'pp')
print('Predicted Leave   :', round(preds.mean()*100, 1), '%')
print('Precision =', round(prec*100,1), '%  Recall =', round(rec*100,1), '%  F1 =', round(f1,3))

print()
print('=== SAMPLE SINGLE PREDICTIONS ===')
test_cases = [
    ('HIGH RISK', {
        'Age': 25, 'Gender': 'Male', 'MaritalStatus': 'Single',
        'Department': 'Sales', 'JobRole': 'Sales Representative',
        'JobLevel': 1, 'MonthlyIncome': 2500, 'HourlyRate': 35,
        'MonthlyRate': 4000, 'PercentSalaryHike': 11, 'StockOptionLevel': 0,
        'OverTime': 'Yes', 'BusinessTravel': 'Travel_Frequently',
        'JobSatisfaction': 1, 'JobInvolvement': 1, 'EnvironmentSatisfaction': 1,
        'WorkLifeBalance': 1, 'RelationshipSatisfaction': 1, 'PerformanceRating': 3,
        'TrainingTimesLastYear': 0, 'DistanceFromHome': 25, 'NumCompaniesWorked': 7,
        'YearsAtCompany': 1, 'YearsInCurrentRole': 0, 'YearsSinceLastPromotion': 8,
        'TotalWorkingYears': 2,
    }),
    ('LOW RISK', {
        'Age': 45, 'Gender': 'Male', 'MaritalStatus': 'Married',
        'Department': 'Research & Development', 'JobRole': 'Research Director',
        'JobLevel': 4, 'MonthlyIncome': 14000, 'HourlyRate': 80,
        'MonthlyRate': 20000, 'PercentSalaryHike': 20, 'StockOptionLevel': 3,
        'OverTime': 'No', 'BusinessTravel': 'Non-Travel',
        'JobSatisfaction': 4, 'JobInvolvement': 4, 'EnvironmentSatisfaction': 4,
        'WorkLifeBalance': 4, 'RelationshipSatisfaction': 4, 'PerformanceRating': 3,
        'TrainingTimesLastYear': 5, 'DistanceFromHome': 3, 'NumCompaniesWorked': 1,
        'YearsAtCompany': 15, 'YearsInCurrentRole': 8, 'YearsSinceLastPromotion': 2,
        'TotalWorkingYears': 20,
    }),
]
for label, case in test_cases:
    X_enc = encode_input(case)
    res   = predict_single(X_enc.iloc[0].to_dict())
    prob  = round(res['probability']*100, 1)
    pred  = res['prediction']
    risk  = res['risk_level']
    thv   = res['threshold_used']
    print(f'  [{label}]  prob={prob}%  prediction={pred}  risk={risk}  threshold={thv}')
