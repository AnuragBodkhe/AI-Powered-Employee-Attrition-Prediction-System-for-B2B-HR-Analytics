"""
Model Training Pipeline
Trains and evaluates machine learning models for attrition prediction
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, Any
import joblib
import json
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)

logger = logging.getLogger(__name__)

MODEL_DIR = Path("backend/models")
DATA_DIR = Path("backend/data")


def load_data(file_path: str = None) -> pd.DataFrame:
    """
    Load HR employee attrition dataset
    
    Args:
        file_path: Path to CSV file. If None, uses default sample data
        
    Returns:
        DataFrame with employee data
    """
    if file_path is None:
        file_path = DATA_DIR / "HR_Employee_Attrition_sample.csv"

    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records from {file_path}")
    return df


def preprocess_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Preprocess data: handle missing values, encode categorical features, scale numeric features
    
    Args:
        df: Raw dataframe
        
    Returns:
        Tuple of (processed_df, target_series, preprocessing_artifacts)
    """
    # Create working copy
    data = df.copy()

    # Handle missing values
    data = data.fillna(data.mean(numeric_only=True))
    data = data.fillna(data.mode().iloc[0])

    # Separate target variable
    target = data["Attrition"] if "Attrition" in data.columns else None
    if target is not None:
        target = target.map({"Yes": 1, "No": 0})
        data = data.drop("Attrition", axis=1)

    # Identify categorical and numeric columns
    categorical_cols = data.select_dtypes(include=["object"]).columns
    numeric_cols = data.select_dtypes(include=["int64", "float64"]).columns

    # Label encode categorical features
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        data[col] = le.fit_transform(data[col].astype(str))
        label_encoders[col] = le

    # Scale numeric features
    scaler = StandardScaler()
    data[numeric_cols] = scaler.fit_transform(data[numeric_cols])

    # Store preprocessing artifacts
    preprocessing_artifacts = {
        "label_encoders": label_encoders,
        "scaler": scaler,
        "feature_columns": list(data.columns),
        "categorical_columns": list(categorical_cols),
        "numeric_columns": list(numeric_cols),
    }

    return data, target, preprocessing_artifacts


def train_models(
    X_train: pd.DataFrame, y_train: pd.Series
) -> Dict[str, Any]:
    """
    Train multiple models (Logistic Regression, Random Forest, XGBoost)
    
    Args:
        X_train: Training features
        y_train: Training target
        
    Returns:
        Dictionary with trained models
    """
    models = {}

    # Logistic Regression
    logger.info("Training Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    models["LogisticRegression"] = lr

    # Random Forest
    logger.info("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    models["RandomForest"] = rf

    # XGBoost
    logger.info("Training XGBoost...")
    xgb_model = xgb.XGBClassifier(
        n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, n_jobs=-1
    )
    xgb_model.fit(X_train, y_train)
    models["XGBoost"] = xgb_model

    return models


def evaluate_models(models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict]:
    """
    Evaluate all trained models
    
    Args:
        models: Dictionary of trained models
        X_test: Test features
        y_test: Test target
        
    Returns:
        Dictionary with evaluation metrics for each model
    """
    results = {}

    for model_name, model in models.items():
        logger.info(f"Evaluating {model_name}...")

        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        results[model_name] = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }

        logger.info(f"{model_name} Metrics: {results[model_name]}")

    return results


def save_model_artifacts(
    best_model: Any,
    label_encoders: Dict,
    scaler: StandardScaler,
    feature_columns: list,
    model_name: str = "best_model",
):
    """
    Save trained model and preprocessing artifacts
    
    Args:
        best_model: Trained model to save
        label_encoders: Dictionary of label encoders
        scaler: StandardScaler instance
        feature_columns: List of feature column names
        model_name: Name for the saved model
    """
    MODEL_DIR.mkdir(exist_ok=True)

    # Save model
    joblib.dump(best_model, MODEL_DIR / f"{model_name}.pkl")
    logger.info(f"Saved model to {MODEL_DIR / f'{model_name}.pkl'}")

    # Save preprocessors
    joblib.dump(label_encoders, MODEL_DIR / "label_encoders.pkl")
    joblib.dump(scaler, MODEL_DIR / "scaler.pkl")
    joblib.dump(feature_columns, MODEL_DIR / "feature_columns.pkl")

    # Save metadata
    metadata = {
        "model_name": model_name,
        "model_type": type(best_model).__name__,
        "feature_count": len(feature_columns),
        "features": feature_columns,
    }
    with open(MODEL_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("Saved all model artifacts")


def run_pipeline(data_file: str = None) -> Dict[str, Any]:
    """
    Run complete training pipeline
    
    Args:
        data_file: Path to training data CSV
        
    Returns:
        Dictionary with results and artifacts paths
    """
    # Load data
    df = load_data(data_file)

    # Preprocess
    X, y, artifacts = preprocess_data(df)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train models
    models = train_models(X_train, y_train)

    # Evaluate models
    results = evaluate_models(models, X_test, y_test)

    # Select best model (based on ROC-AUC)
    best_model_name = max(results, key=lambda x: results[x]["roc_auc"])
    best_model = models[best_model_name]

    logger.info(f"Best model: {best_model_name} with ROC-AUC: {results[best_model_name]['roc_auc']:.4f}")

    # Save artifacts
    save_model_artifacts(
        best_model,
        artifacts["label_encoders"],
        artifacts["scaler"],
        artifacts["feature_columns"],
    )

    return {
        "best_model": best_model_name,
        "metrics": results,
        "all_metrics": results,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_pipeline()
