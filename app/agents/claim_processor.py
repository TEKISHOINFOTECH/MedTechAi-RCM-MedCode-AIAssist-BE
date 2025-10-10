"""
Claim Processing Agent for automated insurance claim analysis and optimization.
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from .base_agent import BaseAgent
from app.schemas.medical_code import MedicalCodeValidationRequest
from app.models.medical_code import CodeType
from config import settings

logger = logging.getLogger(__name__)


class ClaimProcessingAgent(BaseAgent):
    """
    AI agent for processing insurance claims and optimizing for approval.
    
    Capabilities:
    - Analyze claim completeness and accuracy
    - Detect potential denial risks
    - Suggest improvements for claim approval
    - Validate billing codes against medical documentation
    - Optimize claim submission strategy
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        provider: str = "openai",
        risk_threshold: float = 0.75,
        **kwargs
    ):
        super().__init__(
            agent_name="claim_processor",
            model_name=model_name,
            provider=provider,
            risk_threshold=risk_threshold,
            **kwargs
        )
        
        self.risk_threshold = risk_threshold
        
        # Initialize AI client based on provider
        if provider.lower() == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif provider.lower() == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate claim processing input data."""
        required_fields = ["patient_info", "claims_data", "codes"]
        
        for field in required_fields:
            if field not in input_data:
                logger.warning(f"Missing required field in claim processing: {field}")
                return False
        
        # Validate that codes exist
        codes = input_data.get("codes", [])
        if not codes:
            logger.warning("No medical codes provided for claim processing")
            return False
        
        return True
    
    async def process(self, claim_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process insurance claim for optimization and risk assessment.
        
        Args:
            claim_data: Dictionary containing claim information
              - patient_info: Patient demographic and insurance info
              - claims_data: Claim details (amounts, dates, providers)
              - codes: List of medical codes (CPT, ICD-10, HCPCS)
              - documentation: Optional clinical notes or documentation
              - provider_info: Provider/service location information
            
        Returns:
            Dict containing:
            - risk_score: Overall denial risk (0.0-1.0)
            - risk_factors: List of identified risk factors
            - recommendations: List of improvement suggestions
            - code_validation: Individual code validation results
            - optimized_codes: Suggested code modifications
            - documentation_needs: Missing documentation requirements
        """
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(claim_data):
                raise ValueError("Invalid claim processing input data")
            
            logger.info(
                "Processing insurance claim",
                num_codes=len(claim_data.get("codes", [])),
                patient_id=claim_data.get("patient_info", {}).get("id"),
                agent=self.agent_name
            )
            
            # Create claim analysis prompt
            prompt = self._create_claim_analysis_prompt(claim_data)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt)
            
            # Parse AI response
            processing_result = self._parse_processing_response(ai_response, claim_data)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            tokens_used = self._estimate_tokens(prompt, ai_response)
            self._update_metrics(processing_time, tokens_used, True)
            
            logger.info(
                "Claim processing completed",
                risk_score=processing_result.get("risk_score", 0.0),
                num_recommendations=len(processing_result.get("recommendations", [])),
                processing_time_ms=processing_time
            )
            
            return processing_result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(processing_time, 0, False)
            
            logger.error(
                "Claim processing failed",
                error=str(e),
                patient_id=claim_data.get("patient_info", {}).get("id"),
                agent=self.agent_name
            )
            
            # Return error response
            return {
                "risk_score": 1.0,  # Maximum risk due to processing failure
                "risk_factors": [f"Processing error: {str(e)}"],
                "recommendations": ["Manual review required due to processing error"],
                "code_validation": [],
                "optimized_codes": [],
                "documentation_needs": [],
                "error": str(e),
                "processing_time_ms": processing_time
            }
    
    def _create_claim_analysis_prompt(self, claim_data: Dict[str, Any]) -> str:
        """Create comprehensive claim analysis prompt for AI agent."""
        
        codes_text = ""
        for code in claim_data.get("codes", []):
            codes_text += f"\n- {code.get('type', 'UNKNOWN')}: {code.get('code', '')} - {code.get('description', 'No description')}"
        
        prompt = f"""
You are an expert healthcare revenue cycle management (RCM) specialist with deep expertise in insurance claim processing and denial prevention.

Task: Analyze the following insurance claim and provide comprehensive risk assessment and optimization recommendations.

CLAIM DETAILS:
Patient Information: {json.dumps(claim_data.get('patient_info', {}), indent=2)}
Provider Information: {json.dumps(claim_data.get('provider_info', {}), indent=2)}
Claim Data: {json.dumps(claim_data.get('claims_data', {}), indent=2)}

MEDICAL CODES:{codes_text}

ADDITIONAL DATA:
Documentation: {claim_data.get('documentation', 'Not provided')}

Please provide a comprehensive analysis including:

1. RISK ASSESSMENT:
   - Overall denial risk score (0.0-1.0)
   - Key risk factors identified
   - Risk categorization (low/medium/high/critical)

2. CODE VALIDATION:
   - Individual code validation with specific issues
   - Code appropriateness for diagnosis/procedure
   - Missing required codes or modifiers

3. COMPLIANCE CHECK:
   - Documentation requirements
   - Authorization requirements
   - Billing compliance issues
   - Regulatory considerations

4. OPTIMIZATION RECOMMENDATIONS:
   - Specific actions to reduce denial risk
   - Code improvements/modifications
   - Documentation enhancements needed
   - Process improvements

5. DENIAL PREVENTION:
   - Targeted interventions for identified risks
   - Preventive measures for similar future claims
   - Best practices recommendations

Respond in JSON format:
{{
    "risk_assessment": {{
        "overall_risk_score": 0.0-1.0,
        "risk_level": "low|medium|high|critical",
        "risk_factors": ["factor1", "factor2"],
        "confidence": 0.0-1.0
    }},
    "code_validation": [
        {{
            "code": "code_value",
            "code_type": "CPT|ICD10|HCPCS",
            "is_valid": true/false,
            "issues": ["issue1", "issue2"],
            "suggestions": ["suggestion1", "suggestion2"]
        }}
    ],
    "recommendations": [
        {{
            "priority": "high|medium|low",
            "category": "coding|documentation|authorization|billing",
            "title": "Recommendation title",
            "description": "Detailed recommendation",
            "impact_score": 0.0-1.0
        }}
    ],
    "documentation_needs": [
        {{
            "requirement": "document type",
            "status": "missing|incomplete|adequate",
            "priority": "high|medium|low",
            "description": "what is needed"
        }}
    ],
    "optimized_codes": [
        {{
            "original_code": "original",
            "recommended_code": "recommended",
            "reason": "justification",
            "impact": "risk reduction estimate"
        }}
    ]
}}
"""
        return prompt
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI provider."""
        try:
            if self.provider.lower() == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif self.provider.lower() == "anthropic":
                response = await self.client.messages.create(
                    model=self.model_name,
                    max_tokens=2000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error("AI API call failed", provider=self.provider, error=str(e))
            raise
    
    def _parse_processing_response(self, ai_response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured processing result."""
        try:
            # Clean and parse JSON response
            response_text = ai_response.strip()
            
            # Extract JSON from response if wrapped in markdown
            if "```json" in response_text:
                json_start = response_text.find("```json") + 8
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            
            parsed_response = json.loads(response_text.strip())
            
            # Transform to expected format
            risk_assessment = parsed_response.get("risk_assessment", {})
            
            return {
                "risk_score": float(risk_assessment.get("overall_risk_score", 1.0)),
                "risk_factors": risk_assessment.get("risk_factors", []),
                "risk_level": risk_assessment.get("risk_level", "high"),
                "recommendations": self._format_recommendations(parsed_response.get("recommendations", [])),
                "code_validation": parsed_response.get("code_validation", []),
                "optimized_codes": parsed_response.get("optimized_codes", []),
                "documentation_needs": parsed_response.get("documentation_needs", []),
                "confidence": float(risk_assessment.get("confidence", 0.0))
            }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to parse AI response", error=str(e), response=ai_response)
            
            # Fallback: provide basic risk assessment
            return {
                "risk_score": 0.8,  # High risk due to parsing failure
                "risk_factors": ["Unable to parse AI analysis results"],
                "risk_level": "high",
                "recommendations": ["Manual review recommended due to analysis parsing failure"],
                "code_validation": [],
                "optimized_codes": [],
                "documentation_needs": [],
                "confidence": 0.0
            }
    
    def _format_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format recommendations for consistent output."""
        formatted = []
        for rec in recommendations:
            formatted.append({
                "type": rec.get("category", "general"),
                "priority": rec.get("priority", "medium"),
                "title": rec.get("title", "Recommendation"),
                "description": rec.get("description", ""),
                "impact_score": float(rec.get("impact_score", 0.5))
            })
        return formatted
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token usage for billing and monitoring."""
        total_chars = len(prompt) + len(response or "")
        return total_chars // 4
