"""
RCM API routes for EDI processing and medical coding.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
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
    edi_json_payload: Union[str, Dict[str, Any]] = Field(..., description="JSON string or object to persist")


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


class ClaimIdsDataRecord(BaseModel):
    """Model for claim_ids_data_table records."""
    id: str = Field(..., description="Record ID")
    claimid: str = Field(..., description="Claim ID")
    patientid: str = Field(..., description="Patient ID")
    providerid: str = Field(..., description="Provider ID")
    dateofservice: date = Field(..., description="Date of service")
    amount: float = Field(..., description="Claim amount")
    denialrisk: Optional[str] = Field(None, description="Denial risk level")
    claimriskscore: Optional[float] = Field(None, description="Claim risk score")
    created_at: datetime = Field(..., description="Record creation timestamp")


class ClaimIdsDataResponse(BaseModel):
    """Response model for claim_ids_data_table data."""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: List[ClaimIdsDataRecord] = Field(..., description="List of claim data records")
    total_count: Optional[int] = Field(None, description="Total number of records")
    timestamp: str = Field(..., description="Operation timestamp")


class AISuggestedICDRequest(BaseModel):
    """Request model for AI suggested ICD codes."""
    clinical_note: str = Field(..., description="Clinical note text")
    patient_historical_ailments: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Patient's historical ailments/diagnoses"
    )


class ICDCodeSuggestion(BaseModel):
    """Individual ICD code suggestion."""
    icd_code: str = Field(..., description="ICD-10 code")
    icd_title: str = Field(..., description="ICD-10 code title")
    confidence_score: float = Field(..., description="Confidence level as percentage")
    explanation: str = Field(..., description="1-2 line summary why this code is relevant")
    clinical_relevance: Optional[str] = Field(None, description="Short reasoning describing clinical link")


class AISuggestedICDResponse(BaseModel):
    """Response model for AI suggested ICD codes."""
    ai_suggested_icd_codes: List[ICDCodeSuggestion] = Field(..., description="List of AI suggested ICD codes")


class AISuggestedCPTRequest(BaseModel):
    """Request model for AI suggested CPT codes."""
    clinical_notes: str = Field(..., description="Free-text clinician documentation for this encounter.")
    history: Optional[str] = Field(None, description="Pertinent history/ongoing problems, meds, devices, allergies.")
    selected_icds: Optional[List[str]] = Field(None, description="ICD-10-CM codes marked as relevant.")
    max_results: int = Field(10, ge=1, le=20, description="Maximum CPT items to return")


class CPTSuggestion(BaseModel):
    """Individual CPT code suggestion adhering to ProCoder schema."""
    code: str = Field(..., description="CPT code (AMA CPT only)")
    confidence: int = Field(..., ge=90, le=100, description="Integer confidence between 90 and 100")
    short_title: str = Field(..., description="Concise CPT short title")
    description: str = Field(..., description="1–2 line rationale tied to documentation and related diagnosis")


class AISuggestedCPTResponse(BaseModel):
    """Response model for AI suggested CPT codes."""
    results: List[CPTSuggestion] = Field(..., description="CPT suggestions sorted by confidence desc")


class SOAPFormatRequest(BaseModel):
    """Request model for SOAP format conversion."""
    clinical_note: str = Field(..., description="Clinical note text to convert to SOAP format")


class SOAPFormattedText(BaseModel):
    """SOAP formatted text structure."""
    Subjective: List[str] = Field(..., description="Patient-reported symptoms and history")
    Objective: List[str] = Field(..., description="Observable findings and measurements")
    Assessment: List[str] = Field(..., description="Diagnoses and medical impressions")
    Plan: List[str] = Field(..., description="Treatment plans and follow-up actions")


class SOAPFormatResponse(BaseModel):
    """Response model for SOAP format conversion."""
    SOAP_Formatted_Text: SOAPFormattedText = Field(..., description="SOAP formatted clinical notes")


# SOAP CONVERSION FUNCTION

async def convert_to_soap_format(clinical_note: str) -> SOAPFormattedText:
    """
    Convert clinical notes to SOAP format using LLM.
    
    Args:
        clinical_note: The clinical note text to convert
        
    Returns:
        SOAPFormattedText: Structured SOAP format data
        
    Raises:
        Exception: If LLM call or parsing fails
    """
    from app.utils.llm import LLMClient
    import json
    
    # Initialize LLM client
    llm_client = LLMClient()
    
    # Construct the prompt
    prompt = f"""You are a senior medical scribe. Convert the following free-text clinical note into a SOAP summary. 

