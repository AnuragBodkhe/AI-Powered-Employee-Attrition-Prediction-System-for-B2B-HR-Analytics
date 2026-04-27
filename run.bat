@echo off
title EAPS - Employee Attrition Prediction System
color 0A
echo.
echo ===============================================================
echo   EAPS - Employee Attrition Prediction System
echo   Starting Flask Server...
echo ===============================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [2/3] Checking required packages...
python -c "import flask, pandas, joblib, sklearn; print('   All core packages OK')"
if errorlevel 1 (
    echo.
    echo Installing missing packages...
    pip install flask pandas scikit-learn joblib xgboost shap
)

echo [3/3] Starting Flask app on http://localhost:5000 ...
echo.
echo Press CTRL+C to stop the server.
echo.

python -u flask_app\server.py

pause
