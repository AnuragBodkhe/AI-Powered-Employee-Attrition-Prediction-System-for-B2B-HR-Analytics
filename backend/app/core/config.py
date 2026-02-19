"""
Application Configuration
Handles environment variables, settings, and constants
"""

import os
from typing import List
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Project
    PROJECT_NAME: str = "Employee Attrition Prediction System"
    PROJECT_VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-Powered B2B HR Analytics Platform"

    # API
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/attrition_db"
    DATABASE_ECHO: bool = False

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    UPLOAD_DIR: str = "backend/uploads"
    ALLOWED_EXTENSIONS: List[str] = [".xlsx", ".xls", ".csv"]

    # ML Model
    MODEL_PATH: str = "backend/models"
    MODEL_NAME: str = "best_model.pkl"
    LABEL_ENCODERS_PATH: str = "backend/models/label_encoders.pkl"
    SCALER_PATH: str = "backend/models/scaler.pkl"
    FEATURE_COLUMNS_PATH: str = "backend/models/feature_columns.pkl"
    MODEL_METADATA_PATH: str = "backend/models/model_metadata.json"

    # AWS (Optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # Risk Thresholds
    HIGH_RISK_THRESHOLD: float = 0.7
    MEDIUM_RISK_THRESHOLD: float = 0.4

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
