"""
Integration tests for AI Suggested ICD Codes endpoint.
Tests the /rcm-api/getAISuggested_ICDCodes endpoint with various scenarios.
"""
import pytest
import json
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestAISuggestedICDCodes:
    """Test AI Suggested ICD Codes endpoint functionality."""
    
    def test_complex_esrd_case_with_historical_ailments(self, test_client: TestClient, check_openai_key):
        """Test complex ESRD case with historical ailments."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": "This 70-year-old female has end-stage renal disease on hemodialysis through a right internal jugular catheter. She underwent left brachial basilic AV fistula transposition on May 28, 2024. The fistula is functioning well, and she presents for removal of the tunneled catheter.",
            "patient_historical_ailments": [
                {
                    "VisitDate": "2024-08-15",
                    "Diagnosis Code": "E11.9",
                    "ShortDescription": "Type 2 Diabetes Mellitus"
                }
            ]
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "ai_suggested_icd_codes" in data
        assert isinstance(data["ai_suggested_icd_codes"], list)
        assert len(data["ai_suggested_icd_codes"]) > 0
        
        # Validate ICD code structure
        for code in data["ai_suggested_icd_codes"]:
            assert "icd_code" in code
            assert "icd_title" in code
            assert "confidence_score" in code
            assert "explanation" in code
            assert isinstance(code["confidence_score"], (int, float))
            assert 0 <= code["confidence_score"] <= 100
        
        print(f"✓ Complex ESRD case: {len(data['ai_suggested_icd_codes'])} ICD codes suggested")
    
    def test_acute_myocardial_infarction(self, test_client: TestClient, check_openai_key):
        """Test acute myocardial infarction case."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": "Patient presents with chest pain and shortness of breath. EKG shows ST elevation in leads II, III, and aVF. Troponin levels are elevated. Patient is diagnosed with acute myocardial infarction."
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_suggested_icd_codes" in data
        assert len(data["ai_suggested_icd_codes"]) > 0
        
        # Check for myocardial infarction code
        icd_codes = [code["icd_code"] for code in data["ai_suggested_icd_codes"]]
        assert any("I21" in code for code in icd_codes)  # Myocardial infarction codes start with I21
        
        print(f"✓ Acute MI case: {len(data['ai_suggested_icd_codes'])} ICD codes suggested")
    
    def test_simple_diabetes_diagnosis(self, test_client: TestClient, check_openai_key):
        """Test simple diabetes diagnosis."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": "Patient has diabetes."
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_suggested_icd_codes" in data
        assert len(data["ai_suggested_icd_codes"]) > 0
        
        # Check for diabetes code
        icd_codes = [code["icd_code"] for code in data["ai_suggested_icd_codes"]]
        assert any("E11" in code or "E10" in code for code in icd_codes)  # Diabetes codes
        
        print(f"✓ Simple diabetes case: {len(data['ai_suggested_icd_codes'])} ICD codes suggested")
    
    def test_empty_clinical_note(self, test_client: TestClient, check_openai_key):
        """Test empty clinical note."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": ""
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_suggested_icd_codes" in data
        assert isinstance(data["ai_suggested_icd_codes"], list)
        # Should return empty list for empty clinical note
        assert len(data["ai_suggested_icd_codes"]) == 0
        
        print("✓ Empty clinical note handled correctly")
    
    def test_routine_followup_with_multiple_historical_ailments(self, test_client: TestClient, check_openai_key):
        """Test routine follow-up with multiple historical ailments."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": "Patient presents for routine follow-up.",
            "patient_historical_ailments": [
                {
                    "VisitDate": "2024-08-15",
                    "Diagnosis Code": "E11.9",
                    "ShortDescription": "Type 2 Diabetes Mellitus"
                },
                {
                    "VisitDate": "2024-07-20",
                    "Diagnosis Code": "I10",
                    "ShortDescription": "Essential hypertension"
                }
            ]
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ai_suggested_icd_codes" in data
        assert len(data["ai_suggested_icd_codes"]) > 0
        
        # Should include historical ailments
        icd_codes = [code["icd_code"] for code in data["ai_suggested_icd_codes"]]
        assert any("E11" in code for code in icd_codes)  # Diabetes
        assert any("I10" in code for code in icd_codes)  # Hypertension
        
        print(f"✓ Routine follow-up: {len(data['ai_suggested_icd_codes'])} ICD codes suggested")
    
    def test_invalid_payload_missing_clinical_note(self, test_client: TestClient):
        """Test invalid payload with missing required clinical_note field."""
        payload = {
            "patient_historical_ailments": [
                {
                    "VisitDate": "2024-08-15",
                    "Diagnosis Code": "E11.9",
                    "ShortDescription": "Type 2 Diabetes Mellitus"
                }
            ]
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data
        
        print("✓ Invalid payload validation working correctly")
    
    def test_invalid_json_payload(self, test_client: TestClient):
        """Test invalid JSON payload."""
        response = test_client.post(
            "/rcm-api/getAISuggested_ICDCodes",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
        
        print("✓ Invalid JSON payload handled correctly")
    
    def test_malformed_historical_ailments(self, test_client: TestClient, check_openai_key):
        """Test malformed historical ailments structure."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        payload = {
            "clinical_note": "Patient has diabetes.",
            "patient_historical_ailments": [
                {
                    "invalid_field": "value"
                }
            ]
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        # Should still work but handle malformed data gracefully
        assert response.status_code in [200, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "ai_suggested_icd_codes" in data
        
        print("✓ Malformed historical ailments handled gracefully")
    
    @pytest.mark.slow
    def test_large_clinical_note(self, test_client: TestClient, check_openai_key):
        """Test with large clinical note."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        # Create a large clinical note
        large_note = "Patient presents with multiple symptoms. " * 100
        
        payload = {
            "clinical_note": large_note
        }
        
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        # Should handle large input gracefully
        assert response.status_code in [200, 422, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "ai_suggested_icd_codes" in data
        
        print("✓ Large clinical note handled gracefully")
    
    def test_response_time_performance(self, test_client: TestClient, check_openai_key):
        """Test response time performance."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        import time
        
        payload = {
            "clinical_note": "Patient has diabetes."
        }
        
        start_time = time.time()
        response = test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30  # Should respond within 30 seconds
        
        print(f"✓ Response time: {response_time:.2f} seconds")
    
    def test_concurrent_requests(self, test_client: TestClient, check_openai_key):
        """Test handling multiple concurrent requests."""
        if not check_openai_key:
            pytest.skip("OpenAI API key required for AI ICD code suggestions")
        
        import concurrent.futures
        
        def make_request():
            payload = {
                "clinical_note": "Patient has diabetes."
            }
            return test_client.post("/rcm-api/getAISuggested_ICDCodes", json=payload)
        
        # Make 3 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [f.result() for f in futures]
        
        # All should complete successfully
        assert len(responses) == 3
        assert all(r.status_code == 200 for r in responses)
        
        print("✓ Concurrent requests handled successfully")
