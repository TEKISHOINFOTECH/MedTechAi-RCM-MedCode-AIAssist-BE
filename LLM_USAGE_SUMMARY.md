# 🤖 LLM Usage Summary - MedTechAI RCM

## Overview

This document details all LLM (Large Language Model) API calls being used in the MedTechAI RCM Medical Code Validation application.

---

## 🎯 LLM Providers Supported

| Provider | Status | Model | API Key Required |
|----------|--------|-------|------------------|
| **OpenAI** | ✅ Active | `gpt-4o-mini` (default) | `OPENAI_API_KEY` |
| **Anthropic** | 🟡 Configured | `claude-3-sonnet-20240229` | `ANTHROPIC_API_KEY` (optional) |
| **Google AI** | 🟡 Configured | `gemini-pro` | `GOOGLE_API_KEY` (optional) |

**Current Configuration**: Using **OpenAI GPT-4o-mini**

---

## 📊 LLM Call Locations

### 1. **Core LLM Client** (`app/utils/llm.py`)

**Purpose**: Unified abstraction layer for all LLM providers

**Functions**:
- `LLMClient.chat()` - Main chat completion interface
- `EmbeddingClient.embed()` - Generate embeddings for RAG

**Providers Supported**:
```python
# OpenAI
await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=2000
)

# Anthropic
await client.messages.create(
    model="claude-3-sonnet",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=2000
)

# Google AI
model.generate_content(prompt)
```

---

## 🔬 Agent LLM Usage

### 2. **ParserAgent** (`app/agents/parser_agent.py`)

**LLM Usage**: ❌ **No LLM calls**
- Pure parsing logic (CSV, HL7, PDF)
- Uses `unstructured` library for document parsing
- No AI required

---

### 3. **NoteToICDAgent** (`app/agents/note_to_icd_agent.py`)

**LLM Usage**: ✅ **1 LLM call per execution**

**Purpose**: Extract ICD-10 diagnosis codes from clinical SOAP notes

**Prompt Template**:
```
You are a medical coding expert. From the SOAP/clinical notes below, 
extract top 5 ICD-10 codes with short descriptions and confidence 0-1.

Notes: [clinical notes]

Respond strictly as JSON list with objects:
[
  {"code": "ICD10", "description": "...", "confidence": 0.0}
]
```

**LLM Settings**:
- Temperature: `0.1` (default from LLMClient)
- Max Tokens: `2000` (default)
- Model: `gpt-4o-mini` (configurable)

**Input**: Clinical SOAP notes
**Output**: JSON array of ICD-10 codes with confidence scores

**Example Call**:
```python
await self.llm.chat([{"role": "user", "content": prompt}])
```

---

### 4. **ICDToCPTAgent** (`app/agents/icd_to_cpt_agent.py`)

**LLM Usage**: ✅ **1 LLM call per execution**

**Purpose**: Suggest CPT/HCPCS procedure codes based on ICD-10 diagnosis codes

**Prompt Template**:
```
You are a certified medical coder. Given ICD-10 codes, propose up to 10 
CPT/HCPCS procedure codes. Include a probability 0-1 for each suggestion 
and short rationale.

ICD10: [list of ICD codes]

Return strictly JSON list: 
[{"code":"CPT/HCPCS","prob":0.0,"rationale":"..."}]
```

**LLM Settings**:
- Temperature: `0.1`
- Max Tokens: `2000`
- Model: `gpt-4o-mini`

**Input**: List of ICD-10 codes
**Output**: JSON array of CPT/HCPCS codes with probability and rationale

**Example Call**:
```python
await self.llm.chat([{"role": "user", "content": prompt}])
```

---

### 5. **CodeValidationAgent** (`app/agents/code_validation_agent.py`)

**LLM Usage**: ✅ **1 LLM call per execution**

**Purpose**: Compare AI-suggested codes vs manual coder codes, identify gaps

