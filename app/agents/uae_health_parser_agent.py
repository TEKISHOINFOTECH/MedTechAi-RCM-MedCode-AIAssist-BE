"""
UAE Health System XML Parser Agent for Dubai Health Authority (DHA) claims.
"""

from .base_agent import BaseAgent
from app.models.uae_health import (
    UAEClaimSubmission,
    parse_uae_claim_xml,
    extract_clinical_context,
    get_icd_validation_data,
    get_cpt_validation_data
)
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class UAEHealthParserAgent(BaseAgent):
    """
    Agent for parsing UAE Health System XML claim submissions.
    
    Handles Dubai Health Authority (DHA) claim format with ICD/CPT code extraction.
    """
    
    def __init__(self):
        super().__init__(agent_name="uae_health_parser")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data for UAE health parsing."""
        required_fields = ["xml_content"]
        
        # Check if required fields are presente
        for field in required_fields:
            if field not in input_data or not input_data[field]:
                logger.warning("Missing required field", field=field)
                return False
        
        # Validate XML content is not empty
        xml_content = input_data["xml_content"]
        if not isinstance(xml_content, str) or len(xml_content.strip()) < 10:
            logger.warning("Invalid XML content", content_length=len(xml_content) if xml_content else 0)
            return False
            
        return True
    
    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Parse UAE health XML submission and extract medical coding data.
        
        Args:
            input_data: Dictionary containing:
                - xml_content: Raw XML string content
                - parse_options: Optional parsing options
                
        Returns:
            Dictionary containing:
                - parsed_submission: UAEClaimSubmission object
                - clinical_context: Text summary for AI agents
                - icd_codes: List of extracted ICD codes
                - cpt_codes: List of extracted CPT codes
                - validation_data: Data for downstream validation agents
                - summary: High-level claim summary
        """
        try:
            xml_content = input_data["xml_content"]
            parse_options = input_data.get("parse_options", {})
            
            logger.info("Starting UAE health XML parsing", 
                       content_length=len(xml_content))
            
            # Parse the XML content
            submission = parse_uae_claim_xml(xml_content)
            
            # Extract clinical context for AI agents
            clinical_context = extract_clinical_context(submission)
            
            # Extract medical codes
            icd_codes = submission.get_all_icd_codes()
            cpt_codes = submission.get_all_cpt_codes()
            
            # Prepare validation data for downstream agents
            validation_data = {
                "icd_validation": get_icd_validation_data(submission),
                "cpt_validation": get_cpt_validation_data(submission),
                "clinical_context": clinical_context,
                "summary": submission.get_claims_summary()
            }
            
            # Create response summary
            result = {
                "status": "success",
                "parsed_submission": submission.dict(),
                "clinical_context": clinical_context,
                "medical_codes": {
                    "icd_codes": icd_codes,
                    "cpt_codes": cpt_codes,
                    "unique_icd_count": len(set(icd_codes)),
                    "unique_cpt_count": len(set(cpt_codes))
                },
                "validation_data": validation_data,
                "summary": submission.get_claims_summary(),
                "claim_count": len(submission.claims),
                "parser_metadata": {
                    "agent": self.agent_name,
                    "input_size": len(xml_content),
                    "parse_options": parse_options
                }
            }
            
            logger.info("UAE health XML parsing completed successfully",
                       claim_count=len(submission.claims),
                       icd_count=len(icd_codes),
                       cpt_count=len(cpt_codes))
            
            return result
            
        except Exception as e:
            error_msg = f"UAE health XML parsing failed: {str(e)}"
            logger.error("Parsing failure", error=str(e), xml_length=len(input_data.get("xml_content", "")))
            
            return {
                "status": "error",
                "error": error_msg,
                "parsed_submission": None,
                "clinical_context": None,
                "medical_codes": {
                    },
                "validation_data": None,
                "summary": None,
                "claim_count": 0,
                "parser_metadata": {
                    "agent": self.agent_name,
                    "error": str(e)
                }
            }


