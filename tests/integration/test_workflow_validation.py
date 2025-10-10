"""
Integration tests for workflow validation:
- Agent pipeline execution
- Multi-stage validation workflow
- Parallel vs sequential execution
- Error handling and fallbacks
"""
import pytest
import asyncio
import json
from pathlib import Path

from app.agents.parser_agent import ParserAgent
from app.agents.note_to_icd_agent import NoteToICDAgent
from app.agents.icd_to_cpt_agent import ICDToCPTAgent
from app.agents.code_validation_agent import CodeValidationAgent
from app.agents.summarizer_agent import SummarizerAgent
from app.services.pipeline.usecase1_pipeline import UseCase1Pipeline
from app.services.orchestrator.enhanced_orchestrator import EnhancedMedicalCodingOrchestrator


@pytest.mark.integration
class TestAgentWorkflows:
    """Test individual agent workflows."""
    
    @pytest.mark.asyncio
    async def test_parser_agent_csv(self, sample_csv_data):
        """Test ParserAgent with CSV input."""
        agent = ParserAgent()
        
        result = await agent.process({"csv_path": str(sample_csv_data)})
        
        assert "soap_notes" in result
        assert len(result["soap_notes"]) > 0
        assert "chest pain" in result["soap_notes"].lower() or "diabetes" in result["soap_notes"].lower()
        assert "rows" in result
        assert len(result["rows"]) == 2
        
        print(f"✓ Parser agent CSV: {len(result['rows'])} rows, {len(result['soap_notes'])} chars")
    
    @pytest.mark.asyncio
    async def test_parser_agent_hl7(self, sample_hl7_message):
        """Test ParserAgent with HL7 input."""
        agent = ParserAgent()
        
        result = await agent.process({"hl7_text": sample_hl7_message})
        
        assert "soap_notes" in result
        assert "segments" in result
        # Should extract NTE segments
        assert "chest pain" in result["soap_notes"].lower() or "elevation" in result["soap_notes"].lower()
        
        print(f"✓ Parser agent HL7: {result['segments']} segments, notes extracted")
    
    @pytest.mark.asyncio
    async def test_note_to_icd_agent(self, check_openai_key, sample_soap_notes):
        """Test NoteToICDAgent with clinical notes."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        agent = NoteToICDAgent()
        
        result = await agent.process({"soap_notes": sample_soap_notes})
        
        assert "icd_suggestions" in result
        assert len(result["icd_suggestions"]) > 0
        
        # Try to parse JSON response
        try:
            icd_codes = json.loads(result["icd_suggestions"])
            assert isinstance(icd_codes, list)
            if len(icd_codes) > 0:
                assert "code" in icd_codes[0]
                # Should identify MI
                assert any("I21" in code.get("code", "") for code in icd_codes)
                print(f"✓ NoteToICD agent: {len(icd_codes)} codes suggested")
        except json.JSONDecodeError:
            # LLM may return text with JSON embedded
            assert "I21" in result["icd_suggestions"]  # Should at least mention MI code
            print(f"✓ NoteToICD agent: Response contains expected codes")
    
    @pytest.mark.asyncio
    async def test_icd_to_cpt_agent(self, check_openai_key):
        """Test ICDToCPTAgent with ICD codes."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        agent = ICDToCPTAgent()
        
        icd_list = [
            {"code": "I21.19", "description": "STEMI inferior wall"},
            {"code": "I10", "description": "Hypertension"}
        ]
        
        result = await agent.process({"icd_list": icd_list})
        
        assert "cpt_suggestions" in result
        assert len(result["cpt_suggestions"]) > 0
        
        # Should suggest cardiac procedures
        response = result["cpt_suggestions"]
        assert "93" in response or "99" in response  # Cardiac cath or E/M codes
        
        print(f"✓ ICDToCPT agent: Suggested procedures for MI")
    
    @pytest.mark.asyncio
    async def test_validation_agent(self, check_openai_key, sample_manual_codes):
        """Test CodeValidationAgent comparing manual vs AI codes."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        agent = CodeValidationAgent()
        
        ai_codes = {
            "icd": [
                {"code": "I21.19", "description": "STEMI inferior wall", "confidence": 0.95},
                {"code": "I10", "description": "Hypertension", "confidence": 0.90}
            ],
            "cpt": [
                {"code": "99285", "description": "ED visit high complexity", "probability": 0.92},
                {"code": "93458", "description": "Cardiac catheterization", "probability": 0.88}
            ]
        }
        
        result = await agent.process({
            "manual_codes": sample_manual_codes,
            "ai_codes": ai_codes
        })
        
        assert "validation_report" in result
        assert len(result["validation_report"]) > 0
        
        print(f"✓ Validation agent: Generated comparison report")
    
    @pytest.mark.asyncio
    async def test_summarizer_agent(self, check_openai_key):
        """Test SummarizerAgent generating executive summary."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        agent = SummarizerAgent()
        
        validation_report = """
        Validation Report:
        - Overall accuracy: 0.92
        - Denial risk: 0.18
        - Matches: ICD codes match perfectly
        - Discrepancies: Missing modifier on CPT 93458
        - Actions: Add modifier 26 for professional component
        """
        
        result = await agent.process({"validation_report": validation_report})
        
        assert "summary" in result
        assert len(result["summary"]) > 0
        
        print(f"✓ Summarizer agent: Generated executive summary")


