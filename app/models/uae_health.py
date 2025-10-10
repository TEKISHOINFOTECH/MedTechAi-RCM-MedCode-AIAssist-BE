"""
UAE Health System Data Models for Dubai Health Authority (DHA) claims.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from decimal import Decimal
import xml.etree.ElementTree as ET


class ClaimHeader(BaseModel):
    """Header information for claim submission."""
    sender_id: str = Field(..., alias="SenderID")
    receiver_id: str = Field(..., alias="ReceiverID")
    transaction_date: datetime = Field(..., alias="TransactionDate")
    record_count: int = Field(..., alias="RecordCount")
    disposition_flag: Literal["Original", "Correction", "Cancellation"] = Field(..., alias="DispositionFlag")


class EncounterRecord(BaseModel):
    """Healthcare encounter details."""
    facility_id: str = Field(..., alias="FacilityID")
    encounter_type: Literal["OP", "ER", "IP"] = Field(..., alias="Type")
    patient_id: str = Field(..., alias="PatientID")
    start_datetime: datetime = Field(..., alias="Start")
    end_datetime: Optional[datetime] = Field(None, alias="End")
    start_type: Optional[str] = Field(None, alias="StartType")
    end_type: Optional[str] = Field(None, alias="EndType")
    transfer_source: Optional[str] = Field(None, alias="TransferSource")
    transfer_destination: Optional[str] = Field(None, alias="TransferDestination")


class DiagnosisRecord(BaseModel):
    """Diagnosis information (ICD codes)."""
    diagnosis_type: Literal["Primary", "Secondary"] = Field(..., alias="Type")
    icd_code: str = Field(..., alias="Code")
    
    @validator('icd_code')
    def validate_icd_format(cls, v):
        """Validate ICD-10 code format."""
        if not isinstance(v, str):
            raise ValueError("ICD code must be a string")
        if len(v) < 3:
            raise ValueError("ICD code too short")
        return v.upper()


class ObservationRecord(BaseModel):
    """Clinical observation data."""
    observation_type: str = Field(..., alias="Type")
    observation_code: str = Field(..., alias="Code")
    value: Optional[str] = Field(None, alias="Value")
    value_type: Optional[str] = Field(None, alias="ValueType")


class ActivityRecord(BaseModel):
    """Medical activity/procedure record (CPT codes)."""
    activity_id: str = Field(..., alias="ID")
    start_datetime: datetime = Field(..., alias="Start")
    activity_type: Literal["Consultation", "Laboratory", "Procedure", "Radiology", "Medication", "Pharmacy"] = Field(..., alias="Type")
    cpt_code: str = Field(..., alias="Code")
    quantity: int = Field(..., alias="Quantity")
    net_amount: Decimal = Field(..., alias="Net")
    clinician_id: str = Field(..., alias="Clinician")
    prior_auth_id: Optional[str] = Field(None, alias="PriorAuthorizationID")
    observations: List[ObservationRecord] = Field(default_factory=list, alias="Observation")


class FinancialRecord(BaseModel):
    """Financial information for the claim."""
    gross_amount: Decimal = Field(..., alias="Gross")
    patient_share: Decimal = Field(..., alias="PatientShare")
    net_amount: Decimal = Field(..., alias="Net")
    
    @validator('net_amount')
    def validate_financial_consistency(cls, v, values):
        """Validate that Net = Gross - PatientShare."""
        if 'gross_amount' in values and 'patient_share' in values:
            expected_net = values['gross_amount'] - values['patient_share']
            if abs(v - expected_net) > Decimal('0.01'):  # Allow small rounding differences
                raise ValueError(f"Net amount {v} doesn't match Gross - PatientShare calculation")
        return v


class ResubmissionRecord(BaseModel):
    """Resubmission information if applicable."""
    resubmission_type: str = Field(..., alias="Type")
    comment: str = Field(..., alias="Comment")
    attachment: Optional[str] = Field(None, alias="Attachment")


class ContractRecord(BaseModel):
    """Contract/package information."""
    package_name: Optional[str] = Field(None, alias="PackageName")


class UAEClaim(BaseModel):
    """Individual UAE health claim."""
    claim_id: str = Field(..., alias="ID")
    payer_claim_id: Optional[str] = Field(None,alias="IDPayer")
    member_id: Optional[str] = Field(None, alias="MemberID")
    payer_id: str = Field(..., alias="PayerID")
    provider_id: str = Field(..., alias="ProviderID")
    emirates_id: str = Field(..., alias="EmiratesIDNumber")
    
    # Financial data
    financial: FinancialRecord
    
    # Encounter information
    encounter: EncounterRecord
    
    # Medical coding data
    diagnoses: List[DiagnosisRecord] = Field(default_factory=list, alias="Diagnosis")
    activities: List[ActivityRecord] = Field(default_factory=list, alias="Activity")
    
    # Optional sections
    resubmission: Optional[ResubmissionRecord] = Field(None, alias="Resubmission")
    contract: Optional[ContractRecord] = Field(None, alias="Contract")
    
    @validator('emirates_id')
    def validate_emirates_id(cls, v):
        """Validate Emirates ID format."""
        if not isinstance(v, str):
            raise ValueError("Emirates ID must be a string")
        # UAE Emirates ID format: 784-YYYY-NNNNNNN-C
        if not v.startswith('784-') or len(v) < 12:
            raise ValueError("Invalid Emirates ID format")
        return v
    
    def get_icd_codes(self) -> List[str]:
        """Extract all ICD codes from diagnoses."""
        return [diagnosis.icd_code for diagnosis in self.diagnoses]
    
    def get_cpt_codes(self) -> List[str]:
        """Extract all CPT codes from activities."""
        return [activity.cpt_code for activity in self.activities]
    
    def get_primary_diagnosis(self) -> Optional[str]:
        """Get primary diagnosis ICD code."""
        for diagnosis in self.diagnoses:
            if diagnosis.diagnosis_type == "Primary":
                return diagnosis.icd_code
        return None
    
    def get_total_actvity_value(self) -> Decimal:
        """Calculate total activity net amounts."""
        return sum(activity.net_amount for activity in self.activities)


class UAEClaimSubmission(BaseModel):
    """Complete UAE health claim submission."""
    header: ClaimHeader = Field(..., alias="Header")
    claims: List[UAEClaim] = Field(..., alias="Claim")
    
    @validator('claims')
    def validate_record_count(cls, v, values):
        """Validate that actual claim count matches header record count."""
        if 'header' in values:
            expected_count = values['header'].record_count
            actual_count = len(v)
            if actual_count != expected_count:
                raise ValueError(f"Expected {expected_count} claims but found {actual_count}")
        return v
    
    def get_all_icd_codes(self) -> List[str]:
        """Extract all ICD codes from all claims."""
        all_icds = []
        for claim in self.claims:
            all_icds.extend(claim.get_icd_codes())
        return all_icds
    
    def get_all_cpt_codes(self) -> List[str]:
        """Extract all CPT codes from all claims."""
        all_cpts = []
        for claim in self.claims:
            all_cpts.extend(claim.get_cpt_codes())
        return all_cpts
    
    def get_claims_summary(self) -> dict:
        """Get summary statistics for all claims."""
        total_claims = len(self.claims)
        total_gross = sum(claim.financial.gross_amount for claim in self.claims)
        total_net = sum(claim.financial.net_amount for claim in self.claims)
        total_patient_share = sum(claim.financial.patient_share for claim in self.claims)
        
        unique_icds = set(self.get_all_icd_codes())
        unique_cpts = set(self.get_all_cpt_codes())
        
        return {
            "source": self.header.sender_id,
            "receiver": self.header.receiver_id,
            "transaction_date": self.header.transaction_date,
            "total_claims": total_claims,
            "total_gross_amount": float(total_gross),
            "total_net_amount": float(total_net),
            "total_patient_share": float(total_patient_share),
            "unique_icd_codes": len(unique_icds),
            "unique_cpt_codes": len(unique_cpts),
            "icd_codes": list(unique_icds),
            "cpt_codes": list(unique_cpts)
        }


def parse_uae_claim_xml(xml_content: str) -> UAEClaimSubmission:
    """
    Parse UAE health claim XML into structured data models.
    
    Args:
        xml_content: Raw XML string content
        
    Returns:
        UAEClaimSubmission: Parsed and validated claim data
        
    Raises:
        ValueError: If XML parsing or validation fails
        ET.ParseError: If XML is malformed
    """
    try:
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Convert to dictionary for Pydantic parsing
        xml_dict = _xml_to_dict(root)
        
        # Create UAEClaimSubmission from parsed data
        submission = UAEClaimSubmission(**xml_dict)
        
        return submission
        
    except ET.ParseError as e:
        raise ValueError(f"Invalid XML format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing UAE claim XML: {e}")


def _xml_to_dict(element: ET.Element) -> dict:
    """
    Convert XML element to dictionary recursively.
    Handles UAE health claim XML structure.
    """
    result = {}
    
    # Handle text content
    if element.text and element.text.strip():
        return element.text.strip()
    
    # Handle child elements
    for child in element:
        child_key = child.tag.split('}')[-1] if '}' in child.tag else child.tag  # Remove namespace
        child_value = _xml_to_dict(child)
        
        # Handle multiple elements with same tag (like Diagnosis, Activity)
        if child_key in result:
            if not isinstance(result[child_key], list):
                result[child_key] = [result[child_key]]
            result[child_key].append(child_value)
        else:
            result[child_key] = child_value
    
    return result


def extract_clinical_context(submission: UAEClaimSubmission) -> str:
    """
    Extract clinical context as text for AI agents.
    
    Args:
        submission: Parsed UAE claim submission
        
    Returns:
        str: Clinical context summary
    """
    context_parts = []
    
    for claim in submission.claims:
        # Basic claim info
        context_parts.append(f"Claim ID: {claim.claim_id}")
        context_parts.append(f"Emirates ID: {claim.emirates_id}")
        context_parts.append(f"Encounter Type: {claim.encounter.encounter_type}")
        context_parts.append(f"Facility: {claim.encounter.facility_id}")
        
        # Diagnoses
        context_parts.append("Diagnoses:")
        for diagnosis in claim.diagnoses:
            context_parts.append(f"  - {diagnosis.diagnosis_type}: {diagnosis.icd_code}")
        
        # Activities
        context_parts.append("Activities:")
        for activity in claim.activities:
            context_parts.append(f"  - {activity.activity_type}: {activity.cpt_code} (Qty: {activity.quantity}, Amount: AED {activity.net_amount})")
            
            # Add observations if present<｜tool▁sep｜>icd
            if activity.observations:
                context_parts.append("    Clinical Observations:")
                for obs in activity.observations:
                    context_parts.append(f"      - {obs.observation_type}: {obs.observation_code} = {obs.value} {obs.value_type or ''}")
        
        # Financial summary
        context_parts.append(f"Financial: Gross AED {claim.financial.gross_amount}, Patient Share AED {claim.financial.patient_share}, Net AED {claim.financial.net_amount}")
        context_parts.append("")
    
    return "\n".join(context_parts)


# Convenience functions for common operations

def get_icd_validation_data(submission: UAEClaimSubmission) -> dict:
    """Extract ICD codes and context for validation."""
    return {
        "icd_codes": submission.get_all_icd_codes(),
        "clinical_context": extract_clinical_context(submission),
        "dental_count": len(submission.claims),
        "encounter_types": [claim.encounter.encounter_type for claim in submission.claims]
    }


def get_cpt_validation_data(submission: UAEClaimSubmission) -> dict:
    """Extract CPT codes and context for validation."""
    return {
        "cpt_codes": submission.get_all_cpt_codes(),
        "icd_codes": submission.get_all_icd_codes(),
        "clinical_context": extract_clinical_context(submission),
        "claim_count": len(submission.claims)
    }