**Prompt Template**:
```
You are a senior RCM auditor. Compare manual coder codes versus AI suggestions. 
Identify matches, mismatches, missing modifiers, payer constraints, and provide 
a gap analysis with corrective actions. 

Respond as JSON object with keys:
{
  "matches": {"icd":[], "cpt":[]},
  "mismatches": {"icd":[], "cpt":[]},
  "missing_modifiers": [],
  "risk_assessment": {"overall": 0-1, "reasons": []},
  "actions": ["..."],
  "notes": "..."
}

Manual: [manual codes]
AI: [AI suggested codes]
```

**LLM Settings**:
- Temperature: `0.0` (deterministic validation)
- Max Tokens: `2000`
- Model: `gpt-4o-mini`

**Input**: Manual codes and AI-suggested codes
**Output**: JSON validation report with matches, mismatches, and actions

**Example Call**:
```python
await self.llm.chat([{"role": "user", "content": prompt}], temperature=0.0)
```

---

### 6. **SummarizerAgent** (`app/agents/summarizer_agent.py`)

**LLM Usage**: ✅ **1 LLM call per execution**

**Purpose**: Create executive summary and action plan from validation report

**Prompt Template**:
```
Create a concise executive summary and actionable steps from the following 
validation report. Include: impact estimate, priority actions (P1/P2/P3), 
and next steps checklist.

Report: [validation report]

Return JSON: 
{
  "summary": "...", 
  "impact": "...", 
  "priority_actions": ["..."], 
  "checklist": ["..."]
}
```

**LLM Settings**:
- Temperature: `0.2` (slightly creative for summaries)
- Max Tokens: `2000`
- Model: `gpt-4o-mini`

**Input**: Validation report
**Output**: JSON executive summary with action items

**Example Call**:
```python
await self.llm.chat([{"role": "user", "content": prompt}], temperature=0.2)
```

---

### 7. **MedicalCodeValidationAgent** (`app/agents/medical_validator.py`)

**LLM Usage**: ✅ **1 LLM call per validation request**

**Purpose**: Comprehensive medical code validation with context awareness

**Prompt Template**: Complex structured prompt with:
- Medical code details
- Patient context
- Provider information
- Insurance details
- Validation criteria

**LLM Settings**:
- Temperature: `0.1`
- Max Tokens: `1000`
- Provider: OpenAI or Anthropic

**Input**: `MedicalCodeValidationRequest` (Pydantic model)
**Output**: `MedicalCodeValidationResponse` with validation details

**Example Call**:
```python
# OpenAI
await self.client.chat.completions.create(
    model=self.model_name,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=1000
)

# Anthropic
await self.client.messages.create(
    model=self.model_name,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=1000
)
```

---

### 8. **ClaimProcessingAgent** (`app/agents/claim_processor.py`)

**LLM Usage**: ✅ **1 LLM call per claim analysis**

**Purpose**: Analyze insurance claims for denial risk and optimization

**Prompt Template**: Structured analysis prompt for:
- Denial risk assessment
- Medical necessity validation
- Code optimization
- Payer-specific rules

**LLM Settings**:
- Temperature: `0.1`
- Max Tokens: `2000`
- Provider: OpenAI or Anthropic

**Example Call**:
```python
await self.client.chat.completions.create(
    model=self.model_name,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    max_tokens=2000
)
```

---

### 9. **DenialAnalysisAgent** (`app/agents/denial_analyzer.py`)

**LLM Usage**: ✅ **1 LLM call per denial analysis**

**Purpose**: Analyze denied claims and suggest appeal strategies

**Prompt Template**: (From advanced prompts in `app/services/prompt_templates.py`)
- Root cause identification
- Appeal probability assessment
- Mitigation strategies
- Financial impact estimation

**LLM Settings**:
- Temperature: `0.1`
- Max Tokens: `2500`
- Model: `gpt-4o-mini`

---

### 10. **Enhanced Orchestrator** (`app/services/orchestrator/enhanced_orchestrator.py`)

