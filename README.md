# AI-Powered Employee Attrition Prediction System

A comprehensive B2B HR analytics platform using machine learning to predict employee attrition risk and provide actionable insights for HR departments.

## 🚀 Features

### Core Functionality
- **Dual Prediction Modes**
  - Manual: Single employee prediction via form
  - Bulk: Excel file upload for batch predictions
  
- **Advanced Analytics**
  - Real-time risk assessment
  - Department-wise attrition analysis
  - Salary impact visualization
  - Risk factor explanations (SHAP)

- **Dashboard & Reporting**
  - KPI metrics and trends
  - Interactive charts and filters
  - Employee risk database
  - Excel export capabilities

### Technical Features
- Multi-tenant architecture
- Role-based access control
- JWT authentication
- PostgreSQL database with 6 optimized tables
- RESTful API with FastAPI
- React-based responsive UI
- ML models: Logistic Regression, Random Forest, XGBoost

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints (auth, predict, dashboard)
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── ml/               # ML pipeline and prediction engine
│   │   ├── core/             # Configuration and security
│   │   ├── utils/            # Utilities
│   │   └── main.py           # FastAPI entry point
│   ├── data/                 # Training data
│   ├── models/               # Saved ML artifacts
│   ├── tests/                # Test suite
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── utils/            # Utilities
│   │   ├── styles/           # CSS files
│   │   └── App.js
│   ├── package.json
│   ├── .env.example
│   └── tailwind.config.js
│
├── docker-compose.yml        # Container orchestration
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL + SQLAlchemy
- **ML**: scikit-learn, XGBoost, SHAP
- **Data**: Pandas, NumPy
- **Security**: JWT, Passlib, bcrypt

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Charts**: Recharts, Chart.js
- **Styling**: Tailwind CSS, CSS Modules
- **Build**: Create React App

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm start
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 📊 Database Schema

### Tables
1. **organizations** - Multi-tenant support
2. **users** - User accounts and authentication
3. **employees** - Employee master data (30+ attributes)
4. **predictions** - Risk scores and results
5. **uploads** - Excel upload tracking
6. **audit_logs** - Activity logging

## 🤖 ML Pipeline

### Training
```bash
cd backend
python -m app.ml.train
```

Creates:
- `best_model.pkl` - Trained model
- `label_encoders.pkl` - Feature encoders
- `scaler.pkl` - Feature scaler
- `feature_columns.pkl` - Column list
- `model_metadata.json` - Model info

### Prediction
Uses `AttritionPredictor` class with:
- Preprocessing with saved artifacts
- SHAP value calculation for explainability
- Risk classification (Low/Medium/High)

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Current user profile
- `PUT /api/auth/change-password` - Change password

### Predictions
- `POST /api/predict/manual` - Single employee prediction
- `POST /api/predict/excel` - Bulk upload
- `GET /api/predict/download/{id}` - Download results
- `GET /api/predict/history` - Upload history

### Dashboard
- `GET /api/dashboard/metrics` - KPI metrics
- `GET /api/dashboard/charts/*` - Chart data
- `GET /api/dashboard/employees` - Employee list
- `GET /api/dashboard/filters/options` - Filter options

## 🔐 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- Trusted host middleware
- Environment variable configuration
- Database connection pooling

## 📈 Performance Considerations

- Label encoding for categorical features
- Standard scaling for numeric features
- Model caching in memory
- Async API endpoints
- Database indexing on key columns
- Pagination for large datasets

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## 📦 Deployment

### Docker
```bash
docker build -t attrition-backend ./backend
docker build -t attrition-frontend ./frontend
docker-compose up
```

### AWS Deployment
- ECS for containers
- RDS for PostgreSQL
- S3 for file storage
- CloudFront for CDN

## 🔄 CI/CD

Configure GitHub Actions or GitLab CI:
- Run tests on push
- Build Docker images
- Push to registry
- Deploy to staging/production

## 📝 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key
DEBUG=False
AWS_ACCESS_KEY_ID=your-key
S3_BUCKET_NAME=your-bucket
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_ENV=development
```



---

**Built with ❤️ for HR Analytics**
