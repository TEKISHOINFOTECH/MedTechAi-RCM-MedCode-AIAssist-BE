# Testing Guide - MedTechAI RCM

## Quick Start

```bash
# 1. Set API key
export OPENAI_API_KEY="sk-your-key-here"

# 2. Install test dependencies
make dev

# 3. Run fast tests
make test-fast

# 4. Run full integration suite
make test-integration
```

## Test Categories

### 🔌 External Connectivity Tests
**Purpose**: Verify connections to LLM providers and vector database

```bash
# Test all external services
make test-connectivity

# Test specific providers
pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity -v
pytest tests/integration/test_external_connectivity.py::TestEmbeddingConnectivity -v
pytest tests/integration/test_external_connectivity.py::TestVectorStoreConnectivity -v
```

**What it tests**:
- ✅ OpenAI chat completion API
- ✅ OpenAI embeddings API
- ✅ Google Generative AI (optional)
- ✅ Anthropic Claude (optional)
- ✅ ChromaDB vector store operations
- ✅ RAG pipeline (ingest → query → generate)
- ✅ Concurrent request handling
- ✅ Error handling with invalid credentials

**Expected time**: ~30 seconds

### 🔄 Workflow Validation Tests
**Purpose**: Validate agent pipelines and orchestration

```bash
# Test all workflows
make test-workflow

# Test specific workflows
pytest tests/integration/test_workflow_validation.py::TestAgentWorkflows -v
pytest tests/integration/test_workflow_validation.py::TestPipelineWorkflows -v
```

**What it tests**:
- ✅ ParserAgent (CSV, HL7 parsing)
- ✅ NoteToICDAgent (clinical notes → ICD codes)
- ✅ ICDToCPTAgent (ICD codes → CPT codes)
- ✅ CodeValidationAgent (AI vs manual comparison)
- ✅ SummarizerAgent (executive summaries)
- ✅ Simple pipeline execution
- ✅ Enhanced orchestrator (sequential & parallel)
- ✅ Performance comparison
- ✅ Validation logic and decision making
- ✅ Error recovery and fallbacks

**Expected time**: ~75 seconds

### 🌐 API Endpoint Tests
**Purpose**: Test FastAPI routes and error handling

```bash
# Start backend first
make run &

# Then run API tests
make test-api

# Or test specific endpoints
pytest tests/integration/test_api_endpoints.py::TestHealthEndpoints -v
pytest tests/integration/test_api_endpoints.py::TestUseCase1Endpoints -v
pytest tests/integration/test_api_endpoints.py::TestRAGEndpoints -v
```

**What it tests**:
- ✅ Health check endpoints
- ✅ UseCase1 pipeline endpoints (simple & enhanced)
- ✅ RAG ingestion and search endpoints
- ✅ Request validation
- ✅ Error responses (404, 405, 422, 500)
- ✅ CORS configuration
- ✅ Concurrent API requests
- ✅ End-to-end workflows

**Expected time**: ~22 seconds

## Test Execution Strategies

### Development Workflow

```bash
# During active development - fast iteration
make test-fast

# Before committing - full validation
make test-integration

# Check coverage
make test-coverage
```

### CI/CD Pipeline

```bash
# Minimal tests for quick feedback
pytest tests/integration/ -m "integration and not slow" -v

# Full suite for release validation
pytest tests/integration/ -v --cov=app
```

### Debugging Failed Tests

```bash
# Verbose output with full traceback
pytest tests/integration/test_external_connectivity.py::test_openai_connection -vv --tb=long

# Stop on first failure
pytest tests/integration/ --maxfail=1 -v

# Run specific test with debug logging
pytest tests/integration/ -k "test_openai" -vv --log-cli-level=DEBUG

# Print output even for passing tests
pytest tests/integration/ -v -s
```

## Configuration

### Required Environment Variables

```bash
# Minimum (for basic tests)
export OPENAI_API_KEY="sk-..."

# Full (for all provider tests)
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

### Optional Configuration

```bash
# Override LLM provider
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"

# Override embedding model
export EMBEDDING_MODEL="text-embedding-3-large"

