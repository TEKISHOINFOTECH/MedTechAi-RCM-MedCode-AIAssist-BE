#!/usr/bin/env python3
"""
Test script for UAE Health System integration with MedTechAi RCM.
"""

import asyncio
import json
import requests
from pathlib import Path


async def test_uae_health_parsing():
    """Test UAE health XML parsing."""
    print("🇦🇪 Testing UAE Health System Integration")
    print("=" * 50)
    
    # Load sample XML
    xml_content = Path("sample_uae_claim.xml").read_text()
    print(f"✅ Loaded sample XML ({len(xml_content)} characters)")
    
    # Test API endpoint
    try:
        print("\n🧪 Testing /api/v1/uae-health/parse endpoint...")
        
        response = requests.post(
            "http://localhost:8000/api/v1/uae-health/parse",
            json={
                "xml_content": xml_content,
                "parse_options": {"validate_emirates_id": True}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ XML parsing successful!")
            
            # Display results
            summary = data["data"]["claims_summary"]
            medical_codes = data["data"]["medical_codes"]
            
            print(f"📋 Claims Summary:")
            print(f"  - Source: {summary['source']}")
            print(f"  - Receiver: {summary['receiver']}")
            print(f"  - Total Claims: {summary['total_claims']}")
            print(f"  - Total Gross: AED {summary['total_gross_amount']}")
            print(f"  - Total Net: AED {summary['total_net_amount']}")
            
            print(f"\n🏥 Medical Codes:")
            print(f"  - ICD Codes ({medical_codes['unique_icd_count']}): {medical_codes['icd_codes']}")
            print(f"  - CPT Codes ({medical_codes['unique_cpt_count']}): {medical_codes['cpt_codes']}")
            
            return data
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing parsing: {e}")
        return None


async def test_uae_medical_coding():
    """Test UAE health medical coding validation."""
    print("\n🤖 Testing UAE Medical Coding Validation...")
    
    try:
        # Load sample XML
        xml_content = Path("sample_uae_claim.xml").read_text()
        
        response = requests.post(
            "http://localhost:8000/api/v1/uae-health/medical-coding",
            json={
                "xml_content": xml_content,
                "payer_id": "PAYER_SAMPLE",
                "provider_id": "PROV_SAMPLE"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Medical coding validation successful!")
            
            # Display AI validation results
            ai_validation = data["data"]["ai_validation"]
            
            print(f"\n🎯 AI Validation Results:")
            print(f"  - ICD Suggestions: {len(ai_validation.get('icd', []))}")
            print(f"  - CPT Suggestions: {len(ai_validation.get('cpt', []))}")
            
            if ai_validation.get("validation"):
                print(f"  - Validation Status: {ai_validation['validation'].get('status', 'Unknown')}")
            
            # Show recommendations if available
            if ai_validation.get("summary"):
                summary_text = ai_validation["summary"].get("summary", "")
                if summary_text:
                    print(f"  - AI Summary: {summary_text[:200]}...")
            
            return data
            
        else:
            print(f"❌ Medical coding validation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing medical coding: {e}")
        return None


async def test_uae_validation():
    """Test UAE-specific validation rules."""
    print("\n🔍 Testing UAE Health Validation Rules...")
    
    try:
        # Use sample data endpoint first
        response = requests.get("http://localhost:8000/api/v1/uae-health/sample-data")
        
        if response.status_code == 200:
            sample_data = response.json()
            xml_content = sample_data["xml_content"]
            
            print("✅ Loaded sample data for validation testing")
            
            # Parse first to get structured data
            parse_response = requests.post(
                "http://localhost:8000/api/v1/uae-health/parse",
                json={"xml_content": xml_content}
            )
            
            if parse_response.status_code == 200:
                parsed_data = parse_response.json()
                
                # Now validate
                validation_response = requests.post(
                    "http://localhost:8000/api/v1/uae-health/validate",
                    json={
                        "submission_data": parsed_data["data"]["parsed_submission"],
                        "validation_level": "comprehensive"
                    }
                )
                
                if validation_response.status_code == 200:
                    validation_data = validation_response.json()
                    print("✅ UAE validation rules successful!")
                    
                    # Display validation results
                    validation_results = validation_data["validation_results"]
                    overall_status = validation_data["validation_status"]
                    
                    print(f"📊 Overall Status: {overall_status}")
                    
                    # Check Emirates ID validation
                    emirates_check = validation_results.get("emirates_id_validation", {})
                    print(f"🆔 Emirates IDs: {emirates_check.get('valid_emirates_ids', 0)}/{emirates_check.get('total_claims', 0)} valid")
                    
                    # Check financial validation
                    financial_check = validation_results.get("financial_validation", {})
                    print(f"💰 Financial: {financial_check.get('consistent_calculations', 0)}/{financial_check.get('total_claims', 0)} consistent")
                    
                    # Check credentials
                    credential_check = validation_results.get("dha_credential_validation", {})
                    print(f"🏥 DHA Credentials: {credential_check.get('valid_credentials', 0)}/{credential_check.get('total_activities', 0)} valid")
                    
                    return validation_data
                    
                else:
                    print(f"❌ Validation failed: {validation_response.status_code}")
                    return None
            else:
                print(f"❌ Parsing for validation failed: {parse_response.status_code}")
                return None
        else:
            print(f"❌ Sample data request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing validation: {e}")
        return None


async def test_api_health():
    """Test API health endpoints."""
    print("\n🏥 Testing API Health...")
    
    try:
        # Test main health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Main API health check passed")
        
        # Test UAE health specific health endpoint
        response = requests.get("http://localhost:8000/api/v1/uae-health/health")
        if response.status_code == 200:
            health_data = response.json()
            print("✅ UAE Health API health check passed")
            endpoints = health_data.get("endpoints", [])
            capabilities = health_data.get("capabilities", [])
            print(f"   📡 Available endpoints: {len(endpoints)}")
            print(f"   🎯 Capabilities: {len(capabilities)}")
            
            return True
        else:
            print(f"❌ UAE Health API health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


async def main():
    """Run all UAE health integration tests."""
    print("🚀 Starting UAE Health System Integration Tests")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend API not running on localhost:8000")
            print("   Please start the backend with: uv run python main.py")
            return
    except requests.exceptions.RequestException:
        print("❌ Backend API not running on localhost:8000")
        print("   Please start the backend with: uv run python main.py")
        return
    
    print("✅ Backend API is running")
    
    # Run tests
    tests = [
        ("API Health Check", test_api_health()),
        ("UAE Health Parsing", test_uae_health_parsing()),
        ("UAE Medical Coding", test_uae_medical_coding()),
        ("UAE Validation Rules", test_uae_validation()),
    ]
    
    results = {}
    
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results[test_name] = result is not None
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_status in results.items():
        status = "✅ PASS" if passed_status else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! UAE Health integration is working correctly!")
        print("\n🔗 You can now test via:")
        print("   - Streamdit UI: http://localhost:8501")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - UAE Health endpoints: http://localhost:8000/api/v1/uae-health/")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Check the output above for details.")
    
    print("\n📝 Sample usage:")
    print("   curl -X POST http://localhost:8000/api/v1/uae-health/parse \\")
    print("          -H 'Content-Type: application/json' \\")
    print("          -d '{\"xml_content\": \"$(cat sample_uae_claim.xml)\"}'")
    

if __name__ == "__main__":
    asyncio.run(main())

