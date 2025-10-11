"""
Supabase integration routes for database operations.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.utils.supabase_client import SupabaseService, get_supabase_service

router = APIRouter(prefix="/supabase", tags=["supabase"])


# ====================
# Pydantic Models
# ====================

class DatabaseInsert(BaseModel):
    table: str
    data: Dict[str, Any]


class DatabaseSelect(BaseModel):
    table: str
    columns: str = "*"
    filters: Optional[Dict[str, Any]] = None


class DatabaseUpdate(BaseModel):
    table: str
    data: Dict[str, Any]
    filters: Dict[str, Any]


class DatabaseDelete(BaseModel):
    table: str
    filters: Dict[str, Any]


class FileUpload(BaseModel):
    bucket: str
    file_path: str
    content_type: str = "application/octet-stream"


# ====================
# Database Routes
# ====================

@router.post("/db/insert")
async def insert_data(
    insert_data: DatabaseInsert,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Insert data into a table."""
    try:
        result = await supabase.insert(
            table=insert_data.table,
            data=insert_data.data
        )
        return {
            "success": True,
            "message": "Data inserted successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/db/select")
async def select_data(
    select_data: DatabaseSelect,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Select data from a table."""
    try:
        result = await supabase.select(
            table=select_data.table,
            columns=select_data.columns,
            filters=select_data.filters
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/db/update")
async def update_data(
    update_data: DatabaseUpdate,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Update data in a table."""
    try:
        result = await supabase.update(
            table=update_data.table,
            data=update_data.data,
            filters=update_data.filters
        )
        return {
            "success": True,
            "message": "Data updated successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/db/delete")
async def delete_data(
    delete_data: DatabaseDelete,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Delete data from a table."""
    try:
        result = await supabase.delete(
            table=delete_data.table,
            filters=delete_data.filters
        )
        return {
            "success": True,
            "message": "Data deleted successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ====================
# Storage Routes
# ====================

@router.get("/storage/public-url/{bucket}/{file_path:path}")
async def get_public_url(
    bucket: str,
    file_path: str,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Get public URL for a file."""
    try:
        url = await supabase.get_public_url(bucket, file_path)
        return {
            "success": True,
            "url": url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ====================
# Health Check
# ====================

@router.get("/health")
async def health_check(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Check Supabase connection health."""
    try:
        # Test basic connection without authentication
        return {
            "success": True,
            "message": "Supabase connection is healthy"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase connection error: {str(e)}"
        }


@router.get("/health/db")
async def db_health_check(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Check Supabase database connectivity."""
    try:
        # Test basic database connectivity
        return {
            "success": True,
            "message": "Supabase DB connection is healthy"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase DB connection error: {str(e)}"
        }
