"""
SQLAlchemy Database Models
Defines 6 main tables for the attrition prediction system
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Organization(Base):
    """Organizations table - Multi-tenant support"""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    industry = Column(String(100))
    subscription_tier = Column(String(50), default="starter")  # starter, pro, enterprise
    high_risk_threshold = Column(Float, default=0.7)
    medium_risk_threshold = Column(Float, default=0.4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    employees = relationship(
        "Employee", back_populates="organization", cascade="all, delete-orphan"
    )
    uploads = relationship("Upload", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """Users table - Authentication and role management"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="viewer")  # admin, manager, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")


class Employee(Base):
    """Employees table - Employee master data with 30+ attributes"""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)

    # Personal Information
    age = Column(Integer)
    gender = Column(String(20))
    marital_status = Column(String(20))

    # Department & Job Info
    department = Column(String(100), index=True)
    job_role = Column(String(100))
    job_level = Column(Integer)

    # Compensation & Benefits
    monthly_income = Column(Float)
    hourly_rate = Column(Float)
    daily_rate = Column(Float)
    stock_option_level = Column(Integer)

    # Work-Life Metrics
    years_at_company = Column(Integer)
    years_since_last_promotion = Column(Integer)
    years_in_current_role = Column(Integer)
    over_time = Column(Boolean)
    job_satisfaction = Column(Integer)  # 1-4 scale
    work_life_balance = Column(Integer)  # 1-4 scale
    job_involvement = Column(Integer)  # 1-4 scale
    performance_rating = Column(Float)

    # Additional Metrics
    education_field = Column(String(100))
    education_level = Column(Integer)  # 1-5 scale
    distance_from_home = Column(Integer)  # in km
    num_companies_worked = Column(Integer)
    training_times_last_year = Column(Integer)

    # Additional Fields
    business_travel = Column(String(50))
    department_relocation = Column(Boolean)
    employee_count = Column(Integer)
    manager_id = Column(String(50))

    # Prediction & Status
    attrition = Column(Boolean, nullable=True)  # Historical attrition status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="employees")
    predictions = relationship("Prediction", back_populates="employee", cascade="all, delete-orphan")


class Prediction(Base):
    """Predictions table - Risk scores and model results"""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)

    # Prediction Results
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), index=True)  # Low, Medium, High
    prediction_probability = Column(Float)

    # SHAP Values & Explainability
    shap_values = Column(JSON)  # Store top factors
    top_factors = Column(JSON)  # List of contributing factors

    # Model Information
    model_version = Column(String(50))
    model_name = Column(String(100))

    # Metadata
    prediction_date = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="predictions")
    upload = relationship("Upload", back_populates="predictions")


class Upload(Base):
    """Uploads table - Excel upload tracking"""

    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File Information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    s3_key = Column(String(500))  # S3 path if stored in AWS

    # Processing Status
    status = Column(
        String(50), default="processing"
    )  # pending, processing, completed, failed
    progress = Column(Integer, default=0)  # 0-100%
    total_rows = Column(Integer)
    processed_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)

    # Results
    error_message = Column(Text, nullable=True)
    result_file_path = Column(String(500))  # Path to results Excel
    result_s3_key = Column(String(500))  # S3 path if stored in AWS

    # Summary Statistics
    high_risk_count = Column(Integer, default=0)
    medium_risk_count = Column(Integer, default=0)
    low_risk_count = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="uploads")
    predictions = relationship("Prediction", back_populates="upload", cascade="all, delete-orphan")


class AuditLog(Base):
    """Audit Logs table - User actions and system events"""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Action Information
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(100))  # User, Employee, Upload, etc.
    entity_id = Column(Integer, nullable=True)

    # Details
    description = Column(Text)
    old_values = Column(JSON)  # Previous values if update
    new_values = Column(JSON)  # New values if update
    status = Column(String(50))  # success, failure

    # Metadata
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")


# Export all models
__all__ = [
    "Base",
    "Organization",
    "User",
    "Employee",
    "Prediction",
    "Upload",
    "AuditLog",
]