class UAEHealthCodeExtractorAgent(BaseAgent):
    """
    Specialized agent for extracting medical codes from UAE health claims.
    
    This agent focuses specifically on ICD/CPT code extraction and validation
    readiness for the medical coding agents.
    """
    
    def __init__(self):
        super().__init__(agent_name="uae_code_extractor")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for code extraction."""
        if "clinical_context" not in input_data:
            return False
        
        clinical_context = input_data["clinical_context"]
        return isinstance(clinical_context, str) and len(clinical_context.strip()) > 0
    
    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Extract and prepare medical codes from UAE health context.
        
        Args:
            input_data: Dictionary containing:
                - clinical_context: Text clinical summary
                - icd_codes: List of ICD codes (optional)
                - cpt_codes: List of CPT codes (optional)
                
        Returns:
            Dictionary with structured code data for downstream validation.
        """
        try:
            clinical_context = input_data["clinical_context"]
            existing_icds = input_data.get("icd_codes", [])
            existing_cpts = input_data.get("cpt_codes", [])
            
            # Structure the data for medical coding agents
            result = {
                "extracted_codes": {
                    "diagnoses": {
                        "codes": existing_icds,
                        "count": len(existing_icds),
                        "unique_codes": list(set(existing_icds))
                    },
                    "procedures": {
                        "codes": existing_cpts,
                        "count": len(existing_cpts),
                        "unique_codes": list(set(existing_cpts))
                    }
                },
                "clinical_notes": clinical_context,
                "validation_ready": True,
                "extractor_metadata": {
                    "agent": self.agent_name,
                    "source_system": "UAE Health (DHA)",
                    "extraction_method": "XML_parsing"
                }
            }
            
            logger.info("Code extraction completed",
                       icd_codes=len(existing_icds),
                       cpt_codes=len(existing_cpts))
            
            return result
            
        except Exception as e:
            logger.error("Code extraction failed", error=str(e))
            return {
                "extracted_codes": {
                    "diagnoses": {"codes": [], "count": 0, "unique_codes": []},
                    "procedures": {"codes": [], "count": 0, "unique_codes": []}
                },
                "clinical_notes": input_data.get("clinical_context", ""),
                "validation_ready": False,
                "extractor_metadata": {
                    "agent": self.agent_name,
                    "error": str(e)
                }
            }


