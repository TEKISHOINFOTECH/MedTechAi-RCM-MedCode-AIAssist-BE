"""
Pydantic schemas for medical code validation API endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.medical_code import CodeType


class MedicalCodeBase(BaseModel):
    """Base medical code schema."""
    code: str = Field(..., min_length=1, max_length=20, description="Medical code")
    code_type: CodeType = Field(..., description="Type of medical code")
    description: Optional[str] = Field(None, description="Code description")
    category: Optional[str] = Field(None, description="Code category")
    subcategory: Optional[str] = Field(None, description="Code subcategory")
    
    @validator('code')
    def validate_code_format(cls, v):
        """Validate medical code format."""
        # Remove spaces and make uppercase for validation
        code = v.strip().upper().replace(' ', '')
        if not code:
            raise ValueError('Code cannot be empty')
        return code


class MedicalCodeCreate(MedicalCodeBase):
    """Schema for creating a new medical code."""
    standard_price: Optional[float] = Field(None, ge=0, description="Standard price for the code")
    coverage_status: Optional[str] = Field(None, description="Coverage status")


class MedicalCodeUpdate(BaseModel):
    """Schema for updating a medical code."""
    description: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    standard_price: Optional[float] = Field(None, ge=0)
    coverage_status: Optional[str] = None
    is_valid: Optional[bool] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_reason: Optional[str] = None


class MedicalCodeResponse(MedicalCodeBase):
    """Schema for medical code API response."""
    id: int
    is_valid: bool
    confidence_score: float
    validation_reason: Optional[str]
    standard_price: Optional[float]
    coverage_status: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class MedicalCodeValidationRequest(BaseModel):
    """Schema for medical code validation request."""
    code: str = Field(..., description="Medical code to validate")
    code_type: CodeType = Field(..., description="Type of medical code")
    context: Optional[str] = Field(None, description="Additional context for validation")
    patient_info: Optional[dict] = Field(None, description="Patient information")
    provider_info: Optional[dict] = Field(None, description="Provider information")
    insurance_info: Optional[dict] = Field(None, description="Insurance information")
    
    @validator('code')
    def validate_code_format(cls, v):
        """Validate medical code format."""
        code = v.strip().upper().replace(' ', '')
        if not code:
            raise ValueError('Code cannot be empty')
        return code


class MedicalCodeValidationResponse(BaseModel):
    """Schema for medical code validation response."""
    code: str
    code_type: CodeType
    is_valid: bool
    confidence_score: float
    validation_message: str
    suggestions: Optional[List[str]] = None
    alternative_codes: Optional[List[str]] = None
    validation_details: Optional[dict] = None
    processing_time_ms: Optional[float] = None
    
    class Config:
        from_attributes = True


class BatchValidationRequest(BaseModel):
    """Schema for batch medical code validation."""
    codes: List[MedicalCodeValidationRequest] = Field(..., min_items=1, max_items=50)
    async_processing: bool = Field(False, description="Process batch asynchronously")
    
    @validator('codes')
    def validate_codes_list(cls, v):
        """Validate codes list."""
        if len(v) == 0:
            raise ValueError('At least one code is required')
        return v


class BatchValidationResponse(BaseModel):
    """Schema for batch validation response."""
    batch_id: str
    total_codes: int
    processed_count: int
    success_count: int
    failed_count: int
    results: List[MedicalCodeValidationResponse]
    processing_time_ms: Optional[float] = None
    errors: Optional[List[str]] = None
