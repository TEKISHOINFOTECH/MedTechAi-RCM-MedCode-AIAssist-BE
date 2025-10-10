# 🏗️ MedTechAI RCM - Architecture Diagrams (Mermaid)

This document contains comprehensive Mermaid diagrams for the entire backend agentic application.

---

## 📊 Table of Contents

1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Agent Workflow - Simple Pipeline](#2-agent-workflow---simple-pipeline)
3. [Agent Workflow - Enhanced Pipeline](#3-agent-workflow---enhanced-pipeline)
4. [LLM Integration Flow](#4-llm-integration-flow)
5. [RAG System Architecture](#5-rag-system-architecture)
6. [API Request Flow](#6-api-request-flow)
7. [Database Schema](#7-database-schema)
8. [Agent Class Hierarchy](#8-agent-class-hierarchy)
9. [Configuration Management](#9-configuration-management)
10. [Error Handling Flow](#10-error-handling-flow)

---

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        UI[Streamlit UI<br/>Port 8501]
        API_CLIENT[External API Clients]
    end
    
    subgraph "API Layer - FastAPI"
        HEALTH[health<br/>Health Check]
        ROOT[<br/>Root Endpoint]
        PIPELINE[api/v1/uc1/pipeline/run<br/>Enhanced Pipeline]
        SIMPLE[api/v1/uc1/pipeline/run/simple<br/>Simple Pipeline]
        RAG_INGEST[api/v1/uc1/rag/ingest<br/>Document Ingestion]
        RAG_SEARCH[api/v1/uc1/rag/search<br/>Semantic Search]
    end
    
    subgraph "Orchestration Layer"
        SIMPLE_ORCH[UseCase1Pipeline<br/>Simple Orchestrator]
        ENHANCED_ORCH[EnhancedOrchestrator<br/>Advanced Orchestration]
    end
    
    subgraph "Agent Layer"
        PARSER[ParserAgent<br/>Document Parsing]
        NOTE_ICD[NoteToICDAgent<br/>Notes → ICD]
        ICD_CPT[ICDToCPTAgent<br/>ICD → CPT]
        VALIDATOR[CodeValidationAgent<br/>Code Validation]
        SUMMARIZER[SummarizerAgent<br/>Executive Summary]
        MED_VAL[MedicalCodeValidationAgent<br/>Comprehensive Validation]
        CLAIM_PROC[ClaimProcessingAgent<br/>Claim Analysis]
        DENIAL[DenialAnalysisAgent<br/>Denial Analysis]
    end
    
    subgraph "Service Layer"
        LLM[LLM Client<br/>OpenAI/Anthropic/Google]
        RAG[RAG Service<br/>ChromaDB + Embeddings]
        PROMPTS[Prompt Templates<br/>Chain-of-Thought]
    end
    
    subgraph "Data Layer"
        DB[(SQLite/PostgreSQL<br/>Relational DB)]
        VECTOR[(ChromaDB<br/>Vector Store)]
        FILES[(/docs<br/>Medical Guidelines)]
    end
    
    subgraph "Configuration"
        ENV[.env<br/>Environment Variables]
        SETTINGS[Settings<br/>Pydantic Config]
    end
    
    %% Client connections
    UI --> PIPELINE
    UI --> RAG_INGEST
    API_CLIENT --> SIMPLE
    
    %% API routing
    PIPELINE --> ENHANCED_ORCH
    SIMPLE --> SIMPLE_ORCH
    RAG_INGEST --> RAG
    RAG_SEARCH --> RAG
    
    %% Orchestrator to agents
    SIMPLE_ORCH --> PARSER
    SIMPLE_ORCH --> NOTE_ICD
    SIMPLE_ORCH --> ICD_CPT
    SIMPLE_ORCH --> VALIDATOR
    SIMPLE_ORCH --> SUMMARIZER
    
    ENHANCED_ORCH --> PARSER
    ENHANCED_ORCH --> NOTE_ICD
    ENHANCED_ORCH --> ICD_CPT
    ENHANCED_ORCH --> VALIDATOR
    ENHANCED_ORCH --> SUMMARIZER
    ENHANCED_ORCH --> MED_VAL
    ENHANCED_ORCH --> CLAIM_PROC
    ENHANCED_ORCH --> DENIAL
    
    %% Agents to services
    NOTE_ICD --> LLM
    ICD_CPT --> LLM
    VALIDATOR --> LLM
    SUMMARIZER --> LLM
    MED_VAL --> LLM
    CLAIM_PROC --> LLM
    DENIAL --> LLM
    
    NOTE_ICD --> RAG
    ICD_CPT --> RAG
    VALIDATOR --> RAG
    
    NOTE_ICD --> PROMPTS
    ICD_CPT --> PROMPTS
    VALIDATOR --> PROMPTS
    
    %% Services to data
    RAG --> VECTOR
    RAG --> FILES
    LLM --> DB
    
    %% Configuration
    ENV --> SETTINGS
    SETTINGS --> LLM
    SETTINGS --> RAG
    
    %% Styling
    classDef apiClass fill:#667eea,stroke:#764ba2,stroke-width:2px,color:#fff
    classDef agentClass fill:#f093fb,stroke:#f5576c,stroke-width:2px,color:#fff
    classDef serviceClass fill:#4facfe,stroke:#00f2fe,stroke-width:2px,color:#fff
    classDef dataClass fill:#43e97b,stroke:#38f9d7,stroke-width:2px,color:#fff
    
    class PIPELINE,SIMPLE,RAG_INGEST,RAG_SEARCH apiClass
    class PARSER,NOTE_ICD,ICD_CPT,VALIDATOR,SUMMARIZER,MED_VAL,CLAIM_PROC,DENIAL agentClass
    class LLM,RAG,PROMPTS serviceClass
    class DB,VECTOR,FILES dataClass
```

---

## 2. Agent Workflow - Simple Pipeline

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Pipeline as UseCase1Pipeline
    participant Parser as ParserAgent
    participant NoteICD as NoteToICDAgent
    participant ICDCPT as ICDToCPTAgent
    participant Validator as CodeValidationAgent
    participant Summarizer as SummarizerAgent
    participant LLM as LLM Client
    
    Client->>API: POST /api/v1/uc1/pipeline/run/simple
    activate API
    
    API->>Pipeline: run(csv_path, manual_codes)
    activate Pipeline
    
    %% Stage 1: Parse
    Pipeline->>Parser: process(csv_path, hl7_text)
    activate Parser
    Parser->>Parser: Parse CSV/HL7
    Parser-->>Pipeline: {soap_notes, segments}
    deactivate Parser
    
    %% Stage 2: Notes to ICD
    Pipeline->>NoteICD: process(soap_notes)
    activate NoteICD
    NoteICD->>LLM: chat(extract ICD codes prompt)
    activate LLM
    LLM-->>NoteICD: ICD codes JSON
    deactivate LLM
    NoteICD-->>Pipeline: {icd_suggestions}
    deactivate NoteICD
    
    %% Stage 3: ICD to CPT
    Pipeline->>ICDCPT: process(icd_list)
    activate ICDCPT
    ICDCPT->>LLM: chat(suggest CPT codes prompt)
    activate LLM
    LLM-->>ICDCPT: CPT codes JSON
    deactivate LLM
    ICDCPT-->>Pipeline: {cpt_suggestions}
    deactivate ICDCPT
    
    %% Stage 4: Validation
    Pipeline->>Validator: process(manual_codes, ai_codes)
    activate Validator
    Validator->>LLM: chat(validation prompt, temp=0.0)
    activate LLM
    LLM-->>Validator: Validation report JSON
    deactivate LLM
    Validator-->>Pipeline: {validation_report}
    deactivate Validator
    
    %% Stage 5: Summary
    Pipeline->>Summarizer: process(validation_report)
    activate Summarizer
    Summarizer->>LLM: chat(summary prompt, temp=0.2)
    activate LLM
    LLM-->>Summarizer: Summary JSON
    deactivate LLM
    Summarizer-->>Pipeline: {summary}
    deactivate Summarizer
    
    Pipeline-->>API: {parsed, icd, cpt, validation, summary}
    deactivate Pipeline
    
    API-->>Client: 200 OK with results
    deactivate API
```

---

## 3. Agent Workflow - Enhanced Pipeline

```mermaid
flowchart TD
    START([Client Request]) --> PARSE[Stage 1: Parse Documents<br/>ParserAgent]
    
    PARSE --> RAG_RETRIEVE[Stage 2: RAG Retrieval<br/>Query ChromaDB for guidelines]
    
    RAG_RETRIEVE --> PARALLEL{Execution Mode?}
    
    PARALLEL -->|Parallel| PAR_START[Parallel Execution]
    PARALLEL -->|Sequential| SEQ_START[Sequential Execution]
    
    %% Parallel branch
    PAR_START --> ICD_PAR[Stage 3a: Extract ICD<br/>NoteToICDAgent + RAG]
    PAR_START --> CPT_PREP[Wait for ICD...]
    
    ICD_PAR --> CPT_PAR[Stage 3b: Suggest CPT<br/>ICDToCPTAgent + Context]
    CPT_PREP --> CPT_PAR
    
    CPT_PAR --> VAL_PARALLEL[Stage 4: Parallel Validation]
    
    VAL_PARALLEL --> VAL1[Validation Check<br/>CodeValidationAgent]
    VAL_PARALLEL --> VAL2[Medical Necessity<br/>Direct LLM Call]
    VAL_PARALLEL --> VAL3[Compliance Check<br/>NCCI, LCD, Bundling]
    
    VAL1 --> GATHER_PAR[Gather Results]
    VAL2 --> GATHER_PAR
    VAL3 --> GATHER_PAR
    
    %% Sequential branch
    SEQ_START --> ICD_SEQ[Stage 3: Extract ICD<br/>NoteToICDAgent + RAG]
    ICD_SEQ --> CPT_SEQ[Stage 4: Suggest CPT<br/>ICDToCPTAgent + Context]
    CPT_SEQ --> VAL_SEQ1[Stage 5a: Validation<br/>CodeValidationAgent]
    VAL_SEQ1 --> VAL_SEQ2[Stage 5b: Medical Necessity]
    VAL_SEQ2 --> VAL_SEQ3[Stage 5c: Compliance Check]
    VAL_SEQ3 --> GATHER_SEQ[Results Ready]
    
    GATHER_PAR --> SUMMARY
    GATHER_SEQ --> SUMMARY
    
    SUMMARY[Stage 6: Executive Summary<br/>SummarizerAgent] --> DECISION{Decision Engine}
    
    DECISION -->|Confidence >= 0.85<br/>Denial Risk < 0.2| APPROVE[✅ Auto-Approve]
    DECISION -->|Denial Risk > 0.7| REJECT[❌ Reject - Critical Issues]
    DECISION -->|Otherwise| REVIEW[⚠️ Manual Review Required]
    
    APPROVE --> RESULT[Return Results]
    REJECT --> RESULT
    REVIEW --> RESULT
    
    RESULT --> END([Response to Client])
    
    %% Styling
    classDef parseStyle fill:#ffd93d,stroke:#f77f00,stroke-width:2px
    classDef ragStyle fill:#6a4c93,stroke:#1982c4,stroke-width:2px,color:#fff
    classDef agentStyle fill:#f72585,stroke:#b5179e,stroke-width:2px,color:#fff
    classDef decisionStyle fill:#06ffa5,stroke:#06d6a0,stroke-width:3px
    classDef approveStyle fill:#52b788,stroke:#1b4332,stroke-width:2px,color:#fff
    classDef rejectStyle fill:#ef476f,stroke:#c1121f,stroke-width:2px,color:#fff
    
    class PARSE parseStyle
    class RAG_RETRIEVE ragStyle
    class ICD_PAR,CPT_PAR,ICD_SEQ,CPT_SEQ,VAL1,VAL2,VAL3,SUMMARY agentStyle
    class DECISION decisionStyle
    class APPROVE approveStyle
    class REJECT,REVIEW rejectStyle
```

---

## 4. LLM Integration Flow

```mermaid
graph TB
    subgraph "Application Layer"
        AGENT[Any Agent<br/>NoteToICD, ICDToCPT, etc.]
    end
    
    subgraph "LLM Abstraction Layer"
        CLIENT[LLM Client<br/>Unified Interface]
        
        subgraph "Provider Selection"
            ROUTER{Provider?}
        end
    end
    
    subgraph "Provider Clients"
        OPENAI[AsyncOpenAI<br/>gpt-4o-mini]
        ANTHROPIC[AsyncAnthropic<br/>claude-3-sonnet]
        GOOGLE[Google GenAI<br/>gemini-pro]
    end
    
    subgraph "External APIs"
        OPENAI_API[OpenAI API<br/>api.openai.com]
        ANTHROPIC_API[Anthropic API<br/>api.anthropic.com]
        GOOGLE_API[Google API<br/>generativelanguage]
    end
    
    subgraph "Configuration"
        ENV_VARS[Environment Variables<br/>.env file]
        SETTINGS_OBJ[Settings Object<br/>Pydantic]
    end
    
    %% Flow
    AGENT -->|await chat| CLIENT
    CLIENT --> ROUTER
    
    ROUTER -->|provider='openai'| OPENAI
    ROUTER -->|provider='anthropic'| ANTHROPIC
    ROUTER -->|provider='google'| GOOGLE
    
    OPENAI -->|HTTP POST| OPENAI_API
    ANTHROPIC -->|HTTP POST| ANTHROPIC_API
    GOOGLE -->|gRPC| GOOGLE_API
    
    OPENAI_API -->|Response| OPENAI
    ANTHROPIC_API -->|Response| ANTHROPIC
    GOOGLE_API -->|Response| GOOGLE
    
    OPENAI -->|Extract text| CLIENT
    ANTHROPIC -->|Extract text| CLIENT
    GOOGLE -->|Extract text| CLIENT
    
    CLIENT -->|Return string| AGENT
    
    ENV_VARS -->|Load| SETTINGS_OBJ
    SETTINGS_OBJ -->|API Keys| OPENAI
    SETTINGS_OBJ -->|API Keys| ANTHROPIC
    SETTINGS_OBJ -->|API Keys| GOOGLE
    SETTINGS_OBJ -->|Provider/Model| ROUTER
    
    %% Styling
    classDef agentClass fill:#f093fb,stroke:#f5576c,stroke-width:2px,color:#fff
    classDef clientClass fill:#4facfe,stroke:#00f2fe,stroke-width:2px,color:#fff
    classDef providerClass fill:#43e97b,stroke:#38f9d7,stroke-width:2px
    classDef apiClass fill:#fa709a,stroke:#fee140,stroke-width:2px,color:#fff
    classDef configClass fill:#a8edea,stroke:#fed6e3,stroke-width:2px
    
    class AGENT agentClass
    class CLIENT,ROUTER clientClass
    class OPENAI,ANTHROPIC,GOOGLE providerClass
    class OPENAI_API,ANTHROPIC_API,GOOGLE_API apiClass
    class ENV_VARS,SETTINGS_OBJ configClass
```

---

## 5. RAG System Architecture

```mermaid
graph TB
    subgraph "Document Ingestion"
        DOCS[(/docs<br/>Medical Guidelines<br/>PDF, TXT, MD)]
        UNSTRUCTURED[Unstructured Library<br/>Document Parsing]
        CHUNKER[Text Chunking<br/>Size: 1200<br/>Overlap: 150]
    end
    
    subgraph "Embedding Generation"
        EMB_CLIENT[Embedding Client]
        OPENAI_EMB[OpenAI Embeddings<br/>text-embedding-3-large]
    end
    
    subgraph "Vector Storage"
        CHROMA[(ChromaDB<br/>Vector Store<br/>./rag_index)]
        COLLECTION[Medical Docs<br/>Collection]
    end
    
    subgraph "Query Processing"
        AGENT_QUERY[Agent Query<br/>Clinical Notes]
        SEMANTIC_SEARCH[Semantic Search<br/>Cosine Similarity]
        TOP_K[Top-K Results<br/>K=5 default]
    end
    
    subgraph "RAG-Enhanced Prompting"
        CONTEXT[Retrieved Context<br/>Relevant Guidelines]
        PROMPT_BUILDER[Prompt Builder<br/>Context + Query]
        LLM_CALL[LLM API Call<br/>With Context]
    end
    
    %% Ingestion flow
    DOCS --> UNSTRUCTURED
    UNSTRUCTURED --> CHUNKER
    CHUNKER --> EMB_CLIENT
    EMB_CLIENT --> OPENAI_EMB
    OPENAI_EMB -->|Vectors| CHROMA
    CHROMA --> COLLECTION
    
    %% Query flow
    AGENT_QUERY --> SEMANTIC_SEARCH
    SEMANTIC_SEARCH --> COLLECTION
    COLLECTION -->|Search Results| TOP_K
    TOP_K --> CONTEXT
    CONTEXT --> PROMPT_BUILDER
    AGENT_QUERY --> PROMPT_BUILDER
    PROMPT_BUILDER --> LLM_CALL
    
    %% Styling
    classDef docClass fill:#ffd93d,stroke:#f77f00,stroke-width:2px
    classDef embClass fill:#6a4c93,stroke:#1982c4,stroke-width:2px,color:#fff
    classDef vectorClass fill:#06ffa5,stroke:#06d6a0,stroke-width:2px
    classDef queryClass fill:#f72585,stroke:#b5179e,stroke-width:2px,color:#fff
    classDef llmClass fill:#4facfe,stroke:#00f2fe,stroke-width:2px,color:#fff
    
    class DOCS,UNSTRUCTURED,CHUNKER docClass
    class EMB_CLIENT,OPENAI_EMB embClass
    class CHROMA,COLLECTION vectorClass
    class AGENT_QUERY,SEMANTIC_SEARCH,TOP_K queryClass
    class CONTEXT,PROMPT_BUILDER,LLM_CALL llmClass
```

---

## 6. API Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant CORS as CORS Middleware
    participant Auth as Auth Middleware (Future)
    participant Router as API Router
    participant Orchestrator
    participant Agent
    participant LLM
    participant DB as Database
    
    Client->>FastAPI: HTTP Request
    activate FastAPI
    
    FastAPI->>CORS: Check CORS
    activate CORS
    CORS-->>FastAPI: ✓ Allowed
    deactivate CORS
    
    FastAPI->>Auth: Authenticate (Future)
    activate Auth
    Auth-->>FastAPI: ✓ Authenticated
    deactivate Auth
    
    FastAPI->>Router: Route Request
    activate Router
    
    Router->>Router: Validate Pydantic Model
    
    alt Validation Success
        Router->>Orchestrator: Call orchestrator
        activate Orchestrator
        
        Orchestrator->>Agent: Execute agent(s)
        activate Agent
        
        Agent->>LLM: LLM API Call
        activate LLM
        LLM-->>Agent: Response
        deactivate LLM
        
        Agent->>DB: Store results (optional)
        activate DB
        DB-->>Agent: ✓ Stored
        deactivate DB
        
        Agent-->>Orchestrator: Results
        deactivate Agent
        
        Orchestrator-->>Router: Aggregated Results
        deactivate Orchestrator
        
        Router-->>FastAPI: 200 OK + Data
    else Validation Error
        Router-->>FastAPI: 422 Unprocessable Entity
    end
    
    deactivate Router
    
    FastAPI-->>Client: HTTP Response
    deactivate FastAPI
```

---

## 7. Database Schema

```mermaid
erDiagram
    MEDICAL_CODE {
        int id PK
        string code_type "CPT|ICD10|HCPCS"
        string code_value "Actual code"
        string description
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    INSURANCE_CLAIM {
        int id PK
        string claim_id UK
        string patient_id
        string provider_id
        string payer_name
        string payer_type "MEDICARE|MEDICAID|etc"
        float claim_amount
        float billed_amount
        string status "SUBMITTED|APPROVED|DENIED|etc"
        datetime submitted_date
        datetime processed_date
        float approved_amount
        string denial_reason
        boolean appeal_submitted
        boolean ai_validation_passed
        float validation_confidence
        string correction_suggestions
        datetime created_at
        datetime updated_at
    }
    
    VALIDATION_RESULT {
        int id PK
        int medical_code_id FK
        string validation_method "AI_LLM|RULE_BASED|HYBRID"
        string status "VALID|INVALID|WARNING"
        float confidence_score
        string input_code
        string input_type
        string input_context
        string validated_code
        string validation_message
        string suggestions "JSON"
        string error_message
        float processing_time_ms
        int tokens_used
        string agent_name
        string agent_version
        datetime created_at
        datetime updated_at
    }
    
    AGENT_CONFIG {
        int id PK
        string agent_name UK
        string agent_type "PARSER|VALIDATOR|etc"
        boolean is_enabled
        string model_name
        string provider "openai|anthropic|google"
        float temperature
        int max_tokens
        float confidence_threshold
        string config_json "Additional settings"
        datetime created_at
        datetime updated_at
    }
    
    VALIDATION_RESULT ||--o{ MEDICAL_CODE : "validates"
    INSURANCE_CLAIM ||--o{ VALIDATION_RESULT : "has"
```

---

## 8. Agent Class Hierarchy

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +str agent_name
        +str model_name
        +str provider
        +dict metrics
        +validate_input(input_data)* bool
        +process(input_data, kwargs)* dict
        +_update_metrics(time, tokens, success)
        +get_metrics() dict
    }
    
    class ParserAgent {
        +agent_name = "parser_agent"
        +validate_input(input_data) bool
        +process(input_data) dict
        -_parse_csv(path) list
        -_parse_hl7(text) dict
    }
    
    class NoteToICDAgent {
        +LLMClient llm
        +agent_name = "note_to_icd"
        +validate_input(input_data) bool
        +process(input_data) dict
    }
    
    class ICDToCPTAgent {
        +LLMClient llm
        +agent_name = "icd_to_cpt"
        +validate_input(input_data) bool
        +process(input_data) dict
    }
    
    class CodeValidationAgent {
        +LLMClient llm
        +agent_name = "code_validation"
        +validate_input(input_data) bool
        +process(input_data) dict
    }
    
    class SummarizerAgent {
        +LLMClient llm
        +agent_name = "summarizer_agent"
        +validate_input(input_data) bool
        +process(input_data) dict
    }
    
    class MedicalCodeValidationAgent {
        +AsyncOpenAI|AsyncAnthropic client
        +float confidence_threshold
        +validate_input(request) bool
        +process(request) response
        -_create_validation_prompt(request) str
        -_get_ai_response(prompt) str
        -_parse_validation_response(response) dict
    }
    
    class ClaimProcessingAgent {
        +client llm_client
        +validate_input(claim_data) bool
        +process(claim_data) dict
        -_create_claim_analysis_prompt(data) str
        -_get_ai_response(prompt) str
        -_parse_processing_response(response) dict
    }
    
    class DenialAnalysisAgent {
        +client llm_client
        +validate_input(request) bool
        +process(request) dict
        -_create_analysis_prompt(request) str
        -_get_ai_response(prompt) str
        -_parse_ai_response(response) dict
    }
    
    BaseAgent <|-- ParserAgent
    BaseAgent <|-- NoteToICDAgent
    BaseAgent <|-- ICDToCPTAgent
    BaseAgent <|-- CodeValidationAgent
    BaseAgent <|-- SummarizerAgent
    BaseAgent <|-- MedicalCodeValidationAgent
    BaseAgent <|-- ClaimProcessingAgent
    BaseAgent <|-- DenialAnalysisAgent
    
    NoteToICDAgent o-- LLMClient
    ICDToCPTAgent o-- LLMClient
    CodeValidationAgent o-- LLMClient
    SummarizerAgent o-- LLMClient
```

---

## 9. Configuration Management

```mermaid
flowchart LR
    subgraph "Environment"
        ENV_FILE[.env File<br/>OPENAI_API_KEY=sk-...]
        ENV_VARS[Environment Variables<br/>Export commands]
        SHELL_PROFILE[Shell Profile<br/>~/.zshrc]
    end
    
    subgraph "Pydantic Settings"
        SETTINGS_CLASS[Settings Class<br/>BaseSettings]
        VALIDATORS[Field Validators<br/>@validator]
        CONFIG[Config Class<br/>env_file='.env']
    end
    
    subgraph "Application Config"
        SETTINGS_INSTANCE[Settings Instance<br/>@lru_cache]
        
        subgraph "Config Sections"
            APP_CONFIG[App Config<br/>name, version, env]
            DB_CONFIG[Database<br/>database_url]
            AI_CONFIG[AI Services<br/>api_keys, models]
            RAG_CONFIG[RAG Config<br/>vector_db, chunks]
            LOG_CONFIG[Logging<br/>level, format]
        end
    end
    
    subgraph "Consumers"
        FASTAPI[FastAPI App]
        AGENTS[AI Agents]
        LLM_CLIENT[LLM Client]
        RAG_SERVICE[RAG Service]
        DB_ENGINE[DB Engine]
    end
    
    %% Flow
    ENV_FILE --> SETTINGS_CLASS
    ENV_VARS --> SETTINGS_CLASS
    SHELL_PROFILE --> ENV_VARS
    
    SETTINGS_CLASS --> VALIDATORS
    VALIDATORS --> CONFIG
    CONFIG --> SETTINGS_INSTANCE
    
    SETTINGS_INSTANCE --> APP_CONFIG
    SETTINGS_INSTANCE --> DB_CONFIG
    SETTINGS_INSTANCE --> AI_CONFIG
    SETTINGS_INSTANCE --> RAG_CONFIG
    SETTINGS_INSTANCE --> LOG_CONFIG
    
    APP_CONFIG --> FASTAPI
    DB_CONFIG --> DB_ENGINE
    AI_CONFIG --> LLM_CLIENT
    AI_CONFIG --> AGENTS
    RAG_CONFIG --> RAG_SERVICE
    LOG_CONFIG --> FASTAPI
    
    %% Styling
    classDef envClass fill:#ffd93d,stroke:#f77f00,stroke-width:2px
    classDef settingsClass fill:#6a4c93,stroke:#1982c4,stroke-width:2px,color:#fff
    classDef configClass fill:#06ffa5,stroke:#06d6a0,stroke-width:2px
    classDef consumerClass fill:#f72585,stroke:#b5179e,stroke-width:2px,color:#fff
    
    class ENV_FILE,ENV_VARS,SHELL_PROFILE envClass
    class SETTINGS_CLASS,VALIDATORS,CONFIG settingsClass
    class APP_CONFIG,DB_CONFIG,AI_CONFIG,RAG_CONFIG,LOG_CONFIG configClass
    class FASTAPI,AGENTS,LLM_CLIENT,RAG_SERVICE,DB_ENGINE consumerClass
```

---

## 10. Error Handling Flow

```mermaid
stateDiagram-v2
    [*] --> RequestReceived
    
    RequestReceived --> ValidateInput
    
    ValidateInput --> InputValid: Valid
    ValidateInput --> Return422: Invalid
    
    InputValid --> ProcessAgent
    
    ProcessAgent --> LLMCall
    
    LLMCall --> LLMSuccess: Success
    LLMCall --> LLMError: API Error
    
    LLMError --> Retry: Retriable?
    Retry --> LLMCall: Retry (max 3)
    Retry --> LogError: Max retries
    
    LLMSuccess --> ParseResponse
    
    ParseResponse --> ParseSuccess: Valid JSON
    ParseResponse --> ParseError: Invalid JSON
    
    ParseError --> UseFallback
    UseFallback --> Return200Partial
    
    ParseSuccess --> StoreResults
    
    StoreResults --> DBSuccess: Success
    StoreResults --> DBError: DB Error
    
    DBError --> LogWarning
    LogWarning --> Return200
    
    DBSuccess --> Return200
    
    Return422 --> [*]
    Return200Partial --> [*]
    Return200 --> [*]
    LogError --> Return500
    Return500 --> [*]
    
    note right of Return422
        422 Unprocessable Entity
        - Invalid request format
        - Missing required fields
        - Validation errors
    end note
    
    note right of Return500
        500 Internal Server Error
        - LLM API failures
        - Unrecoverable errors
        - System errors
    end note
    
    note right of Return200
        200 OK
        - Successful processing
        - Results stored
        - Metrics updated
    end note
    
    note right of Return200Partial
        200 OK (Partial)
        - Processing completed
        - Some warnings
        - Fallback used
    end note
```

---

## 📝 How to Use These Diagrams

### Viewing in GitHub

GitHub automatically renders Mermaid diagrams in Markdown files. Just view this file on GitHub!

### Viewing Locally

1. **VS Code**: Install "Markdown Preview Mermaid Support" extension
2. **Online**: Copy diagram code to https://mermaid.live/
3. **CLI**: Use `mmdc` (mermaid-cli) to generate images

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Generate PNG
mmdc -i ARCHITECTURE_DIAGRAMS.md -o diagram.png
```

### Editing Diagrams

1. Visit https://mermaid.live/
2. Copy the diagram code
3. Edit and preview in real-time
4. Copy back to this file

---

## 🎨 Diagram Legend

| Color | Meaning |
|-------|---------|
| 🟣 Purple | API/Routing Layer |
| 🔴 Pink/Red | Agent Layer |
| 🔵 Blue | Service Layer |
| 🟢 Green | Data/Storage Layer |
| 🟡 Yellow | Processing/Parsing |
| 🟠 Orange | Configuration |

---

## 📚 Related Documentation

- **LLM Usage**: See `LLM_USAGE_SUMMARY.md`
- **Testing**: See `TESTING_GUIDE.md`
- **Use Case 1**: See `USECASE1_GUIDE.md`
- **Current Status**: See `CURRENT_STATUS.md`
- **API Configuration**: See `HOW_TO_CONFIGURE_API_KEY.md`

---

**Generated**: October 2, 2024  
**Diagram Format**: Mermaid v10.x  
**Last Updated**: October 2, 2024

