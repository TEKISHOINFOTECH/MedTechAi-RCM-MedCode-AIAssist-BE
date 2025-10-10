#!/bin/bash
# Integration test runner script

set -e

echo "=================================================="
echo "MedTechAI RCM - Integration Test Suite"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Activating .venv..."
    source .venv/bin/activate || source venv/bin/activate || {
        echo "❌ Could not find virtual environment"
        exit 1
    }
fi

# Check required environment variables
echo "🔍 Checking configuration..."
echo ""

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "⚠️  OPENAI_API_KEY not set - LLM tests will be skipped"
fi

if [[ -z "$GOOGLE_API_KEY" ]]; then
    echo "⚠️  GOOGLE_API_KEY not set - Google AI tests will be skipped"
fi

if [[ -z "$ANTHROPIC_API_KEY" ]]; then
    echo "⚠️  ANTHROPIC_API_KEY not set - Anthropic tests will be skipped"
fi

echo ""
echo "=================================================="
echo "Running Integration Tests"
echo "=================================================="
echo ""

# Parse command line arguments
TEST_FILTER="${1:-}"
PYTEST_ARGS=("${@:2}")

if [[ -n "$TEST_FILTER" ]]; then
    echo "🎯 Running filtered tests: $TEST_FILTER"
    echo ""
fi

# Default pytest options
DEFAULT_ARGS=(
    -v
    -m "integration"
    --tb=short
    --color=yes
    -ra
)

# Run tests based on filter
case "$TEST_FILTER" in
    "connectivity")
        echo "🔌 Testing external connectivity only..."
        pytest tests/integration/test_external_connectivity.py "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "workflow")
        echo "🔄 Testing workflow validation only..."
        pytest tests/integration/test_workflow_validation.py "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "api")
        echo "🌐 Testing API endpoints only..."
        pytest tests/integration/test_api_endpoints.py "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "llm")
        echo "🤖 Testing LLM connectivity only..."
        pytest tests/integration/ -m "llm" "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "rag")
        echo "📚 Testing RAG/vector database only..."
        pytest tests/integration/ -m "rag" "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "fast")
        echo "⚡ Running fast tests only (excluding slow)..."
        pytest tests/integration/ -m "integration and not slow" "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    "all"|"")
        echo "🚀 Running all integration tests..."
        pytest tests/integration/ "${PYTEST_ARGS[@]:-${DEFAULT_ARGS[@]}}"
        ;;
    *)
        echo "❌ Unknown filter: $TEST_FILTER"
        echo ""
        echo "Usage: $0 [filter] [pytest-args...]"
        echo ""
        echo "Available filters:"
        echo "  connectivity  - Test external service connectivity"
        echo "  workflow      - Test agent workflows and pipelines"
        echo "  api           - Test API endpoints"
        echo "  llm           - Test LLM providers only"
        echo "  rag           - Test vector database only"
        echo "  fast          - Run fast tests only (skip slow tests)"
        echo "  all           - Run all integration tests (default)"
        echo ""
        echo "Examples:"
        echo "  $0                      # Run all tests"
        echo "  $0 connectivity         # Test connectivity only"
        echo "  $0 fast                 # Run fast tests only"
        echo "  $0 all -k test_openai   # Run tests matching 'test_openai'"
        echo "  $0 workflow --maxfail=1 # Stop after first failure"
        exit 1
        ;;
esac

TEST_EXIT_CODE=$?

echo ""
echo "=================================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=================================================="

exit $TEST_EXIT_CODE

