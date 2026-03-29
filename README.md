# 📊 Employee Attrition Prediction System (EAPS)

> **AI-Powered B2B HR Analytics** | MIT School of Computing  
> *Anurag Bodkhe et al.*

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0+-green)](https://xgboost.readthedocs.io)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://docker.com)

---

## 🎯 Overview

EAPS predicts employee attrition risk using four classical ML algorithms trained on the **IBM HR Analytics dataset** (1,470 employees, 30 features). It is built as a production-ready **Flask web application** with:

- **Single-employee prediction** with SHAP explainability
- **Batch CSV prediction** with downloadable results
- **Interactive analytics dashboard** (Plotly charts)
- **Model comparison** (metrics table, radar chart, leaderboard)

---

## 📈 Model Performance (IBM HR — SMOTE balanced)

| Model | Accuracy | AUC-ROC | F1 Score | Precision | Recall |
|---|---|---|---|---|---|
| Logistic Regression | 77.94% | 0.8612 | 0.7883 | 0.7575 | 0.8219 |
| SVM (RBF kernel) | 91.09% | 0.9746 | 0.9137 | 0.8859 | 0.9433 |
| **Random Forest** | **96.96%** | **0.9979** | **0.9703** | 0.9496 | **0.9919** |
| XGBoost | 95.55% | 0.9972 | 0.9567 | 0.9310 | 0.9838 |

> 🏆 **Best Model: Random Forest** (AUC-ROC = 0.9979)

---

## 🗂️ Project Structure

```
├── eaps_ml_pipeline.py        ← Train all 4 models, save .pkl + result plots
├── requirements.txt
├── Dockerfile
├── .env                       ← Secrets (never commit)
├── .gitignore
│
├── flask_app/
│   ├── server.py              ← Flask entry point (all routes + REST API)
│   ├── templates/
│   │   ├── base.html          ← Shared layout (nav, footer)
│   │   ├── index.html         ← Home / landing page
│   │   ├── predict.html       ← Single employee risk form
│   │   ├── batch.html         ← CSV upload + bulk predictions
│   │   ├── dashboard.html     ← Plotly analytics dashboard
│   │   └── compare.html       ← Model comparison & leaderboard
│   └── static/
│       └── app.js             ← Global JS (nav highlighting, helpers)
│
├── utils/
│   ├── __init__.py
│   ├── model_loader.py        ← Loads .pkl models, predict_single/batch
│   ├── preprocess.py          ← Encodes form input for model
│   └── shap_explain.py        ← SHAP waterfall chart per prediction
│
├── data/                      ← Place your CSV datasets here
│   ├── WA_Fn-UseC_-HR-Employee-Attrition.csv   (1,470 rows · IBM HR)
│   ├── employee_attrition_dataset.csv            (1,000 rows · custom)
│   └── employee_attrition_dataset_10000.csv      (10,000 rows · custom)
│
├── models/                    ← Auto-created after running pipeline
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── logistic_regression.pkl
│   ├── svm.pkl
│   └── scaler.pkl
│
└── results/                   ← Auto-created after running pipeline
    ├── roc_curves.png
    ├── confusion_matrices.png
    ├── model_comparison.png
    ├── feature_importance_random_forest.png
    ├── feature_importance_xgboost.png
    └── smote_class_balance.png
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add the IBM HR dataset
Download `WA_Fn-UseC_-HR-Employee-Attrition.csv` from [Kaggle](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) and place it in `data/`.

### 3. Train all models
```bash
python eaps_ml_pipeline.py
```
This creates `models/*.pkl` and `results/*.png`.

### 4. Launch the Flask app
```bash
python flask_app/server.py
```
App opens at **http://localhost:5000**

---

## 🐳 Docker Deployment

```bash
# Build
docker build -t eaps .

# Run locally
docker run -p 5000:5000 eaps

# Deploy to AWS/GCP — push image to ECR/Artifact Registry
```

---

## 📋 Features

| Page | URL | Description |
|---|---|---|
| 🏠 **Home** | `/` | System overview + model status |
| 🎯 **Predict** | `/predict` | 30-field form → instant risk score + SHAP waterfall + HR tips |
| 📂 **Batch** | `/batch` | Upload CSV → predict all → download results with risk labels |
| 📊 **Dashboard** | `/dashboard` | Dept/role/age/income/overtime charts (Plotly) |
| 🔬 **Compare** | `/compare` | Radar chart, bar chart, AUC leaderboard, paper metrics table |

### REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict` | Single employee prediction (JSON body) |
| `POST` | `/api/batch` | Batch prediction via CSV upload |
| `GET` | `/api/chart-data` | Dashboard chart data (JSON) |

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| ML | scikit-learn, XGBoost, imbalanced-learn (SMOTE) |
| Explainability | SHAP |
| Visualisation | Plotly, Matplotlib, Seaborn |
| Web App | **Flask 3.x** |
| Frontend | HTML5, Vanilla CSS, JavaScript |
| Deployment | Docker, AWS/GCP/Docker Hub |

---

## 👨‍💻 Authors

- **Anurag Bodkhe** - Bodkheanurag235@gmail.com
---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
