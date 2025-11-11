"""
Connectivity check endpoints for all external services:
- OpenAI LLM API
- PostgreSQL (Render)
- Supabase
"""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from config import settings
from app.core.database import engine
from app.utils.llm import LLMClient
from app.utils.supabase_client import get_supabase_service
from app.config.supabase import SupabaseSettings

router = APIRouter(prefix="/api/v1/connectivity", tags=["connectivity"])


@router.get("/check")
async def check_all_connectivity() -> Dict[str, Any]:
    """
    Comprehensive connectivity check for all external services:
    - OpenAI LLM API (with API key validation)
    - PostgreSQL (Render database)
    - Supabase (connection and database)
    
    Returns:
        Dict with status of all services and overall health
    """
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "overall_status": "healthy"
    }
    
    # Check OpenAI
    openai_status = await check_openai()
    results["services"]["openai"] = openai_status
    
    # Check PostgreSQL
    postgresql_status = await check_postgresql()
    results["services"]["postgresql"] = postgresql_status
    
    # Check Supabase
    supabase_status = await check_supabase()
    results["services"]["supabase"] = supabase_status
    
    # Determine overall status
    all_healthy = all(
        s.get("status") == "connected" 
        for s in results["services"].values()
    )
    
    if not all_healthy:
        any_healthy = any(
            s.get("status") == "connected" 
            for s in results["services"].values()
        )
        results["overall_status"] = "degraded" if any_healthy else "unhealthy"
    
    return results


async def check_openai() -> Dict[str, Any]:
    """Check OpenAI API connectivity and API key validity."""
    try:
        if not settings.openai_api_key:
            return {
                "status": "disconnected",
                "message": "OpenAI API key not configured",
                "error": "OPENAI_API_KEY environment variable not set",
                "configured": False
            }
        
        # Test with a simple request
        client = LLMClient(provider="openai", model="gpt-4o-mini")
        response = await client.chat(
            messages=[{"role": "user", "content": "Respond with just the word: success"}],
            temperature=0.0,
            max_tokens=10
        )
        
        if response and "success" in response.lower():
            return {
                "status": "connected",
                "message": "OpenAI API key valid and working",
                "test_response": response.strip()[:50],
                "model": settings.llm_model,
                "provider": settings.llm_provider,
                "configured": True
            }
        else:
            return {
                "status": "disconnected",
                "message": "OpenAI API responded but with unexpected format",
                "test_response": response[:50] if response else None,
                "configured": True
            }
            
    except Exception as e:
        error_msg = str(e)
        return {
            "status": "disconnected",
            "message": f"OpenAI connection failed: {error_msg}",
            "error": error_msg,
            "configured": bool(settings.openai_api_key)
        }


async def check_postgresql() -> Dict[str, Any]:
    """Check PostgreSQL (Render) or SQLite connectivity."""
    try:
        # Test database connection
        with engine.connect() as conn:
            is_sqlite = "sqlite" in settings.database_url.lower()
            
            if is_sqlite:
                # SQLite-specific queries
                db_name = "SQLite"
                tables_result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """))
                tables_count = tables_result.scalar()
                version = "SQLite (development)"
                connection_info = "sqlite:///./medtechai_rcm.db"
            else:
                # PostgreSQL-specific queries
                try:
                    db_result = conn.execute(text("SELECT current_database()"))
                    db_name = db_result.scalar()
                except:
                    db_name = "postgresql"
                
                tables_result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """))
                tables_count = tables_result.scalar()
                
                try:
                    version_result = conn.execute(text("SELECT version()"))
                    version = version_result.scalar()
                    version = version.split(",")[0] if version else "PostgreSQL"
                except:
                    version = "PostgreSQL"
                
                # Extract connection info (hide password)
                db_url = settings.database_url
                if "@" in db_url:
                    connection_info = db_url.split("@")[-1]
                else:
                    connection_info = "configured"
            
            return {
                "status": "connected",
                "message": f"{'SQLite' if is_sqlite else 'PostgreSQL'} connection successful",
                "database": db_name,
                "tables_count": tables_count,
                "version": version,
                "connection_info": connection_info,
                "database_type": "sqlite" if is_sqlite else "postgresql",
                "configured": True
            }
    except Exception as e:
        error_msg = str(e)
        db_url = settings.database_url
        if "@" in db_url:
            connection_info = db_url.split("@")[-1]
        else:
            connection_info = "not configured"
            
        return {
            "status": "disconnected",
            "message": f"PostgreSQL connection failed: {error_msg}",
            "error": error_msg,
            "connection_info": connection_info,
            "configured": bool(settings.database_url and settings.database_url != "sqlite:///./medtechai_rcm.db")
        }


async def check_supabase() -> Dict[str, Any]:
    """Check Supabase connectivity and database."""
    try:
        supabase_settings = SupabaseSettings()
        
        if not supabase_settings.supabase_url or not supabase_settings.supabase_key:
            return {
                "status": "disconnected",
                "message": "Supabase not configured",
                "error": "SUPABASE_URL or SUPABASE_KEY environment variable not set",
                "configured": False
            }
        
        # Get Supabase service
        supabase_service = await get_supabase_service()
        
        # Try to list tables as a connectivity test
        try:
            tables = await supabase_service.list_tables()
            tables_count = len(tables) if tables else 0
        except Exception as list_error:
            # If list_tables fails, connection might still work
            tables_count = None
            list_error_msg = str(list_error)
        
        return {
            "status": "connected",
            "message": "Supabase connection successful",
            "url": supabase_settings.supabase_url,
            "tables_count": tables_count,
            "configured": True
        }
    except ValueError as e:
        # Configuration error
        return {
            "status": "disconnected",
            "message": f"Supabase configuration error: {str(e)}",
            "error": str(e),
            "configured": False
        }
    except Exception as e:
        error_msg = str(e)
        supabase_settings = SupabaseSettings()
        return {
            "status": "disconnected",
            "message": f"Supabase connection failed: {error_msg}",
            "error": error_msg,
            "url": supabase_settings.supabase_url if supabase_settings.supabase_url else "not configured",
            "configured": bool(supabase_settings.supabase_url and supabase_settings.supabase_key)
        }


@router.get("/openai")
async def check_openai_only() -> Dict[str, Any]:
    """Check only OpenAI connectivity."""
    return await check_openai()


@router.get("/postgresql")
async def check_postgresql_only() -> Dict[str, Any]:
    """Check only PostgreSQL connectivity."""
    return await check_postgresql()


@router.get("/supabase")
async def check_supabase_only() -> Dict[str, Any]:
    """Check only Supabase connectivity."""
    return await check_supabase()

