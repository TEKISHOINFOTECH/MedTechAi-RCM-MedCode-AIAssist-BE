"""
Database API routes for direct database operations.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db, init_db
from app.models.medical_code import MedicalCode, CodeType
from app.models.insurance_claim import InsuranceClaim, ClaimStatus, PayerType
from app.models.validation_result import ValidationResult


router = APIRouter(prefix="/api/v1/db", tags=["database"])


# Pydantic models for request/response
class MedicalCodeCreate(BaseModel):
    code: str = Field(..., description="Medical code")
    code_type: CodeType = Field(..., description="Type of medical code")
    description: Optional[str] = Field(None, description="Code description")
    category: Optional[str] = Field(None, description="Code category")
    subcategory: Optional[str] = Field(None, description="Code subcategory")
    standard_price: Optional[float] = Field(None, description="Standard price")
    coverage_status: Optional[str] = Field(None, description="Coverage status")


class MedicalCodeUpdate(BaseModel):
    description: Optional[str] = None
    is_valid: Optional[bool] = None
    confidence_score: Optional[float] = None
    validation_reason: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    standard_price: Optional[float] = None
    coverage_status: Optional[str] = None


class MedicalCodeResponse(BaseModel):
    id: int
    code: str
    code_type: CodeType
    description: Optional[str]
    is_valid: bool
    confidence_score: float
    validation_reason: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    standard_price: Optional[float]
    coverage_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


class InsuranceClaimCreate(BaseModel):
    claim_id: str = Field(..., description="Unique claim identifier")
    medical_code_id: int = Field(..., description="Associated medical code ID")
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Provider identifier")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")
    payer_name: str = Field(..., description="Insurance payer name")
    payer_type: PayerType = Field(..., description="Type of insurance payer")
    claim_amount: float = Field(..., description="Total claim amount")
    billed_amount: float = Field(..., description="Amount billed")


class InsuranceClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    approved_amount: Optional[float] = None
    ai_validation_passed: Optional[bool] = None
    validation_confidence: Optional[float] = None
    correction_suggestions: Optional[str] = None
    denial_reason: Optional[str] = None
    appeal_submitted: Optional[bool] = None


class InsuranceClaimResponse(BaseModel):
    id: int
    claim_id: str
    medical_code_id: int
    patient_id: str
    provider_id: str
    policy_number: Optional[str]
    payer_name: str
    payer_type: PayerType
    claim_amount: float
    billed_amount: float
    approved_amount: Optional[float]
    status: ClaimStatus
    submitted_date: datetime
    processed_date: Optional[datetime]
    ai_validation_passed: bool
    validation_confidence: float
    correction_suggestions: Optional[str]
    denial_reason: Optional[str]
    appeal_submitted: bool
    appeal_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


# Database Health and Management
@router.get("/health")
async def database_health(db: Session = Depends(get_db)):
    """Check database connection and health."""
    try:
        # Test database connection
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


@router.post("/init")
async def initialize_database():
    """Initialize database tables."""
    try:
        init_db()
        return {
            "status": "success",
            "message": "Database tables initialized successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")


# Medical Codes CRUD
@router.post("/medical-codes", response_model=MedicalCodeResponse)
async def create_medical_code(
    code_data: MedicalCodeCreate,
    db: Session = Depends(get_db)
):
    """Create a new medical code."""
    try:
        # Check if code already exists
        existing_code = db.query(MedicalCode).filter(
            MedicalCode.code == code_data.code,
            MedicalCode.code_type == code_data.code_type
        ).first()
        
        if existing_code:
            raise HTTPException(
                status_code=400,
                detail=f"Medical code {code_data.code} of type {code_data.code_type} already exists"
            )
        
        # Create new medical code
        medical_code = MedicalCode(
            code=code_data.code,
            code_type=code_data.code_type,
            description=code_data.description,
            category=code_data.category,
            subcategory=code_data.subcategory,
            standard_price=code_data.standard_price,
            coverage_status=code_data.coverage_status,
            created_by="api_user"
        )
        
        db.add(medical_code)
        db.commit()
        db.refresh(medical_code)
        
        return medical_code
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create medical code: {str(e)}")


@router.get("/medical-codes", response_model=List[MedicalCodeResponse])
async def get_medical_codes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    code_type: Optional[CodeType] = Query(None, description="Filter by code type"),
    is_valid: Optional[bool] = Query(None, description="Filter by validation status"),
    search: Optional[str] = Query(None, description="Search in code or description"),
    db: Session = Depends(get_db)
):
    """Get medical codes with filtering and pagination."""
    try:
        query = db.query(MedicalCode)
        
        # Apply filters
        if code_type:
            query = query.filter(MedicalCode.code_type == code_type)
        if is_valid is not None:
            query = query.filter(MedicalCode.is_valid == is_valid)
        if search:
            query = query.filter(
                (MedicalCode.code.contains(search)) |
                (MedicalCode.description.contains(search))
            )
        
        # Apply pagination
        codes = query.offset(skip).limit(limit).all()
        return codes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve medical codes: {str(e)}")


@router.get("/medical-codes/{code_id}", response_model=MedicalCodeResponse)
async def get_medical_code(code_id: int, db: Session = Depends(get_db)):
    """Get a specific medical code by ID."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Medical code not found")
        return code
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve medical code: {str(e)}")


