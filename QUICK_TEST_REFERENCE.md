# Quick Test Reference Card

## 🚀 One-Line Commands

```bash
# Setup
export OPENAI_API_KEY="sk-..." && make dev

# Run all tests
make test-integration

# Run fast tests (< 10s each)
make test-fast

# Test connectivity only
make test-connectivity

# Test workflows only
make test-workflow

# Test API only (requires backend running)
make run & sleep 5 && make test-api

# Coverage report
make test-coverage && open htmlcov/index.html
```

## 📋 Test Files

| File | Tests | Purpose | Time |
|------|-------|---------|------|
| `test_external_connectivity.py` | 15 | LLM, embeddings, vector DB | ~30s |
| `test_workflow_validation.py` | 18 | Agent pipelines, orchestration | ~75s |
| `test_api_endpoints.py` | 20 | FastAPI routes, error handling | ~22s |

## 🎯 Common Scenarios

### First Time Setup
```bash
git clone <repo>
cd MedTechAi-RCM-MedCode-Assist-POC
export OPENAI_API_KEY="sk-your-key"
make dev
make test-fast
```

### Before Committing
```bash
make format
make lint
make test-integration
```

### Debugging Failed Test
```bash
pytest tests/integration/test_external_connectivity.py::test_openai_connection -vv --tb=long
```

### CI/CD
```bash
pytest tests/integration/ -m "integration and not slow" --cov=app
```

## 📊 Test Markers

| Marker | Usage | Example |
|--------|-------|---------|
| `integration` | All integration tests | `pytest -m integration` |
| `slow` | Tests > 10 seconds | `pytest -m "not slow"` |
| `llm` | Requires LLM API | `pytest -m llm` |
| `rag` | Requires vector DB | `pytest -m rag` |

## 🔑 Required Environment

```bash
# Minimum (43 tests)
export OPENAI_API_KEY="sk-..."

# Full (53 tests)
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

## ✅ Expected Results

```
# Full configuration
==================== 53 passed in 127s ====================

# Partial configuration
==================== 43 passed, 10 skipped in 85s ====================
```

## 🐛 Quick Fixes

### Tests Skipped
```bash
export OPENAI_API_KEY="sk-your-key"
```

### API Tests Fail
```bash
# Terminal 1: Start backend
make run

# Terminal 2: Run tests
make test-api
```

### ChromaDB Errors
```bash
mkdir -p ./rag_index && chmod 755 ./rag_index
```

### Rate Limiting
```bash
pytest tests/integration/ -m "not llm"
```

## 📖 Documentation

- **Full Guide**: `TESTING_GUIDE.md`
- **Detailed Docs**: `tests/README.md`
- **Implementation**: `INTEGRATION_TESTS_SUMMARY.md`

## 💡 Pro Tips

```bash
# Stop on first failure
pytest tests/integration/ --maxfail=1

# Run specific test
pytest tests/integration/test_external_connectivity.py::TestLLMConnectivity::test_openai_connection

# Watch for changes (requires pytest-watch)
ptw tests/integration/

# Parallel execution (requires pytest-xdist)
pytest tests/integration/ -n auto

# Debug with pdb
pytest tests/integration/ --pdb
```

## 🎨 Makefile Targets

```bash
make help              # Show all commands
make test              # Run all tests
make test-integration  # Run integration tests
make test-connectivity # Test external services
make test-workflow     # Test agent workflows
make test-api          # Test API endpoints
make test-fast         # Run fast tests only
make test-coverage     # Generate coverage report
```

## 📞 Support

- **Errors**: Check `pytest --tb=long` output
- **Docs**: See `TESTING_GUIDE.md`
- **Issues**: GitHub Issues with test output

---

**Last Updated**: October 2024
**Version**: 1.0.0

