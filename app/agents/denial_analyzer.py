"""
Denial Analysis Agent for analyzing denied claims and generating appeal strategies.
"""
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from .base_agent import BaseAgent
from config import settings

logger = logging.getLogger(__name__)


class DenialAnalysisAgent(BaseAgent):
    """
    AI agent for analyzing denied insurance claims and generating successful appeal strategies.
    
    Capabilities:
    - Analyze denial reasons and patterns
    - Generate targeted appeal letters
    - Identify documentation gaps
    - Suggest legal and regulatory arguments
    - Predict appeal success likelihood
    - Monitor denial trend patterns
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        provider: str = "openai",
        success_threshold: float = 0.7,
        **kwargs
    ):
        super().__init__(
            agent_name="denial_analyzer",
            model_name=model_name,
            provider=provider,
            success_threshold=success_threshold,
            **kwargs
        )
        
        self.success_threshold = success_threshold
        
        # Initialize AI client based on provider
        if provider.lower() == "openai":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        elif provider.lower() == "anthropic":
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate denial analysis input data."""
        required_for_single = ["denial_reason", "original_claim_data"]
        required_for_batch = ["denials"]
        
        # Check if single denial or batch
        if "denial_reason" in input_data:
            for field in required_for_single:
                if field not in input_data:
                    logger.warning(f"Missing required field for denial analysis: {field}")
                    return False
        elif "denials" in input_data:
            denials = input_data.get("denials", [])
            if not denials:
                logger.warning("No denials provided for batch analysis")
                return False
        else:
            logger.warning("Invalid input format for denial analysis")
            return False
        
        return True
    
    async def process(self, denial_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process insurance claim denial for appeal strategy generation.
        
        Args:
            denial_data: Dictionary containing denial information
              Single denial:
                - denial_reason: Official reason for denial
                - denial_details: Detailed denial explanation
                - denial_date: Date of denial
                - payer: Insurance payer information
                - original_claim_data: Original claim that was denied
                - patient_info: Patient demographic information
              
              Batch analysis:
                - denials: List of denial records
                - analysis_type: "pattern|trend|root_cause"
        
        Returns:
            Dict containing:
            - appeal_strategy: Detailed appeal approach
            - success_probability: Likelihood of successful appeal (0.0-1.0)
            - required_documentation: Documents needed for appeal
            - timeline_recommendations: Suggested appeal timeline
            - legal_arguments: Regulatory and legal basis for appeal
            - preventive_measures: Actions to prevent similar denials
        """
        start_time = datetime.utcnow()
        
        try:
            if not self.validate_input(denial_data):
                raise ValueError("Invalid denial analysis input data")
            
            logger.info(
                "Processing denial analysis",
                analysis_type=denial_data.get("analysis_type", "single_denial"),
                agent=self.agent_name
            )
            
            # Create denial analysis prompt
            prompt = self._create_denial_analysis_prompt(denial_data)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt)
            
            # Parse AI response
            analysis_result = self._parse_analysis_response(ai_response, denial_data)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            tokens_used = self._estimate_tokens(prompt, ai_response)
            self._update_metrics(processing_time, tokens_used, True)
            
            logger.info(
                "Denial analysis completed",
                success_probability=analysis_result.get("success_probability", 0.0),
                num_recommendations=len(analysis_result.get("preventive_measures", [])),
                processing_time_ms=processing_time
            )
            
            return analysis_result
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_metrics(processing_time, 0, False)
            
            logger.error(
                "Denial analysis failed",
                error=str(e),
                agent=self.agent_name
            )
            
            # Return error response
            return {
                "success_probability": 0.0,
                "appeal_strategy": "Manual review required due to analysis failure",
                "required_documentation": ["Current clinical documentation"],
                "legal_arguments": ["Standard billing practice"],
                "preventive_measures": ["Review processing error"],
                "timeline_recommendations": "As soon as possible",
                "error": str(e),
                "processing_time_ms": processing_time
            }
    
    def _create_denial_analysis_prompt(self, denial_data: Dict[str, Any]) -> str:
        """Create comprehensive denial analysis prompt for AI agent."""
        
        if "denials" in denial_data:
            # Batch analysis mode
            denials_text = ""
            for i, denial in enumerate(denial_data.get("denials", []), 1):
                denials_text += f"\nDenial {i}: {json.dumps(denial, indent=2)}"
            
            prompt = f"""
You are an expert healthcare revenue cycle management specialist with extensive experience in denial management and appeals.

Task: Analyze the following batch of denied insurance claims to identify patterns, trends, and root causes.

DENIALS DATA:{denials_text}

ANALYSIS TYPE: {denial_data.get('analysis_type', 'pattern')}

Please provide a comprehensive analysis including:

1. PATTERN IDENTIFICATION:
   - Common denial reasons
   - Payer-specific patterns
   - Temporal patterns (time-based trends)
   - Provider-specific issues

2. ROOT CAUSE ANALYSIS:
   - Systemic issues affecting claims processing
   - Process gaps and bottlenecks
   - Documentation deficiencies
   - Training needs

3. TREND ANALYSIS:
   - Denial frequency trends
   - Risk escalation patterns
   - Financial impact trends
   - Seasonal variations

4. STRATEGIC RECOMMENDATIONS:
   - Process improvements
   - System enhancements
   - Training requirements
   - Payer relationship strategies

5. PREVENTIVE MEASURES:
   - Early warning systems
   - Proactive interventions
   - Quality assurance protocols
   - Documentation standards

Respond in JSON format:
{{
    "pattern_analysis": {{
        "top_denial_reasons": ["reason1", "reason2"],
        "payer_patterns": {{
            "payer_name": ["common_reason1", "common_reason2"]
        }},
        "frequency_patterns": {{
            "high_frequency": ["code_type", "procedure"],
            "increasing_trends": ["denial_type"]
        }}
    }},
    "root_causes": [
        {{
            "cause": "root_cause_description",
            "severity": "high|medium|low",
            "impact": "description of impact",
            "solutions": ["solution1", "solution2"]
        }}
    ],
    "trends": {{
        "denial_rate_trend": "increasing|decreasing|stable",
        "financial_impact": "estimated_monthly_loss",
        "risk_level": "low|medium|high|critical"
    }},
    "strategic_recommendations": [
        {{
            "priority": "high|medium|low",
            "category": "process|technology|training|documentation",
            "title": "Recommendation title",
            "description": "Detailed recommendation",
            "implementation_time": "timeline",
            "expected_impact": "improvement estimate"
        }}
    ],
    "prevention_strategy": {{
        "early_warning_signs": ["sign1", "sign2"],
        "quality_measures": ["measure1", "measure2"],
        "monitoring_protocols": ["protocol1", "protocol2"]
    }}
}}"""
        
        else:
            # Single denial analysis mode
            prompt = f"""
You are an expert healthcare revenue cycle management specialist with extensive experience in denial management and successful appeals.

Task: Analyze the following denied insurance claim and develop a comprehensive appeal strategy with high success probability.

DENIAL INFORMATION:
Denial Reason: {denial_data.get('denial_reason', 'Not specified')}
Denial Details: {denial_data.get('denial_details', 'No additional details')}
Denial Date: {denial_data.get('denial_date', 'Date not provided')}
Payer: {json.dumps(denial_data.get('payer', {}), indent=2)}

ORIGINAL CLAIM DATA: {json.dumps(denial_data.get('original_claim_data', {}), indent=2)}

PATIENT INFORMATION: {json.dumps(denial_data.get('patient_info', {}), indent=2)}

Please provide a comprehensive denial analysis including:

1. DENIAL ASSESSMENT:
   - Denial reason classification
   - Validity of denial reason
   - Potential payer errors or misunderstandings
   - Documentation gaps

2. APPEAL STRATEGY:
   - Specific arguments against denial
   - Regulatory or policy references
   - Clinical evidence to present
   - Documentation to include

3. SUCCESS PROBABILITY:
   - Overall likelihood of successful appeal (0.0-1.0)
   - Confidence level in success
   - Key success factors
   - Risk factors limiting success

4. REQUIRED ACTIONS:
   - Documents to gather/includ
   - People to involve (physicians, coders, etc.)
   - Timeline for appeal submission
   - Follow-up actions needed

5. LEGAL/REGULATORY ARGUMENTS:
   - Applicable regulations or policies
   - Precedent cases or rulings
   - Medical necessity justification
   - Coding accuracy arguments

Respond in JSON format:
{{
    "appeal_strategy": {{
        "primary_argument": "main appeal argument",
        "supporting_evidence": ["evidence1", "evidence2"],
        "approach": "aggressive|conservative|collaborative",
        "success_probability": 0.0-1.0,
        "confidence_level": "high|medium|low"
    }},
    "required_documentation": [
        {{
            "document_type": "document name",
            "status": "available|missing|needs_update",
            "priority": "critical|high|medium|low",
            "purpose": "why this document is needed",
            "provider": "who should provide this"
        }}
    ],
    "legal_arguments": [
        {{
            "argument_type": "regulatory|clinical|coding|billing",
            "title": "argument title",
            "description": "detailed argument",
            "supporting_source": "regulation/policy/case",
            "strength": "strong|moderate|weak"
        }}
    ],
    "timeline_recommendations": {{
        "urgency": "immediate|high|medium|low",
        "optimal_submission_date": "target date",
        "deadline": "actual deadline if known",
        "follow_up_schedule": "recommended follow-up actions"
    }},
    "preventive_measures": [
        {{
            "measure_type": "process|documentation|coding|authorization",
            "title": "prevention measure",
            "description": "how to prevent similar denials",
            "implementation": "easy|moderate|complex",
            "impact": "high|medium|low"
        }}
    ],
    "risk_factors": [
        {{
            "factor": "risk factor description",
            "likelihood": "high|medium|low",
            "impact": "description of potential impact",
            "mitigation": "how to address this risk"
        }}
    ]
}}"""
        
        return prompt
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI provider."""
        try:
            if self.provider.lower() == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=2500
                )
                return response.choices[0].message.content
            
            elif self.provider.lower() == "anthropic":
                response = await self.client.messages.create(
                    model=self.model_name,
                    max_tokens=2500,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error("AI API call failed", provider=self.provider, error=str(e))
            raise
    
    def _parse_analysis_response(self, ai_response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI response into structured denial analysis result."""
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
            
            # Handle both single denial and batch analysis responses
            if "appeal_strategy" in parsed_response:
                # Single denial analysis
                appeal_strategy = parsed_response.get("appeal_strategy", {})
                return {
                    "success_probability": float(appeal_strategy.get("success_probability", 0.0)),
                    "confidence_level": appeal_strategy.get("confidence_level", "low"),
                    "appeal_strategy": appeal_strategy.get("primary_argument", ""),
                    "approach": appeal_strategy.get("approach", "conservative"),
                    "required_documentation": parsed_response.get("required_documentation", []),
                    "legal_arguments": parsed_response.get("legal_arguments", []),
                    "timeline_recommendations": parsed_response.get("timeline_recommendations", {}),
                    "preventive_measures": parsed_response.get("preventive_measures", []),
                    "risk_factors": parsed_response.get("risk_factors", [])
                }
            else:
                # Batch analysis
                return {
                    "analysis_type": original_data.get("analysis_type", "batch"),
                    "pattern_analysis": parsed_response.get("pattern_analysis", {}),
                    "root_causes": parsed_response.get("root_causes", []),
                    "trends": parsed_response.get("trends", {}),
                    "strategic_recommendations": parsed_response.get("strategic_recommendations", []),
                    "prevention_strategy": parsed_response.get("prevention_strategy", {})
                }
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Failed to parse AI response", error=str(e), response=ai_response)
            
            # Fallback: provide basic analysis
            return {
                "success_probability": 0.3,  # Conservative due to parsing failure
                "confidence_level": "low",
                "appeal_strategy": "Manual review and appeal preparation required",
                "approach": "conservative",
                "required_documentation": ["Clinical documentation review"],
                "legal_arguments": ["Standard billing practices"],
                "timeline_recommendations": {"urgency": "medium"},
                "preventive_measures": ["Review denial analysis parsing failure"],
                "risk_factors": [{"factor": "Analysis parsing error", "likelihood": "high", "impact": "Unknown appeal potential"}]
            }
    
    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token usage for billing and monitoring."""
        total_chars = len(prompt) + len(response or "")
        return total_chars // 4
