# MedTechAi RCM Medical Code Assistant

An advanced AI-powered platform for Revenue Cycle Management (RCM) that validates medical codes and optimizes insurance claim success rates using cutting-edge artificial intelligence.

## 🚀 Features

- **AI-Powered Medical Code Validation**: Uses GPT-4 and Claude-3 for intelligent validation of CPT, ICD-10, and HCPCS codes
- **Real-time Claim Analysis**: Automated processing and validation of insurance claims
- **Risk Assessment**: Advanced denial risk scoring and mitigation strategies
- **Agentic Architecture**: Modular AI agents for different RCM tasks
- **Modern Web Interface**: Beautiful, responsive React TypeScript frontend
- **Configurable AI Models**: Support for multiple AI providers and models
- **Comprehensive Monitoring**: Built-in metrics, logging, and health checks

## 🏗️ Architecture



### Backend (Python)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Advanced ORM for database operations
- **AsyncIO**: Asynchronous processing for optimal performance
- **Pydantic**: Data validation and serialization
- **UV**: Fast, modern Python package management

### Frontend (React + TypeScript)
- **React 18**: Modern component-based UI framework
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vite**: Fast build tool and development server
- **Lucide React**: Beautiful, customizable icons

### AI & ML
- **OpenAI GPT-4**: Advanced language model for medical validation
- **Anthropic Claude**: Alternative AI provider
- **LangChain**: Framework for building LLM applications
- **LangGraph**: Agent orchestration and workflow management

## 📦 Installation

### Prerequisites
- Python 3.11+ 
- Node.js 18+
- Docker & Docker Compose (optional)
- UV package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Quick Start with UV

1. **Clone the repository**
   ```bash
   git clone https://github.com/devtechai/MedTechAi-RCM-MedCode-Assist-POC.git
   cd MedTechAi-RCM-MedCode-Assist-POC
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Initialize the application**
   ```bash
   uv run python scripts/init.py
   ```

4. **Run the development server**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

5. **Start the frontend**
   ```bash
   cd frontend/dlrcm-main
   npm install
   npm run dev
   ```

### Docker Deployment

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - PostgreSQL: localhost:5432
   - Redis: localhost:6379

## 🛠️ Development

### Available Commands

```bash
# Development
make dev          # Install development dependencies
make run          # Run development server
make test         # Run tests
make lint         # Run linting
make format       # Format code

# Docker
make docker-build  # Build Docker images
make docker-up    # Start services
make docker-down  # Stop services

# Utilities
make clean        # Clean cache files
make docs         # Generate documentation
make security     # Run security scans
```

### Project Structure

```
MedTechAi-RCM-MedCode-Assist-POC/
├── app/                          # Backend application
│   ├── agents/                   # AI agents
│   │   ├── base_agent.py
│   │   ├── medical_validator.py
│   │   └── claim_processor.py
│   ├── core/                     # Core functionality
│   │   ├── database.py
│   │   └── __init__.py
│   ├── models/                   # SQLAlchemy models
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Business logic
│   ├── api/                      # API routes
│   └── utils/                    # Utilities
├── frontend/dlrcm-main/          # React frontend
├── config/                       # Configuration
├── scripts/                      # Utility scripts
├── tests/                        # Test suite
├── data/                         # Data storage
├── deployment/                   # Deployment configs
├── pyproject.toml               # UV project config
├── docker-compose.yml           # Docker services
└── Makefile                     # Development commands
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Application
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/medtechai_rcm

# AI Services
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### AI Model Configuration

The application supports multiple AI providers and models:

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3 Sonnet, Claude-3 Haiku

Configure in `config/settings.py` or environment variables.

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/v1/medical-codes/validate` - Validate medical codes
- `POST /api/v1/claims/process` - Process insurance claims
- `GET /api/v1/agents/health` - Agent health status
- `POST /api/v1/validation/batch` - Batch validation

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_medical_validator.py

# Run integration tests
uv run pytest -m integration
```

## 🚀 Deployment

### Production Deployment

1. **Configure environment**
   ```bash
   cp .env.example .env.production
   # Edit with production values
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Monitoring

The application includes comprehensive monitoring:
- **Prometheus metrics** at `/metrics`
- **Health checks** at `/health`
- **Structured logging** with JSON format
- **Error tracking** and performance metrics

## 🔐 Security

- **Input validation** with Pydantic
- **SQL injection protection** with SQLAlchemy ORM
- **Authentication** with JWT tokens
- **Environment-based configuration**
- **Security scanning** with Bandit

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write type hints for all functions
- Add tests for new features
- Update documentation as needed
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Anthropic** for Claude API
- **FastAPI** team for the excellent web framework
- **React** team for the component framework

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/devtechai/MedTechAi-RCM-MedCode-Assist-POC/wiki)
- **Issues**: [GitHub Issues](https://github.com/devtechai/MedTechAi-RCM-MedCode-Assist-POC/issues)
- **Teams**: [DevTechAI Support](mailto:support@devtechai.com)

---

**Built with ❤️ by the DevTechAI Team**
