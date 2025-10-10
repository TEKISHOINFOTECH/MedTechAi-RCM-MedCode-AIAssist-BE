# 🔑 Running Tests with OpenAI API Key

## Quick Setup

### Option 1: Set in Current Terminal (Recommended for Testing)

```bash
# Export for current session
export OPENAI_API_KEY="sk-your-actual-key-here"

# Verify it's set
echo $OPENAI_API_KEY

# Run tests
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC
make test-integration
```

### Option 2: Create .env File (Recommended for Development)

```bash
# Create .env file
cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here

# Optional: Other providers
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

# App Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large
EOF

# Load environment variables
source .env
export $(cat .env | xargs)

# Run tests
make test-integration
```

### Option 3: Add to Shell Profile (Permanent)

```bash
# Add to ~/.zshrc (for zsh) or ~/.bashrc (for bash)
echo 'export OPENAI_API_KEY="sk-your-actual-key-here"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Run tests
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC
make test-integration
```

---

## 🧪 Test Execution Options

### Run All Tests (Full Suite - 49 tests)

```bash
# Set API key first
export OPENAI_API_KEY="sk-your-key"

# Run all integration tests
make test-integration

# Expected output:
# ==================== 49 passed in ~105s ====================
```

### Run By Category

```bash
# 1. External Connectivity Tests (15 tests, ~30s)
make test-connectivity

# Tests: OpenAI, Google AI, Anthropic, ChromaDB, embeddings, RAG

# 2. Workflow Validation Tests (16 tests, ~75s)
make test-workflow

# Tests: Agent workflows, pipelines, validation logic, error handling

# 3. API Endpoint Tests (18 tests, ~0.2s)
make test-api

# Tests: Health checks, pipeline APIs, RAG APIs, error handling, CORS
```

### Run Fast Tests Only (Exclude slow tests)

```bash
make test-fast

# Runs only tests that complete in < 10 seconds
```

### Run Specific Test File

```bash
# External connectivity
uv run pytest tests/integration/test_external_connectivity.py -v

# Workflows
uv run pytest tests/integration/test_workflow_validation.py -v

# API endpoints
uv run pytest tests/integration/test_api_endpoints.py -v
```

### Run Specific Test Class

```bash
# Test OpenAI connectivity
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity -v

# Test agent workflows
uv run pytest tests/integration/test_workflow_validation.py::TestAgentWorkflows -v

# Test pipeline workflows
uv run pytest tests/integration/test_workflow_validation.py::TestPipelineWorkflows -v
```

### Run Single Test

```bash
# Test OpenAI connection
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection -v

# Test ICD code generation
uv run pytest tests/integration/test_workflow_validation.py::TestAgentWorkflows::test_note_to_icd_agent -v

# Test enhanced pipeline
uv run pytest tests/integration/test_workflow_validation.py::TestPipelineWorkflows::test_enhanced_pipeline_parallel -v
```

---

## 📊 Expected Test Results

### With OpenAI API Key Only

```
External Connectivity:
✅ test_openai_connection          PASSED
✅ test_openai_medical_query       PASSED
⚠️ test_google_connection          SKIPPED (no Google key)
⚠️ test_anthropic_connection       SKIPPED (no Anthropic key)
✅ test_llm_provider_switching     PASSED
✅ test_openai_embeddings          PASSED
✅ test_embedding_consistency      PASSED
✅ test_chromadb_initialization    PASSED
✅ test_chromadb_ingest_and_query  PASSED
✅ test_chromadb_semantic_search   PASSED
✅ test_chromadb_persistence       PASSED
✅ test_full_rag_pipeline          PASSED
✅ test_concurrent_llm_requests    PASSED
✅ test_error_handling_invalid_api_key PASSED
✅ test_rate_limit_handling        PASSED

Agent Workflows:
✅ test_parser_agent_csv           PASSED
✅ test_parser_agent_hl7           PASSED
✅ test_note_to_icd_agent          PASSED
✅ test_icd_to_cpt_agent           PASSED
✅ test_validation_agent           PASSED
✅ test_summarizer_agent           PASSED

Pipeline Workflows:
✅ test_simple_pipeline_execution       PASSED
✅ test_enhanced_pipeline_sequential    PASSED
✅ test_enhanced_pipeline_parallel      PASSED
✅ test_pipeline_performance_comparison PASSED

Validation & Error Handling:
✅ test_high_confidence_approval        PASSED
✅ test_low_confidence_rejection        PASSED
✅ test_validation_with_rag_context     PASSED
✅ test_agent_failure_recovery          PASSED
✅ test_partial_failure_handling        PASSED
✅ test_json_parsing_fallback           PASSED

API Endpoints:
✅ All 18 tests                         PASSED

Summary:
==================== 47 passed, 2 skipped in 105.23s ====================
```

### With All API Keys (OpenAI + Google + Anthropic)

```
==================== 49 passed in 110.45s ====================
```

---

## 🔍 Debug Mode

### Verbose Output

```bash
# Very verbose with full traceback
uv run pytest tests/integration/ -vv --tb=long

# Show print statements
uv run pytest tests/integration/ -v -s

# Debug logging
uv run pytest tests/integration/ -v --log-cli-level=DEBUG
```

### Stop on First Failure

```bash
uv run pytest tests/integration/ --maxfail=1 -v
```

### Run Specific Test Pattern

