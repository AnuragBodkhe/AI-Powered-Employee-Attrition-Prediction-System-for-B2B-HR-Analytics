# Complete Setup Guide - Employee Attrition Prediction System

## Overview
This guide covers setting up and running both the backend (FastAPI) and frontend (React) applications.

## System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                      User Browser                            │
│                   React App (Port 3000)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP Requests
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   FastAPI Backend                            │
│                   (Port 8000)                                │
├─────────────┬────────────┬─────────────────────────────────┤
│   Auth API  │ Predict    │  Dashboard                      │
│   Routes    │   API      │  Routes                         │
└─────────────┼────────────┼─────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   SQLite Database   │
    │  (Development)      │
    └─────────────────────┘
```

## Prerequisites

### Required Software
- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **npm or yarn** - Comes with Node.js

### Verify Installations
```bash
# Check Python
python --version
# or
python3 --version

# Check Node.js
node --version
npm --version
```

---

## Part 1: Backend Setup (FastAPI)

### Step 1: Navigate to Project Root
```bash
cd "d:\AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics"
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Backend Dependencies
```bash
pip install -r backend/requirements.txt
```

### Step 4: Setup Environment Configuration
```bash
# Copy example environment file
copy .env.example .env
# Or on Linux/Mac:
# cp .env.example .env
```

### Step 5: Create Required Directories
```bash
# Create uploads directory
mkdir backend/uploads
# Or on Windows:
# New-Item -ItemType Directory -Force -Path "backend/uploads"
```

### Step 6: Start Backend Server

**Option A: Using Startup Script (Recommended)**

Windows:
```bash
run_backend.bat
```

Mac/Linux:
```bash
bash run_backend.sh
```

**Option B: Manual Start**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Verify Backend is Running

Open in your browser or use curl:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "application": "Employee Attrition Prediction System",
  "version": "1.0.0"
}
```

✅ **Backend is ready!** Visit API docs at: http://localhost:8000/docs

---

## Part 2: Frontend Setup (React)

### Step 1: Open New Terminal/Command Prompt
Don't close the backend terminal - keep it running!

### Step 2: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 3: Install Frontend Dependencies
```bash
npm install
```

### Step 4: Create Frontend Environment File
```bash
# Create .env file in frontend directory
echo REACT_APP_API_URL=http://localhost:8000/api > .env
```

Or manually create `frontend/.env` with:
```
REACT_APP_API_URL=http://localhost:8000/api
```

### Step 5: Start Frontend Development Server
```bash
npm start
```

The frontend will automatically open in your browser at `http://localhost:3000`

✅ **Frontend is ready!**

---

## Part 3: Testing the Full System

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Register a New Account
1. Visit `http://localhost:3000`
2. Click "Register"
3. Fill in the form:
   - Email: `test@example.com`
   - Password: `Test@123`
   - Full Name: `Test User`
   - Organization: `Test Company`
4. Click "Register"

### Test 3: Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test@123"
  }'
```

Response will include `access_token` and `refresh_token`

### Test 4: Access Dashboard
1. After logging in, you'll be redirected to the Dashboard
2. View KPI metrics and charts
3. Explore filter options and employee list

### Test 5: Make a Prediction
1. Navigate to "Predict" → "Manual Prediction"
2. Fill in employee details
3. Click "Predict"
4. View the risk score and contributing factors

### Test 6: Upload Excel File
1. Navigate to "Predict" → "Excel Upload"
2. Upload a CSV or Excel file with employee data
3. View processing status
4. Download results

---

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Use a different port
python -m uvicorn app.main:app --port 8001
# Then update frontend .env to use 8001
```

#### ModuleNotFoundError
```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r backend/requirements.txt
```

#### Database Errors
```bash
# Delete the old database and restart
rm attrition_db.db  # or delete manually on Windows
python -m uvicorn app.main:app --reload
```

#### CORS Errors in Frontend
Update `CORS_ORIGINS` in `.env`:
```
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

### Frontend Issues

#### `npm install` Failed
```bash
# Clear npm cache and try again
npm cache clean --force
npm install
```

#### Port 3000 Already in Use
```bash
# Use environment variable to specify a different port
set PORT=3001 && npm start  # Windows
PORT=3001 npm start  # Mac/Linux
```

#### Blank Page or 404
- Ensure backend is running
- Check browser console for errors (F12)
- Verify `REACT_APP_API_URL` in `frontend/.env`

#### Can't Connect to Backend
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `REACT_APP_API_URL` matches backend URL
3. Check CORS settings in backend `.env`

---

## API Documentation

### Interactive Docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

#### Predictions
- `POST /api/predict/manual` - Single employee prediction
- `POST /api/predict/excel` - Bulk upload
- `GET /api/predict/history` - Upload history
- `GET /api/predict/status/{upload_id}` - Check processing status

#### Dashboard
- `GET /api/dashboard/metrics` - KPI metrics
- `GET /api/dashboard/charts/* ` - Chart data
- `GET /api/dashboard/employees` - Employee list
- `GET /api/dashboard/export/excel` - Export data

---

## Development Workflow

### 1. Backend Development
- Backend runs on http://localhost:8000 with hot-reload
- Edit files in `backend/app/*`
- Server automatically restarts on changes

### 2. Frontend Development
- Frontend runs on http://localhost:3000 with hot-reload
- Edit files in `frontend/src/*`
- Page automatically refreshes on changes

### 3. Debugging

**Backend:**
```bash
# Use verbose logging
export DEBUG=True  # Linux/Mac
set DEBUG=True     # Windows
# Then restart backend
```

**Frontend:**
- Press F12 to open browser DevTools
- Check Console tab for errors
- Check Network tab for API calls

---

## Running in Production

### Backend Production Build
```bash
# Build and run with production settings
set DEBUG=False
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Production Build
```bash
cd frontend
npm run build
# Output goes to frontend/build/
```

### Environment Variables for Production
Update `.env`:
```
DEBUG=False
SECRET_KEY=your-secret-production-key
CORS_ORIGINS=["https://yourdomain.com"]
DATABASE_URL=postgresql://user:pass@host:5432/db
```

---

## Docker Setup (Optional)

### Run with Docker Compose
```bash
docker-compose up -d
```

This will start:
- Backend on port 8000
- Frontend on port 3000
- PostgreSQL database

---

## Useful Commands

### Backend
```bash
# Run tests
pytest backend/tests

# Format code
black backend/

# Lint code
flake8 backend/

# Run migrations (if using PostgreSQL)
alembic upgrade head
```

### Frontend
```bash
# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint

# Analyze bundle size
npm run analyze
```

---

## Support & Documentation

- **Backend Docs**: See `BACKEND_SETUP.md`
- **Frontend Docs**: See `frontend/IMPLEMENTATION_STATUS.md`
- **Project Overview**: See `PROJECT_OVERVIEW.md`
- **API Docs**: http://localhost:8000/docs (when running)

---

## Next Steps

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 3000
3. 📝 Register a test account
4. 🔍 Explore the dashboard
5. 📊 Make predictions
6. 📈 Upload employee data

Enjoy using the Employee Attrition Prediction System!
