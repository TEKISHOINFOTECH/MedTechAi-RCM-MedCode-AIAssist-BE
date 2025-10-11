"""
RCM API routes for EDI processing and medical coding.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db

router = APIRouter(prefix="/rcm-api", tags=["RCM API"])


# Pydantic models for request/response
class DocNotesRequest(BaseModel):
    doc_notes: str = Field(..., description="Doctor's clinical notes and observations")
    patient_historical_info: Optional[str] = Field(None, description="Patient's historical information (optional)")
    earlier_suggested_icd_codes: Optional[List[str]] = Field(None, description="Previously suggested ICD codes")


class ICDCodeRequest(BaseModel):
    doc_notes: str = Field(..., description="Doctor's clinical notes and observations")


class CPTCodeRequest(BaseModel):
    doc_notes: str = Field(..., description="Doctor's clinical notes and observations")
    patient_historical_info: Optional[str] = Field(None, description="Patient's historical information (optional)")
    earlier_suggested_icd_codes: Optional[List[str]] = Field(None, description="Previously suggested ICD codes")


class ICDCodeResponse(BaseModel):
    suggested_icd_codes: List[str] = Field(..., description="AI suggested ICD codes")
    confidence_scores: List[float] = Field(..., description="Confidence scores for each ICD code")
    reasoning: str = Field(..., description="AI reasoning for the suggestions")


class CPTCodeResponse(BaseModel):
    suggested_cpt_codes: List[str] = Field(..., description="AI suggested CPT codes")
    confidence_scores: List[float] = Field(..., description="Confidence scores for each CPT code")
    reasoning: str = Field(..., description="AI reasoning for the suggestions")


class SOAPResponse(BaseModel):
    improved_soap_format: str = Field(..., description="AI improved SOAP format notes")
    changes_made: List[str] = Field(..., description="List of improvements made")
    confidence_score: float = Field(..., description="Confidence in the improvements")


class XMLSaveRequest(BaseModel):
    xml_content: str = Field(..., description="Generated XML content to save")
    claim_id: Optional[str] = Field(None, description="Associated claim ID")


class XMLSaveResponse(BaseModel):
    status: str = Field(..., description="Save status")
    saved_xml_id: str = Field(..., description="ID of the saved XML")
    message: str = Field(..., description="Success message")


class ClaimDataRequest(BaseModel):
    """Request model for saving claim data to Supabase."""
    claim_id: str = Field(..., description="Claim ID (key from JSON object)")
    edi_json_payload: str = Field(..., description="JSON string to persist")


class ClaimDataResponse(BaseModel):
    """Response model for claim data operations."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    claim_id: str = Field(..., description="Claim ID")
    record_id: Optional[str] = Field(None, description="Database record ID")
    timestamp: str = Field(..., description="Operation timestamp")


class EDIClaimsRequest(BaseModel):
    """Request model for retrieving EDI claims data."""
    claim_id: Optional[str] = Field(None, description="Specific claim ID to retrieve (optional)")
    limit: Optional[int] = Field(10, description="Number of records to retrieve (default: 10)")
    offset: Optional[int] = Field(0, description="Number of records to skip (default: 0)")


