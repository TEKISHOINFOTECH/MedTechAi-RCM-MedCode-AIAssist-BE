"""
Validation result model for storing AI validation outcomes.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ValidationStatus(str, enum.Enum):
    """Validation status enumeration."""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"
    PENDING = "PENDING"


class ValidationMethod(str, enum.Enum):
    """Validation method enumeration."""
    AI_MODEL = "AI_MODEL"
    RULE_BASED = "RULE_BASED"
    EXTERNAL_API = "EXTERNAL_API"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class ValidationResult(Base):
    """Validation result model for tracking AI validation processes."""
    
    __tablename__ = "validation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Medical code reference
    medical_code_id = Column(Integer, ForeignKey("medical_codes.id"))
    medical_code = relationship("MedicalCode", back_populates="validation_results")
    
    # Validation details
    validation_method = Column(Enum(ValidationMethod), nullable=False)
    status = Column(Enum(ValidationStatus), nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    # Input data
    input_code = Column(String(100), nullable=False)
    input_type = Column(String(50), nullable=False)
    input_context = Column(Text, nullable=True)
    
    # Output results
    validated_code = Column(String(100), nullable=True)
    validation_message = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Performance metrics
    processing_time_ms = Column(Float, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    
    # Agent information
    agent_name = Column(String(100), nullable=True)
    agent_version = Column(String(50), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ValidationResult(status='{self.status}', confidence={self.confidence_score})>"
