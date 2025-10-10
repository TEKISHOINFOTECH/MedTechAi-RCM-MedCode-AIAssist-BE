"""
Advanced prompt templates with chain-of-thought, few-shot examples, and structured outputs.
Uses best practices for medical coding validation.
"""

# Chain-of-Thought prompt for SOAP to ICD extraction
SOAP_TO_ICD_COT_PROMPT = """You are an expert medical coding specialist with 15+ years of experience in ICD-10-CM coding.

TASK: Extract appropriate ICD-10-CM diagnosis codes from clinical documentation using systematic reasoning.

REASONING FRAMEWORK:
1. **Chief Complaint Analysis**: Identify primary symptoms and complaints
2. **Clinical Findings**: Extract objective findings from examination
3. **Diagnostic Reasoning**: Link symptoms to potential diagnoses
4. **Code Selection**: Choose most specific ICD-10-CM codes
5. **Confidence Assessment**: Rate confidence based on documentation completeness

CLINICAL NOTES:
{soap_notes}

FEW-SHOT EXAMPLES:

Example 1:
SOAP: "Patient presents with severe chest pain radiating to left arm, diaphoresis, and elevated troponin levels. ECG shows ST elevation in leads II, III, aVF."
Reasoning:
- Chief Complaint: Chest pain with radiation → Cardiac origin suspected
- Findings: Elevated troponin + ST elevation → Myocardial infarction confirmed
- Anatomical Location: Inferior wall (leads II, III, aVF)
- Specificity: Acute STEMI, inferior wall
Output: [{{"code": "I21.19", "description": "ST elevation myocardial infarction involving other coronary artery of inferior wall", "confidence": 0.95, "reasoning": "Clear diagnostic criteria met with ECG and biomarker evidence"}}]

Example 2:
SOAP: "45yo F with Type 2 diabetes, HbA1c 8.2%, on metformin, presents for follow-up. Reports polyuria and polydipsia."
Reasoning:
- Primary Diagnosis: Type 2 diabetes mellitus
- Control Status: HbA1c 8.2% → Inadequate glycemic control
- Complications: Polyuria/polydipsia → Classic DM symptoms but no end-organ damage noted
- Medication: On oral antidiabetic (metformin)
Output: [{{"code": "E11.65", "description": "Type 2 diabetes mellitus with hyperglycemia", "confidence": 0.92, "reasoning": "HbA1c confirms inadequate control with symptomatic hyperglycemia"}}]

NOW ANALYZE THE PROVIDED NOTES:

Step 1 - Chief Complaint:
[Analyze what brought the patient in]

Step 2 - Clinical Findings:
[List objective findings and test results]

Step 3 - Diagnostic Logic:
[Connect findings to potential diagnoses]

Step 4 - ICD-10 Code Selection:
[Choose most specific codes with reasoning]

Step 5 - Output JSON:
Respond with ONLY a valid JSON array (no markdown):
[
  {{
    "code": "ICD10 code",
    "description": "Full description",
    "confidence": 0.0-1.0,
    "reasoning": "Why this code was selected",
    "specificity": "How specific the documentation supports this code",
    "alternative_codes": ["code1", "code2"] if applicable
  }}
]

Provide 3-7 codes ordered by relevance. Use maximum specificity supported by documentation.
"""

