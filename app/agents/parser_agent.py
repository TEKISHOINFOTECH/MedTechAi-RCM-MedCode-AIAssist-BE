"""
ParserAgent: parses HL7/CSV claim files and extracts SOAP notes and metadata.

For now we implement a CSV/HL7-lite parser stub that extracts columns or
segments resembling clinical notes and encounter metadata.
"""
from __future__ import annotations

import csv
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent


class ParserAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="parser_agent")

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return bool(input_data and (input_data.get("csv_path") or input_data.get("hl7_text")))

    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        if not self.validate_input(input_data):
            raise ValueError("csv_path or hl7_text required")

        if input_data.get("csv_path"):
            return await self._parse_csv(input_data["csv_path"])

        return await self._parse_hl7(input_data.get("hl7_text", ""))

    async def _parse_csv(self, path: str) -> Dict[str, Any]:
        soap_notes: List[str] = []
        rows: List[Dict[str, Any]] = []
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
                note = r.get("soap") or r.get("clinical_notes") or r.get("notes") or ""
                if note:
                    soap_notes.append(note)

        return {"soap_notes": "\n\n".join(soap_notes), "rows": rows}

    async def _parse_hl7(self, hl7_text: str) -> Dict[str, Any]:
        # Minimal HL7 segment splitting to find OBX/PRB/AL1/EVN that may contain notes
        notes: List[str] = []
        for line in hl7_text.splitlines():
            if line.startswith("OBX|") or line.startswith("NTE|"):
                parts = line.split("|")
                if len(parts) > 5:
                    notes.append(parts[-1])
        return {"soap_notes": "\n".join(notes), "segments": len(hl7_text.splitlines())}


