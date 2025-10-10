"""
Base agent class for all AI agents in the MedTechAi RCM system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
import logging

from config import settings


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Provides common functionality and structure for all agents including:
    - Configuration management
    - Error handling
    - Performance monitoring
    - Token usage tracking
    """
    
    def __init__(
        self,
        agent_name: str,
        model_name: str = "gpt-4",
        provider: str = "openai",
        **kwargs
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_name: Unique identifier for the agent
            model_name: AI model to use (e.g., gpt-4, claude-3)
            provider: AI provider (e.g., openai, anthropic)
            **kwargs: Additional configuration parameters
        """
        self.agent_name = agent_name
        self.model_name = model_name
        self.provider = provider
        self.config = kwargs
        
        # Performance tracking
        self.total_requests = 0
        self.total_tokens_used = 0
        self.average_processing_time = 0.0
        
        # Error tracking
        self.request_errors = 0
        self.last_error_time = None
        
        logger.info(f"Initialized agent: {self.agent_name} ({self.provider}:{self.model_name})")
    
    @abstractmethod
    async def process(self, input_data: Any, **kwargs) -> Any:
        """
        Process input data using the agent's AI capabilities.
        
        Args:
            input_data: Input data to process
            **kwargs: Additional processing parameters
            
        Returns:
            Processed result
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent health status.
        
        Returns:
            Dictionary containing health status information
        """
        return {
            "agent_name": self.agent_name,
            "status": "healthy",
            "model": self.model_name,
            "provider": self.provider,
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "average_processing_time_ms": self.average_processing_time,
            "error_rate": self.request_errors / max(1, self.total_requests),
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get performance metrics for the agent.
        
        Returns:
            Dictionary containing performance metrics
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "average_processing_time_ms": self.average_processing_time,
            "error_rate": self.request_errors / max(1, self.total_requests),
        }
    
    def _update_metrics(self, processing_time_ms: float, tokens_used: int, success: bool = True):
        """
        Update internal performance metrics.
        
        Args:
            processing_time_ms: Request processing time in milliseconds
            tokens_used: Number of tokens consumed
            success: Whether the request was successful
        """
        self.total_requests += 1
        self.total_tokens_used += tokens_used
        
        # Update average processing time (exponential moving average)
        if self.total_requests == 1:
            self.average_processing_time = processing_time_ms
        else:
            alpha = 0.1  # Smoothing factor
            self.average_processing_time = (
                alpha * processing_time_ms + 
                (1 - alpha) * self.average_processing_time
            )
        
        if not success:
            self.request_errors += 1
            self.last_error_time = datetime.utcnow()
    
    async def _retry_with_backoff(self, func, *args, max_retries: int = 3, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            max_retries: Maximum number of retry attempts
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"Max retries exceeded for {self.agent_name}: {str(e)}")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"Attempt {attempt + 1} failed for {self.agent_name}, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.agent_name}', model='{self.model_name}')>"