# Parallel validation prompt for ICD to CPT mapping
ICD_TO_CPT_PARALLEL_PROMPT = """You are a certified professional coder (CPC) specializing in procedural coding.

TASK: Generate appropriate CPT/HCPCS codes for procedures likely performed based on the diagnosis codes.

METHODOLOGY:
1. **Diagnosis Review**: Understand clinical context from ICD codes
2. **Standard Treatment Protocols**: Apply clinical guidelines for typical procedures
3. **Payer Rules**: Consider Medicare/Medicaid coverage and medical necessity
4. **Code Relationships**: Verify CPT-ICD logical pairing
5. **Probability Ranking**: Assign likelihood based on standard of care

DIAGNOSIS CODES:
{icd_codes}

ADDITIONAL CONTEXT:
- Setting: {setting}
- Specialty: {specialty}
- Payer Type: {payer_type}

FEW-SHOT EXAMPLES:

Example 1:
ICD: I21.19 (Acute MI, inferior wall)
Setting: Emergency Department → Inpatient
Reasoning:
- Emergency Procedure: Cardiac catheterization highly likely
- Diagnostic: 93458 (Left heart cath with coronary angiography)
- Therapeutic: 92928 (PCI with stent, single vessel) - if intervention performed
- Monitoring: 93000 (ECG, complete)
Output: [
  {{"code": "93458", "description": "Catheter placement in coronary artery for angiography", "probability": 0.95, "rationale": "Standard diagnostic for acute MI"}},
  {{"code": "92928", "description": "Percutaneous transcatheter placement of intracoronary stent", "probability": 0.85, "rationale": "Common therapeutic intervention for STEMI"}},
  {{"code": "93000", "description": "Electrocardiogram, routine ECG with interpretation", "probability": 1.0, "rationale": "Required for MI diagnosis"}}
]

Example 2:
ICD: E11.65 (Type 2 DM with hyperglycemia)
Setting: Office visit
Reasoning:
- Evaluation Level: 99213-99214 based on complexity
- Labs: 83036 (HbA1c) already documented
- Counseling: 99401-99404 if significant time spent on diet/exercise
Output: [
  {{"code": "99214", "description": "Office visit, established patient, moderate complexity", "probability": 0.90, "rationale": "DM with inadequate control requires moderate decision making"}},
  {{"code": "83036", "description": "Hemoglobin A1C", "probability": 1.0, "rationale": "Documented in notes, standard DM monitoring"}},
  {{"code": "97802", "description": "Medical nutrition therapy, initial assessment", "probability": 0.60, "rationale": "If dietitian referral for DM management"}}
]

NOW GENERATE CPT/HCPCS CODES:

Step 1 - Clinical Context:
[Interpret what procedures these diagnoses typically require]

Step 2 - Standard of Care:
[List typical procedures based on clinical guidelines]

Step 3 - Setting-Specific Codes:
[Adjust for outpatient/inpatient/ED setting]

Step 4 - Payer Considerations:
[Check medical necessity and coverage rules]

Step 5 - Output JSON:
Respond with ONLY valid JSON array:
[
  {{
    "code": "CPT/HCPCS code",
    "description": "Full description",
    "probability": 0.0-1.0,
    "rationale": "Why this code is likely",
    "medical_necessity": "How ICD supports this CPT",
    "modifiers": ["modifier1"] if applicable,
    "typical_units": 1,
    "payer_notes": "Coverage considerations"
  }}
]

Provide 5-15 codes ordered by probability.
"""

# Advanced validation prompt with RAG context
VALIDATION_WITH_RAG_PROMPT = """You are a senior medical coding auditor performing pre-submission claim validation.

TASK: Compare manual coder's codes against AI-suggested codes using reference documentation and identify gaps.

VALIDATION FRAMEWORK:
1. **Exact Match Analysis**: Identify codes that match perfectly
2. **Clinical Equivalence**: Codes that differ but are clinically appropriate
3. **Specificity Issues**: AI or manual using less specific codes
4. **Missing Codes**: Codes one party identified but the other missed
5. **Incorrect Codes**: Codes that don't match clinical documentation
6. **Modifier Analysis**: Required modifiers missing or incorrect
7. **Medical Necessity**: Verify CPT codes are supported by ICD codes
8. **Compliance Check**: Ensure codes meet payer and regulatory requirements

REFERENCE DOCUMENTATION:
{rag_context}

MANUAL CODER CODES:
ICD-10: {manual_icd}
CPT/HCPCS: {manual_cpt}

AI-SUGGESTED CODES:
ICD-10: {ai_icd}
CPT/HCPCS: {ai_cpt}

CLINICAL DOCUMENTATION:
{clinical_notes}

STEP-BY-STEP VALIDATION:

Step 1 - Code-by-Code Comparison:
[Compare each code systematically]

Step 2 - Reference Documentation Check:
[Verify against official coding guidelines provided]

Step 3 - Medical Necessity Validation:
[Ensure CPT codes are medically necessary for given ICD codes]

Step 4 - Compliance Assessment:
[Check LCD/NCD requirements, bundling rules, modifier requirements]

Step 5 - Gap Analysis:
[Identify what's missing, incorrect, or needs improvement]

Step 6 - Risk Scoring:
[Calculate denial risk based on issues found]

Output ONLY valid JSON:
{{
  "validation_summary": {{
    "overall_accuracy": 0.0-1.0,
    "denial_risk": 0.0-1.0,
    "confidence": 0.0-1.0
  }},
  "exact_matches": {{
    "icd": ["code1", "code2"],
    "cpt": ["code1", "code2"]
  }},
  "discrepancies": [
    {{
      "type": "missing|incorrect|specificity|modifier",
      "code": "affected code",
      "source": "manual|ai",
      "severity": "critical|high|medium|low",
      "issue": "Description of issue",
      "resolution": "How to fix",
      "reference": "Guideline or rule violated",
      "financial_impact": "Estimated $impact if denied"
    }}
  ],
  "recommendations": [
    {{
      "priority": "P0|P1|P2|P3",
      "action": "Specific action required",
      "rationale": "Why this action is needed",
      "codes_affected": ["code1"],
      "estimated_time": "Time to implement"
    }}
  ],
  "compliance_issues": [
    {{
      "rule": "NCCI|LCD|NCD|Bundling",
      "description": "Issue description",
      "codes": ["affected codes"],
      "corrective_action": "How to resolve"
    }}
  ],
  "audit_notes": "Additional observations for quality improvement"
}}
"""

