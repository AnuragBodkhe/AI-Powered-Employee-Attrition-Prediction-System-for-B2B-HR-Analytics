#!/bin/bash
# Backend startup script for Mac/Linux

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -r backend/requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p backend/uploads

# Copy .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please review and update .env file if needed"
fi

# Start the server
echo "Starting Employee Attrition Prediction Backend..."
echo "API will be available at: http://localhost:8000"
echo "Docs available at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the server"

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