@router.put("/medical-codes/{code_id}", response_model=MedicalCodeResponse)
async def update_medical_code(
    code_id: int,
    update_data: MedicalCodeUpdate,
    db: Session = Depends(get_db)
):
    """Update a medical code."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Medical code not found")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(code, field, value)
        
        code.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(code)
        return code
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update medical code: {str(e)}")


@router.delete("/medical-codes/{code_id}")
async def delete_medical_code(code_id: int, db: Session = Depends(get_db)):
    """Delete a medical code."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        if not code:
            raise HTTPException(status_code=404, detail="Medical code not found")
        
        db.delete(code)
        db.commit()
        
        return {"message": "Medical code deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete medical code: {str(e)}")


# Insurance Claims CRUD
@router.post("/claims", response_model=InsuranceClaimResponse)
async def create_insurance_claim(
    claim_data: InsuranceClaimCreate,
    db: Session = Depends(get_db)
):
    """Create a new insurance claim."""
    try:
        # Check if claim already exists
        existing_claim = db.query(InsuranceClaim).filter(
            InsuranceClaim.claim_id == claim_data.claim_id
        ).first()
        
        if existing_claim:
            raise HTTPException(
                status_code=400,
                detail=f"Insurance claim {claim_data.claim_id} already exists"
            )
        
        # Verify medical code exists
        medical_code = db.query(MedicalCode).filter(
            MedicalCode.id == claim_data.medical_code_id
        ).first()
        if not medical_code:
            raise HTTPException(
                status_code=400,
                detail=f"Medical code with ID {claim_data.medical_code_id} not found"
            )
        
        # Create new claim
        claim = InsuranceClaim(
            claim_id=claim_data.claim_id,
            medical_code_id=claim_data.medical_code_id,
            patient_id=claim_data.patient_id,
            provider_id=claim_data.provider_id,
            policy_number=claim_data.policy_number,
            payer_name=claim_data.payer_name,
            payer_type=claim_data.payer_type,
            claim_amount=claim_data.claim_amount,
            billed_amount=claim_data.billed_amount,
            created_by="api_user"
        )
        
        db.add(claim)
        db.commit()
        db.refresh(claim)
        
        return claim
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create insurance claim: {str(e)}")


