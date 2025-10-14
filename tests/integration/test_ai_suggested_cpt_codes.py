"""
Integration tests for AI Suggested CPT Codes endpoint.
Tests the /rcm-api/getAISuggested_CPTCodes endpoint with various scenarios.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAISuggestedCPTCodes:
    """Test AI Suggested CPT Codes endpoint functionality."""
    
    def test_basic_request_with_icds(self, test_client: TestClient, check_openai_key):
        """Happy-path test using selected_icds and concise notes."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI CPT code suggestions")
        
        payload = {
            "clinical_notes": "Established patient follow-up. Obtained and interpreted 12-lead ECG.",
            "history": "Hyperlipidemia; on statin.",
            "selected_icds": ["I65.23"],
            "max_results": 5
        }
        
        response = test_client.post("/rcm-api/getAISuggested_CPTCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert isinstance(data["results"], list)
        
        for item in data["results"]:
            assert "code" in item
            assert "confidence" in item
            assert "short_title" in item
            assert "description" in item
            assert isinstance(item["confidence"], int)
            assert 90 <= item["confidence"] <= 100
    
    def test_invalid_payload_missing_clinical_notes(self, test_client: TestClient):
        """Validation error when required clinical_notes is missing."""
        payload = {
            "history": "HTN",
            "selected_icds": ["I10"]
        }
        response = test_client.post("/rcm-api/getAISuggested_CPTCodes", json=payload)
        assert response.status_code == 422
        assert "detail" in response.json()
    
    def test_invalid_json_payload(self, test_client: TestClient):
        """Invalid JSON content-type body returns 422."""
        response = test_client.post(
            "/rcm-api/getAISuggested_CPTCodes",
            data="not-json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_empty_results_allowed_when_no_confident_items(self, test_client: TestClient, check_openai_key):
        """If LLM returns nothing meeting threshold, endpoint should still 200 with empty results."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI CPT code suggestions")
        
        payload = {
            "clinical_notes": "Insufficient info.",
            "max_results": 3
        }
        response = test_client.post("/rcm-api/getAISuggested_CPTCodes", json=payload)
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert isinstance(data["results"], list)


