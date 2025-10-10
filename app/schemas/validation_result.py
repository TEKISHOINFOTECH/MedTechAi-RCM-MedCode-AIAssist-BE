"""
Pydantic schemas for validation result API endpoints.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator

from app.models.validation_result import ValidationStatus, ValidationMethod


class ValidationResultCreate(BaseModel):
    """Schema for creating a new validation result."""
    medical_code_id: Optional[int] = Field(None, description="Associated medical code ID")
    validation_method: ValidationMethod = Field(..., description="Method used for validation")
    status: ValidationStatus = Field(..., description="Validation status")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    
    # Input data
    input_code: str = Field(..., min_length=1, max_length=100, description="Input medical code")
    input_type: str = Field(..., min_length=1, max_length=50, description="Code type")
    input_context: Optional[str] = Field(None, description="Validation context")
    
    # Output results
    validated_code: Optional[str] = Field(None, max_length=100, description="Validated/corrected code")
    validation_message: Optional[str] = Field(None, description="Validation result message")
    suggestions: Optional[List[str]] = Field(None, description="Suggestions for improvement")
    error_message: Optional[str] = Field(None, description="Error message if validation failed")
    
    # Performance metrics
    processing_time_ms: Optional[float] = Field(None, ge=0, description="Processing time in milliseconds")
    tokens_used: Optional[int] = Field(None, ge=0, description="Tokens consumed during validation")
    
    # Agent information
    agent_name: Optional[str] = Field(None, max_length=100, description="Agent that performed validation")
    agent_version: Optional[str] = Field(None, max_length=50, description="Agent version")
    
    @validator('input_code')
    def validate_input_code(cls, v):
        """Validate input code format."""
        code = v.strip().upper().replace(' ', '')
        if not code:
            raise ValueError('Input code cannot be empty')
        return code


class ValidationResultResponse(ValidationResultCreate):
    """Schema for validation result API response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ValidationRequest(BaseModel):
    """Schema for general validation request."""
    codes: List[dict] = Field(..., min_items=1, description="Medical codes to validate")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional validation context")
    validation_type: Optional[str] = Field("comprehensive", description="Type of validation to perform")
    include_alternatives: bool = Field(True, description="Include alternative code suggestions")
    validate_context: bool = Field(True, description="Perform context-aware validation")
    
    @validator('codes')
    def validate_codes_list(cls, v):
        """Validate codes list."""
        if not v:
            raise ValueError('At least one medical code is required')
        
        required_fields = ['code', 'code_type']
        for code in v:
            for field in required_fields:
                if field not in code:
                    raise ValueError(f'Missing required field "{field}" in code: {code}')
        
        return v


class ValidationSummary(BaseModel):
    """Schema for validation summary statistics."""
    total_validations: int = Field(..., ge=0, description="Total number of validations")
    successful_validations: int = Field(..., ge=0, description="Number of successful validations")
    failed_validations: int = Field(..., ge=0, description="Number of failed validations")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    average_processing_time: float = Field(..., ge=0, description="Average processing time in MS")
    validation_method_stats: Dict[str, int] = Field(default_factory=dict, description="Statistics by validation method")
    agent_performance: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Agent performance metrics")


class BulkValidationRequest(BaseModel):
    """Schema for bulk validation request."""
    validation_requests: List[ValidationRequest] = Field(..., min_items=1, max_items=100, description="List of validation requests")
    parallel_processing: bool = Field(True, description="Process requests in parallel")
    return_detailed_results: bool = Field(True, description="Include detailed results for each validation")
    
    @validator('validation_requests')
    def validate_request_limit(cls, v):
        """Validate request count limit."""
        if len(v) > 100:
            raise ValueError('Maximum 100 validation requests allowed per bulk operation')
        return v


class BulkValidationResponse(BaseModel):
    """Schema for bulk validation response."""
    batch_id: str = Field(..., description="Unique batch identifier")
    total_requests: int = Field(..., ge=0, description="Total number of validation requests")
    processed_count: int = Field(..., ge=0, description="Number of processed requests")
    success_count: int = Field(..., ge=0, description="Number of successful validations")
    failed_count: int = Field(..., ge=0, description="Number of failed validations")
    results: List[ValidationResultResponse] = Field(default_factory=list, description="Validation results")
    summary: Optional[ValidationSummary] = Field(None, description="Validation summary statistics")
    processing_time_ms: Optional[float] = Field(None, description="Total processing time")
    errors: Optional[List[str]] = Field(None, description="Error messages for failed validations")
    
    class Config:
        from_attributes = True