@router.get("/claims", response_model=List[InsuranceClaimResponse])
async def get_insurance_claims(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    status: Optional[ClaimStatus] = Query(None, description="Filter by claim status"),
    payer_type: Optional[PayerType] = Query(None, description="Filter by payer type"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    provider_id: Optional[str] = Query(None, description="Filter by provider ID"),
    db: Session = Depends(get_db)
):
    """Get insurance claims with filtering and pagination."""
    try:
        query = db.query(InsuranceClaim)
        
        # Apply filters
        if status:
            query = query.filter(InsuranceClaim.status == status)
        if payer_type:
            query = query.filter(InsuranceClaim.payer_type == payer_type)
        if patient_id:
            query = query.filter(InsuranceClaim.patient_id == patient_id)
        if provider_id:
            query = query.filter(InsuranceClaim.provider_id == provider_id)
        
        # Apply pagination
        claims = query.offset(skip).limit(limit).all()
        return claims
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insurance claims: {str(e)}")


@router.get("/claims/{claim_id}", response_model=InsuranceClaimResponse)
async def get_insurance_claim(claim_id: str, db: Session = Depends(get_db)):
    """Get a specific insurance claim by claim ID."""
    try:
        claim = db.query(InsuranceClaim).filter(InsuranceClaim.claim_id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=404, detail="Insurance claim not found")
        return claim
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insurance claim: {str(e)}")


@router.put("/claims/{claim_id}", response_model=InsuranceClaimResponse)
async def update_insurance_claim(
    claim_id: str,
    update_data: InsuranceClaimUpdate,
    db: Session = Depends(get_db)
):
    """Update an insurance claim."""
    try:
        claim = db.query(InsuranceClaim).filter(InsuranceClaim.claim_id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=404, detail="Insurance claim not found")
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(claim, field, value)
        
        # Update processed_date if status changes
        if update_data.status and update_data.status in [ClaimStatus.APPROVED, ClaimStatus.DENIED]:
            claim.processed_date = datetime.utcnow()
        
        # Update appeal_date if appeal is submitted
        if update_data.appeal_submitted and update_data.appeal_submitted:
            claim.appeal_date = datetime.utcnow()
        
        claim.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(claim)
        return claim
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update insurance claim: {str(e)}")


# Database Statistics and Analytics
@router.get("/stats")
async def get_database_statistics(db: Session = Depends(get_db)):
    """Get database statistics and analytics."""
    try:
        # Medical codes statistics
        total_codes = db.query(MedicalCode).count()
        valid_codes = db.query(MedicalCode).filter(MedicalCode.is_valid == True).count()
        invalid_codes = db.query(MedicalCode).filter(MedicalCode.is_valid == False).count()
        
        # Claims statistics
        total_claims = db.query(InsuranceClaim).count()
        approved_claims = db.query(InsuranceClaim).filter(InsuranceClaim.status == ClaimStatus.APPROVED).count()
        denied_claims = db.query(InsuranceClaim).filter(InsuranceClaim.status == ClaimStatus.DENIED).count()
        pending_claims = db.query(InsuranceClaim).filter(InsuranceClaim.status == ClaimStatus.PENDING).count()
        
        # Payer type breakdown
        payer_stats = db.query(InsuranceClaim.payer_type, db.func.count(InsuranceClaim.id)).group_by(InsuranceClaim.payer_type).all()
        
        # Code type breakdown
        code_type_stats = db.query(MedicalCode.code_type, db.func.count(MedicalCode.id)).group_by(MedicalCode.code_type).all()
        
        return {
            "medical_codes": {
                "total": total_codes,
                "valid": valid_codes,
                "invalid": invalid_codes,
                "validation_rate": round(valid_codes / total_codes * 100, 2) if total_codes > 0 else 0
            },
            "insurance_claims": {
                "total": total_claims,
                "approved": approved_claims,
                "denied": denied_claims,
                "pending": pending_claims,
                "approval_rate": round(approved_claims / total_claims * 100, 2) if total_claims > 0 else 0
            },
            "payer_breakdown": {payer_type.value: count for payer_type, count in payer_stats},
            "code_type_breakdown": {code_type.value: count for code_type, count in code_type_stats},
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve database statistics: {str(e)}")


# Bulk Operations
@router.post("/medical-codes/bulk")
async def create_medical_codes_bulk(
    codes_data: List[MedicalCodeCreate],
    db: Session = Depends(get_db)
):
    """Create multiple medical codes in bulk."""
    try:
        created_codes = []
        errors = []
        
        for code_data in codes_data:
            try:
                # Check if code already exists
                existing_code = db.query(MedicalCode).filter(
                    MedicalCode.code == code_data.code,
                    MedicalCode.code_type == code_data.code_type
                ).first()
                
                if existing_code:
                    errors.append(f"Code {code_data.code} of type {code_data.code_type} already exists")
                    continue
                
                # Create new medical code
                medical_code = MedicalCode(
                    code=code_data.code,
                    code_type=code_data.code_type,
                    description=code_data.description,
                    category=code_data.category,
                    subcategory=code_data.subcategory,
                    standard_price=code_data.standard_price,
                    coverage_status=code_data.coverage_status,
                    created_by="api_user"
                )
                
                db.add(medical_code)
                created_codes.append(medical_code)
                
            except Exception as e:
                errors.append(f"Failed to create code {code_data.code}: {str(e)}")
        
        db.commit()
        
        return {
            "message": f"Bulk operation completed",
            "created_count": len(created_codes),
            "error_count": len(errors),
            "errors": errors,
            "created_codes": [{"id": code.id, "code": code.code, "type": code.code_type.value} for code in created_codes]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")
