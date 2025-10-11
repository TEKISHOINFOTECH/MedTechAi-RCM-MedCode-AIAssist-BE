"""
Supabase configuration and client setup.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from supabase import create_client, Client


class SupabaseSettings(BaseSettings):
    """Supabase configuration settings."""
    
    # Supabase Project Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    
    # Optional: Service Role Key for admin operations
    supabase_service_role_key: Optional[str] = None
    
    # Optional: JWT Secret for token verification
    supabase_jwt_secret: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = ""
        extra = "ignore"


# Global Supabase client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Get or create Supabase client instance.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ValueError: If Supabase URL or key is not configured
    """
    global _supabase_client
    
    if _supabase_client is None:
        settings = SupabaseSettings()
        
        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError(
                "Supabase URL and key must be configured. "
                "Please set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    return _supabase_client


def get_supabase_admin_client() -> Client:
    """
    Get Supabase admin client with service role key.
    
    Returns:
        Client: Supabase admin client instance
        
    Raises:
        ValueError: If service role key is not configured
    """
    settings = SupabaseSettings()
    
    if not settings.supabase_service_role_key:
        raise ValueError(
            "Supabase service role key must be configured. "
            "Please set SUPABASE_SERVICE_ROLE_KEY environment variable."
        )
    
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )


def reset_supabase_client():
    """Reset the global Supabase client instance."""
    global _supabase_client
    _supabase_client = None


# Convenience function for dependency injection
def get_supabase() -> Client:
    """Dependency function for FastAPI."""
    return get_supabase_client()
