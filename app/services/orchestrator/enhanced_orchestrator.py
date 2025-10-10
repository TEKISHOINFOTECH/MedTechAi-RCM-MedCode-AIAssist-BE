"""
Enhanced orchestrator with parallel/sequential execution, RAG integration, and advanced validation.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.agents.parser_agent import ParserAgent
from app.agents.note_to_icd_agent import NoteToICDAgent
from app.agents.icd_to_cpt_agent import ICDToCPTAgent
from app.agents.code_validation_agent import CodeValidationAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.services.rag.chroma_store import ChromaVectorStore
from app.utils.llm import LLMClient
from app.services.prompt_templates import (
    format_soap_to_icd_prompt,
    format_icd_to_cpt_prompt,
    format_validation_prompt,
    format_summary_prompt
)

logger = logging.getLogger(__name__)


class EnhancedMedicalCodingOrchestrator:
    """
    Advanced orchestrator with:
    - Parallel agent execution where appropriate
    - RAG-integrated validation
    - Multi-stage validation with confidence thresholds
    - Comprehensive error handling and fallbacks
    """
    
    def __init__(self):
        self.parser = ParserAgent()
        self.rag_store = ChromaVectorStore()
        self.llm = LLMClient()
        
    async def execute_pipeline(
        self,
        *,
        csv_path: Optional[str] = None,
        hl7_text: Optional[str] = None,
        clinical_notes: Optional[str] = None,
        manual_codes: Optional[Dict[str, Any]] = None,
        setting: str = "Outpatient",
        specialty: str = "General Practice",
        payer_type: str = "Commercial",
        enable_parallel: bool = True,
        confidence_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Execute enhanced validation pipeline with parallel processing and RAG.
        
        Args:
            csv_path: Path to CSV claim file
            hl7_text: Raw HL7 message text
            clinical_notes: Pre-extracted clinical documentation
            manual_codes: Manual coder's codes for comparison
            setting: Clinical setting (Outpatient/Inpatient/ED)
            specialty: Medical specialty
            payer_type: Insurance payer type
            enable_parallel: Enable parallel execution where possible
            confidence_threshold: Minimum confidence for auto-approval
            
        Returns:
            Comprehensive validation results with recommendations
        """
        start_time = datetime.utcnow()
        pipeline_results = {
            "metadata": {
                "pipeline_version": "2.0-enhanced",
                "execution_mode": "parallel" if enable_parallel else "sequential",
                "start_time": start_time.isoformat(),
                "confidence_threshold": confidence_threshold
            },
            "stages": {}
        }
        
        try:
            # Stage 1: Parse and extract clinical notes
            logger.info("Stage 1: Parsing clinical documentation")
            if clinical_notes:
                soap_notes = clinical_notes
                pipeline_results["stages"]["parsing"] = {
                    "status": "bypassed",
                    "source": "direct_input"
                }
            else:
                parsed = await self.parser.process({
                    "csv_path": csv_path,
                    "hl7_text": hl7_text
                })
                soap_notes = parsed.get("soap_notes", "")
                pipeline_results["stages"]["parsing"] = {
                    "status": "success",
                    "soap_length": len(soap_notes),
                    "rows_parsed": len(parsed.get("rows", []))
                }
            
            # Stage 2: RAG - Retrieve relevant coding guidelines
            logger.info("Stage 2: Retrieving coding guidelines from RAG")
            rag_context = await self._get_rag_context(soap_notes)
            pipeline_results["stages"]["rag_retrieval"] = {
                "status": "success",
                "documents_retrieved": len(rag_context),
                "relevance_scores": [doc.get("distance") for doc in rag_context]
            }
            
            # Stage 3: Parallel AI code generation
            logger.info("Stage 3: Generating ICD and CPT codes")
            if enable_parallel:
                # Run ICD extraction in parallel with RAG-enhanced context
                icd_task = self._extract_icd_codes_enhanced(soap_notes, rag_context)
                
                # Wait for ICD codes before CPT (CPT depends on ICD)
                ai_icd_codes = await icd_task
                
                # Now generate CPT codes based on ICD codes
                ai_cpt_codes = await self._extract_cpt_codes_enhanced(
                    ai_icd_codes,
                    setting=setting,
                    specialty=specialty,
                    payer_type=payer_type
                )
            else:
                # Sequential execution
                ai_icd_codes = await self._extract_icd_codes_enhanced(soap_notes, rag_context)
                ai_cpt_codes = await self._extract_cpt_codes_enhanced(
                    ai_icd_codes,
                    setting=setting,
                    specialty=specialty,
                    payer_type=payer_type
                )
            
            pipeline_results["stages"]["code_generation"] = {
                "status": "success",
                "icd_codes_generated": len(ai_icd_codes),
                "cpt_codes_generated": len(ai_cpt_codes),
                "avg_icd_confidence": self._calc_avg_confidence(ai_icd_codes),
                "avg_cpt_confidence": self._calc_avg_confidence(ai_cpt_codes)
            }
            
            # Stage 4: Multi-stage validation
            logger.info("Stage 4: Validating codes with RAG-enhanced validation")
            manual = manual_codes or {"icd": [], "cpt": []}
            
            # Parallel validation checks
            if enable_parallel:
                validation_tasks = [
                    self._validate_with_rag(
                        manual_icd=manual.get("icd", []),
                        manual_cpt=manual.get("cpt", []),
                        ai_icd=ai_icd_codes,
                        ai_cpt=ai_cpt_codes,
                        clinical_notes=soap_notes,
                        rag_context=rag_context
                    ),
                    self._check_medical_necessity(ai_icd_codes, ai_cpt_codes),
                    self._check_compliance_rules(ai_icd_codes, ai_cpt_codes, payer_type)
                ]
                
                validation_result, necessity_check, compliance_check = await asyncio.gather(
                    *validation_tasks,
                    return_exceptions=True
                )
            else:
                validation_result = await self._validate_with_rag(
                    manual_icd=manual.get("icd", []),
                    manual_cpt=manual.get("cpt", []),
                    ai_icd=ai_icd_codes,
                    ai_cpt=ai_cpt_codes,
                    clinical_notes=soap_notes,
                    rag_context=rag_context
                )
                necessity_check = await self._check_medical_necessity(ai_icd_codes, ai_cpt_codes)
                compliance_check = await self._check_compliance_rules(ai_icd_codes, ai_cpt_codes, payer_type)
            
            # Handle exceptions from parallel execution
            if isinstance(validation_result, Exception):
                logger.error(f"Validation failed: {validation_result}")
                validation_result = {"error": str(validation_result)}
            if isinstance(necessity_check, Exception):
                logger.error(f"Necessity check failed: {necessity_check}")
                necessity_check = {"error": str(necessity_check)}
            if isinstance(compliance_check, Exception):
                logger.error(f"Compliance check failed: {compliance_check}")
                compliance_check = {"error": str(compliance_check)}
            
            pipeline_results["stages"]["validation"] = {
                "status": "success",
                "validation": validation_result,
                "medical_necessity": necessity_check,
                "compliance": compliance_check
            }
            
            # Stage 5: Executive summary and recommendations
            logger.info("Stage 5: Generating executive summary")
            summary = await self._generate_executive_summary(
                validation_result,
                necessity_check,
                compliance_check
            )
            
            pipeline_results["stages"]["summary"] = {
                "status": "success",
                "summary": summary
            }
            
            # Calculate overall metrics
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            pipeline_results["metadata"]["end_time"] = end_time.isoformat()
            pipeline_results["metadata"]["processing_time_seconds"] = processing_time
            
            # Final decision
            pipeline_results["final_decision"] = self._make_final_decision(
                validation_result,
                summary,
                confidence_threshold
            )
            
            return pipeline_results
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            end_time = datetime.utcnow()
            pipeline_results["metadata"]["end_time"] = end_time.isoformat()
            pipeline_results["metadata"]["error"] = str(e)
            pipeline_results["final_decision"] = {
                "approved": False,
                "reason": f"Pipeline error: {str(e)}",
                "requires_manual_review": True
            }
            return pipeline_results
    
    async def _get_rag_context(self, clinical_notes: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant coding guidelines from RAG store."""
        try:
            # Extract key medical terms for better retrieval
            query = f"Medical coding guidelines for: {clinical_notes[:500]}"
            results = await self.rag_store.query(query, k=k)
            return results
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
            return []
    
    async def _extract_icd_codes_enhanced(
        self,
        soap_notes: str,
        rag_context: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract ICD codes with RAG-enhanced prompting."""
        try:
            # Add RAG context to prompt
            rag_text = "\n\n".join([
                f"REFERENCE: {doc.get('document', '')[:500]}"
                for doc in rag_context[:3]
            ])
            
            prompt = format_soap_to_icd_prompt(soap_notes)
            if rag_text:
                prompt = prompt.replace(
                    "CLINICAL NOTES:",
                    f"REFERENCE GUIDELINES:\n{rag_text}\n\nCLINICAL NOTES:"
                )
            
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse JSON response
            codes = self._safe_json_parse(response, default=[])
            return codes
            
        except Exception as e:
            logger.error(f"ICD extraction failed: {e}")
            return []
    
    async def _extract_cpt_codes_enhanced(
        self,
        icd_codes: List[Dict[str, Any]],
        setting: str,
        specialty: str,
        payer_type: str
    ) -> List[Dict[str, Any]]:
        """Extract CPT codes with contextual information."""
        try:
            prompt = format_icd_to_cpt_prompt(
                icd_codes=icd_codes,
                setting=setting,
                specialty=specialty,
                payer_type=payer_type
            )
            
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2000
            )
            
            codes = self._safe_json_parse(response, default=[])
            return codes
            
        except Exception as e:
            logger.error(f"CPT extraction failed: {e}")
            return []
    
    async def _validate_with_rag(
        self,
        manual_icd: List,
        manual_cpt: List,
        ai_icd: List[Dict[str, Any]],
        ai_cpt: List[Dict[str, Any]],
        clinical_notes: str,
        rag_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive validation with RAG context."""
        try:
            rag_text = "\n\n".join([
                f"{doc.get('metadata', {}).get('source', 'Unknown')}: {doc.get('document', '')[:300]}"
                for doc in rag_context[:5]
            ])
            
            prompt = format_validation_prompt(
                manual_icd=manual_icd,
                manual_cpt=manual_cpt,
                ai_icd=ai_icd,
                ai_cpt=ai_cpt,
                clinical_notes=clinical_notes,
                rag_context=rag_text
            )
            
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=3000
            )
            
            validation = self._safe_json_parse(response, default={})
            return validation
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {"error": str(e)}
    
    async def _check_medical_necessity(
        self,
        icd_codes: List[Dict[str, Any]],
        cpt_codes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Verify medical necessity between ICD and CPT codes."""
        prompt = f"""Verify medical necessity: Do these CPT codes have appropriate ICD support?

ICD Codes: {json.dumps(icd_codes, indent=2)}
CPT Codes: {json.dumps(cpt_codes, indent=2)}

Respond with JSON:
{{
  "overall_necessity": 0.0-1.0,
  "issues": [
    {{"cpt": "code", "icd_support": "weak|none|adequate", "recommendation": "..."}}
  ]
}}
"""
        try:
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1500
            )
            return self._safe_json_parse(response, default={"overall_necessity": 0.5, "issues": []})
        except Exception as e:
            logger.error(f"Medical necessity check failed: {e}")
            return {"error": str(e), "overall_necessity": 0.5}
    
    async def _check_compliance_rules(
        self,
        icd_codes: List[Dict[str, Any]],
        cpt_codes: List[Dict[str, Any]],
        payer_type: str
    ) -> Dict[str, Any]:
        """Check compliance with NCCI, LCD, bundling rules."""
        prompt = f"""Check compliance for {payer_type} payer:

ICD: {[c.get('code') for c in icd_codes]}
CPT: {[c.get('code') for c in cpt_codes]}

Check:
1. NCCI bundling edits
2. Modifier requirements
3. Medical policy (LCD/NCD)
4. Frequency limitations

Respond with JSON:
{{
  "compliant": true/false,
  "violations": [{{"rule": "...", "codes": [], "fix": "..."}}],
  "required_modifiers": [{{"code": "...", "modifier": "..."}}]
}}
"""
        try:
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=1500
            )
            return self._safe_json_parse(response, default={"compliant": True, "violations": []})
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            return {"error": str(e), "compliant": True}
    
    async def _generate_executive_summary(
        self,
        validation_result: Dict[str, Any],
        necessity_check: Dict[str, Any],
        compliance_check: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary with actionable insights."""
        try:
            combined_report = json.dumps({
                "validation": validation_result,
                "medical_necessity": necessity_check,
                "compliance": compliance_check
            }, indent=2)
            
            prompt = format_summary_prompt(combined_report)
            
            response = await self.llm.chat(
                [{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=2500
            )
            
            summary = self._safe_json_parse(response, default={})
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {"error": str(e)}
    
    def _make_final_decision(
        self,
        validation_result: Dict[str, Any],
        summary: Dict[str, Any],
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """Make final approval decision based on all validation stages."""
        try:
            # Extract key metrics
            val_summary = validation_result.get("validation_summary", {})
            accuracy = val_summary.get("overall_accuracy", 0.0)
            denial_risk = val_summary.get("denial_risk", 1.0)
            
            exec_summary = summary.get("executive_summary", {})
            claim_status = exec_summary.get("claim_status", "needs_review")
            
            # Decision logic
            if claim_status == "clean" and accuracy >= confidence_threshold and denial_risk < 0.2:
                return {
                    "approved": True,
                    "confidence": accuracy,
                    "denial_risk": denial_risk,
                    "recommendation": "Approve for submission",
                    "requires_manual_review": False
                }
            elif claim_status == "critical_issues" or denial_risk > 0.7:
                return {
                    "approved": False,
                    "confidence": accuracy,
                    "denial_risk": denial_risk,
                    "recommendation": "Do not submit - critical issues found",
                    "requires_manual_review": True,
                    "escalation_reason": "High denial risk"
                }
            else:
                return {
                    "approved": False,
                    "confidence": accuracy,
                    "denial_risk": denial_risk,
                    "recommendation": "Hold for manual review",
                    "requires_manual_review": True,
                    "review_priority": "Medium" if denial_risk < 0.5 else "High"
                }
                
        except Exception as e:
            logger.error(f"Decision making failed: {e}")
            return {
                "approved": False,
                "recommendation": "Manual review required due to decision error",
                "requires_manual_review": True,
                "error": str(e)
            }
    
    def _safe_json_parse(self, text: str, default: Any = None) -> Any:
        """Safely parse JSON from LLM response."""
        try:
            # Clean markdown code blocks
            if "```json" in text:
                start = text.find("```json") + 7
                end = text.find("```", start)
                text = text[start:end]
            elif "```" in text:
                start = text.find("```") + 3
                end = text.find("```", start)
                text = text[start:end]
            
            return json.loads(text.strip())
        except Exception as e:
            logger.warning(f"JSON parse failed: {e}")
            return default
    
    def _calc_avg_confidence(self, codes: List[Dict[str, Any]]) -> float:
        """Calculate average confidence from code list."""
        if not codes:
            return 0.0
        confidences = [
            c.get("confidence", c.get("probability", 0.0))
            for c in codes
        ]
        return sum(confidences) / len(confidences) if confidences else 0.0