Return ONLY valid JSON in this exact schema: 

"SOAP_Formatted_Text" : {{ 
  "Subjective": ["...","..."],   // bullet points; strings only 
  "Objective": ["...","..."], 
  "Assessment": ["...","..."],   // diagnoses/impressions 
  "Plan": ["...","..."]          // treatments, orders, follow-up 
}} 

Rules: 
- No fields outside the 4 keys above. 
- No hallucinations or inferences beyond the source. 
- If a section is empty, use ["None documented."]. 
- Normalize units/dates; expand abbreviations only if unambiguous. 

Source clinical notes: 
{clinical_note}"""

    # Prepare messages for LLM
    messages = [
        {"role": "system", "content": "You are a senior medical scribe specializing in SOAP note conversion."},
        {"role": "user", "content": prompt}
    ]
    
    # Call LLM
    response = await llm_client.chat(
        messages=messages,
        temperature=0.1,
        max_tokens=2000
    )
    
    # Parse the JSON response
    try:
        # Extract JSON from response (in case there's extra text)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_response = response[json_start:json_end]
            parsed_response = json.loads(json_response)
        else:
            parsed_response = json.loads(response)
        
        # Extract SOAP data from response
        soap_data = parsed_response.get("SOAP_Formatted_Text", {})
        
        # Create SOAPFormattedText object with defaults for missing sections
        soap_formatted_text = SOAPFormattedText(
            Subjective=soap_data.get("Subjective", ["None documented."]),
            Objective=soap_data.get("Objective", ["None documented."]),
            Assessment=soap_data.get("Assessment", ["None documented."]),
            Plan=soap_data.get("Plan", ["None documented."])
        )
        
        return soap_formatted_text
        
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse LLM response as JSON: {str(e)}. Response: {response}")


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
    - claim_id: Claim ID from frontend (used directly as text)
    - edi_json_payload: JSON string or object to persist (will be cleansed and validated)
    
    **BE Processing:**
    - Accepts both string and object payloads
    - Validates JSON format
    - Handles escaped sequences (newlines, tabs)
    - Removes escape characters
    - Uses provided claim_id directly as text
    - Stores clean JSON in Supabase
    
    **BE Response:**
    - Success status and record details
    """
    import json
    
    # Clean and validate the JSON payload first
    try:
        # Handle both string and object payloads
        if isinstance(request.edi_json_payload, str):
            # Parse the JSON string to validate it and remove escape characters
            parsed_json = json.loads(request.edi_json_payload)
        else:
            # Already a dictionary/object, use it directly
            parsed_json = request.edi_json_payload
        
        # Convert to clean JSON string without escape characters
        clean_json_payload = json.dumps(parsed_json, separators=(',', ':'))
        
    except json.JSONDecodeError as json_error:
        # If initial parsing fails, try to fix common issues
        try:
            # Replace escaped newlines and other escape sequences
            fixed_payload = request.edi_json_payload.replace('\\n', '\n').replace('\\t', '\t')
            parsed_json = json.loads(fixed_payload)
            clean_json_payload = json.dumps(parsed_json, separators=(',', ':'))
        except json.JSONDecodeError as second_error:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON payload: {str(second_error)}"
            )
    
    try:
        from app.utils.supabase_client import get_supabase_service
        import uuid
        
        # Get Supabase service
        supabase_service = await get_supabase_service()
        
        # Use the claim_id from the request directly (now supports text)
        claim_data = {
            "claim_id": request.claim_id,
            "edi_json_payload": clean_json_payload
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
            claim_id=request.claim_id,
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


@router.get("/getClaimIdsData", summary="Get Claim IDs Data Table", response_model=ClaimIdsDataResponse)
async def get_claim_ids_data(
    claimid: Optional[str] = Query(None, description="Specific claim ID to retrieve (optional)"),
    patientid: Optional[str] = Query(None, description="Specific patient ID to retrieve (optional)"),
    providerid: Optional[str] = Query(None, description="Specific provider ID to retrieve (optional)"),
    limit: int = Query(10, description="Number of records to retrieve (default: 10)"),
    offset: int = Query(0, description="Number of records to skip (default: 0)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve claim metadata from claim_ids_data_table.
    
    **Priority: High**
    
    **UI Request:**
    - claimid: Optional specific claim ID to retrieve
    - patientid: Optional specific patient ID to retrieve
    - providerid: Optional specific provider ID to retrieve
    - limit: Number of records to retrieve (default: 10)
    - offset: Number of records to skip (default: 0)
    
    **BE Response:**
    - List of claim metadata records with risk scores and amounts
    - Only returns the latest record for each claim ID (deduplicated)
    - Records are ordered by creation timestamp (newest first)
    """
    try:
        from app.utils.supabase_client import get_supabase_service

        supabase_service = await get_supabase_service()
        
        # Build filters
        filters = {}
        if claimid:
            filters["claimid"] = claimid
        if patientid:
            filters["patientid"] = patientid
        if providerid:
            filters["providerid"] = providerid

        # Retrieve data from Supabase - order by created_at DESC to get latest records first
        result = await supabase_service.select(
            table="claim_ids_data_table",
            columns="id, claimid, patientid, providerid, dateofservice, amount, denialrisk, claimriskscore, created_at",
            filters=filters,
            order_by="created_at",
            order_direction="desc"
        )
        
        # Group by claimid and keep only the latest record for each claimid
        latest_records = {}
        for record in result:
            claimid = record.get("claimid")
            if claimid not in latest_records:
                latest_records[claimid] = record
        
        # Convert to list and apply pagination
        unique_records = list(latest_records.values())
        total_count = len(unique_records)
        paginated_result = unique_records[offset:offset + limit]

        # Convert to Pydantic models
        claim_records = []
        for record in paginated_result:
            claim_records.append(ClaimIdsDataRecord(
                id=record.get("id"),
                claimid=record.get("claimid"),
                patientid=record.get("patientid"),
                providerid=record.get("providerid"),
                dateofservice=record.get("dateofservice"),
                amount=record.get("amount"),
                denialrisk=record.get("denialrisk"),
                claimriskscore=record.get("claimriskscore"),
                created_at=record.get("created_at")
            ))

        return ClaimIdsDataResponse(
            success=True,
            message=f"Retrieved {len(claim_records)} claim data records",
            data=claim_records,
            total_count=total_count,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve claim IDs data: {str(e)}"
        )


@router.post("/getAISuggested_ICDCodes", summary="Get AI Suggested ICD Codes", response_model=AISuggestedICDResponse)
async def get_ai_suggested_icd_codes(
    request: AISuggestedICDRequest,
    db: Session = Depends(get_db)
):
    """
    AI LLM Call to get AI Suggested ICD Codes based on clinical notes.
    
    **Priority: High**
    
    **UI Request:** 
    - clinical_note: Clinical note text string
    - patient_historical_ailments: Optional list of historical diagnoses
    
    **BE Response:** AI LLM ICD Codes with confidence scores and explanations
    """
    try:
        from app.utils.llm import LLMClient
        import json
        
        # Initialize LLM client
        llm_client = LLMClient()
        
        # Format patient historical ailments for the prompt
        historical_ailments_text = ""
        if request.patient_historical_ailments:
            historical_ailments_text = "\n".join([
                f"VisitDate: {ailment.get('VisitDate', 'N/A')}\n"
                f"Diagnosis Code: {ailment.get('Diagnosis Code', 'N/A')}\n"
                f"ShortDescription: {ailment.get('ShortDescription', 'N/A')}\n"
                for ailment in request.patient_historical_ailments
            ])
        
        # Construct the prompt
        prompt = f"""You are an expert medical coder trained in ICD-10-CM classification.   

Given a doctor's clinical note, identify the most relevant ICD-10 codes along with their clinical descriptions and confidence levels. 

Return your response **strictly in JSON format** that follows this structure: 

{{ 
  "ai_suggested_icd_codes": [ 
    {{ 
      "icd_code": "string",                  // ICD-10 code, e.g., "N18.6" 
      "icd_title": "string",                 // ICD-10 code title, e.g., "End-stage renal disease" 
      "confidence_score": "number",          // Confidence level as % (integer or float) 
      "explanation": "string",               // 1-2 line summary why this code is relevant to the note 
      "clinical_relevance": "string"         // Optional: short reasoning describing clinical link 
    }} 
  ] 
}} 

Rules: 
- Include only 1–5 of the most relevant ICD-10 codes. 
- Do not include unrelated or speculative codes. 
- Confidence scores must be above >90%. 
- Avoid adding notes or explanations outside of JSON. 
- The JSON must be valid and parsable. 

Input-doc-clinical-Notes: 
{{ 
  "clinical_note": "{request.clinical_note}" 
}} 

Input-Patient-Historical-Ailments: 
{historical_ailments_text if historical_ailments_text else "No historical ailments provided"}"""

        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": "You are an expert medical coder specializing in ICD-10-CM classification."},
            {"role": "user", "content": prompt}
        ]
        
        # Call LLM
        response = await llm_client.chat(
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )
        
        # Parse the JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_response = response[json_start:json_end]
                parsed_response = json.loads(json_response)
            else:
                parsed_response = json.loads(response)
            
            # Validate and format the response
            ai_suggested_codes = []
            for code_data in parsed_response.get("ai_suggested_icd_codes", []):
                ai_suggested_codes.append(ICDCodeSuggestion(
                    icd_code=code_data.get("icd_code", ""),
                    icd_title=code_data.get("icd_title", ""),
                    confidence_score=float(code_data.get("confidence_score", 0)),
                    explanation=code_data.get("explanation", ""),
                    clinical_relevance=code_data.get("clinical_relevance")
                ))
            
            return AISuggestedICDResponse(
                ai_suggested_icd_codes=ai_suggested_codes
            )
            
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse LLM response as JSON: {str(e)}. Response: {response}"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"AI ICD code suggestion failed: {str(e)}"
        )


@router.post("/getAISuggested_CPTCodes", summary="Get AI Suggested CPT Codes", response_model=AISuggestedCPTResponse)
async def get_ai_suggested_cpt_codes(
    request: AISuggestedCPTRequest,
    db: Session = Depends(get_db)
):
    """
    Suggest medically necessary CPT codes for the encounter using ProCoder rules.
    Returns JSON array only, constrained to CPT codes and confidence 90–100.
    """
    try:
        from app.utils.llm import LLMClient
        import json

        system_prompt = """You are ProCoder, a conservative, standards-compliant CPT coding assistant.

Objective
From the provided inputs, suggest the most accurate CPT® procedure/service codes that are medically necessary for the encounter. Output JSON only using the exact schema below. Include only items you can justify at ≥90% confidence.

Inputs (from caller)
clinical_notes: free-text clinician documentation for this encounter.
history: pertinent past history/ongoing problems, meds, devices, allergies.
selected_icds: zero or more ICD-10-CM codes the clinician marked as relevant.

Hard Rules
Code set: Use CPT (AMA) codes only. Do not output ICD, HCPCS Level II, SNOMED, or local codes.
Medical necessity link: Every suggested CPT must be clearly supported by the clinical notes and clinically consistent with at least one condition (from notes or selected_icds). If a procedure is not supported, do not return it.
Encounter scope only: Code only what was performed this encounter (or what is clearly ordered/performed). Do not anticipate future care.
Granularity & components: Choose the most specific CPT. Use combined/“bundled” codes when they inherently include components.
NCCI bundling logic: Avoid mutually exclusive or bundled pairings. Return a single most-appropriate code set.
E/M (2021+ rules): If an E/M visit is documented, select the level by MDM or total time, but exclude it if a global surgical package makes it non-billable unless documentation supports a separately identifiable service (modifier -25 eligible).
Modifiers (advice only): You may suggest common modifiers in the description text (e.g., -25, -26, -TC, laterality -RT/-LT, -59/-XS), but do not output modifier codes as separate CPT items.
Imaging/Procedures: Distinguish procedure vs. interpretation (e.g., ECG 93000 vs. 93010/93005; CT with/without contrast; ultrasound limited vs. complete; supervision & interpretation included/excluded).
Anesthesia: Return anesthesia CPT only if clearly documented.
Diagnostics ordered vs. performed: Return diagnostics only if performed and documented (or explicitly “performed and interpreted”). “Ordered only” → exclude.
Confidence threshold: Return only items with confidence between 90 and 100 (integer). If nothing reaches 90, return an empty array.

Deterministic output:
Sort by confidence (desc).
Limit to max_results.
JSON array only, no prose, no extra fields.
PHI: Do not echo any PHI from the notes in the output.

Output Schema (JSON array only)
Each element must match exactly:
{
  "code": "#####",
  "confidence": 95,
  "short_title": "concise CPT short title",
  "description": "1–2 line plain-English rationale tying the service to the documentation and related diagnosis."
}

Confidence rubric (do not output reasoning)
100: Procedure explicitly documented with all required qualifiers.
95: Explicitly documented; one minor qualifier implied by standard context.
90: Strong evidence; nearly complete qualifiers but minor ambiguity.
<90: Any significant ambiguity, missing performance evidence, or bundling conflict.

Guardrails
Prefer one primary code per procedure; add distinct secondary procedures only if separately performed and not bundled.
If selected_icds are provided and supported, favor CPTs that are medically necessary for those diagnoses.
If documentation is insufficient for specificity, withhold the code rather than guessing.

Return JSON only.
"""

        inference_prompt = f"""clinical_notes: {request.clinical_notes}
history: {request.history or ""}
selected_icds: {(request.selected_icds or [])}
max_results: {request.max_results}

Return:
JSON array of objects with fields: code, confidence (90–100), short_title, description. Nothing else.
"""

        llm = LLMClient()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": inference_prompt},
        ]

        raw = await llm.chat(messages=messages, temperature=0.1, max_tokens=1200)

        # Parse JSON array robustly
        try:
            start = raw.find('[')
            end = raw.rfind(']') + 1
            payload = raw[start:end] if start != -1 and end != -1 else raw
            data = json.loads(payload)
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []

        # Normalize and filter
        items: List[CPTSuggestion] = []
        for item in data:
            try:
                code = str(item.get("code", "")).strip()
                confidence = int(item.get("confidence", 0))
                short_title = str(item.get("short_title", "")).strip()
                description = str(item.get("description", "")).strip()
                if code and 90 <= confidence <= 100 and short_title and description:
                    items.append(CPTSuggestion(
                        code=code,
                        confidence=confidence,
                        short_title=short_title,
                        description=description
                    ))
            except Exception:
                continue

        # Sort and limit
        items.sort(key=lambda x: x.confidence, reverse=True)
        items = items[: request.max_results]

        return AISuggestedCPTResponse(results=items)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI CPT code suggestion failed: {str(e)}")


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


@router.post("/improveToSOAP", summary="Convert Clinical Notes to SOAP Format", response_model=SOAPFormatResponse)
async def improve_to_soap(
    request: SOAPFormatRequest,
    db: Session = Depends(get_db)
):
    """
    Convert clinical notes to SOAP format using AI LLM.
    
    **Priority: Medium**
    
    **UI Request:** 
    - clinical_note: Clinical note text string
    
    **BE Response:** SOAP formatted clinical notes with Subjective, Objective, Assessment, and Plan sections
    """
    try:
        # Use the separate LLM function for SOAP conversion
        soap_formatted_text = await convert_to_soap_format(request.clinical_note)
        
        return SOAPFormatResponse(
            SOAP_Formatted_Text=soap_formatted_text
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"SOAP format conversion failed: {str(e)}"
        )


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
            "GET /rcm-api/getClaimIdsData (High Priority - Claim Metadata)",
            "POST /rcm-api/getAISuggested_ICDCodes (High Priority)",
            "POST /rcm-api/getAISuggested_CPTCodes (High Priority)",
            "POST /rcm-api/getCPTCodes (High Priority)",
            "POST /rcm-api/uploadEDI_XML (Medium Priority)",
            "POST /rcm-api/improveToSOAP (Medium Priority)",
            "GET /rcm-api/getEDIclaims_data (Low Priority)",
            "POST /rcm-api/saveXML (Low Priority)"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
