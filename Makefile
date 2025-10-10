# Makefile for MedTechAI RCM Medical Code Validation

.PHONY: help install dev test test-integration test-connectivity test-workflow test-api test-fast test-coverage clean format lint run docker-build docker-up docker-down

# Default target
help:
	@echo "MedTechAI RCM - Available Commands"
	@echo "==================================="
	@echo ""
	@echo "Setup:"
	@echo "  make install           - Install production dependencies"
	@echo "  make dev               - Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run all tests"
	@echo "  make test-integration  - Run integration tests"
	@echo "  make test-connectivity - Test external connectivity only"
	@echo "  make test-workflow     - Test workflows only"
	@echo "  make test-api          - Test API endpoints only"
	@echo "  make test-fast         - Run fast tests only"
	@echo "  make test-coverage     - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format            - Format code with black and isort"
	@echo "  make lint              - Run linters (ruff, flake8, mypy)"
	@echo ""
	@echo "Run:"
	@echo "  make run               - Start development server"
	@echo "  make run-prod          - Start production server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      - Build Docker images"
	@echo "  make docker-up         - Start Docker containers"
	@echo "  make docker-down       - Stop Docker containers"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean             - Clean temporary files"
	@echo "  make rag-ingest        - Ingest documents into RAG store"
	@echo ""

# Installation
install:
	uv sync

dev:
	uv sync --group dev --group test

# Testing
test:
	pytest tests/ -v

test-integration:
	./scripts/run_integration_tests.sh all

test-connectivity:
	./scripts/run_integration_tests.sh connectivity

test-workflow:
	./scripts/run_integration_tests.sh workflow

test-api:
	./scripts/run_integration_tests.sh api

test-fast:
	./scripts/run_integration_tests.sh fast

test-coverage:
	pytest tests/integration/ -v --cov=app --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "Coverage report generated: htmlcov/index.html"

# Code Quality
format:
	@echo "Running black..."
	black app/ tests/ scripts/ --line-length 100
	@echo "Running isort..."
	isort app/ tests/ scripts/
	@echo "Code formatted successfully!"

lint:
	@echo "Running ruff..."
	ruff check app/ tests/
	@echo "Running flake8..."
	flake8 app/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running mypy..."
	mypy app/ --ignore-missing-imports
	@echo "Linting complete!"

# Run application
run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

run-prod:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Utilities
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "Clean complete!"

rag-ingest:
	@echo "Ingesting documents into RAG store..."
	curl -X POST "http://localhost:8001/api/v1/uc1/rag/ingest?directory=./docs"
	@echo ""
	@echo "Documents ingested successfully!"

# CI/CD
ci-test: dev lint test-integration

# Health check
health:
	@curl -s http://localhost:8001/health | python -m json.tool

# Database migrations (if using Alembic)
migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-create:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"
