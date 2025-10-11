"""
Supabase client utilities and helper functions.
"""
from typing import Any, Dict, List, Optional, Union
import asyncio
from supabase import Client
from app.config.supabase import get_supabase_client


class SupabaseService:
    """Service class for Supabase operations."""
    
    def __init__(self, client: Optional[Client] = None):
        """Initialize with Supabase client."""
        self.client = client or get_supabase_client()
    
    # ====================
    # Authentication Methods
    # ====================
    
    async def sign_up(self, email: str, password: str, user_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Sign up a new user.
        
        Args:
            email: User email
            password: User password
            user_metadata: Additional user metadata
            
        Returns:
            Dict containing user data and session
        """
        try:
            def _do():
                return self.client.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "data": user_metadata or {}
                    }
                })

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"Sign up failed: {str(e)}")
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Sign in a user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Dict containing user data and session
        """
        try:
            def _do():
                return self.client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"Sign in failed: {str(e)}")
    
    async def sign_out(self) -> None:
        """Sign out the current user."""
        try:
            await asyncio.to_thread(self.client.auth.sign_out)
        except Exception as e:
            raise Exception(f"Sign out failed: {str(e)}")
    
    async def get_user(self) -> Optional[Dict[str, Any]]:
        """Get current user."""
        try:
            def _do():
                return self.client.auth.get_user()

            response = await asyncio.to_thread(_do)
            return response.user if getattr(response, "user", None) else None
        except Exception as e:
            raise Exception(f"Get user failed: {str(e)}")
    
    # ====================
    # Database Methods
    # ====================
    
    async def insert(self, table: str, data: Union[Dict, List[Dict]]) -> Dict[str, Any]:
        """
        Insert data into a table.
        
        Args:
            table: Table name
            data: Data to insert (dict or list of dicts)
            
        Returns:
            Inserted data
        """
        try:
            def _do():
                return self.client.table(table).insert(data).execute()

            response = await asyncio.to_thread(_do)
            return response.data
        except Exception as e:
            raise Exception(f"Insert failed: {str(e)}")
    
    async def select(self, table: str, columns: str = "*", filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Select data from a table.
        
        Args:
            table: Table name
            columns: Columns to select (default: "*")
            filters: Filter conditions
            
        Returns:
            List of records
        """
        try:
            def _do():
                query = self.client.table(table).select(columns)

                if filters:
                    for key, value in filters.items():
                        if isinstance(value, dict):
                            # Handle operators like {'gte': 10}
                            for op, val in value.items():
                                query = getattr(query, op)(key, val)
                        else:
                            query = query.eq(key, value)

                response = query.execute()
                return response.data

            response_data = await asyncio.to_thread(_do)
            return response_data
        except Exception as e:
            raise Exception(f"Select failed: {str(e)}")
    
    async def update(self, table: str, data: Dict, filters: Dict) -> List[Dict[str, Any]]:
        """
        Update data in a table.
        
        Args:
            table: Table name
            data: Data to update
            filters: Filter conditions
            
        Returns:
            Updated records
        """
        try:
            def _do():
                query = self.client.table(table).update(data)

                for key, value in filters.items():
                    query = query.eq(key, value)

                response = query.execute()
                return response.data

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"Update failed: {str(e)}")
    
    async def delete(self, table: str, filters: Dict) -> List[Dict[str, Any]]:
        """
        Delete data from a table.
        
        Args:
            table: Table name
            filters: Filter conditions
            
        Returns:
            Deleted records
        """
        try:
            def _do():
                query = self.client.table(table).delete()

                for key, value in filters.items():
                    query = query.eq(key, value)

                response = query.execute()
                return response.data

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"Delete failed: {str(e)}")
    
    # ====================
    # Storage Methods
    # ====================
    
    async def upload_file(self, bucket: str, file_path: str, file_data: bytes, content_type: str = "application/octet-stream") -> Dict[str, Any]:
        """
        Upload a file to Supabase Storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path in the bucket
            file_data: File data as bytes
            content_type: MIME type
            
        Returns:
            Upload response
        """
        try:
            def _do():
                return self.client.storage.from_(bucket).upload(
                    path=file_path,
                    file=file_data,
                    file_options={"content-type": content_type}
                )

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"File upload failed: {str(e)}")
    
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """
        Download a file from Supabase Storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path in the bucket
            
        Returns:
            File data as bytes
        """
        try:
            def _do():
                return self.client.storage.from_(bucket).download(file_path)

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"File download failed: {str(e)}")
    
    async def delete_file(self, bucket: str, file_path: str) -> Dict[str, Any]:
        """
        Delete a file from Supabase Storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Path in the bucket
            
        Returns:
            Delete response
        """
        try:
            def _do():
                return self.client.storage.from_(bucket).remove([file_path])

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"File delete failed: {str(e)}")
    
    async def get_public_url(self, bucket: str, file_path: str) -> str:
        """
        Get public URL for a file.
        
        Args:
            bucket: Storage bucket name
            file_path: Path in the bucket
            
        Returns:
            Public URL
        """
        try:
            def _do():
                return self.client.storage.from_(bucket).get_public_url(file_path)

            response = await asyncio.to_thread(_do)
            return response
        except Exception as e:
            raise Exception(f"Get public URL failed: {str(e)}")


# Global service instance
supabase_service = SupabaseService()


# Convenience functions
async def get_supabase_service() -> SupabaseService:
    """Get Supabase service instance."""
    return supabase_service
