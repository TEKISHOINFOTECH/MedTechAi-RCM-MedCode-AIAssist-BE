"""
NoteToICDAgent: takes SOAP/clinical notes and proposes ICD-10 codes.
"""
from __future__ import annotations

from typing import Dict, Any, List

from .base_agent import BaseAgent
from app.utils.llm import LLMClient
from app.models.medical_code import CodeType
from app.schemas.medical_code import MedicalCodeValidationRequest, MedicalCodeValidationResponse


class NoteToICDAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="note_to_icd")
        self.llm = LLMClient()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data and input_data.get("soap_notes"))

    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        prompt = f"""
You are a medical coding expert. From the SOAP/clinical notes below, extract top 5 ICD-10 codes with
short descriptions and confidence 0-1.

Notes:\n{input_data.get('soap_notes', '')}

Respond strictly as JSON list with objects:
[
  {{"code": "ICD10", "description": "...", "confidence": 0.0}}
]
"""
        text = await self.llm.chat([{"role": "user", "content": prompt}])
        # Return raw text; a higher layer can parse JSON robustly
        return {"icd_suggestions": text}


