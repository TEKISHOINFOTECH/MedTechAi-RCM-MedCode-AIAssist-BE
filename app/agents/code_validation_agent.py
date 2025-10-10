"""
CodeValidationAgent: compares AI-suggested codes with manual coder's codes and validates via rules.
"""
from __future__ import annotations

import json
from typing import Dict, Any, List

from .base_agent import BaseAgent
from app.utils.llm import LLMClient


class CodeValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="code_validation")
        self.llm = LLMClient()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data and input_data.get("manual_codes") is not None and input_data.get("ai_codes") is not None)

    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        manual_codes = input_data.get("manual_codes")  # {"icd":[], "cpt":[]}
        ai_codes = input_data.get("ai_codes")          # same shape or JSON strings

        prompt = f"""
You are a senior RCM auditor. Compare manual coder codes versus AI suggestions. Identify matches, mismatches,
missing modifiers, payer constraints, and provide a gap analysis with corrective actions. Respond as JSON object with keys:
{{
  "matches": {{"icd":[], "cpt":[]}},
  "mismatches": {{"icd":[], "cpt":[]}},
  "missing_modifiers": [],
  "risk_assessment": {{"overall": 0-1, "reasons": []}},
  "actions": ["..."],
  "notes": "..."
}}

Manual: {manual_codes}
AI: {ai_codes}
"""
        text = await self.llm.chat([{"role": "user", "content": prompt}], temperature=0.0)
        return {"validation_report": text}


