"""
API routes for Use Case 1 pipeline and RAG ingestion/query.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel

from app.services.pipeline.usecase1_pipeline import UseCase1Pipeline
from app.services.orchestrator.enhanced_orchestrator import EnhancedMedicalCodingOrchestrator
from app.services.rag.chroma_store import ChromaVectorStore


router = APIRouter(prefix="/api/v1/uc1", tags=["usecase1"])


class PipelineRequest(BaseModel):
    """Enhanced pipeline request with all parameters."""
    csv_path: Optional[str] = None
    hl7_text: Optional[str] = None
    clinical_notes: Optional[str] = None
    manual_codes: Optional[Dict[str, Any]] = None
    setting: str = "Outpatient"
    specialty: str = "General Practice"
    payer_type: str = "Commercial"
    enable_parallel: bool = True
    confidence_threshold: float = 0.85


@router.post("/pipeline/run")
async def run_pipeline(request: PipelineRequest):
    """
    Execute enhanced medical coding validation pipeline.
    
    Features:
    - Parallel agent execution for faster processing
    - RAG-integrated validation against medical coding guidelines
    - Multi-stage validation (code accuracy, medical necessity, compliance)
    - Executive summary with financial impact and priority actions
    - Automated approval decision with confidence scoring
    """
    try:
        orchestrator = EnhancedMedicalCodingOrchestrator()
        result = await orchestrator.execute_pipeline(
            csv_path=request.csv_path,
            hl7_text=request.hl7_text,
            clinical_notes=request.clinical_notes,
            manual_codes=request.manual_codes,
            setting=request.setting,
            specialty=request.specialty,
            payer_type=request.payer_type,
            enable_parallel=request.enable_parallel,
            confidence_threshold=request.confidence_threshold
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/run/simple")
async def run_simple_pipeline(csv_path: Optional[str] = None, hl7_text: Optional[str] = None, manual_icd: Optional[list] = None, manual_cpt: Optional[list] = None):
    """
    Simple pipeline execution (legacy endpoint for backward compatibility).
    """
    try:
        pipe = UseCase1Pipeline()
        result = await pipe.run(csv_path=csv_path, hl7_text=hl7_text, manual_codes={"icd": manual_icd or [], "cpt": manual_cpt or []})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rag/ingest")
async def rag_ingest(directory: Optional[str] = None):
    try:
        store = ChromaVectorStore()
        count = await store.ingest_directory(directory)
        return {"ingested": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag/search")
async def rag_search(q: str, k: int = 5):
    try:
        store = ChromaVectorStore()
        results = await store.query(q, k)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