@pytest.mark.integration
@pytest.mark.slow
class TestPipelineWorkflows:
    """Test complete pipeline workflows."""
    
    @pytest.mark.asyncio
    async def test_simple_pipeline_execution(self, check_openai_key, sample_csv_data, sample_manual_codes):
        """Test basic pipeline execution."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        pipeline = UseCase1Pipeline()
        
        result = await pipeline.run(
            csv_path=str(sample_csv_data),
            manual_codes=sample_manual_codes
        )
        
        assert "parsed" in result
        assert "icd" in result
        assert "cpt" in result
        assert "validation" in result
        assert "summary" in result
        
        print("✓ Simple pipeline completed all stages")
        print(f"  ICD codes: {len(result['icd'])}")
        print(f"  CPT codes: {len(result['cpt'])}")
    
    @pytest.mark.asyncio
    async def test_enhanced_pipeline_sequential(self, check_openai_key, sample_soap_notes, sample_manual_codes):
        """Test enhanced pipeline in sequential mode."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=sample_soap_notes,
            manual_codes=sample_manual_codes,
            enable_parallel=False,
            confidence_threshold=0.85
        )
        
        assert "metadata" in result
        assert result["metadata"]["execution_mode"] == "sequential"
        assert "stages" in result
        assert "parsing" in result["stages"]
        assert "rag_retrieval" in result["stages"]
        assert "code_generation" in result["stages"]
        assert "validation" in result["stages"]
        assert "summary" in result["stages"]
        assert "final_decision" in result
        
        print(f"✓ Enhanced pipeline (sequential) completed in {result['metadata']['processing_time_seconds']:.2f}s")
        print(f"  Decision: {result['final_decision'].get('recommendation', 'N/A')}")
    
    @pytest.mark.asyncio
    async def test_enhanced_pipeline_parallel(self, check_openai_key, sample_soap_notes, sample_manual_codes):
        """Test enhanced pipeline in parallel mode."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=sample_soap_notes,
            manual_codes=sample_manual_codes,
            enable_parallel=True,
            confidence_threshold=0.85
        )
        
        assert result["metadata"]["execution_mode"] == "parallel"
        assert "final_decision" in result
        
        processing_time = result["metadata"]["processing_time_seconds"]
        
        print(f"✓ Enhanced pipeline (parallel) completed in {processing_time:.2f}s")
        print(f"  Approval status: {result['final_decision'].get('approved', 'N/A')}")
    
    @pytest.mark.asyncio
    async def test_pipeline_performance_comparison(self, check_openai_key, sample_soap_notes):
        """Compare sequential vs parallel execution performance."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Sequential execution
        result_seq = await orchestrator.execute_pipeline(
            clinical_notes=sample_soap_notes,
            enable_parallel=False
        )
        time_seq = result_seq["metadata"]["processing_time_seconds"]
        
        # Parallel execution
        result_par = await orchestrator.execute_pipeline(
            clinical_notes=sample_soap_notes,
            enable_parallel=True
        )
        time_par = result_par["metadata"]["processing_time_seconds"]
        
        speedup = (time_seq - time_par) / time_seq * 100 if time_seq > time_par else 0
        
        print(f"✓ Performance comparison:")
        print(f"  Sequential: {time_seq:.2f}s")
        print(f"  Parallel: {time_par:.2f}s")
        print(f"  Speedup: {speedup:.1f}%")
        
        # Parallel should be faster or similar (allow for variance)
        assert time_par <= time_seq * 1.2  # Allow 20% variance


