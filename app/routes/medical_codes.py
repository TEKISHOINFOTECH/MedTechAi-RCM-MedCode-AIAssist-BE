"""
FastAPI routes for medical code validation and management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.database import get_db
from app.models.medical_code import MedicalCode
from app.schemas.medical_code import (
    MedicalCodeCreate,
    MedicalCodeUpdate,
    MedicalCodeResponse,
    MedicalCodeValidationRequest,
    MedicalCodeValidationResponse,
    BatchValidationRequest,
    BatchValidationResponse,
)
from app.agents import MedicalCodeValidationAgent

router = APIRouter(prefix="/api/v1/medical-codes", tags=["medical-codes"])


# Medical Code CRUD Operations
@router.post("/", response_model=MedicalCodeResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_code(
    code_data: MedicalCodeCreate,
    db: Session = Depends(get_db)
):
    """Create a new medical code record."""
    try:
        # Check if code already exists
        existing_code = db.query(MedicalCode).filter(
            MedicalCode.code == code_data.code,
            MedicalCode.code_type == code_data.code_type
        ).first()
        
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medical code {code_data.code} of type {code_data.code_type} already exists"
            )
        
        # Create new medical code
        new_code = MedicalCode(
            code=code_data.code,
            code_type=code_data.code_type,
            description=code_data.description,
            category=code_data.category,
            subcategory=code_data.subcategory,
            standard_price=code_data.standard_price,
            coverage_status=code_data.coverage_status,
            created_by="system"  # In production, get from auth context
        )
        
        db.add(new_code)
        db.commit()
        db.refresh(new_code)
        
        return new_code
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating medical code: {str(e)}"
        )


@router.get("/", response_model=List[MedicalCodeResponse])
async def get_medical_codes(
    skip: int = 0,
    limit: int = 100,
    code_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get medical codes with optional filtering."""
    try:
        query = db.query(MedicalCode)
        
        # Apply filters
        if code_type:
            query = query.filter(MedicalCode.code_type == code_type)
        
        if search:
            query = query.filter(
                (MedicalCode.code.ilike(f"%{search}%")) |
                (MedicalCode.description.ilike(f"%{search}%"))
            )
        
        # Apply pagination
        codes = query.offset(skip).limit(limit).all()
        return codes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving medical codes: {str(e)}"
        )


@router.get("/{code_id}", response_model=MedicalCodeResponse)
async def get_medical_code(
    code_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific medical code by ID."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical code with ID {code_id} not found"
            )
        
        return code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving medical code: {str(e)}"
        )


@router.put("/{code_id}", response_model=MedicalCodeResponse)
async def update_medical_code(
    code_id: int,
    code_data: MedicalCodeUpdate,
    db: Session = Depends(get_db)
):
    """Update a medical code."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical code with ID {code_id} not found"
            )
        
        # Update fields
        update_data = code_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(code, field, value)
        
        code.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(code)
        
        return code
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating medical code: {str(e)}"
        )


@router.delete("/{code_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_code(
    code_id: int,
    db: Session = Depends(get_db)
):
    """Delete a medical code."""
    try:
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical code with ID {code_id} not found"
            )
        
        db.delete(code)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting medical code: {str(e)}"
        )


# Medical Code Validation Operations
@router.post("/validate", response_model=MedicalCodeValidationResponse)
async def validate_medical_code(
    request: MedicalCodeValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate a single medical code using AI."""
    try:
        # Initialize medical validation agent
        agent = MedicalCodeValidationAgent()
        
        # Process validation request
        validation_result = await agent.process(request)
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating medical code: {str(e)}"
        )


@router.post("/validate/batch", response_model=BatchValidationResponse)
async def validate_medical_codes_batch(
    request: BatchValidationRequest,
    db: Session = Depends(get_db)
):
    """Validate multiple medical codes in a batch operation."""
    try:
        # Initialize medical validation agent
        agent = MedicalCodeValidationAgent()
        
        # Process batch validation
        start_time = datetime.utcnow()
        validation_results = await agent.batch_validate(request.codes)
        end_time = datetime.utcnow()
        
        # Calculate processing statistics
        processing_time = (end_time - start_time).total_seconds() * 1000
        success_count = len([r for r in validation_results if r.is_valid])
        failed_count = len(validation_results) - success_count
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        return BatchValidationResponse(
            batch_id=batch_id,
            total_codes=len(request.codes),
            processed_count=len(validation_results),
            success_count=success_count,
            failed_count=failed_count,
            results=validation_results,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing batch validation: {str(e)}"
        )


@router.get("/types")
async def get_medical_code_types():
    """Get available medical code types."""
    from app.models.medical_code import CodeType
    
    return {
        "available_types": [code_type.value for code_type in CodeType],
        "descriptions": {
            "CPT": "Current Procedural Terminology - Medical procedures",
            "ICD10": "International Classification of Diseases - Diagnosis codes",
            "HCPCS": "Healthcare Common Procedure Coding System - Services/supplies",
            "DRG": "Diagnosis Related Group - Hospital inpatient classification",
            "REVENUE": "Revenue codes - Healthcare facility services"
        }
    }


@router.get("/{code_id}/validation-history")
async def get_validation_history(
    code_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get validation history for a specific medical code."""
    try:
        # First check if code exists
        code = db.query(MedicalCode).filter(MedicalCode.id == code_id).first()
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medical code with ID {code_id} not found"
            )
        
        # Get validation results (assuming we have ValidationResult model with relationship)
        from app.models.validation_result import ValidationResult
        
        validations = db.query(ValidationResult).filter(
            ValidationResult.medical_code_id == code_id
        ).order_by(ValidationResult.created_at.desc()).limit(limit).all()
        
        return {
            "medical_code": {
                "id": code.id,
                "code": code.code,
                "code_type": code.code_type.value,
                "description": code.description
            },
            "validation_history": [
                {
                    "id": v.id,
                    "status": v.status.value,
                    "confidence_score": v.confidence_score,
                    "validation_method": v.validation_method.value,
                    "created_at": v.created_at,
                    "agent_name": v.agent_name
                }
                for v in validations
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving validation history: {str(e)}"
        )