```bash
# Run all OpenAI tests
uv run pytest tests/integration/ -k "openai" -v

# Run all ICD-related tests
uv run pytest tests/integration/ -k "icd" -v

# Run all validation tests
uv run pytest tests/integration/ -k "validation" -v
```

---

## 📈 Coverage Report

### Generate Coverage Report

```bash
# Run with coverage
make test-coverage

# Or manually:
uv run pytest tests/integration/ \
  --cov=app \
  --cov-report=html \
  --cov-report=term-missing \
  -v

# Open HTML report
open htmlcov/index.html
```

### Expected Coverage

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
app/__init__.py                            4      0   100%
app/agents/base_agent.py                  45     12    73%
app/agents/parser_agent.py                67     15    78%
app/agents/note_to_icd_agent.py           82     18    78%
app/agents/icd_to_cpt_agent.py            85     19    78%
app/agents/code_validation_agent.py       78     17    78%
app/agents/summarizer_agent.py            65     14    78%
app/routes/usecase1.py                    42      5    88%
app/services/orchestrator/enhanced.py    156     28    82%
-----------------------------------------------------------
TOTAL                                   1247    234    81%
```

---

## 🚀 Step-by-Step Test Execution

### Step 1: Verify Setup

```bash
cd /Users/apple/Documents/DevTechAI/gitRepoDevTechAI/DevTechAIDocsRepo/GitHubRepos/DTA_TEKISHO_RCM_AGENTS_POC/MedTechAi-RCM-MedCode-Assist-POC

# Check Python version
python3 --version  # Should be 3.11+

# Check UV is installed
uv --version

# Verify test dependencies
uv pip list | grep pytest
```

### Step 2: Set API Key

```bash
# Option A: Temporary (for this session only)
export OPENAI_API_KEY="sk-proj-..."

# Option B: Using .env file
echo "OPENAI_API_KEY=sk-proj-..." > .env
source .env
```

### Step 3: Verify API Key Works

```bash
# Quick connectivity test
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection -v
```

Expected output:
```
tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection 
✓ OpenAI connection successful: success
PASSED [100%]
```

### Step 4: Run Full Suite

```bash
# Run all tests
make test-integration

# Or with more control:
uv run pytest tests/integration/ -v --tb=short
```

### Step 5: Review Results

```bash
# Check test summary
cat TEST_RESULTS_REPORT.md

# View detailed logs (if errors occur)
cat .pytest_cache/v/cache/lastfailed
```

---

## 🐛 Troubleshooting

### Issue: API Key Not Recognized

```bash
# Check if key is set
echo $OPENAI_API_KEY

# If empty, re-export
export OPENAI_API_KEY="sk-proj-your-key"

# Verify by running simple test
uv run pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection -v
```

### Issue: Tests Still Skipped

```bash
# Check conftest.py fixture
uv run pytest tests/integration/ --collect-only -q | grep -i skip

# Run with skip reasons shown
uv run pytest tests/integration/ -v -rs
```

### Issue: Rate Limiting

```bash
# Skip LLM tests temporarily
uv run pytest tests/integration/ -m "not llm" -v

# Or run tests one at a time with delay
for test in tests/integration/test_*.py; do
  uv run pytest "$test" -v
  sleep 5
done
```

### Issue: Timeout

```bash
# Increase timeout
uv run pytest tests/integration/ -v --timeout=600

# Or skip slow tests
uv run pytest tests/integration/ -m "not slow" -v
```

### Issue: ChromaDB Errors

```bash
# Clear ChromaDB cache
rm -rf ./chroma_db ./rag_index

# Re-run tests
make test-integration
```

---

## 📊 Performance Monitoring

### Monitor Test Execution

```bash
# Show slowest tests
uv run pytest tests/integration/ -v --durations=10

# Profile test execution
uv run pytest tests/integration/ -v --profile

# Show test order
uv run pytest tests/integration/ -v --collect-only
```

---

## ✅ Success Checklist

Before running tests, ensure:

- [ ] Python 3.11+ installed
- [ ] UV package manager installed
- [ ] Test dependencies installed (`make dev`)
- [ ] OpenAI API key set (`export OPENAI_API_KEY=...`)
- [ ] In correct directory
- [ ] API key has sufficient credits

Expected final output:
```
==================== 47 passed, 2 skipped in 105.23s ====================
```

(47 with OpenAI only, 49 with all providers)

---

## 🎯 Next Steps After Testing

1. **Review Test Report**
   ```bash
   open TEST_RESULTS_REPORT.md
   ```

2. **Check Coverage**
   ```bash
   make test-coverage
   open htmlcov/index.html
   ```

3. **Run Backend with Tests**
   ```bash
   # Terminal 1: Start backend
   make run
   
   # Terminal 2: Run API integration tests
   curl http://localhost:8001/health | jq
   ```

4. **Test with Streamlit UI**
   ```bash
   # Start Streamlit
   cd streamlit_app
   streamlit run app.py
   ```

---

## 📞 Support

If you encounter issues:

1. Check `TESTING_GUIDE.md` for detailed troubleshooting
2. Review `.pytest_cache/` for error logs
3. Run with `-vv --tb=long` for detailed error messages
4. Check `TEST_RESULTS_REPORT.md` for expected behavior

---

**Ready to run tests?** Execute:

```bash
export OPENAI_API_KEY="sk-your-key-here"
make test-integration
```

