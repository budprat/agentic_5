"""Generic Supabase client for A2A-MCP framework."""

import os
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Generic Supabase client for A2A-MCP framework."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role for full access
            
            if not url or not key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment")
            
            cls._instance = create_client(url, key)
        
        return cls._instance
    
    @classmethod
    def execute_query(cls, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a SQL query using Supabase RPC or direct query."""
        client = cls.get_client()
        
        # For complex queries, you might need to create PostgreSQL functions
        # and call them via RPC
        # return client.rpc('function_name', params).execute()
        
        # For simple queries, use the table operations
        # This is a placeholder - actual implementation depends on query type
        pass
    
    # Generic database operations
    def __init__(self):
        """Initialize with client."""
        self.client = self.get_client()
        
    async def select_records(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                           limit: Optional[int] = None, order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generic select records from table."""
        query = self.client.table(table).select("*")
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        if order_by:
            query = query.order(order_by, desc=True)
            
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        return response.data
        
    async def insert_record(self, table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic insert record into table."""
        response = self.client.table(table).insert(data).execute()
        return response.data[0] if response.data else None
        
    async def update_record(self, table: str, record_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generic update record in table."""
        response = self.client.table(table).update(data).eq('id', record_id).execute()
        return response.data[0] if response.data else None
        
    async def delete_record(self, table: str, record_id: str) -> bool:
        """Generic delete record from table."""
        response = self.client.table(table).delete().eq('id', record_id).execute()
        return len(response.data) > 0
    
    async def count_records(self, table: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Generic count records in table."""
        query = self.client.table(table).select("id", count="exact")
        
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
                
        response = query.execute()
        return response.count
    
    # Helper methods for common patterns
    async def get_user_records(self, table: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get records belonging to a specific user."""
        return await self.select_records(table, {"user_id": user_id}, limit=limit)
    
    async def get_recent_records(self, table: str, limit: int = 10, created_field: str = "created_at") -> List[Dict[str, Any]]:
        """Get most recent records from table."""
        return await self.select_records(table, limit=limit, order_by=created_field)
    
    async def search_records(self, table: str, search_field: str, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search records by field containing term."""
        # Note: This uses simple equality - for text search you might need PostgreSQL full-text search
        return await self.select_records(table, {search_field: search_term}, limit=limit)