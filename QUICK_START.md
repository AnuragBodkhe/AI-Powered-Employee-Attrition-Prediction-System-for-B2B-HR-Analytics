# Quick Start Guide

## 🚀 5-Minute Setup

### Option 1: Using Docker (Easiest)

```bash
# 1. Start all services
docker-compose up -d

# 2. Access applications
# Backend API: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup (Development)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your settings:
# DATABASE_URL=postgresql://user:pass@localhost:5432/attrition_db
# SECRET_KEY=your-secret-key

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Update .env if needed:
# REACT_APP_API_URL=http://localhost:8000/api

# Start development server
npm start
```

---

## 📚 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | User interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| Health Check | http://localhost:8000/health | API health status |

---

## 🔐 Default Credentials (After Setup)

Register a new account through the frontend:
1. Go to http://localhost:3000/register
2. Create organization and user account
3. Login at http://localhost:3000/login

---

## 🤖 Train ML Model

```bash
cd backend

# Activate virtual environment first

# Run training pipeline
python -m app.ml.train

# This creates model artifacts in backend/models/
```

---

## 🧪 Test the System

### Backend
```bash
cd backend
pytest tests/
```

### Frontend
```bash
cd frontend
npm test
```

---

## 📊 Database Setup

### Using Docker Compose
PostgreSQL starts automatically with:
- Host: `localhost`
- Port: `5432`
- User: `attrition_user`
- Password: `attrition_password`
- Database: `attrition_db`

### Manual PostgreSQL
```bash
# Create database
createdb attrition_db

# Update backend/.env:
DATABASE_URL=postgresql://username:password@localhost:5432/attrition_db
```

---

## 🔌 API Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword",
    "full_name": "John Doe",
    "organization_name": "Acme Corp"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepassword"
  }'
```

### Single Prediction
```bash
curl -X POST http://localhost:8000/api/predict/manual \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "department": "Sales",
    "job_role": "Sales Manager",
    "monthly_income": 5000,
    "years_at_company": 5,
    "over_time": false,
    "job_satisfaction": 3,
    "work_life_balance": 3,
    "job_involvement": 3,
    "education_level": 2,
    "performance_rating": 3.5,
    "num_companies_worked": 1,
    "years_in_current_role": 2,
    "years_since_last_promotion": 1,
    "distance_from_home": 1,
    "training_times_last_year": 2
  }'
```

---

## 📁 Project Structure Overview

```
project-root/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── models/            # Database models
│   │   ├── ml/                # ML pipeline
│   │   ├── core/              # Config & security
│   │   └── main.py            # FastAPI app
│   ├── data/                  # Training data
│   ├── models/                # Saved ML models
│   ├── requirements.txt       # Python packages
│   └── Dockerfile
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API client
│   │   ├── utils/             # Utilities
│   │   └── App.js
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml         # Container orchestration
└── README.md                  # Full documentation
```

---

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### React App Not Loading
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 🔒 Security Notes

⚠️ **Before Production:**
- Change `SECRET_KEY` in `.env`
- Set `DEBUG=False`
- Update `CORS_ORIGINS` to your domain
- Configure proper database credentials
- Use environment-specific configurations
- Enable HTTPS
- Set strong passwords

---

## 📈 Performance Tips

- Model inference is cached in memory
- Database queries are indexed
- Frontend uses React lazy loading
- API implements pagination
- CORS is optimized
- Compression is enabled

---

## 🚀 Ready to Deploy?

See `README.md` for deployment instructions:
- Docker Compose
- AWS ECS + RDS
- GitHub Actions CI/CD
- Kubernetes

---

**Happy coding! 🎉**
