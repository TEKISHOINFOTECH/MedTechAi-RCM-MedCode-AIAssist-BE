"""
API routes for the Enhanced Medical Coding Orchestrator.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.services.orchestrator.enhanced_orchestrator import EnhancedMedicalCodingOrchestrator


router = APIRouter(prefix="/api/v1/orchestrator", tags=["orchestrator"])


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator execution."""
    csv_path: Optional[str] = Field(None, description="Path to CSV file with medical data")
    hl7_text: Optional[str] = Field(None, description="HL7 formatted text data")
    clinical_notes: Optional[str] = Field(None, description="Clinical notes text")
    manual_codes: Optional[Dict[str, Any]] = Field(None, description="Manually provided codes")
    setting: str = Field("Outpatient", description="Clinical setting (Outpatient/Inpatient)")
    specialty: str = Field("General Practice", description="Medical specialty")
    payer_type: str = Field("Commercial", description="Insurance payer type")
    enable_parallel: bool = Field(True, description="Enable parallel processing")
    confidence_threshold: float = Field(0.85, description="Confidence threshold for validation")


class OrchestratorResponse(BaseModel):
    """Response model for orchestrator execution."""
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    confidence_score: Optional[float] = None
    recommendations: Optional[List[str]] = None


@router.post("/execute", response_model=OrchestratorResponse)
async def execute_orchestrator(request: OrchestratorRequest):
    """
    Execute the Enhanced Medical Coding Orchestrator.
    
    This endpoint provides access to the full orchestrator pipeline with:
    - Parallel agent execution for faster processing
    - RAG-integrated validation against medical coding guidelines
    - Multi-stage validation (code accuracy, medical necessity, compliance)
    - Executive summary with financial impact and priority actions
    - Automated approval decision with confidence scoring
    
    Args:
        request: OrchestratorRequest with all necessary parameters
        
    Returns:
        OrchestratorResponse with execution results and recommendations
    """
    try:
        import time
        start_time = time.time()
        
        # Initialize orchestrator
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Execute pipeline
        result = await orchestrator.execute_pipeline(
            csv_path=request.csv_path,
            hl7_text=request.hl7_text,
            clinical_notes=request.clinical_notes,
            manual_codes=request.manual_codes,
            setting=request.setting,
            specialty=request.specialty,
            payer_type=request.payer_type,
            enable_parallel=request.enable_parallel,
            confidence_threshold=request.confidence_threshold
        )
        
        execution_time = time.time() - start_time
        
        # Extract key metrics
        confidence_score = result.get('confidence_score', 0.0)
        recommendations = result.get('recommendations', [])
        
        return OrchestratorResponse(
            success=True,
            message="Orchestrator execution completed successfully",
            result=result,
            execution_time=execution_time,
            confidence_score=confidence_score,
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator execution failed: {str(e)}"
        )


@router.get("/health")
async def orchestrator_health():
    """
    Health check for the orchestrator service.
    
    Returns:
        Dict with orchestrator status and capabilities
    """
    try:
        # Test orchestrator initialization
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        return {
            "status": "healthy",
            "service": "Enhanced Medical Coding Orchestrator",
            "capabilities": [
                "Parallel agent execution",
                "RAG-integrated validation",
                "Multi-stage validation",
                "Executive summary generation",
                "Automated approval decisions"
            ],
            "supported_inputs": [
                "CSV files",
                "HL7 text",
                "Clinical notes",
                "Manual codes"
            ],
            "supported_settings": [
                "Outpatient",
                "Inpatient"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator health check failed: {str(e)}"
        )


@router.get("/capabilities")
async def get_orchestrator_capabilities():
    """
    Get detailed information about orchestrator capabilities.
    
    Returns:
        Dict with detailed capability information
    """
    return {
        "orchestrator": "Enhanced Medical Coding Orchestrator",
        "version": "1.0.0",
        "features": {
            "parallel_execution": {
                "description": "Execute multiple agents in parallel for faster processing",
                "enabled": True
            },
            "rag_integration": {
                "description": "RAG-integrated validation against medical coding guidelines",
                "enabled": True
            },
            "multi_stage_validation": {
                "description": "Multi-stage validation (code accuracy, medical necessity, compliance)",
                "enabled": True
            },
            "executive_summary": {
                "description": "Generate executive summary with financial impact and priority actions",
                "enabled": True
            },
            "automated_decisions": {
                "description": "Automated approval decisions with confidence scoring",
                "enabled": True
            }
        },
        "supported_agents": [
            "ParserAgent",
            "NoteToICDAgent", 
            "ICDToCPTAgent",
            "CodeValidationAgent",
            "SummarizerAgent"
        ],
        "supported_formats": [
            "CSV",
            "HL7",
            "Clinical Notes",
            "Manual Codes"
        ]
    }


@router.post("/validate-codes")
async def validate_medical_codes(
    codes: List[str] = Body(..., description="List of medical codes to validate"),
    setting: str = Body("Outpatient", description="Clinical setting"),
    specialty: str = Body("General Practice", description="Medical specialty")
):
    """
    Validate a list of medical codes using the orchestrator.
    
    Args:
        codes: List of medical codes to validate
        setting: Clinical setting
        specialty: Medical specialty
        
    Returns:
        Validation results for each code
    """
    try:
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Create manual codes dict
        manual_codes = {
            "icd_codes": [code for code in codes if code.startswith(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'))],
            "cpt_codes": [code for code in codes if code.isdigit()],
            "hcpcs_codes": [code for code in codes if code.startswith(('A', 'B', 'C', 'D', 'E', 'G', 'H', 'J', 'K', 'L', 'M', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'))]
        }
        
        result = await orchestrator.execute_pipeline(
            manual_codes=manual_codes,
            setting=setting,
            specialty=specialty,
            enable_parallel=True,
            confidence_threshold=0.85
        )
        
        return {
            "success": True,
            "validated_codes": codes,
            "results": result,
            "summary": result.get('executive_summary', {}),
            "confidence_score": result.get('confidence_score', 0.0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Code validation failed: {str(e)}"
        )
