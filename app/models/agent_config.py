"""
Agent configuration model for AI agent settings and management.
"""
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, Float, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AgentType(str, enum.Enum):
    """Agent type enumeration."""
    MEDICAL_CODE_VALIDATOR = "MEDICAL_CODE_VALIDATOR"
    CLAIM_PROCESSOR = "CLAIM_PROCESSER"
    DENIAL_ANALYZER = "DENIAL_ANALYZER"
    APPEAL_GENERATOR = "APPEAL_GENERATOR"
    POLICY_CHECKER = "POLICY_CHECKER"


class AgentStatus(str, enum.Enum):
    """Agent status enumeration."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"


class AgentConfig(Base):
    """Agent configuration model for managing AI agents."""
    
    __tablename__ = "agent_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Agent identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    agent_type = Column(Enum(AgentType), nullable=False)
    description = Column(Text, nullable=True)
    
    # Agent configuration
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE)
    provider = Column(String(50), nullable=False)  # e.g., "openai", "anthropic"
    model_name = Column(String(100), nullable=False)  # e.g., "gpt-4", "claude-3"
    
    # Performance settings
    max_concurrent_requests = Column(Integer, default=10)
    timeout_seconds = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)
    
    # Validation thresholds
    confidence_threshold = Column(Float, default=0.85)
    auto_correction_enabled = Column(Boolean, default=True)
    
    # Specialized settings
    supported_code_types = Column(Text, nullable=True)  # JSON string
    validation_rules = Column(Text, nullable=True)  # JSON string
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<AgentConfig(name='{self.name}', type='{self.agent_type}', status='{self.status}')>"