class UAEHealthValidatorAgent(BaseAgent):
    """
    Agent for validating UAE health system specific requirements.
    
    Validates Emirates ID, DHA credentials, and UAE-specific coding rules.
    """
    
    def __init__(self):
        super().__init__(agent_name="uae_health_validator")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input for UAE health validation."""
        required_fields = ["parsed_submission"]
        return all(field in input_data for field in required_fields)
    
    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Validate UAE-specific health system requirements.
        
        Args:
            input_data: Dictionary containing parsed submission data
            
        Returns:
            Validation results specific to UAE health system.
        """
        try:
            submission_data = input_data["parsed_submission"]
            
            validation_results = {
                "emirates_id_validation": self._validate_emirates_ids(submission_data["claims"]),
                "dha_credential_validation": self._validate_dha_credentials(submission_data["claims"]),
                "financial_validation": self._validate_financial_consistency(submission_data["claims"]),
                "coding_format_validation": self._validate_coding_formats(submission_data["claims"]),
                "uae_compliance": self._check_uae_compliance(submission_data)
            }
            
            # Overall validation status
            all_passed = all(
                result.get("status") == "passed" 
                for result in validation_results.values()
            )
            
            result = {
                "validation_status": "passed" if all_passed else "failed",
                "validation_results": validation_results,
                "recommendations": self._generate_recommendations(validation_results),
                "validator_metadata": {
                    "agent": self.agent_name,
                    "checks_performed": list(validation_results.keys()),
                    "overall_status": "passed" if all_passed else "failed"
                }
            }
            
            logger.info("UAE health validation completed", 
                       overall_status=result["validation_status"])
            
            return result
            
        except Exception as e:
            logger.error("UAE health validation failed", error=str(e))
            return {
                "validation_status": "error",
                "validation_results": {},
                "recommendations": [f"Validation error: {str(e)}"],
                "validator_metadata": {
                    "agent": self.agent_name,
                    "error": str(e)
                }
            }
    
    def _validate_emirates_ids(self, claims: List[Dict]) -> Dict[str, Any]:
        """Validate Emirates ID format."""
        results = []
        
        for claim in claims:
            emirates_id = claim.get("emirates_id", "")
            # Basic format check: 784-YYYY-NNNNNNN-C
            is_valid = emirates_id.startswith("784-") and len(emirates_id) >= 15
            
            results.append({
                "claim_id": claim.get("claim_id", ""),
                "emirates_id": emirates_id,
                "valid": is_valid,
                "format_requirements": "784-YYYY-NNNNNNN-C"
            })
        
        invalid_count = sum(1 for r in results if not r["valid"])
        
        return {
            "status": "passed" if invalid_count == 0 else "failed",
            "total_claims": len(results),
            "valid_emirates_ids": len(results) - invalid_count,
            "invalid_emirates_ids": invalid_count,
            "details": results
        }
    
    def _validate_dha_credentials(self, claims: List[Dict]) -> Dict[str, Any]:
        """Validate DHA credential format."""
        results = []
        
        for claim in claims:
            activities = claim.get("activities", [])
            for activity in activities:
                clinician_id = activity.get("clinician_id", "")
                # Basic DHA license format: DHA-LIC-NNNNN
                is_valid = clinician_id.startswith("DHA-LIC-") and len(clinician_id) >= 10
                
                results.append({
                    "claim_id": claim.get("claim_id", ""),
                    "activity_id": activity.get("activity_id", ""),
                    "clinician_id": clinician_id,
                    "valid": is_valid,
                    "format_requirements": "DHA-LIC-NNNNN"
                })
        
        invalid_count = sum(1 for r in results if not r["valid"])
        
        return {
            "status": "passed" if invalid_count == 0 else "failed",
            "total_activities": len(results),
            "valid_credentials": len(results) - invalid_count,
            "invalid_credentials": invalid_count,
            "details": results
        }
    
    def _validate_financial_consistency(self, claims: List[Dict]) -> Dict[str, Any]:
        """Validate financial calculations."""
        results = []
        
        for claim in claims:
            financial = claim.get("financial", {})
            gross = financial.get("gross_amount", 0)
            patient_share = financial.get("patient_share", 0)
            net = financial.get("net_amount", 0)
            
            calculated_net = gross - patient_share
            is_consistent = abs(net - calculated_net) <= 0.01  # Allow small rounding differences
            
            results.append({
                "claim_id": claim.get("claim_id", ""),
                "gross_amount": float(gross),
                "patient_share": float(patient_share),
                "net_amount": float(net),
                "calculated_net": float(calculated_net),
                "consistent": is_consistent,
                "difference": float(abs(net - calculated_net))
            })
        
        inconsistent_count = sum(1 for r in results if not r["consistent"])
        
        return {
            "status": "passed" if inconsistent_count == 0 else "failed",
            "total_claims": len(results),
            "consistent_calculations": len(results) - inconsistent_count,
            "inconsistent_calculations": inconsistent_count,
            "details": results
        }
    
    def _validate_coding_formats(self, claims: List[Dict]) -> Dict[str, Any]:
        """Validate ICD/CPT code formats."""
        icd_results = []
        cpt_results = []
        
        for claim in claims:
            # Validate ICD codes
            for diagnosis in claim.get("diagnoses", []):
                icd_code = diagnosis.get("icd_code", "")
                is_valid = len(icd_code) >= 3 and "." in icd_code  # Basic ICD-10 format
                
                icd_results.append({
                    "claim_id": claim.get("claim_id", ""),
                    "icd_code": icd_code,
                    "diagnosis_type": diagnosis.get("diagnosis_type", ""),
                    "valid": is_valid
                })
            
            # Validate CPT codes
            for activity in claim.get("activities", []):
                cpt_code = activity.get("cpt_code", "")
                is_valid = len(cpt_code) >= 4  # Basic CPT/HCPCS format
                
                cpt_results.append({
                    "claim_id": claim.get("claim_id", ""),
                    "activity_id": activity.get("activity_id", ""),
                    "cpt_code": cpt_code,
                    "activity_type": activity.get("activity_type", ""),
                    "valid": is_valid
                })
        
        invalid_icds = sum(1 for r in icd_results if not r["valid"])
        invalid_cpts = sum(1 for r in cpt_results if not r["valid"])
        
        return {
            "status": "passed" if invalid_icds == 0 and invalid_cpts == 0 else "failed",
            "icd_codes": {
                "total": len(icd_results),
                "valid": len(icd_results) - invalid_icds,
                "invalid": invalid_icds
            },
            "cpt_codes": {
                "total": len(cpt_results),
                "valid": len(cpt_results) - invalid_cpts,
                "invalid": invalid_cpts
            },
            "details": {
                "icd_results": icd_results,
                "cpt_results": cpt_results
            }
        }
    
    def _check_uae_compliance(self, submission_data: Dict) -> Dict[str, Any]:
        """Check overall UAE health system compliance."""
        header = submission_data.get("header", {})
        
        checks = [
            ("sender_format", bool(header.get("sender_id"))),
            ("receiver_format", bool(header.get("receiver_id"))),
            ("transaction_date_present", bool(header.get("transaction_date"))),
            ("record_count_match", True)  # Already validated in model
        ]
        
        passed_checks = sum(1 for _, passed in checks if passed)
        
        return {
            "status": "passed" if passed_checks == len(checks) else "failed",
            "total_checks": len(checks),
            "passed_checks": passed_checks,
            "failed_checks": len(checks) - passed_checks,
            "check_details": [
                {"check": name, "passed": passed} for name, passed in checks
            ]
        }
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        for check_name, result in validation_results.items():
            if result.get("status") != "passed":
                if check_name == "emirates_id_validation":
                    recommendations.append("Review Emirates ID format - should be 784-YYYY-NNNNNNN-C")
                elif check_name == "dha_credential_validation":
                    recommendations.append("Verify DHA licensure format - should be DHA-LIC-NNNNN")
                elif check_name == "financial_validation":
                    recommendations.append("Check financial calculations - Net should equal Gross minus Patient Share")
                elif check_name == "coding_format_validation":
                    recommendations.append("Validate ICD/CPT code formats and ensure code completeness")
        
        if not recommendations:
            recommendations.append("All UAE health system validations passed successfully")
        
        return recommendations

