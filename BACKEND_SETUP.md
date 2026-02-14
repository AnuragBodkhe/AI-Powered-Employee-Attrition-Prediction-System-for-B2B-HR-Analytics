# Backend Setup Instructions

## Quick Start

### 1. Prerequisites
- Python 3.9+
- pip (Python package installer)
- Virtual environment (recommended)

### 2. Setup Virtual Environment

**Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install required packages
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file and update SECRET_KEY (optional but recommended for production)
# On Windows: type .env
# On Mac/Linux: cat .env
```

The default configuration uses SQLite for development, which requires no additional setup.

### 5. Run the Backend Server

```bash
# From the backend directory, run:
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

### 6. Verify Backend is Running

Visit the health check endpoint:
```
http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "application": "Employee Attrition Prediction System",
  "version": "1.0.0"
}
```

## Database

### SQLite (Development - Default)
- Database file: `attrition_db.db` (auto-created)
- Tables auto-created on startup
- No additional configuration needed

### PostgreSQL (Production)

To use PostgreSQL instead of SQLite:

1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE attrition_db;
   ```

3. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/attrition_db
   ```

4. Restart the server

## API Endpoints

### Authentication (`/api/auth/*`)
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get tokens
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout
- `PUT /api/auth/change-password` - Change password
- `POST /api/auth/refresh-token` - Refresh JWT tokens

### Predictions (`/api/predict/*`)
- `POST /api/predict/manual` - Single employee prediction
- `POST /api/predict/excel` - Bulk upload from Excel
- `GET /api/predict/history` - Get upload history
- `GET /api/predict/status/{upload_id}` - Get upload status
- `GET /api/predict/download/{upload_id}` - Download results

### Dashboard (`/api/dashboard/*`)
- `GET /api/dashboard/metrics` - KPI metrics
- `GET /api/dashboard/charts/risk-distribution` - Risk distribution chart
- `GET /api/dashboard/charts/department-comparison` - Department comparison
- `GET /api/dashboard/charts/salary-impact` - Salary impact analysis
- `GET /api/dashboard/filters/options` - Filter options
- `GET /api/dashboard/employees` - Employee list with filters
- `GET /api/dashboard/export/excel` - Export employee data

## Testing

### Using Interactive Docs
Visit `http://localhost:8000/docs` for Swagger UI

### Testing Authentication

1. **Register:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User",
    "organization_name": "Test Company"
  }'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

3. **Get Dashboard Metrics (with token):**
```bash
curl -X GET "http://localhost:8000/api/dashboard/metrics" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Troubleshooting

### ModuleNotFoundError
If you get `ModuleNotFoundError`, ensure:
1. Virtual environment is activated
2. Dependencies are installed with `pip install -r requirements.txt`
3. You're running from the project root directory

### Database errors
If database tables don't exist:
1. Delete `attrition_db.db` file
2. Restart the server
3. Tables will be auto-created

### Port already in use
If port 8000 is in use, specify a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### CORS errors
Check the `CORS_ORIGINS` in `.env` includes your frontend URL:
```
CORS_ORIGINS=["http://localhost:3000"]
```

## Next Steps

1. Start the frontend application on port 3000
2. Access the application at `http://localhost:3000`
3. Register a new account and start using the system

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Use a production database (PostgreSQL recommended)
3. Set a strong `SECRET_KEY`
4. Configure proper `CORS_ORIGINS`
5. Use environment variables for sensitive data
6. Deploy with a production ASGI server (Gunicorn + Uvicorn)

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```