class EDIClaimsResponse(BaseModel):
    """Response model for EDI claims data."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    claims: List[Dict[str, Any]] = Field(..., description="List of claim records")
    total_count: Optional[int] = Field(None, description="Total number of records")
    timestamp: str = Field(..., description="Operation timestamp")


# HIGH PRIORITY ENDPOINTS

@router.post("/edi_json_persist", summary="Save Claim Data to Supabase", response_model=ClaimDataResponse)
async def save_claim_data(
    request: ClaimDataRequest,
    db: Session = Depends(get_db)
):
    """
    Save claim data (JSON string) to Supabase claim_data table.
    
    **Priority: High**
    
    **UI Request:**
    - claim_id: Key from JSON object
    - edi_json_payload: JSON string to persist
    
    **BE Response:**
    - Success status and record details
    """
    try:
        from app.utils.supabase_client import get_supabase_service
        import uuid
        
        # Get Supabase service
        supabase_service = await get_supabase_service()
        
        # Generate UUID for claim_id and prepare data for insertion
        claim_uuid = str(uuid.uuid4())
        claim_data = {
            "claim_id": claim_uuid,
            "edi_json_payload": request.edi_json_payload
        }
        
        # Insert into Supabase
        result = await supabase_service.insert(
            table="claim_data",
            data=claim_data
        )
        
        # Extract record ID from result
        record_id = result[0].get("id") if result and len(result) > 0 else None
        
        return ClaimDataResponse(
            success=True,
            message="Claim data saved successfully to Supabase",
            claim_id=claim_uuid,
            record_id=record_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save claim data: {str(e)}"
        )


@router.get("/getEDIclaims_Jsondata", summary="Get EDI Claims JSON Data", response_model=EDIClaimsResponse)
async def get_edi_claims_jsondata(
    claim_id: Optional[str] = Query(None, description="Specific claim ID to retrieve (optional)"),
    limit: int = Query(10, description="Number of records to retrieve (default: 10)"),
    offset: int = Query(0, description="Number of records to skip (default: 0)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve EDI claims data (JSON payloads) from Supabase claim_data table.
    
    **Priority: High**
    
    **UI Request:**
    - claim_id: Optional specific claim ID to retrieve (query parameter)
    - limit: Number of records to retrieve (default: 10)
    - offset: Number of records to skip (default: 0)
    
    **BE Response:**
    - List of claim records with claim_id and edi_json_payload
    """
    try:
        from app.utils.supabase_client import get_supabase_service
        
        # Get Supabase service
        supabase_service = await get_supabase_service()
        
        # Prepare query parameters
        filters = {}
        if claim_id:
            filters["claim_id"] = claim_id
        
        # Retrieve data from Supabase
        result = await supabase_service.select(
            table="claim_data",
            columns="id, claim_id, edi_json_payload, created_at",
            filters=filters
        )
        
        # Apply pagination
        total_count = len(result)
        paginated_result = result[offset:offset + limit]
        
        # Format response data
        claims = []
        for record in paginated_result:
            claims.append({
                "id": record.get("id"),
                "claim_id": record.get("claim_id"),
                "edi_json_payload": record.get("edi_json_payload"),
                "created_at": record.get("created_at")
            })
        
        return EDIClaimsResponse(
            success=True,
            message=f"Retrieved {len(claims)} EDI claims records",
            claims=claims,
            total_count=total_count,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve EDI claims data: {str(e)}"
        )


