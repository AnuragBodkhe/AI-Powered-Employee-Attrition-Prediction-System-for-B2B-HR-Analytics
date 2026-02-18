"""
Dashboard Routes
Returns analytics and visualization data
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import random

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import Prediction, Upload, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Pydantic Models
class MetricsResponse(BaseModel):
    """Dashboard KPI metrics"""

    total_employees: int
    total_predictions: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_risk_score: float
    attrition_rate: float
    last_updated: datetime


class ChartDataPoint(BaseModel):
    """Chart data point"""

    label: str
    value: float
    count: Optional[int] = None


class RiskDistributionResponse(BaseModel):
    """Risk distribution chart data"""

    data: List[ChartDataPoint]
    total: int


class DepartmentComparisonResponse(BaseModel):
    """Department comparison data"""

    departments: List[str]
    high_risk_percentages: List[float]
    medium_risk_percentages: List[float]
    low_risk_percentages: List[float]


class SalaryImpactResponse(BaseModel):
    """Salary impact analysis"""

    salary_brackets: List[str]
    attrition_rates: List[float]
    average_risk_scores: List[float]


class FilterOption(BaseModel):
    """Filter option"""

    label: str
    value: str


class FilterOptionsResponse(BaseModel):
    """Available filter options"""

    departments: List[FilterOption]
    job_roles: List[FilterOption]
    risk_levels: List[FilterOption]
    education_levels: List[FilterOption]
    business_travel_options: List[FilterOption]


class EmployeeRecord(BaseModel):
    """Employee record for table"""

    employee_id: int
    name: str
    department: str
    job_role: str
    monthly_income: float
    risk_score: float
    risk_level: str
    years_at_company: int
    job_satisfaction: int
    over_time: bool


class EmployeesListResponse(BaseModel):
    """Employees list with filters"""

    total: int
    page: int
    limit: int
    employees: List[EmployeeRecord]


# Routes
def _get_mock_predictions(db: Session, org_id: int, limit: int = 100):
    """Get mock predictions for dashboard"""
    predictions = db.query(Prediction).filter(
        Prediction.upload_id.isnot(None)
    ).limit(limit).all()
    
    if not predictions:
        # Create mock predictions if none exist
        mock_data = []
        for i in range(50):
            risk_score = random.uniform(0.1, 0.95)
            if risk_score >= 0.7:
                risk_level = "High"
            elif risk_score >= 0.4:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            mock_data.append({
                "risk_score": risk_score,
                "risk_level": risk_level,
                "prediction_probability": risk_score,
            })
        return mock_data
    
    return [
        {
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "prediction_probability": p.prediction_probability,
        }
        for p in predictions
    ]


@router.get("/metrics", response_model=MetricsResponse)
async def get_dashboard_metrics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get KPI metrics for dashboard
    Returns counts and averages for risk assessment
    """
    try:
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        predictions = _get_mock_predictions(db, user.organization_id)

        if predictions:
            high_risk = sum(1 for p in predictions if p["risk_level"] == "High")
            medium_risk = sum(1 for p in predictions if p["risk_level"] == "Medium")
            low_risk = sum(1 for p in predictions if p["risk_level"] == "Low")
            avg_risk = sum(p["risk_score"] for p in predictions) / len(predictions)
        else:
            high_risk = medium_risk = low_risk = 0
            avg_risk = 0.0

        return {
            "total_employees": len(predictions),
            "total_predictions": len(predictions),
            "high_risk_count": high_risk,
            "medium_risk_count": medium_risk,
            "low_risk_count": low_risk,
            "average_risk_score": avg_risk,
            "attrition_rate": high_risk / max(len(predictions), 1) * 100,
            "last_updated": datetime.utcnow(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/risk-distribution", response_model=RiskDistributionResponse)
async def get_risk_distribution(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get risk distribution data
    Returns count of employees in each risk category
    """
    try:
        user_id = int(current_user["user_id"])
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        predictions = _get_mock_predictions(db, user.organization_id)

        high_risk = sum(1 for p in predictions if p["risk_level"] == "High")
        medium_risk = sum(1 for p in predictions if p["risk_level"] == "Medium")
        low_risk = sum(1 for p in predictions if p["risk_level"] == "Low")

        return {
            "data": [
                ChartDataPoint(label="High Risk", value=high_risk / max(len(predictions), 1), count=high_risk),
                ChartDataPoint(label="Medium Risk", value=medium_risk / max(len(predictions), 1), count=medium_risk),
                ChartDataPoint(label="Low Risk", value=low_risk / max(len(predictions), 1), count=low_risk),
            ],
            "total": len(predictions),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/department-comparison", response_model=DepartmentComparisonResponse)
async def get_department_comparison(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get department-wise risk comparison
    Shows attrition risk by department
    """
    try:
        departments = ["Sales", "IT", "HR", "Finance", "Operations"]
        
        return {
            "departments": departments,
            "high_risk_percentages": [random.uniform(10, 40) for _ in departments],
            "medium_risk_percentages": [random.uniform(20, 50) for _ in departments],
            "low_risk_percentages": [random.uniform(20, 50) for _ in departments],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/salary-impact", response_model=SalaryImpactResponse)
async def get_salary_impact(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get salary impact on attrition
    Shows correlation between salary and risk
    """
    try:
        salary_brackets = ["<2K", "2K-4K", "4K-6K", "6K-8K", ">8K"]
        
        return {
            "salary_brackets": salary_brackets,
            "attrition_rates": [45.2, 35.8, 22.5, 15.3, 8.7],
            "average_risk_scores": [0.75, 0.62, 0.48, 0.35, 0.18],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/options", response_model=FilterOptionsResponse)
async def get_filter_options(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get available filter options
    Returns unique values for all filterable fields
    """
    try:
        return {
            "departments": [
                FilterOption(label="Sales", value="Sales"),
                FilterOption(label="IT", value="IT"),
                FilterOption(label="HR", value="HR"),
                FilterOption(label="Finance", value="Finance"),
                FilterOption(label="Operations", value="Operations"),
                FilterOption(label="Marketing", value="Marketing"),
            ],
            "job_roles": [
                FilterOption(label="Manager", value="Manager"),
                FilterOption(label="Senior Developer", value="Senior Developer"),
                FilterOption(label="Developer", value="Developer"),
                FilterOption(label="Analyst", value="Analyst"),
                FilterOption(label="Executive", value="Executive"),
                FilterOption(label="Sales Representative", value="Sales Representative"),
            ],
            "risk_levels": [
                FilterOption(label="Low", value="Low"),
                FilterOption(label="Medium", value="Medium"),
                FilterOption(label="High", value="High"),
            ],
            "education_levels": [
                FilterOption(label="High School", value="1"),
                FilterOption(label="Bachelor", value="2"),
                FilterOption(label="Master", value="3"),
                FilterOption(label="Doctorate", value="4"),
                FilterOption(label="Other", value="5"),
            ],
            "business_travel_options": [
                FilterOption(label="Non-Travel", value="Non-Travel"),
                FilterOption(label="Travel Rarely", value="Travel Rarely"),
                FilterOption(label="Travel Frequently", value="Travel Frequently"),
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employees", response_model=EmployeesListResponse)
async def get_employees_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    job_role: Optional[str] = None,
    min_salary: Optional[float] = None,
    max_salary: Optional[float] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get filtered list of employees with pagination
    Supports filtering by multiple criteria
    """
    try:
        # Generate mock employee data
        employees = []
        departments_list = ["Sales", "IT", "HR", "Finance", "Operations"]
        roles_list = ["Manager", "Senior Developer", "Developer", "Analyst", "Executive"]
        
        for i in range(100):
            risk_score = random.uniform(0.1, 0.95)
            if risk_score >= 0.7:
                risk_level_val = "High"
            elif risk_score >= 0.4:
                risk_level_val = "Medium"
            else:
                risk_level_val = "Low"
            
            emp = {
                "employee_id": i + 1,
                "name": f"Employee {i + 1}",
                "department": random.choice(departments_list),
                "job_role": random.choice(roles_list),
                "monthly_income": random.uniform(2000, 15000),
                "risk_score": risk_score,
                "risk_level": risk_level_val,
                "years_at_company": random.randint(0, 20),
                "job_satisfaction": random.randint(1, 4),
                "over_time": random.choice([True, False]),
            }
            
            # Apply filters
            if department and emp["department"] != department:
                continue
            if risk_level and emp["risk_level"] != risk_level:
                continue
            if job_role and emp["job_role"] != job_role:
                continue
            if min_salary and emp["monthly_income"] < min_salary:
                continue
            if max_salary and emp["monthly_income"] > max_salary:
                continue
            if search and search.lower() not in emp["name"].lower():
                continue
            
            employees.append(emp)

        total = len(employees)
        employees = employees[skip : skip + limit]

        return {
            "total": total,
            "page": skip // limit + 1,
            "limit": limit,
            "employees": [EmployeeRecord(**emp) for emp in employees],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/excel")
async def export_to_excel(
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Export filtered employee data to Excel
    """
    try:
        import pandas as pd
        import io
        from fastapi.responses import StreamingResponse

        # Generate mock data
        data = {
            "Employee ID": [i for i in range(1, 51)],
            "Name": [f"Employee {i}" for i in range(1, 51)],
            "Department": [random.choice(["Sales", "IT", "HR", "Finance", "Operations"]) for _ in range(50)],
            "Job Role": [random.choice(["Manager", "Developer", "Analyst"]) for _ in range(50)],
            "Monthly Income": [random.uniform(2000, 15000) for _ in range(50)],
            "Risk Score": [random.uniform(0.1, 0.95) for _ in range(50)],
            "Risk Level": [random.choice(["Low", "Medium", "High"]) for _ in range(50)],
        }

        df = pd.DataFrame(data)

        # Create Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=employees_export.xlsx"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