**LLM Usage**: ✅ **Multiple LLM calls** (orchestrates other agents)

**Purpose**: Coordinate agent execution with advanced prompt engineering

**Features**:
- Chain-of-thought reasoning
- Few-shot learning examples
- RAG-enhanced prompts
- Parallel/sequential execution

**LLM Calls Made**:
1. ICD code extraction (via NoteToICDAgent)
2. CPT code suggestion (via ICDToCPTAgent)
3. Code validation (via CodeValidationAgent)
4. Medical necessity check (direct LLM call)
5. Compliance validation (direct LLM call)
6. Executive summary (via SummarizerAgent)

**Total LLM Calls per Pipeline**: **6-7 calls**

---

## 📈 LLM Usage Summary

### Per Pipeline Execution

| Stage | Agent | LLM Calls | Tokens (approx) | Purpose |
|-------|-------|-----------|-----------------|---------|
| 1. Parse | ParserAgent | 0 | 0 | Document parsing |
| 2. RAG Retrieval | - | 0 | 0 | Vector search |
| 3. ICD Extraction | NoteToICDAgent | 1 | ~500 | Generate ICD codes |
| 4. CPT Suggestion | ICDToCPTAgent | 1 | ~600 | Generate CPT codes |
| 5. Validation | CodeValidationAgent | 1 | ~800 | Compare codes |
| 6. Medical Necessity | Orchestrator | 1 | ~400 | Validate necessity |
| 7. Compliance Check | Orchestrator | 1 | ~400 | Check rules |
| 8. Summary | SummarizerAgent | 1 | ~600 | Executive summary |
| **TOTAL** | **Pipeline** | **6** | **~3,300** | **Full validation** |

### Token Estimation

**Per Pipeline Run**:
- Input tokens: ~2,000
- Output tokens: ~1,300
- **Total: ~3,300 tokens**

**Cost Estimate** (OpenAI GPT-4o-mini pricing):
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens
- **Cost per run**: ~$0.0011 (about 0.1 cents)

---

## 🔧 Configuration

### LLM Provider Settings

```python
# In .env file or config/settings.py

# Provider selection
LLM_PROVIDER=openai  # or anthropic, google
LLM_MODEL=gpt-4o-mini

# API Keys
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=...  # Optional
GOOGLE_API_KEY=...     # Optional

# Model parameters (defaults)
TEMPERATURE=0.1        # Low for deterministic results
MAX_TOKENS=2000        # Max response length
```

### Switching Providers

```python
# Use OpenAI (default)
llm = LLMClient(provider="openai", model="gpt-4o-mini")

# Use Anthropic Claude
llm = LLMClient(provider="anthropic", model="claude-3-sonnet-20240229")

# Use Google Gemini
llm = LLMClient(provider="google", model="gemini-pro")
```

---

## 🎯 LLM Call Flow

### Simple Pipeline (UseCase1Pipeline)

```
1. Input: Clinical notes
   ↓
2. NoteToICDAgent → LLM Call #1
   Prompt: Extract ICD codes from notes
   Output: ICD codes with confidence
   ↓
3. ICDToCPTAgent → LLM Call #2
   Prompt: Suggest CPT codes for ICD codes
   Output: CPT codes with probability
   ↓
4. CodeValidationAgent → LLM Call #3
   Prompt: Compare AI vs manual codes
   Output: Validation report
   ↓
5. SummarizerAgent → LLM Call #4
   Prompt: Create executive summary
   Output: Summary with action items
```

**Total LLM Calls**: 4

### Enhanced Pipeline (EnhancedOrchestrator)

```
1. Input: Clinical notes
   ↓
2. RAG Retrieval (no LLM)
   ↓
3. NoteToICDAgent (RAG-enhanced) → LLM Call #1
   ↓
4. ICDToCPTAgent (context-aware) → LLM Call #2
   ↓
5. Parallel Validation:
   - CodeValidationAgent → LLM Call #3
   - Medical Necessity Check → LLM Call #4
   - Compliance Check → LLM Call #5
   ↓
6. SummarizerAgent → LLM Call #6
```