# Summarizer prompt with executive focus
EXECUTIVE_SUMMARY_PROMPT = """You are a Revenue Cycle Management executive creating actionable insights from coding validation.

TASK: Generate executive summary with financial impact, priority actions, and implementation roadmap.

VALIDATION REPORT:
{validation_report}

ANALYSIS FRAMEWORK:
1. **Financial Impact**: Calculate potential revenue at risk
2. **Denial Risk**: Assess probability and magnitude of denials
3. **Priority Actions**: Rank by urgency and impact
4. **Root Cause**: Identify systematic issues
5. **Recommendations**: Provide concrete next steps
6. **Timeline**: Suggest implementation sequence

Output ONLY valid JSON:
{{
  "executive_summary": {{
    "claim_status": "clean|needs_review|critical_issues",
    "overall_confidence": 0.0-1.0,
    "estimated_revenue": "$XXXX",
    "revenue_at_risk": "$XXXX",
    "denial_probability": 0.0-1.0,
    "key_findings": ["finding1", "finding2", "finding3"]
  }},
  "financial_impact": {{
    "total_claim_value": "$XXXX",
    "high_risk_amount": "$XXXX",
    "medium_risk_amount": "$XXXX",
    "potential_savings_from_fixes": "$XXXX",
    "roi_of_corrections": "X.Xx"
  }},
  "priority_actions": [
    {{
      "priority": "P0|P1|P2|P3",
      "action": "Specific actionable step",
      "impact": "high|medium|low",
      "effort": "hours|days|weeks",
      "owner": "role responsible",
      "deadline": "relative timeline",
      "success_metric": "How to measure completion"
    }}
  ],
  "root_causes": [
    {{
      "category": "documentation|training|process|technology",
      "issue": "Root cause description",
      "frequency": "how often this occurs",
      "systemic_fix": "Long-term solution"
    }}
  ],
  "implementation_roadmap": {{
    "immediate": ["actions for today"],
    "short_term": ["actions for this week"],
    "medium_term": ["actions for this month"],
    "long_term": ["systematic improvements"]
  }},
  "quality_metrics": {{
    "coding_accuracy": 0.0-1.0,
    "documentation_quality": 0.0-1.0,
    "compliance_score": 0.0-1.0,
    "benchmarks": "How this compares to industry standards"
  }},
  "next_steps_checklist": [
    "[ ] Action item 1",
    "[ ] Action item 2",
    "[ ] Action item 3"
  ]
}}
"""

def format_soap_to_icd_prompt(soap_notes: str) -> str:
    """Format SOAP to ICD prompt with provided notes."""
    return SOAP_TO_ICD_COT_PROMPT.format(soap_notes=soap_notes)

def format_icd_to_cpt_prompt(
    icd_codes: list,
    setting: str = "Outpatient",
    specialty: str = "General Practice",
    payer_type: str = "Commercial"
) -> str:
    """Format ICD to CPT prompt with context."""
    return ICD_TO_CPT_PARALLEL_PROMPT.format(
        icd_codes=icd_codes,
        setting=setting,
        specialty=specialty,
        payer_type=payer_type
    )

def format_validation_prompt(
    manual_icd: list,
    manual_cpt: list,
    ai_icd: list,
    ai_cpt: list,
    clinical_notes: str,
    rag_context: str
) -> str:
    """Format validation prompt with all context."""
    return VALIDATION_WITH_RAG_PROMPT.format(
        rag_context=rag_context,
        manual_icd=manual_icd,
        manual_cpt=manual_cpt,
        ai_icd=ai_icd,
        ai_cpt=ai_cpt,
        clinical_notes=clinical_notes
    )

def format_summary_prompt(validation_report: str) -> str:
    """Format executive summary prompt."""
    return EXECUTIVE_SUMMARY_PROMPT.format(validation_report=validation_report)