@router.post("/getAISuggested_ICDCodes", summary="Get AI Suggested ICD Codes")
async def get_ai_suggested_icd_codes(
    request: ICDCodeRequest,
    db: Session = Depends(get_db)
):
    """
    AI LLM Call to get AI Suggested ICD Codes based on clinical notes.
    
    **Priority: High**
    
    **UI Request:** Doc Notes only
    **BE Response:** AI LLM ICD Codes
    """
    try:
        # TODO: Implement AI LLM logic here
        # For now, return mock response
        return {
            "api_method_name": "getAISuggested_ICDCodes",
            "status": "working",
            "message": "AI Suggested ICD Codes endpoint is functional",
            "mock_response": {
                "suggested_icd_codes": ["Z00.00", "Z12.11", "Z51.11"],
                "confidence_scores": [0.95, 0.87, 0.82],
                "reasoning": "Based on clinical notes analysis, these ICD codes best represent the patient's conditions."
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI ICD code suggestion failed: {str(e)}")


@router.post("/getCPTCodes", summary="Get CPT Codes for Selected ICD Code")
async def get_cpt_codes(
    request: CPTCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Get CPT codes for the selected ICD code based on clinical notes and patient history.
    
    **Priority: High**
    
    **UI Request:**
    - Doc Notes
    - Patient Historical Info (Optional, controlled via toggle)
    - Earlier suggested ICD codes
    
    **BE Response:**
    - CPT codes from LLM
    """
    try:
        # TODO: Implement AI LLM logic here
        # For now, return mock response
        return {
            "api_method_name": "getCPTCodes",
            "status": "working",
            "message": "CPT Codes endpoint is functional",
            "mock_response": {
                "suggested_cpt_codes": ["99213", "99214", "99215"],
                "confidence_scores": [0.92, 0.88, 0.85],
                "reasoning": "Based on ICD codes and clinical complexity, these CPT codes are most appropriate."
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPT code suggestion failed: {str(e)}")


# MEDIUM PRIORITY ENDPOINTS

@router.post("/uploadEDI_XML", summary="Upload EDI XML File")
async def upload_edi_xml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process EDI XML file.
    
    **Priority: Medium**
    
    **UI Request:** Will carry the XML file
    **BE Response:** 200 OK successful
    
    **UI Action:** "View Claims" button in "EDI File Upload & Processing" needs to hit this API
    """
    try:
        # TODO: Implement EDI XML processing logic here
        # For now, return mock response
        return {
            "api_method_name": "uploadEDI_XML",
            "status": "working",
            "message": "EDI XML upload endpoint is functional",
            "file_info": {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": "Processing..."
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EDI XML upload failed: {str(e)}")


@router.post("/improveToSOAP", summary="Improve Clinical Notes to SOAP Format")
async def improve_to_soap(
    request: ICDCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Improve clinical notes with SOAP format using AI LLM.
    
    **Priority: Medium**
    
    **UI Request:** Doc Notes
    **BE Response:** SOAP formatted clinical notes
    """
    try:
        # TODO: Implement AI LLM logic here
        # For now, return mock response
        return {
            "api_method_name": "improveToSOAP",
            "status": "working",
            "message": "SOAP improvement endpoint is functional",
            "mock_response": {
                "soap_format": "S: Patient reports chest pain and shortness of breath\nO: Physical examination reveals elevated blood pressure\nA: Assessment shows possible cardiac event\nP: Plan includes EKG, cardiac enzymes, and cardiology consultation",
                "improvements_made": [
                    "Structured notes into SOAP format",
                    "Added objective findings",
                    "Improved assessment clarity",
                    "Enhanced plan specificity"
                ],
                "confidence_score": 0.89
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SOAP improvement failed: {str(e)}")


# LOW PRIORITY ENDPOINTS

@router.get("/getEDIclaims_data", summary="Get EDI Claims Data")
async def get_edi_claims_data(
    limit: int = Query(100, description="Number of claims to retrieve"),
    offset: int = Query(0, description="Number of claims to skip"),
    db: Session = Depends(get_db)
):
    """
    Fetch all available Claims data in JSON format.
    
    **Priority: Low**
    
    **UI GET Request:** To fetch all available Claims data in JSON
    """
    try:
        # TODO: Implement database query logic here
        # For now, return mock response
        return {
            "api_method_name": "getEDIclaims_data",
            "status": "working",
            "message": "EDI Claims data endpoint is functional",
            "mock_response": {
                "claims": [
                    {
                        "claim_id": "CLM-001",
                        "patient_name": "John Doe",
                        "provider": "Dr. Smith",
                        "amount": 150.00,
                        "status": "processed"
                    },
                    {
                        "claim_id": "CLM-002",
                        "patient_name": "Jane Smith",
                        "provider": "Dr. Johnson",
                        "amount": 275.50,
                        "status": "pending"
                    }
                ],
                "total_count": 2,
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EDI claims data retrieval failed: {str(e)}")


@router.post("/saveXML", summary="Save Generated XML")
async def save_xml(
    request: XMLSaveRequest,
    db: Session = Depends(get_db)
):
    """
    Save the UI Generated XML to database.
    
    **Priority: Low**
    
    **UI Request:** Will be XML Generated to BE
    **BE Response:** DB Save Successful
    """
    try:
        # TODO: Implement XML saving logic here
        # For now, return mock response
        return {
            "api_method_name": "saveXML",
            "status": "working",
            "message": "XML save endpoint is functional",
            "mock_response": {
                "saved_xml_id": "XML-12345",
                "status": "success",
                "message": "XML saved successfully to database"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"XML save failed: {str(e)}")


# PING ENDPOINT
@router.get("/ping", summary="RCM API Ping")
async def rcm_api_ping():
    """
    Simple ping endpoint to verify RCM API connectivity.
    """
    return "RCM-BE Ping is Successful"


# HEALTH CHECK ENDPOINT
@router.get("/health", summary="RCM API Health Check")
async def rcm_api_health():
    """
    Health check for RCM API endpoints.
    """
    return {
        "api_method_name": "health",
        "status": "healthy",
        "message": "RCM API is operational",
        "endpoints": [
            "GET /rcm-api/ping (Connectivity Check)",
            "POST /rcm-api/edi_json_persist (High Priority - Supabase Integration)",
            "GET /rcm-api/getEDIclaims_Jsondata (High Priority - Data Retrieval)",
            "POST /rcm-api/getAISuggested_ICDCodes (High Priority)",
            "POST /rcm-api/getCPTCodes (High Priority)",
            "POST /rcm-api/uploadEDI_XML (Medium Priority)",
            "POST /rcm-api/improveToSOAP (Medium Priority)",
            "GET /rcm-api/getEDIclaims_data (Low Priority)",
            "POST /rcm-api/saveXML (Low Priority)"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
