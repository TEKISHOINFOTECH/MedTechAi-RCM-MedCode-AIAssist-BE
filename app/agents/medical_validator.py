"""
Medical Code Validation Agent using AI for comprehensive code validation.
"""
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import structlog

from .base_agent import BaseAgent
from app.schemas.medical_code import MedicalCodeValidationRequest, MedicalCodeValidationResponse
from app.models.medical_code import CodeType
from config import settings


logger = structlog.get_logger()


class MedicalCodeValidationAgent(BaseAgent):
    """
    AI agent for validating medical codes using large language models.
    
    Capabilities:
    - Validate CPT, ICD-10, HCPCS codes
    - Provide confidence scores
    - Suggest corrections and alternatives
    - Context-aware validation
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        provider: str = "openai",
        confidence_threshold: float = 0.85,
        **kwargs
    ):
        super().__init__(
            agent_name="medical_code_validator",
            model_name=model_name,
            provider=provider,
            confidence_threshold=confidence_threshold,
            **kwargs
        )
        
        self.confidence_threshold = confidence_threshold
        
        # Initialize AI client based on provider
        if provider.lower() == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif provider.lower() == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def validate_input(self, input_data: MedicalCodeValidationRequest) -> bool:
        """Validate input medical code request."""
        if not input_data.code:
            logger.warning("Empty medical code provided")
            return False
        
        if not input_data.code_type:
            logger.warning("No code type specified")
            return False
        
        # Basic format validation based on code type
        if input_data.code_type == CodeType.CPT and len(input_data.code) != 5:
            logger.warning(f"CPT code should be 5 characters; got {len(input_data.code)}")
            # Non-critical warning, continue validation
        
        return True
    
    async def process(self, request: MedicalCodeValidationRequest, **kwargs) -> MedicalCodeValidationResponse:
        """
        Process medical code validation request.
        
        Args:
            request: Medical code validation request
            **kwargs: Additional processing parameters
            
        Returns:
            MedicalCodeValidationResponse with validation results
        """
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(request):
                raise ValueError("Invalid input data")
            
            logger.info(
                "Processing medical code validation",
                code=request.code,
                code_type=request.code_type,
                agent=self.agent_name
            )
            
            # Create validation prompt
            prompt = self._create_validation_prompt(request)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt)
            
            # Parse AI response
            validation_result = self._parse_validation_response(ai_response, request)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            tokens_used = self._estimate_tokens(prompt, ai_response)
            self._update_metrics(processing_time, tokens_used, True)
            
            logger.info(
                "Medical code validation completed",
                code=request.code,
                is_valid=validation_result.is_valid,
                confidence=validation_result.confidence_score,
                processing_time_ms=processing_time
            )
            
            return validation_result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(processing_time, 0, False)
            
            logger.error(
                "Medical code validation failed",
                code=request.code,
                error=str(e),
                agent=self.agent_name
            )
            
            # Return error response
            return MedicalCodeValidationResponse(
                code=request.code,
                code_type=request.code_type,
                is_valid=False,
                confidence_score=0.0,
                validation_message=f"Validation failed: {str(e)}",
                processing_time_ms=processing_time
            )
    
    def _create_validation_prompt(self, request: MedicalCodeValidationRequest) -> str:
        """Create validation prompt for AI agent."""
        context_info = ""
        if request.context:
            context_info += f"\nAdditional Context: {request.context}"
        if request.patient_info:
            context_info += f"\nPatient Information: {json.dumps(request.patient_info, indent=2)}"
        if request.provider_info:
            context_info += f"\nProvider Information: {json.dumps(request.provider_info, indent=2)}"
        if request.insurance_info:
            context_info += f"\nInsurance Information: {json.dumps(request.insurance_info, indent=2)}"
        
        prompt = f"""
You are an expert medical coding validator specialized in healthcare revenue cycle management (RCM).

Task: Validate the following medical code and provide detailed analysis.

Medical Code: {request.code}
Code Type: {request.code_type}{context_info}

Please analyze this code and provide:
1. Validity assessment (valid/invalid)
2. Confidence score (0.0-1.0)
3. Detailed explanation
4. Suggestions for improvement (if needed)
5. Alternative codes (if applicable)

Requirements:
- Provide specific clinical reasoning
- Include billing and coverage considerations
- Assess code specificity and necessity
- Consider payer-specific requirements

Respond in JSON format:
{{
    "is_valid": true/false,
    "confidence_score": 0.0-1.0,
    "validation_message": "detailed explanation",
    "suggestions": ["suggestion1", "suggestion2"],
    "alternative_codes": ["alternative1", "alternative2"],
    "validation_details": {{
        "clinical_reasoning": "explanation",
        "billing_considerations": "notes",
        "coverage_assessment": "assessment"
    }}
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
                    temperature=0.1,  # Lower temperature for consistent validation
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif self.provider.lower() == "anthropic":
                response = await self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error("AI API call failed", provider=self.provider, error=str(e))
            raise
    
    def _parse_validation_response(
        self, 
        ai_response: str, 
        original_request: MedicalCodeValidationRequest
    ) -> MedicalCodeValidationResponse:
        """Parse AI response into structured validation result."""
        try:
            # Clean and parse JSON response
            response_text = ai_response.strip()
            
            # Extract JSON from response (remove any markdown formatting)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 8
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            
            parsed_response = json.loads(response_text.strip())
            
            return MedicalCodeValidationResponse(
                code=original_request.code,
                code_type=original_request.code_type,
                is_valid=parsed_response.get("is_valid", False),
                confidence_score=float(parsed_response.get("confidence_score", 0.0)),
                validation_message=parsed_response.get("validation_message", ""),
                suggestions=parsed_response.get("suggestions", []),
                alternative_codes=parsed_response.get("alternative_codes", []),
                validation_details=parsed_response.get("validation_details", {})
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to parse AI response", error=str(e), response=ai_response)
            
            # Fallback: provide basic validation
            return MedicalCodeValidationResponse(
                code=original_request.code,
                code_type=original_request.code_type,
                is_valid=False,
                confidence_score=0.0,
                validation_message="Unable to parse validation response",
                suggestions=[f"Manual review recommended for code {original_request.code}"]
            )
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token usage for billing and monitoring."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        total_chars = len(prompt) + len(response or "")
        return total_chars // 4
    
    async def batch_validate(self, requests: List[MedicalCodeValidationRequest]) -> List[MedicalCodeValidationResponse]:
        """Process multiple validation requests efficiently."""
        logger.info(f"Starting batch validation of {len(requests)} codes")
        
        # Process requests concurrently with rate limiting
        semaphore = asyncio.Semaphore(self.config.get("max_concurrent_requests", 5))
        
        async def process_single(request):
            async with semaphore:
                return await self.process(request)
        
        tasks = [process_single(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch request {i} failed", error=str(result))
                # Create error response
                error_response = MedicalCodeValidationResponse(
                    code=requests[i].code,
                    code_type=requests[i].code_type,
                    is_valid=False,
                    confidence_score=0.0,
                    validation_message=f"Batch processing error: {str(result)}"
                )
                processed_results.append(error_response)
            else:
                processed_results.append(result)
        
        logger.info(f"Completed batch validation, {len(processed_results)} results")
        return processed_results
