"""
Application configuration settings.
"""
import os
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Basic App Configuration
    app_name: str = "MedTechAi RCM Assistant"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True
    
    # Database Configuration
    database_url: str = "sqlite:///./medtechai_rcm.db"  # Default for local dev
    
    # AI Service Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai|anthropic|google
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-large"
    
    # Authentication Configuration
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Medical API Configuration
    cms_api_url: str = "https://api.cms.gov/v1/"
    cpt_api_key: Optional[str] = None
    icd10_api_key: Optional[str] = None
    
    # Insurance Payer APIs
    medicare_api_url: str = "https://api.medicare.gov/v1/"
    medicaid_api_url: str = "https://api.medicaid.gov/v1/"
    commercial_payer_api_url: str = "https://api.payer.com/v1/"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Monitoring Configuration
    prometheus_enabled: bool = True
    metrics_port: int = 8000
    enable_structlog: bool = True

    # RAG / Vector Store
    rag_enabled: bool = True
    vector_store: str = "chroma"  # chroma|faiss
    vector_db_dir: str = "./rag_index"
    ingest_docs_dir: str = "./docs"
    chunk_size: int = 1200
    chunk_overlap: int = 150
    
    # Rate Limiting
    request_rate_limit: int = 100  # requests per minute
    batch_processing_limit: int = 50  # medical codes per batch
    
    # Medical Code Validation Configuration
    supported_code_types: List[str] = ["CPT", "ICD10", "HCPCS"]
    auto_correction_enabled: bool = True
    confidence_threshold: float = 0.85
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
    
    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v
    
    @validator("confidence_threshold")
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