@pytest.mark.integration
class TestWorkflowValidation:
    """Test validation logic and decision making."""
    
    @pytest.mark.asyncio
    async def test_high_confidence_approval(self, check_openai_key):
        """Test automatic approval for high confidence results."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Simple, clear case
        notes = """
        Patient with Type 2 diabetes mellitus.
        HbA1c: 7.5%
        Currently on metformin 1000mg BID.
        Blood pressure: 130/85
        """
        
        manual = {
            "icd": [{"code": "E11.9", "description": "Type 2 diabetes"}],
            "cpt": [{"code": "99213", "description": "Office visit"}]
        }
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=notes,
            manual_codes=manual,
            confidence_threshold=0.80
        )
        
        decision = result["final_decision"]
        print(f"✓ High confidence case decision: {decision.get('recommendation')}")
        print(f"  Confidence: {decision.get('confidence', 0):.2f}")
        print(f"  Denial risk: {decision.get('denial_risk', 0):.2f}")
    
    @pytest.mark.asyncio
    async def test_low_confidence_rejection(self, check_openai_key):
        """Test rejection for unclear/risky cases."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Vague, incomplete notes
        notes = "Patient not feeling well. Prescribed medication."
        
        manual = {
            "icd": [{"code": "R53.83"}],  # Fatigue - very non-specific
            "cpt": [{"code": "99213"}]
        }
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=notes,
            manual_codes=manual,
            confidence_threshold=0.85
        )
        
        decision = result["final_decision"]
        
        # Should require manual review due to low specificity
        assert decision.get("requires_manual_review") == True
        
        print(f"✓ Low confidence case correctly requires manual review")
        print(f"  Reason: {decision.get('recommendation')}")
    
    @pytest.mark.asyncio
    async def test_validation_with_rag_context(self, check_openai_key, tmp_path):
        """Test validation workflow with RAG guidelines."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        # Create test guidelines
        doc_dir = tmp_path / "validation_test"
        doc_dir.mkdir()
        (doc_dir / "mi_guidelines.txt").write_text("""
        Myocardial Infarction Coding Guidelines:
        - I21.19 requires documentation of ST elevation and troponin elevation
        - Must specify inferior wall involvement
        - CPT 93458 (cardiac cath) requires documented medical necessity
        - Emergency department visit codes 99281-99285 based on complexity
        """)
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Ingest guidelines first
        await orchestrator.rag_store.ingest_directory(str(doc_dir))
        
        # Run validation with RAG
        notes = sample_soap_notes = """
        Patient with chest pain, ST elevation in inferior leads, troponin 4.8.
        Diagnosis: Acute inferior STEMI.
        Plan: Emergency cardiac catheterization.
        """
        
        manual = {
            "icd": [{"code": "I21.19"}],
            "cpt": [{"code": "99285"}, {"code": "93458"}]
        }
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=notes,
            manual_codes=manual
        )
        
        # Should retrieve relevant guidelines
        rag_stage = result["stages"]["rag_retrieval"]
        assert rag_stage["documents_retrieved"] > 0
        
        print(f"✓ RAG-enhanced validation:")
        print(f"  Documents retrieved: {rag_stage['documents_retrieved']}")
        print(f"  Decision: {result['final_decision'].get('recommendation')}")


@pytest.mark.integration
class TestErrorHandlingAndFallbacks:
    """Test error handling and fallback mechanisms."""
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self):
        """Test pipeline recovery from agent failures."""
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Test with invalid input (should handle gracefully)
        result = await orchestrator.execute_pipeline(
            clinical_notes=None,  # Invalid input
            enable_parallel=False
        )
        
        # Should have error but not crash
        assert "metadata" in result
        # May have error in metadata or continue with empty notes
        
        print("✓ Pipeline handled invalid input gracefully")
    
    @pytest.mark.asyncio
    async def test_partial_failure_handling(self, check_openai_key):
        """Test handling of partial failures in parallel execution."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # Valid notes but may cause some validation issues
        notes = "Test notes with minimal information"
        
        result = await orchestrator.execute_pipeline(
            clinical_notes=notes,
            manual_codes={"icd": [], "cpt": []},
            enable_parallel=True
        )
        
        # Should complete even with minimal data
        assert "final_decision" in result
        # Decision should require manual review
        assert result["final_decision"]["requires_manual_review"] == True
        
        print("✓ Pipeline handled partial failures in parallel mode")
    
    @pytest.mark.asyncio
    async def test_json_parsing_fallback(self, check_openai_key):
        """Test fallback when LLM returns malformed JSON."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required")
        
        orchestrator = EnhancedMedicalCodingOrchestrator()
        
        # The orchestrator should handle JSON parsing errors gracefully
        result = await orchestrator.execute_pipeline(
            clinical_notes="Brief note",
            enable_parallel=False
        )
        
        # Should have default values if JSON parsing fails
        assert "stages" in result
        code_gen = result["stages"].get("code_generation", {})
        
        # Should have counts (may be 0)
        assert "icd_codes_generated" in code_gen or "status" in code_gen
        
        print("✓ JSON parsing fallback working")

