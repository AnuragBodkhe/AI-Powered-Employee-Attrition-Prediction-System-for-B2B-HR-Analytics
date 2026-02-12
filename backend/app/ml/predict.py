"""
Prediction Engine
Loads trained model and performs predictions with SHAP explanations
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
import joblib
import json
import logging
import shap

logger = logging.getLogger(__name__)

MODEL_DIR = Path("backend/models")


class AttritionPredictor:
    """Prediction engine for employee attrition"""

    def __init__(self, model_dir: str = None):
        """
        Initialize predictor and load artifacts
        
        Args:
            model_dir: Directory containing saved model artifacts
        """
        self.model_dir = Path(model_dir) if model_dir else MODEL_DIR
        self.model = None
        self.label_encoders = None
        self.scaler = None
        self.feature_columns = None
        self.load_artifacts()

    def load_artifacts(self):
        """Load trained model and preprocessing artifacts"""
        try:
            self.model = joblib.load(self.model_dir / "best_model.pkl")
            self.label_encoders = joblib.load(self.model_dir / "label_encoders.pkl")
            self.scaler = joblib.load(self.model_dir / "scaler.pkl")
            self.feature_columns = joblib.load(self.model_dir / "feature_columns.pkl")
            logger.info("Loaded all model artifacts successfully")
        except FileNotFoundError as e:
            logger.error(f"Failed to load model artifacts: {e}")
            raise

    def preprocess_input(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess input data using saved preprocessors
        
        Args:
            data: Input dataframe
            
        Returns:
            Preprocessed dataframe
        """
        df = data.copy()

        # Handle missing values
        df = df.fillna(df.mean(numeric_only=True))
        df = df.fillna(df.mode().iloc[0])

        # Encode categorical features
        for col in self.label_encoders.keys():
            if col in df.columns:
                df[col] = self.label_encoders[col].transform(df[col].astype(str))

        # Scale numeric features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = self.scaler.transform(df[numeric_cols])

        # Ensure correct column order
        df = df[self.feature_columns]

        return df

    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make prediction for single employee
        
        Args:
            data: Employee attributes dictionary
            
        Returns:
            Prediction result with risk score and explanations
        """
        # Convert to dataframe
        df = pd.DataFrame([data])
        X = self.preprocess_input(df)

        # Get prediction and probability
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0][1]

        # Get SHAP values for explanation
        shap_values = self._calculate_shap_values(X)
        top_factors = self._get_top_factors(X, shap_values)

        return {
            "risk_score": float(probability),
            "risk_level": self._classify_risk(probability),
            "prediction_probability": float(probability),
            "top_factors": top_factors,
            "shap_values": shap_values,
        }

    def predict_batch(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Make predictions for multiple employees
        
        Args:
            data: Dataframe with employee data
            
        Returns:
            Dataframe with predictions added
        """
        X = self.preprocess_input(data)

        # Get predictions
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)[:, 1]

        # Add to dataframe
        result = data.copy()
        result["risk_score"] = probabilities
        result["risk_level"] = result["risk_score"].apply(self._classify_risk)
        result["prediction"] = predictions

        return result

    def _calculate_shap_values(self, X: pd.DataFrame) -> Dict:
        """
        Calculate SHAP values for model explanations
        
        Args:
            X: Preprocessed features
            
        Returns:
            Dictionary with SHAP values
        """
        try:
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)

            # Handle different model types
            if isinstance(shap_values, list):
                shap_values = shap_values[1]  # For binary classification

            return {
                "values": shap_values[0].tolist() if isinstance(shap_values, np.ndarray) else shap_values,
                "base_value": float(explainer.expected_value),
            }
        except Exception as e:
            logger.error(f"Failed to calculate SHAP values: {e}")
            return {"values": [], "base_value": 0.0}

    def _get_top_factors(self, X: pd.DataFrame, shap_values: Dict, top_n: int = 5) -> List[Dict]:
        """
        Get top contributing factors for prediction
        
        Args:
            X: Preprocessed features
            shap_values: SHAP values dictionary
            top_n: Number of top factors to return
            
        Returns:
            List of contributing factors with importance scores
        """
        try:
            shap_vals = np.array(shap_values.get("values", []))
            if len(shap_vals) == 0:
                return []

            abs_shap = np.abs(shap_vals)
            top_indices = np.argsort(abs_shap)[-top_n:][::-1]

            factors = []
            for idx in top_indices:
                if idx < len(self.feature_columns):
                    factors.append(
                        {
                            "feature": self.feature_columns[idx],
                            "importance": float(abs_shap[idx]),
                            "value": float(shap_vals[idx]),
                        }
                    )

            return factors
        except Exception as e:
            logger.error(f"Failed to get top factors: {e}")
            return []

    @staticmethod
    def _classify_risk(score: float, high_threshold: float = 0.7, medium_threshold: float = 0.4) -> str:
        """
        Classify risk level based on probability score
        
        Args:
            score: Risk probability score (0-1)
            high_threshold: Score above this is High risk
            medium_threshold: Score above this is Medium risk
            
        Returns:
            Risk level string (Low, Medium, High)
        """
        if score >= high_threshold:
            return "High"
        elif score >= medium_threshold:
            return "Medium"
        else:
            return "Low"


def preprocess_excel_data(file_path: str) -> pd.DataFrame:
    """
    Read and validate Excel file data
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        Dataframe with employee data
    """
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Loaded {len(df)} rows from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        raise


def create_prediction_dataframe(results: pd.DataFrame) -> pd.DataFrame:
    """
    Format predictions for Excel export
    
    Args:
        results: Dataframe with predictions
        
    Returns:
        Formatted dataframe for export
    """
    export_cols = [
        "employee_id",
        "name",
        "department",
        "job_role",
        "risk_score",
        "risk_level",
        "monthly_income",
        "years_at_company",
    ]

    available_cols = [col for col in export_cols if col in results.columns]
    return results[available_cols]
