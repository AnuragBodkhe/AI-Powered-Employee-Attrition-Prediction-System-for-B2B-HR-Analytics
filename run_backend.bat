@echo off
REM Backend startup script for Windows

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
pip install -r backend\requirements.txt

REM Create uploads directory if it doesn't exist
if not exist "backend\uploads" (
    mkdir backend\uploads
)

REM Copy .env if it doesn't exist
if not exist ".env" (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo WARNING: Please review and update .env file if needed
)

REM Start the server
echo Starting Employee Attrition Prediction Backend...
echo API will be available at: http://localhost:8000
echo Docs available at: http://localhost:8000/docs
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
