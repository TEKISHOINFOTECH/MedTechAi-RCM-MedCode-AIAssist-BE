"""
UAE Health System API Routes for Dubai Health Authority (DHA) claims processing.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog

from app.agents.uae_health_parser_agent import (
    UAEHealthParserAgent,
    UAEHealthCodeExtractorAgent,
    UAEHealthValidatorAgent
)
from app.models.uae_health import (
    UAEClaimSubmission,
    parse_uae_claim_xml,
    extract_clinical_context,
    get_icd_validation_data,
    get_cpt_validation_data
)

from .usecase1 import UseCase1Pipeline

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/uae-health", tags=["UAE Health System"])


class UAEXMLRequest(BaseModel):
    """Request model for UAE XML parsing."""
    xml_content: str
    parse_options: Optional[Dict[str, Any]] = {}


class UAEValidationRequest(BaseModel):
    """Request model for UAE health validation."""
    submission_data: Dict[str, Any]
    validation_level: str = "standard"  # standard, comprehensive, medical_only


class UAEMedicalCodingRequest(BaseModel):
    """Request model for UAE medical coding validation."""
    xml_content: str
    payer_id: Optional[str] = None
    provider_id: Optional[str] = None


@router.post("/parse")
async def parse_uae_xml_submission(request: UAEXMLRequest):
    """
    Parse UAE health system XML submission.
    
    Accepts Claim.Submission XML and returns structured medical coding data.
    """
    try:
        logger.info("UAE health XML parsing request started", 
                   xml_length=len(request.xml_content))
        
        # Initialize parser agent
        parser_agent = UAEHealthParserAgent()
        
        # Process XML content
        result = await parser_agent.process({
            "xml_content": request.xml_content,
            "parse_options": request.parse_options or {}
        })
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=400, 
                detail=f"XML parsing failed: {result.get('error', 'Unknown error')}"
            )
        
        logger.info("UAE health XML parsing completed successfully",
                   claim_count=result["claim_count"],
                   icd_count=len(result["medical_codes"]["icd_codes"]),
                   cpt_count=len(result["medical_codes"]["cpt_codes"]))
        
        return {
            "status": "success",
            "data": {
                "claims_summary": result["summary"],
                "medical_codes": result["medical_codes"],
                "clinical_context": result["clinical_context"],
                "validation_data": result["validation_data"],
                "claim_count": result["claim_count"]
            },
            "metadata": result["parser_metadata"]
        }
        
    except Exception as e:
        logger.error("UAE health XML parsing failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_uae_submission(request: UAEValidationRequest):
    """
    Validate UAE-specific health system requirements.
    
    Validates Emirates IDs, DHA credentials, financial consistency, and coding formats.
    """
    try:
        logger.info("UAE health validation request started",
                   validation_level=request.validation_level)
        
        # Initialize validator agent
        validator_agent = UAEHealthValidatorAgent()
        
        # Process validation
        result = await validator_agent.process({
            "parsed_submission": request.submission_data
        })
        
        if result["validation_status"] == "error":
            raise HTTPException(
                status_code=400,
                detail=f"Validation failed: {result.get('recommendations', ['Unknown error'])}"
            )
        
        logger.info("UAE health validation completed",
                   overall_status=result["validation_status"])
        
        return {
            "status": "success",
            "validation_status": result["validation_status"],
            "validation_results": result["validation_results"],
            "recommendations": result["recommendations"],
            "metadata": result["validator_metadata"]
        }
        
    except Exception as e:
        logger.error("UAE health validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/medical-coding")
async def validate_uae_medical_codes(request: UAEMedicalCodingRequest):
    """
    Run medical coding validation for UAE health claims.
    
    Combines UAE XML parsing with AI-powered ICD/CPT code validation.
    """
    try:
        logger.info("UAE medical coding validation started",
                   payer_id=request.payer_id,
                   provider_id=request.provider_id)
        
        # Step 1: Parse XML content
        parser_agent = UAEHealthParserAgent()
        parsed_result = await parser_agent.process({
            "xml_content": request.xml_content
        })
        
        if parsed_result["status"] != "success":
            raise HTTPException(
                status_code=400,
                detail=f"XML parsing failed: {parsed_result.get('error', 'Unknown error')}"
            )
        
        # Step 2: Extract medical codes
        extractor_agent = UAEHealthCodeExtractorAgent()
        extracted_data = await extractor_agent.process({
            "clinical_context": parsed_result["clinical_context"],
            "icd_codes": parsed_result["medical_codes"]["icd_codes"],
            "cpt_codes": parsed_result["medical_codes"]["cpt_codes"]
        })
        
        if not extracted_data["validation_ready"]:
            raise HTTPException(
                status_code=400,
                detail="Code extraction failed - data not ready for validation"
            )
        
        # Step 3: Run medical coding validation pipeline
        pipeline = UseCase1Pipeline()
        
        # Prepare manual codes for comparison (if available)
        manual_codes = {
            "icd": extracted_data["extracted_codes"]["diagnoses"]["codes"],
            "cpt": extracted_data["extracted_codes"]["procedures"]["codes"]
        }
        
        coding_result = await pipeline.run(
            manual_codes=manual_codes,
            hl7_text=extracted_data["clinical_notes"]
        )
        
        logger.info("UAE medical coding validation completed successfully",
                   diagnostic_validation=len(coding_result.get("icd", [])),
                   procedure_validation=len(coding_result.get("cpt", [])),
                   validation_report=coding_result.get("validation", {}).get("status"))
        
        return {
            "status": "success",
            "data": {
                "parsed_submission": parsed_result["summary"],
                "medical_codes": {
                    "icd_codes": extracted_data["extracted_codes"]["diagnoses"]["unique_codes"],
                    "cpt_codes": extracted_data["extracted_codes"]["procedures"]["unique_codes"],
                    "context": extracted_data["clinical_notes"]
                },
                "ai_validation": coding_result
            },
            "metadata": {
                "parser_metadata": parsed_result["parser_metadata"],
                "extractor_metadata": extracted_data["extractor_metadata"]
            }
        }
        
    except Exception as e:
        logger.error("UAE medical coding validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-and-process")
async def upload_uae_xml_file(file: UploadFile = File(...)):
    """
    Upload UAE health XML file and process it end-to-end.
    
    Accepts XML file upload and returns complete validation results.
    """
    try:
        logger.info("UAE health XML file upload started",
                   filename=file.filename,
                   content_type=file.content_type)
        
        # Validate file type
        if not file.filename.endswith('.xml'):
            raise HTTPException(
                status_code=400,
                detail="Only XML files are supported for UAE health processing"
            )
        
        # Read file content
        xml_content = await file.read()
        xml_text = xml_content.decode('utf-8')
        
        # Run complete pipeline
        pipeline_request = UAEMedicalCodingRequest(
            xml_content=xml_text,
            payer_id=None,  # Could be extracted from XML
            provider_id=None  # Could be extracted from XML
        )
        
        result = await validate_uae_medical_codes(pipeline_request)
        
        logger.info("UAE health XML file upload completed successfully",
                   filename=file.filename,
                   size=len(xml_text))
        
        return {
            "status": "success",
            "filename": file.filename,
            "file_size": len(xml_text),
            "data": result["data"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        logger.error("UAE health XML file upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample-data")
async def get_sample_data():
    """
    Get sample UAE health XML data for testing.
    """
    sample_xml = '''<?xml version="1.0" encoding="utf-8"?>
<Claim.Submission xmlns="http://www.eclaimlink.ae/DHD/ValidationSchema">
  <Header>
    <SenderID>HOSPITAL_ABC</SenderID>
    <ReceiverID>DHA_DHPO</ReceiverID>
    <TransactionDate>2025-09-30T14:30:46Z</TransactionDate>
    <RecordCount>1</RecordCount>
    <DispositionFlag>Original</DispositionFlag>
  </Header>
  <Claim>
    <ID>CLM-SAMPLE-001</ID>
    <PayerID>PAYER_SAMPLE</PayerID>
    <ProviderID>PROV_SAMPLE</ProviderID>
    <EmiratesIDNumber>784-1990-1234567-1</EmiratesIDNumber>
    <Gross>350.00</Gross>
    <PatientShare>35.00</PatientShare>
    <Net>315.00</Net>
    <Encounter>
      <FacilityID>FAC-OP-001</FacilityID>
      <Type>OP</Type>
      <PatientID>MRN-SAMPLE</PatientID>
      <Start>2025-09-01T09:15:00</Start>
      <End>2025-09-01T10:05:00</End>
    </Encounter>
    <Diagnosis>
      <Type>Primary</Type>
      <Code>J06.9</Code>
    </Diagnosis>
    <Activity>
      <ID>ACT-1</ID>
      <Start>2025-09-01T09:20:00</Start>
      <Type>Consultation</Type>
      <Code>99213</Code>
      <Quantity>1</Quantity>
      <Net>200.00</Net>
      <Clinician>DHA-LIC-12345</Clinician>
    </Activity>
  </Claim>
</Claim.Submission>'''
    
    return {
        "status": "success",
        "description": "Sample UAE Health System XML for testing",
        "xml_content": sample_xml,
        "instructions": [
            "Copy the XML content above",
            "Use /parse endpoint to test parsing",
            "Use /medical-coding endpoint for AI validation"
        ]
    }


@router.get("/health")
async def uae_health_status():

