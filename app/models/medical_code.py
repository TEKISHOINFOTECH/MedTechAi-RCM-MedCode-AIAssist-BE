"""
Medical code data model representing various medical coding systems.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CodeType(str, enum.Enum):
    """Medical code type enumeration."""
    CPT = "CPT"
    ICD10 = "ICD10"
    HCPCS = "HCPCS"
    DRG = "DRG"
    REVENUE = "REVENUE"


class MedicalCode(Base):
    """Medical code model for storing validated medical codes."""
    
    __tablename__ = "medical_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, index=True)
    code_type = Column(Enum(CodeType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Validation metadata
    is_valid = Column(Boolean, default=False, index=True)
    confidence_score = Column(Float, default=0.0)
    validation_reason = Column(Text, nullable=True)
    
    # Category and hierarchy
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    
    # Pricing and billing information
    standard_price = Column(Float, nullable=True)
    coverage_status = Column(String(50), nullable=True)
    
    # Relationships to claims
    claims = relationship("InsuranceClaim", back_populates="medical_code")
    validation_results = relationship("ValidationResult", back_populates="medical_code")
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<MedicalCode(code='{self.code}', type='{self.code_type}', valid={self.is_valid})>"
