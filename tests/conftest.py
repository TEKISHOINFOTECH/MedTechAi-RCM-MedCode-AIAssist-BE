"""
Pytest configuration and shared fixtures for integration tests.
"""
import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from pathlib import Path

from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from config import settings


# Configure async event loop for pytest
@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def test_client() -> TestClient:
    """Synchronous test client for FastAPI."""
    return TestClient(app)


@pytest.fixture(scope="module")
async def async_client() -> AsyncGenerator:
    """Asynchronous test client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_soap_notes() -> str:
    """Sample clinical notes for testing."""
    return """
CHIEF COMPLAINT: Chest pain

SUBJECTIVE:
67-year-old male presents to ED with severe substernal chest pain radiating to left arm.
Pain started 2 hours ago while mowing lawn. Associated with diaphoresis and shortness of breath.
Patient denies nausea or vomiting. History of hypertension and hyperlipidemia.

OBJECTIVE:
Vitals: BP 156/92, HR 98, RR 22, O2 Sat 94% on RA, Temp 98.6F
Physical exam: Anxious appearing, diaphoretic. Heart exam reveals regular rate and rhythm, no murmurs.
Lungs clear bilaterally. No lower extremity edema.

ECG: ST elevation in leads II, III, aVF (2-3mm)
Troponin I: 4.8 ng/mL (elevated)
BNP: 180 pg/mL
CBC: WNL
CMP: Creatinine 1.1, otherwise normal

ASSESSMENT:
1. Acute ST-elevation myocardial infarction (STEMI), inferior wall
2. Hypertension, uncontrolled
3. Hyperlipidemia

PLAN:
1. Activate cath lab for emergent cardiac catheterization
2. Aspirin 325mg, Plavix 600mg loading dose
3. Heparin drip
4. Admit to CCU
5. Cardiology consult
"""


@pytest.fixture(scope="session")
def sample_manual_codes() -> dict:
    """Sample manual coder codes for comparison."""
    return {
        "icd": [
            {"code": "I21.19", "description": "STEMI involving other coronary artery of inferior wall"},
            {"code": "I10", "description": "Essential hypertension"},
            {"code": "E78.5", "description": "Hyperlipidemia, unspecified"}
        ],
        "cpt": [
            {"code": "99285", "description": "Emergency department visit, high complexity"},
            {"code": "93010", "description": "Electrocardiogram, routine ECG"},
            {"code": "83036", "description": "Hemoglobin; glycosylated (A1C)"},
            {"code": "93458", "description": "Catheter placement in coronary artery for angiography"}
        ]
    }


@pytest.fixture(scope="session")
def check_openai_key() -> bool:
    """Check if OpenAI API key is configured."""
    return bool(os.getenv("OPENAI_API_KEY") or settings.openai_api_key)


@pytest.fixture(scope="session")
def check_google_key() -> bool:
    """Check if Google API key is configured."""
    return bool(os.getenv("GOOGLE_API_KEY") or settings.google_api_key)


@pytest.fixture(scope="session")
def check_anthropic_key() -> bool:
    """Check if Anthropic API key is configured."""
    return bool(os.getenv("ANTHROPIC_API_KEY") or settings.anthropic_api_key)


# Test data samples
@pytest.fixture
def sample_csv_data(test_data_dir: Path) -> Path:
    """Create sample CSV file for testing."""
    csv_path = test_data_dir / "sample_claims.csv"
    csv_path.parent.mkdir(exist_ok=True)
    
    csv_content = """claim_id,patient_id,soap,provider,date_of_service
CLM001,PAT12345,"Patient with chest pain, elevated troponin, ST elevation",Dr. Smith,2024-01-15
CLM002,PAT67890,"Type 2 diabetes follow-up, HbA1c 8.2%",Dr. Jones,2024-01-16
"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_hl7_message() -> str:
    """Sample HL7 message for testing."""
    return """MSH|^~\\&|EPIC|EPICADT|SMS|SMSADT|199912271408|CHARRIS|ADT^A04|1817457|D|2.5|
PID||0493575^^^2^ID 1|454721||DOE^JOHN^^^^|DOE^JOHN^^^^|19480203|M||B|254 MYSTREET AVE^^MYTOWN^OH^44123^USA||(216)123-4567|||M|NON|400003403~1129086|
NK1||ROE^MARIE^^^^|SPO||(216)123-4567||EC|||||||||||||||||||||||||||
PV1||O|168 ~219~C~PMA^^^^^^^^^||||277^ALLEN^BONNIE^^^^|||||||||| ||2688684|||||||||||||||||||||||||199912271408||||||002376853
OBX|1|NM|^Body Height||1.80|m^Meter^ISO+|||||F
OBX|2|NM|^Body Weight||79|kg^Kilogram^ISO+|||||F
NTE|1||Chest pain with radiation to left arm
NTE|2||ST elevation in inferior leads
NTE|3||Elevated troponin consistent with acute MI
"""


# Marker for tests requiring external services
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring external services"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "llm: mark test as requiring LLM API access"
    )
    config.addinivalue_line(
        "markers", "rag: mark test as requiring vector database"
    )