**Total LLM Calls**: 6 (3 in parallel)

---

## 💰 Cost Analysis

### Monthly Cost Estimate

**Assumptions**:
- 1,000 pipeline runs per month
- Average 3,300 tokens per run
- Using GPT-4o-mini

**Calculation**:
```
Input tokens: 2,000,000 × $0.150/1M = $0.30
Output tokens: 1,300,000 × $0.600/1M = $0.78
Total per month: ~$1.08 for 1,000 runs
```

**Cost per claim**: ~$0.001 (0.1 cents)

### Alternative Models

| Model | Input $/1M | Output $/1M | Cost/Run | Monthly (1K runs) |
|-------|-----------|-------------|----------|-------------------|
| GPT-4o-mini | $0.150 | $0.600 | $0.0011 | $1.08 |
| GPT-4o | $2.50 | $10.00 | $0.018 | $18.00 |
| GPT-3.5-turbo | $0.50 | $1.50 | $0.003 | $2.95 |
| Claude Sonnet | $3.00 | $15.00 | $0.026 | $25.50 |

---

## 🔒 Security & Best Practices

### API Key Management

✅ **DO**:
- Store keys in `.env` file (already gitignored)
- Use environment variables in production
- Rotate keys regularly
- Use different keys for dev/staging/prod

❌ **DON'T**:
- Hardcode keys in source code
- Commit keys to git
- Share keys in public channels
- Use production keys in development

### Rate Limiting

Current implementation:
- No built-in rate limiting
- OpenAI tier limits apply:
  - Free tier: 3 RPM (requests per minute)
  - Paid tier: 3,500 RPM for GPT-4o-mini

**Recommendation**: Add rate limiting for production:
```python
from fastapi_limiter import FastAPILimiter

# Limit to 60 requests per minute per user
@limiter.limit("60/minute")
```

---

## 📊 Monitoring

### Track LLM Usage

Current logging (using structlog):
```python
logger.info("LLM call started", agent=agent_name, model=model)
logger.info("LLM call completed", tokens=tokens_used, time=processing_time)
```

### Metrics to Monitor

1. **Request Count**: Number of LLM calls per agent
2. **Token Usage**: Input/output tokens per call
3. **Latency**: Response time per call
4. **Error Rate**: Failed LLM calls
5. **Cost**: Estimated cost per call/day/month

---

## 🎓 Optimization Tips

### 1. Reduce Token Usage

- Use shorter prompts where possible
- Limit max_tokens for responses
- Cache common responses (not implemented yet)

### 2. Batch Requests

- Process multiple codes in one LLM call
- Use parallel execution (already implemented)

### 3. Smart Caching

- Cache ICD/CPT code mappings
- Store common validation results
- Use RAG for guidelines instead of prompting

### 4. Model Selection

- Use GPT-4o-mini for most tasks (cheaper)
- Use GPT-4o only for complex validations
- Consider GPT-3.5-turbo for simple tasks

---

## 📝 Summary

### LLM Integration Points

✅ **8 Agents using LLM**:
1. NoteToICDAgent
2. ICDToCPTAgent
3. CodeValidationAgent
4. SummarizerAgent
5. MedicalCodeValidationAgent
6. ClaimProcessingAgent
7. DenialAnalysisAgent
8. Enhanced Orchestrator (coordinates above)

✅ **1 Agent NOT using LLM**:
1. ParserAgent (pure document parsing)

### Current Status

- **Provider**: OpenAI GPT-4o-mini
- **Status**: ✅ Working and tested
- **Cost**: ~$0.001 per claim validation
- **Performance**: ~2-5 seconds per pipeline run

---

**Generated**: October 2, 2024  
**Last Updated**: October 2, 2024  
**Document Version**: 1.0

