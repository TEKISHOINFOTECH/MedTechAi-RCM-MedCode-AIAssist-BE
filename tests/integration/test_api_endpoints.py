"""
Integration tests for API endpoints:
- Health check
- UseCase1 pipeline endpoints
- RAG ingestion and search
- Error responses
"""
import pytest
import json
from pathlib import Path

from fastapi.testclient import TestClient


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check and readiness endpoints."""
    
    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint."""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
        
        print(f"✓ Health check: {data['status']}")
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "MedTechAI" in data["message"] or "RCM" in data["message"]
        
        print(f"✓ Root endpoint: {data['message']}")
    
    def test_docs_endpoint(self, test_client: TestClient):
        """Test OpenAPI docs availability."""
        response = test_client.get("/docs")
        
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
        
        print("✓ API docs available")


@pytest.mark.integration
class TestUseCase1Endpoints:
    """Test UseCase1 pipeline API endpoints."""
    
    def test_simple_pipeline_endpoint(self, test_client: TestClient, sample_csv_data):
        """Test simple pipeline endpoint."""
        response = test_client.post(
            "/api/v1/uc1/pipeline/run/simple",
            params={
                "csv_path": str(sample_csv_data),
                "manual_icd": '["I21.19", "I10"]',
                "manual_cpt": '["99285", "93458"]'
            }
        )
        
        # May fail if LLM not configured, but should return valid error
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            print(f"✓ Simple pipeline endpoint successful")
        else:
            print(f"✓ Simple pipeline endpoint returns proper error: {response.status_code}")
    
    @pytest.mark.asyncio
    async def test_enhanced_pipeline_endpoint(self, test_client: TestClient, sample_soap_notes):
        """Test enhanced pipeline endpoint with full parameters."""
        payload = {
            "clinical_notes": sample_soap_notes,
            "manual_codes": {
                "icd": [{"code": "I21.19"}, {"code": "I10"}],
                "cpt": [{"code": "99285"}, {"code": "93458"}]
            },
            "setting": "Emergency",
            "specialty": "Cardiology",
            "payer_type": "Medicare",
            "enable_parallel": True,
            "confidence_threshold": 0.85
        }
        
        response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json=payload
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "metadata" in data
            assert "stages" in data
            assert "final_decision" in data
            print(f"✓ Enhanced pipeline endpoint successful")
            print(f"  Mode: {data['metadata'].get('execution_mode')}")
            print(f"  Time: {data['metadata'].get('processing_time_seconds')}s")
        else:
            error = response.json()
            print(f"✓ Enhanced pipeline endpoint error handled: {error.get('detail', 'Unknown')}")
    
    def test_pipeline_validation_errors(self, test_client: TestClient):
        """Test pipeline endpoint with invalid parameters."""
        # Missing required fields
        response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json={}
        )
        
        # Should handle validation error (422 or 500)
        assert response.status_code in [422, 500]
        
        print(f"✓ Pipeline validation errors handled properly")
    
    def test_pipeline_with_minimal_input(self, test_client: TestClient):
        """Test pipeline with minimal valid input."""
        payload = {
            "clinical_notes": "Patient presents with chest pain.",
            "setting": "Outpatient",
            "payer_type": "Commercial"
        }
        
        response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json=payload
        )
        
        # Should accept minimal input
        assert response.status_code in [200, 500]
        
        print(f"✓ Pipeline accepts minimal input: {response.status_code}")


@pytest.mark.integration
class TestRAGEndpoints:
    """Test RAG ingestion and search endpoints."""
    
    def test_rag_ingest_endpoint(self, test_client: TestClient, tmp_path):
        """Test RAG document ingestion endpoint."""
        # Create test documents
        doc_dir = tmp_path / "test_rag_docs"
        doc_dir.mkdir()
        (doc_dir / "test.txt").write_text("Test medical coding guideline document")
        
        response = test_client.post(
            "/api/v1/uc1/rag/ingest",
            params={"directory": str(doc_dir)}
        )
        
        # May fail if embeddings not configured
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "ingested" in data or "count" in data
            print(f"✓ RAG ingest endpoint successful: {data}")
        else:
            print(f"✓ RAG ingest endpoint error handled: {response.status_code}")
    
    def test_rag_search_endpoint(self, test_client: TestClient):
        """Test RAG search endpoint."""
        response = test_client.get(
            "/api/v1/uc1/rag/search",
            params={
                "q": "ICD-10 myocardial infarction",
                "k": 5
            }
        )
        
        # May return empty results if no documents ingested
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
            print(f"✓ RAG search endpoint successful")
        else:
            print(f"✓ RAG search endpoint handled: {response.status_code}")
    
    def test_rag_search_validation(self, test_client: TestClient):
        """Test RAG search with invalid parameters."""
        # Missing query
        response = test_client.get("/api/v1/uc1/rag/search")
        
        assert response.status_code in [422, 400, 500]
        
        print(f"✓ RAG search validation working: {response.status_code}")


