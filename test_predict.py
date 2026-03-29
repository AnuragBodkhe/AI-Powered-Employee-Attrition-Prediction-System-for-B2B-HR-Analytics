import sys
sys.path.insert(0, '.')

from utils.preprocess import encode_input
from utils.model_loader import predict_single

data = {
    'Age': 35, 'Gender': 'Male', 'MaritalStatus': 'Single',
    'Department': 'Sales', 'JobRole': 'Sales Executive', 'JobLevel': 2,
    'JobInvolvement': 3, 'JobSatisfaction': 2, 'OverTime': 'Yes',
    'BusinessTravel': 'Travel_Frequently', 'MonthlyIncome': 2500,
    'HourlyRate': 65, 'MonthlyRate': 14000, 'PercentSalaryHike': 11,
    'StockOptionLevel': 0, 'DistanceFromHome': 25, 'NumCompaniesWorked': 7,
    'EnvironmentSatisfaction': 2, 'WorkLifeBalance': 1,
    'RelationshipSatisfaction': 3, 'PerformanceRating': 3,
    'TrainingTimesLastYear': 1, 'YearsAtCompany': 1,
    'YearsInCurrentRole': 1, 'YearsSinceLastPromotion': 0,
}

X = encode_input(data)
print('Encoded shape:', X.shape)
print('Columns:', list(X.columns))
print()

result = predict_single(X.iloc[0].to_dict(), 'Random Forest')
print('Result:', result)

result2 = predict_single(X.iloc[0].to_dict(), 'XGBoost')
print('XGBoost:', result2)
