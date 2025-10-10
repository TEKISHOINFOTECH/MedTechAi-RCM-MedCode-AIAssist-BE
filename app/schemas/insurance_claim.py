"""
Pydantic schemas for insurance claim API endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.insurance_claim import ClaimStatus, PayerType


class InsuranceClaimBase(BaseModel):
    """Base insurance claim schema."""
    claim_id: str = Field(..., min_length=1, max_length=100, description="Unique claim identifier")
    patient_id: str = Field(..., min_length=1, max_length=100, description="Patient identifier")
    provider_id: str = Field(..., min_length=1, max_length=100, description="Provider identifier")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")
    
    # Payer information
    payer_name: str = Field(..., min_length=1, max_length=200, description="Insurance payer name")
    payer_type: PayerType = Field(..., description="Type of insurance payer")
    
    # Amounts
    claim_amount: float = Field(..., ge=0, description="Total claim amount")
    billed_amount: float = Field(..., ge=0, description="Amount billed")
    
    @validator('claim_id')
    def validate_claim_id(cls, v):
        """Validate claim ID format."""
        claim_id = v.strip()
        if not claim_id:
            raise ValueError('Claim ID cannot be empty')
        return claim_id


class InsuranceClaimCreate(InsuranceClaimBase):
    """Schema for creating a new insurance claim."""
    medical_code_id: Optional[int] = Field(None, description="Associated medical code ID")
    approved_amount: Optional[float] = Field(None, ge=0, description="Approved amount")
    submitted_date: Optional[datetime] = Field(None, description="Claim submission date")


class InsuranceClaimUpdate(BaseModel):
    """Schema for updating an insurance claim."""
    status: Optional[ClaimStatus] = None
    approved_amount: Optional[float] = Field(None, ge=0)
    processed_date: Optional[datetime] = None
    
    # AI validation results
    ai_validation_passed: Optional[bool] = None
    validation_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    correction_suggestions: Optional[str] = None
    
    # Denial and appeal information
    denial_reason: Optional[str] = None
    appeal_submitted: Optional[bool] = None
    appeal_date: Optional[datetime] = None


class InsuranceClaimResponse(InsuranceClaimBase):
    """Schema for insurance claim API response."""
    id: int
    medical_code_id: Optional[int]
    status: ClaimStatus
    submitted_date: datetime
    processed_date: Optional[datetime]
    approved_amount: Optional[float]
    
    # AI validation results
    ai_validation_passed: bool
    validation_confidence: float
    correction_suggestions: Optional[str]
    
    # Denial and appeal information
    denial_reason: Optional[str]
    appeal_submitted: bool
    appeal_date: Optional[datetime]
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ClaimProcessingRequest(BaseModel):
    """Schema for claim processing request."""
    patient_info: dict = Field(..., description="Patient demographic and insurance information")
    claims_data: dict = Field(..., description="Claim details and amounts")
    codes: List[dict] = Field(..., min_items=1, description="Medical codes in claim")
    documentation: Optional[dict] = Field(None, description="Clinical notes or documentation")
    provider_info: Optional[dict] = Field(None, description="Provider/service location information")
    
    @validator('codes')
    def validate_codes(cls, v):
        """Validate codes list."""
        if not v:
            raise ValueError('At least one medical code is required')
        return v


class ClaimProcessingResponse(BaseModel):
    """Schema for claim processing response."""
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall denial risk score")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    risk_level: str = Field(..., description="Risk categorization")
    recommendations: List[dict] = Field(default_factory=list, description="Improvement recommendations")
    code_validation: List[dict] = Field(default_factory=list, description="Individual code validation")
    optimized_codes: List[dict] = Field(default_factory=list, description="Suggested code optimizations")
    documentation_needs: List[dict] = Field(default_factory=list, description="Required documentation")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Analysis confidence")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    
    class Config:
        from_attributes = True


class DenialAnalysisRequest(BaseModel):
    """Schema for denial analysis request."""
    # Single denial analysis
    denial_reason: Optional[str] = Field(None, description="Official reason for denial")
    denial_details: Optional[str] = Field(None, description="Detailed denial explanation")
    denial_date: Optional[datetime] = Field(None, description="Date of denial")
    payer: Optional[dict] = Field(None, description="Insurance payer information")
    original_claim_data: Optional[dict] = Field(None, description="Original denied claim data")
    patient_info: Optional[dict] = Field(None, description="Patient demographic information")
    
    # Batch analysis
    denials: Optional[List[dict]] = Field(None, description="List of denial records for batch analysis")
    analysis_type: Optional[str] = Field("pattern", description="Type of analysis: pattern, trend, root_cause")
    
    @validator('denial_reason', 'denials')
    def validate_single_or_batch(cls, v, values):
        """Ensure we have either single denial or batch data."""
        denial_reason = values.get('denial_reason')
        denials = values.get('denials')
        
        if not denial_reason and not denials:
            raise ValueError('Either denial_reason or denials list must be provided')
        
        return v


class DenialAnalysisResponse(BaseModel):
    """Schema for denial analysis response."""
    # Common fields for both single and batch analysis
    success_probability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Appeal success likelihood")
    analysis_type: Optional[str] = Field(None, description="Type of analysis performed")
    
    # Single denial fields
    confidence_level: Optional[str] = Field(None, description="Confidence in analysis")
    appeal_strategy: Optional[str] = Field(None, description="Primary appeal argument")
    approach: Optional[str] = Field(None, description="Appeal approach style")
    required_documentation: Optional[List[dict]] = Field(None, description="Documents needed for appeal")
    legal_arguments: Optional[List[dict]] = Field(None, description="Legal/regulatory basis for appeal")
    timeline_recommendations: Optional[dict] = Field(None, description="Suggested appeal timeline")
    preventive_measures: Optional[List[dict]] = Field(None, description="Actions to prevent similar denials")
    risk_factors: Optional[List[dict]] = Field(None, description="Risk factors affecting appeal")
    
    # Batch analysis fields
    pattern_analysis: Optional[dict] = Field(None, description="Pattern identification results")
    root_causes: Optional[List[dict]] = Field(None, description="Root cause analysis results")
    trends: Optional[dict] = Field(None, description="Trend analysis results")
    strategic_recommendations: Optional[List[dict]] = Field(None, description="Strategic improvement recommendations")
    prevention_strategy: Optional[dict] = Field(None, description="Prevention strategy framework")
    
    # Meta information
    processing_time_ms: Optional[float] = Field(None, description="Analysis processing time")
    
    class Config:
        from_attributes = True
