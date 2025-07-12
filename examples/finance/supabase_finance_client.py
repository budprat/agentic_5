"""Supabase client configuration for Financial/Market Oracle domain."""

import os
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FinanceSupabaseClient:
    """Supabase client for Financial Market Oracle domain."""
    
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
    
    # Add instance methods for easier use
    def __init__(self):
        """Initialize with client."""
        self.client = self.get_client()
        
    async def get_portfolios(self, user_id: str, limit: int = 10) -> list:
        """Get portfolios for a user."""
        response = self.client.table('portfolios').select("*").eq('user_id', user_id).limit(limit).execute()
        return response.data
        
    async def get_positions(self, portfolio_id: str) -> list:
        """Get positions for a portfolio."""
        response = self.client.table('positions').select("*").eq('portfolio_id', portfolio_id).is_('exit_date', 'null').execute()
        return response.data
        
    async def get_latest_signals(self, limit: int = 10) -> list:
        """Get latest trading signals."""
        response = self.client.table('trading_signals').select("*").order('created_at', desc=True).limit(limit).execute()
        return response.data
    
    # Portfolio operations
    @classmethod
    async def create_portfolio(cls, user_id: str, total_value: float, cash_balance: float) -> Dict[str, Any]:
        """Create a new portfolio."""
        client = cls.get_client()
        
        data = {
            'user_id': user_id,
            'total_value': total_value,
            'cash_balance': cash_balance
        }
        
        response = client.table('portfolios').insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    async def get_portfolio(cls, portfolio_id: str) -> Dict[str, Any]:
        """Get portfolio by ID."""
        client = cls.get_client()
        
        response = client.table('portfolios').select("*").eq('id', portfolio_id).execute()
        return response.data[0] if response.data else None
    
    # Position operations
    @classmethod
    async def create_position(cls, portfolio_id: str, symbol: str, quantity: int, 
                            entry_price: float, position_type: str = 'long') -> Dict[str, Any]:
        """Create a new position."""
        client = cls.get_client()
        
        data = {
            'portfolio_id': portfolio_id,
            'symbol': symbol,
            'quantity': quantity,
            'entry_price': entry_price,
            'current_price': entry_price,
            'position_type': position_type
        }
        
        response = client.table('positions').insert(data).execute()
        return response.data[0] if response.data else None
    
    # Trading signal operations
    @classmethod
    async def create_trading_signal(cls, symbol: str, signal_type: str, confidence: float, 
                                  reasoning: str, data_sources: list) -> Dict[str, Any]:
        """Create a new trading signal."""
        client = cls.get_client()
        
        data = {
            'symbol': symbol,
            'signal_type': signal_type,
            'confidence': confidence,
            'reasoning': reasoning,
            'data_sources': data_sources
        }
        
        response = client.table('trading_signals').insert(data).execute()
        return response.data[0] if response.data else None
    
    # Research operations
    @classmethod
    async def store_research(cls, symbol: str, research_type: str, content: str, 
                           sources: list, analyst_rating: Optional[str] = None) -> Dict[str, Any]:
        """Store investment research."""
        client = cls.get_client()
        
        data = {
            'symbol': symbol,
            'research_type': research_type,
            'content': content,
            'sources': sources,
            'analyst_rating': analyst_rating
        }
        
        response = client.table('investment_research').insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    async def get_sentiment_summary(cls, symbol: str) -> Dict[str, Any]:
        """Get sentiment summary for a symbol."""
        client = cls.get_client()
        
        response = client.table('sentiment_analysis').select("*").eq('symbol', symbol).order('created_at', desc=True).limit(1).execute()
        return response.data[0] if response.data else None