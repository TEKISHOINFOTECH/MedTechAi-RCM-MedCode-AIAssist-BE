"""
Insurance claim data model for tracking RCM processes.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ClaimStatus(str, enum.Enum):
    """Insurance claim status enumeration."""
    SUBMITTED = "SUBMITTED"
    PROCESSING = "PROCESSING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"
    APPEALED = "APPEALED"


class PayerType(str, enum.Enum):
    """Insurance payer type enumeration."""
    MEDICARE = "MEDICARE"
    MEDICAID = "MEDICAID"
    COMMERCIAL = "COMMERCIAL"
    PRIVATE = "PRIVATE"


class InsuranceClaim(Base):
    """Insurance claim model for tracking claim lifecycle."""
    
    __tablename__ = "insurance_claims"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Medical code reference
    medical_code_id = Column(Integer, ForeignKey("medical_codes.id"))
    medical_code = relationship("MedicalCode", back_populates="claims")
    
    # Patient and provider information
    patient_id = Column(String(100), nullable=False, index=True)
    provider_id = Column(String(100), nullable=False, index=True)
    policy_number = Column(String(100), nullable=True)
    
    # Payer information
    payer_name = Column(String(200), nullable=False)
    payer_type = Column(Enum(PayerType), nullable=False)
    
    # Claim details
    claim_amount = Column(Float, nullable=False)
    billed_amount = Column(Float, nullable=False)
    approved_amount = Column(Float, nullable=True)
    
    # Status and processing
    status = Column(Enum(ClaimStatus), default=ClaimStatus.SUBMITTED)
    submitted_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime, nullable=True)
    
    # AI validation results
    ai_validation_passed = Column(Boolean, default=False)
    validation_confidence = Column(Float, default=0.0)
    correction_suggestions = Column(Text, nullable=True)
    
    # Denial and appeal information
    denial_reason = Column(Text, nullable=True)
    appeal_submitted = Column(Boolean, default=False)
    appeal_date = Column(DateTime, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<InsuranceClaim(claim_id='{self.claim_id}', status='{self.status}', amount={self.claim_amount})>"
