"""
ICDToCPTAgent: Given ICD-10 list, propose CPT/HCPCS codes with probabilities.
"""
from __future__ import annotations

from typing import Dict, Any

from .base_agent import BaseAgent
from app.utils.llm import LLMClient


class ICDToCPTAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="icd_to_cpt")
        self.llm = LLMClient()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data and input_data.get("icd_list"))

    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        icd_list = input_data.get("icd_list")
        prompt = f"""
You are a certified medical coder. Given ICD-10 codes, propose up to 10 CPT/HCPCS procedure codes.
Include a probability 0-1 for each suggestion and short rationale.

ICD10: {icd_list}

Return strictly JSON list: [{{"code":"CPT/HCPCS","prob":0.0,"rationale":"..."}}]
"""
        text = await self.llm.chat([{"role": "user", "content": prompt}])
        return {"cpt_suggestions": text}


