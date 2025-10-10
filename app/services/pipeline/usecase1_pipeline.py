"""
Use Case 1 Pipeline: Coding & Documentation validation flow.

Steps:
1) ParserAgent -> extract SOAP from EDI/HL7/CSV
2) NoteToICDAgent -> propose ICD codes
3) ICDToCPTAgent -> propose CPT/HCPCS from ICD
4) CodeValidationAgent -> compare AI vs manual coder codes
5) SummarizerAgent -> executive summary & actions
"""
from __future__ import annotations

import json
from typing import Dict, Any

from app.agents.parser_agent import ParserAgent
from app.agents.note_to_icd_agent import NoteToICDAgent
from app.agents.icd_to_cpt_agent import ICDToCPTAgent
from app.agents.code_validation_agent import CodeValidationAgent
from app.agents.summarizer_agent import SummarizerAgent


class UseCase1Pipeline:
    def __init__(self):
        self.parser = ParserAgent()
        self.note_to_icd = NoteToICDAgent()
        self.icd_to_cpt = ICDToCPTAgent()
        self.validator = CodeValidationAgent()
        self.summarizer = SummarizerAgent()

    async def run(
        self,
        *,
        csv_path: str | None = None,
        hl7_text: str | None = None,
        manual_codes: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Execute pipeline and return structured result."""
        # 1) Parse
        parsed = await self.parser.process({"csv_path": csv_path, "hl7_text": hl7_text})
        soap = parsed.get("soap_notes", "")

        # 2) Notes -> ICD
        icd_raw = await self.note_to_icd.process({"soap_notes": soap})
        icd_text = icd_raw.get("icd_suggestions", "[]")

        # Attempt JSON parse (lenient)
        try:
            icd_list = json.loads(icd_text)
        except Exception:
            icd_list = []

        # 3) ICD -> CPT
        cpt_raw = await self.icd_to_cpt.process({"icd_list": icd_list})
        cpt_text = cpt_raw.get("cpt_suggestions", "[]")
        try:
            cpt_list = json.loads(cpt_text)
        except Exception:
            cpt_list = []

        # 4) Validation vs manual
        manual = manual_codes or {"icd": [], "cpt": []}
        validation = await self.validator.process({"manual_codes": manual, "ai_codes": {"icd": icd_list, "cpt": cpt_list}})

        # 5) Summarize
        summary = await self.summarizer.process({"validation_report": validation.get("validation_report", "")})

        return {
            "parsed": parsed,
            "icd": icd_list,
            "cpt": cpt_list,
            "validation": validation,
            "summary": summary,
        }