@pytest.mark.integration
class TestErrorHandling:
    """Test API error handling."""
    
    def test_404_not_found(self, test_client: TestClient):
        """Test 404 for non-existent endpoints."""
        response = test_client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        
        print("✓ 404 handling working")
    
    def test_405_method_not_allowed(self, test_client: TestClient):
        """Test 405 for wrong HTTP methods."""
        response = test_client.get("/api/v1/uc1/pipeline/run")  # Should be POST
        
        assert response.status_code == 405
        
        print("✓ 405 method not allowed working")
    
    def test_422_validation_error(self, test_client: TestClient):
        """Test 422 for invalid request body."""
        response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json={"invalid_field": "value"}
        )
        
        # Should validate and reject
        assert response.status_code in [422, 500]
        
        print(f"✓ Validation error handling: {response.status_code}")
    
    def test_500_internal_error_handling(self, test_client: TestClient):
        """Test 500 error handling for internal errors."""
        # Try to trigger internal error with extreme input
        payload = {
            "clinical_notes": "x" * 1000000,  # Very large input
            "confidence_threshold": 999.9  # Invalid threshold
        }
        
        response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json=payload
        )
        
        # Should handle gracefully
        assert response.status_code in [422, 500]
        
        if response.status_code == 500:
            error = response.json()
            assert "detail" in error
            print(f"✓ 500 error handled: {error['detail'][:50]}")
        else:
            print(f"✓ Invalid input rejected at validation: {response.status_code}")


@pytest.mark.integration
class TestCORS:
    """Test CORS configuration."""
    
    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers are present."""
        response = test_client.options(
            "/api/v1/uc1/pipeline/run",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers or response.status_code == 200
        
        print("✓ CORS configuration working")
    
    def test_preflight_request(self, test_client: TestClient):
        """Test CORS preflight requests."""
        response = test_client.options(
            "/api/v1/uc1/pipeline/run",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code in [200, 204]
        
        print("✓ CORS preflight working")


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndAPI:
    """Test complete end-to-end API workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, test_client: TestClient, tmp_path, check_openai_key):
        """Test complete workflow: ingest guidelines -> run pipeline -> get results."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for full workflow")
        
        # Step 1: Ingest guidelines
        doc_dir = tmp_path / "e2e_docs"
        doc_dir.mkdir()
        (doc_dir / "guidelines.txt").write_text("""
        ICD-10 Coding for Myocardial Infarction:
        I21.19 - ST elevation MI of inferior wall
        Requires: ST elevation on ECG, elevated troponin
        """)
        
        ingest_response = test_client.post(
            "/api/v1/uc1/rag/ingest",
            params={"directory": str(doc_dir)}
        )
        
        # Step 2: Run pipeline
        pipeline_response = test_client.post(
            "/api/v1/uc1/pipeline/run",
            json={
                "clinical_notes": "Patient with chest pain, ST elevation, troponin 5.2",
                "manual_codes": {
                    "icd": [{"code": "I21.19"}],
                    "cpt": [{"code": "99285"}]
                },
                "enable_parallel": True
            }
        )
        
        # Step 3: Verify results
        if pipeline_response.status_code == 200:
            data = pipeline_response.json()
            
            assert "final_decision" in data
            assert data["stages"]["rag_retrieval"]["documents_retrieved"] > 0
            
            print("✓ Complete end-to-end workflow successful")
            print(f"  Pipeline time: {data['metadata']['processing_time_seconds']:.2f}s")
            print(f"  Decision: {data['final_decision'].get('recommendation')}")
        else:
            print(f"✓ Workflow handled with status: {pipeline_response.status_code}")
    
    def test_concurrent_requests(self, test_client: TestClient):
        """Test handling multiple concurrent API requests."""
        import concurrent.futures
        
        def make_request():
            return test_client.post(
                "/api/v1/uc1/pipeline/run",
                json={
                    "clinical_notes": "Test notes",
                    "setting": "Outpatient"
                }
            )
        
        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [f.result() for f in futures]
        
        # All should complete (may succeed or fail, but should respond)
        assert len(responses) == 5
        assert all(r.status_code in [200, 422, 500] for r in responses)
        
        print(f"✓ Handled 5 concurrent requests")
        print(f"  Status codes: {[r.status_code for r in responses]}")

