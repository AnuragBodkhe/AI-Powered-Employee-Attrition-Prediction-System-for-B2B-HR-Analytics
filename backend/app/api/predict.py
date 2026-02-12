"""
Prediction Routes
Handles single employee predictions and bulk Excel uploads
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io
import os
import random

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import Prediction, Employee, Upload, User
from app.core.config import get_settings

router = APIRouter(prefix="/predict", tags=["predictions"])
settings = get_settings()


# Pydantic Models
class ManualPredictionRequest(BaseModel):
    """Manual employee prediction request"""

    age: int
    department: str
    job_role: str
    monthly_income: float
    years_at_company: int
    over_time: bool
    job_satisfaction: int
    work_life_balance: int
    job_involvement: int
    education_level: int
    performance_rating: float
    num_companies_worked: int
    years_in_current_role: int
    years_since_last_promotion: int
    distance_from_home: int
    training_times_last_year: int
    marital_status: Optional[str] = None
    gender: Optional[str] = None
    business_travel: Optional[str] = None


class PredictionResult(BaseModel):
    """Prediction result response"""

    risk_score: float
    risk_level: str  # Low, Medium, High
    prediction_probability: float
    top_factors: List[dict]  # Contributing factors with importance
    shap_values: Optional[dict] = None


class PredictionWithId(PredictionResult):
    """Prediction result with ID"""

    prediction_id: int
    timestamp: datetime


class ExcelUploadResponse(BaseModel):
    """Excel upload response"""

    upload_id: int
    status: str
    message: str
    total_rows: int
    job_id: Optional[str] = None  # For async processing


class UploadHistoryItem(BaseModel):
    """Upload history item"""

    upload_id: int
    file_name: str
    status: str
    created_at: datetime
    total_rows: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int


class DownloadResultResponse(BaseModel):
    """Download result response"""

    download_url: str
    file_name: str
    size: int


# Routes
def _calculate_mock_risk_score(data: ManualPredictionRequest) -> tuple:
    """
    Calculate mock risk score based on employee attributes
    Returns: (risk_score, risk_level, probability)
    """
    score = 0.0
    
    # Income factor (lower income = higher risk)
    if data.monthly_income < 2000:
        score += 0.3
    elif data.monthly_income < 5000:
        score += 0.15
    
    # Satisfaction factor
    score += (5 - data.job_satisfaction) * 0.1
    score += (5 - data.work_life_balance) * 0.1
    score += (5 - data.job_involvement) * 0.08
    
    # Tenure factor
    if data.years_at_company < 1:
        score += 0.25
    elif data.years_at_company < 3:
        score += 0.15
    
    # Promotion factor
    if data.years_since_last_promotion > 3:
        score += 0.1
    
    # Years in role factor
    if data.years_in_current_role < 6:
        score += (6 - data.years_in_current_role) * 0.02
    
    # Overtime factor
    if data.over_time:
        score += 0.15
    
    # Distance factor
    if data.distance_from_home > 20:
        score += 0.1
    
    # Normalize score
    score = min(max(score, 0.0), 1.0)
    
    # Add some randomness for demo
    score = score * 0.9 + random.random() * 0.1
    score = min(max(score, 0.0), 1.0)
    
    # Determine risk level
    if score >= settings.HIGH_RISK_THRESHOLD:
        risk_level = "High"
    elif score >= settings.MEDIUM_RISK_THRESHOLD:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return score, risk_level, score


def _get_top_factors(score: float, data: ManualPredictionRequest) -> List[dict]:
    """Get top contributing factors to the risk score"""
    factors = []
    
    if data.job_satisfaction < 3:
        factors.append({"name": "Low Job Satisfaction", "importance": 0.25})
    
    if data.work_life_balance < 3:
        factors.append({"name": "Poor Work-Life Balance", "importance": 0.20})
    
    if data.years_at_company < 2:
        factors.append({"name": "New Employee", "importance": 0.18})
    
    if data.monthly_income < 3000:
        factors.append({"name": "Lower Income", "importance": 0.15})
    
    if data.over_time:
        factors.append({"name": "Works Overtime", "importance": 0.12})
    
    if data.distance_from_home > 15:
        factors.append({"name": "Long Distance from Home", "importance": 0.10})
    
    return factors[:5]


@router.post("/manual", response_model=PredictionWithId)
async def predict_single_employee(
    request: ManualPredictionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Predict attrition risk for a single employee
    Takes employee attributes and returns risk score with explanations
    """
    try:
        # Calculate mock prediction
        risk_score, risk_level, probability = _calculate_mock_risk_score(request)
        top_factors = _get_top_factors(risk_score, request)

        # Get user and organization
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Create prediction record
        prediction = Prediction(
            employee_id=user_id,  # Use user_id as placeholder
            upload_id=None,
            risk_score=risk_score,
            risk_level=risk_level,
            prediction_probability=probability,
            shap_values={},
            top_factors=top_factors,
            model_version="1.0.0",
            model_name="AttritionPredictor",
            prediction_date=datetime.utcnow(),
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return {
            "prediction_id": prediction.id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "prediction_probability": probability,
            "top_factors": top_factors,
            "shap_values": None,
            "timestamp": prediction.prediction_date,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post("/excel", response_model=ExcelUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_excel_predictions(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload Excel file for bulk employee predictions
    Processes file asynchronously and returns job ID for status tracking
    """
    try:
        if not file.filename.endswith((".xlsx", ".xls", ".csv")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be .xlsx, .xls, or .csv format",
            )

        # Read file
        content = await file.read()
        
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Get user and organization
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Create upload record
        upload = Upload(
            organization_id=user.organization_id,
            user_id=user_id,
            file_name=file.filename,
            file_path=f"uploads/{file.filename}",
            file_size=len(content),
            status="processing",
            progress=0,
            total_rows=len(df),
            processed_rows=0,
        )
        db.add(upload)
        db.commit()
        db.refresh(upload)

        # Mock process predictions
        high_risk = 0
        medium_risk = 0
        low_risk = 0

        for idx, row in df.iterrows():
            risk_score = random.uniform(0.2, 0.95)
            
            if risk_score >= 0.7:
                risk_level = "High"
                high_risk += 1
            elif risk_score >= 0.4:
                risk_level = "Medium"
                medium_risk += 1
            else:
                risk_level = "Low"
                low_risk += 1

            # Create prediction
            prediction = Prediction(
                employee_id=user_id,
                upload_id=upload.id,
                risk_score=risk_score,
                risk_level=risk_level,
                prediction_probability=risk_score,
                shap_values={},
                top_factors=[],
                model_version="1.0.0",
                model_name="AttritionPredictor",
            )
            db.add(prediction)

        # Update upload status
        upload.status = "completed"
        upload.progress = 100
        upload.processed_rows = len(df)
        upload.high_risk_count = high_risk
        upload.medium_risk_count = medium_risk
        upload.low_risk_count = low_risk
        upload.completed_at = datetime.utcnow()
        db.commit()

        return {
            "upload_id": upload.id,
            "status": "completed",
            "message": f"Successfully processed {len(df)} employees",
            "total_rows": len(df),
            "job_id": str(upload.id),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


@router.get("/download/{upload_id}", response_model=DownloadResultResponse)
async def download_results(
    upload_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Download prediction results for an upload
    Returns Excel file with all predictions and risk scores
    """
    try:
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        upload = db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.organization_id == user.organization_id
        ).first()

        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found",
            )

        # Get predictions for this upload
        predictions = db.query(Prediction).filter(Prediction.upload_id == upload_id).all()

        # Create Excel file
        data = {
            "Employee ID": [p.id for p in predictions],
            "Risk Score": [p.risk_score for p in predictions],
            "Risk Level": [p.risk_level for p in predictions],
            "Probability": [p.prediction_probability for p in predictions],
        }
        
        df = pd.DataFrame(data)
        
        # Save to bytes
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return {
            "download_url": f"/api/predict/download/{upload_id}",
            "file_name": f"predictions_{upload_id}.xlsx",
            "size": len(output.getvalue()),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}",
        )


@router.get("/history", response_model=List[UploadHistoryItem])
async def get_upload_history(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get history of all Excel uploads for current user's organization
    """
    try:
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        uploads = db.query(Upload).filter(
            Upload.organization_id == user.organization_id
        ).offset(skip).limit(limit).all()

        return uploads
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch history: {str(e)}",
        )


@router.get("/status/{upload_id}")
async def get_upload_status(
    upload_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current processing status of an upload
    Returns progress percentage and any error messages
    """
    try:
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        upload = db.query(Upload).filter(
            Upload.id == upload_id,
            Upload.organization_id == user.organization_id
        ).first()

        if not upload:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found",
            )

        return {
            "upload_id": upload.id,
            "status": upload.status,
            "progress": upload.progress,
            "processed_rows": upload.processed_rows,
            "total_rows": upload.total_rows,
            "error_message": upload.error_message,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}",
        )
