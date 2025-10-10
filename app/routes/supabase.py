"""
Supabase integration routes.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from app.utils.supabase_client import SupabaseService, get_supabase_service

router = APIRouter(prefix="/supabase", tags=["supabase"])


# ====================
# Pydantic Models
# ====================

class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    user_metadata: Optional[Dict[str, Any]] = None


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


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
# Authentication Routes
# ====================

@router.post("/auth/signup")
async def sign_up(
    user_data: UserSignUp,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Sign up a new user."""
    try:
        result = await supabase.sign_up(
            email=user_data.email,
            password=user_data.password,
            user_metadata=user_data.user_metadata
        )
        return {
            "success": True,
            "message": "User signed up successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/auth/signin")
async def sign_in(
    user_data: UserSignIn,
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Sign in a user."""
    try:
        result = await supabase.sign_in(
            email=user_data.email,
            password=user_data.password
        )
        return {
            "success": True,
            "message": "User signed in successfully",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/auth/signout")
async def sign_out(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Sign out the current user."""
    try:
        await supabase.sign_out()
        return {
            "success": True,
            "message": "User signed out successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/auth/user")
async def get_current_user(
    supabase: SupabaseService = Depends(get_supabase_service)
):
    """Get current user information."""
    try:
        user = await supabase.get_user()
        if user:
            return {
                "success": True,
                "data": user
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No authenticated user"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


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
        # Try to get current user to test connection
        user = await supabase.get_user()
        return {
            "success": True,
            "message": "Supabase connection is healthy",
            "authenticated": user is not None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Supabase connection error: {str(e)}",
            "authenticated": False
        }
