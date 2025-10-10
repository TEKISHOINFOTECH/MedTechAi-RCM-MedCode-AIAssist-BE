"""
SummarizerAgent: produces an executive summary and action plan from validation report.
"""
from __future__ import annotations

from typing import Dict, Any

from .base_agent import BaseAgent
from app.utils.llm import LLMClient


class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="summarizer_agent")
        self.llm = LLMClient()

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data and input_data.get("validation_report"))

    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        prompt = f"""
Create a concise executive summary and actionable steps from the following validation report. Include: impact estimate,
priority actions (P1/P2/P3), and next steps checklist.

Report:\n{input_data.get('validation_report')}

Return JSON: {{"summary": "...", "impact": "...", "priority_actions": ["..."], "checklist": ["..."]}}
"""
        text = await self.llm.chat([{"role": "user", "content": prompt}], temperature=0.2)
        return {"summary": text}