# Override vector store path
export VECTOR_DB_DIR="./test_rag_index"

# Enable verbose logging
export LOG_LEVEL="DEBUG"
```

## Test Markers Reference

| Marker | Description | Example |
|--------|-------------|---------|
| `integration` | All integration tests | `pytest -m integration` |
| `slow` | Tests > 10 seconds | `pytest -m "not slow"` |
| `llm` | Requires LLM API | `pytest -m llm` |
| `rag` | Requires vector DB | `pytest -m rag` |

### Combining Markers

```bash
# Integration tests that are not slow
pytest -m "integration and not slow"

# LLM tests excluding RAG
pytest -m "llm and not rag"

# Fast integration tests only
pytest -m "integration and not slow and not llm"
```

## Expected Outcomes

### ✅ All Tests Pass (Full Configuration)

```
tests/integration/test_external_connectivity.py ............  [35%]
tests/integration/test_workflow_validation.py ...........     [65%]
tests/integration/test_api_endpoints.py ..............       [100%]

==================== 45 passed in 127.52s ====================
```

### ⚠️ Partial Success (Missing API Keys)

```
tests/integration/test_external_connectivity.py .s.s.s....  [35%]
tests/integration/test_workflow_validation.py ...........    [65%]
tests/integration/test_api_endpoints.py ..............      [100%]

==================== 38 passed, 7 skipped in 85.32s ====================
```

### ❌ Tests Fail (Investigation Required)

```
tests/integration/test_external_connectivity.py F.........

FAILED test_external_connectivity.py::test_openai_connection
    ConnectionError: Could not connect to OpenAI API
    Check: API key, network connection, rate limits

==================== 1 failed, 44 passed in 98.45s ====================
```

## Troubleshooting

### Issue: Tests Skipped

```
SKIPPED [1] test_external_connectivity.py:25: OpenAI API key not configured
```

**Solution**:
```bash
export OPENAI_API_KEY="sk-your-actual-key"
pytest tests/integration/ -v
```

### Issue: ChromaDB Errors

```
chromadb.errors.ChromaError: Could not connect to ChromaDB
```

**Solution**: ChromaDB runs embedded, check write permissions:
```bash
mkdir -p ./rag_index
chmod -R 755 ./rag_index
```

### Issue: API Tests Timeout

```
httpx.ConnectTimeout: timed out
```

**Solution**: Start backend server:
```bash
# Terminal 1
make run

# Terminal 2
make test-api
```

### Issue: Rate Limiting

```
openai.RateLimitError: Rate limit exceeded
```

**Solution**: Run tests with delay or skip LLM tests:
```bash
pytest tests/integration/ -m "not llm" -v
```

### Issue: JSON Parse Errors

```
ValueError: Failed to parse AI response
```

**Solution**: LLM returned unexpected format. Check:
- Model version compatibility
- Prompt template updates
- Token limits
- API status

## Performance Optimization

### Parallel Test Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest tests/integration/ -n auto

# Run specific number of workers
pytest tests/integration/ -n 4
```

### Test Isolation

```bash
# Clear cache between runs
pytest --cache-clear tests/integration/

# Reset vector database
rm -rf ./rag_index
```

## Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| `app/agents/` | 80% | TBD |
| `app/services/` | 85% | TBD |
| `app/routes/` | 90% | TBD |
| `app/utils/` | 75% | TBD |

```bash
# Check current coverage
make test-coverage

# Open HTML report
open htmlcov/index.html
```

## Best Practices

1. **Always run fast tests first** during development
2. **Check for skipped tests** - may indicate missing config
3. **Use verbose mode** (`-v`) when debugging
4. **Isolate failing tests** to debug efficiently
5. **Clean up test artifacts** after runs
6. **Monitor API costs** when running LLM tests
7. **Update fixtures** when adding new agents
8. **Document new test markers** in pytest.ini

## Continuous Integration

Tests run automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

View results: GitHub Actions → Integration Tests workflow

## Support

For test failures or issues:
1. Check test output for specific error
2. Review logs: `pytest --log-cli-level=DEBUG`
3. Consult `tests/README.md` for detailed documentation
4. Open issue with test output and environment details

