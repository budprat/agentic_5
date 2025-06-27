"""Supabase client configuration for Market Oracle."""

import os
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    """Singleton Supabase client for Market Oracle."""
    
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
    
    @classmethod
    async def get_positions(cls, portfolio_id: str) -> list:
        """Get all positions for a portfolio."""
        client = cls.get_client()
        
        response = client.table('positions').select("*").eq('portfolio_id', portfolio_id).execute()
        return response.data or []
    
    # Trading signal operations
    @classmethod
    async def create_trading_signal(cls, symbol: str, signal_type: str, 
                                  confidence_score: float, agent_name: str, 
                                  reasoning: str) -> Dict[str, Any]:
        """Create a trading signal."""
        client = cls.get_client()
        
        data = {
            'symbol': symbol,
            'signal_type': signal_type,
            'confidence_score': confidence_score,
            'agent_name': agent_name,
            'reasoning': reasoning
        }
        
        response = client.table('trading_signals').insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    async def get_latest_signals(cls, symbol: str, limit: int = 10) -> list:
        """Get latest trading signals for a symbol."""
        client = cls.get_client()
        
        response = (client.table('trading_signals')
                   .select("*")
                   .eq('symbol', symbol)
                   .order('created_at', desc=True)
                   .limit(limit)
                   .execute())
        return response.data or []
    
    # Sentiment data operations
    @classmethod
    async def create_sentiment_data(cls, symbol: str, source: str, 
                                  sentiment_score: float, volume_score: int) -> Dict[str, Any]:
        """Create sentiment data entry."""
        client = cls.get_client()
        
        data = {
            'symbol': symbol,
            'source': source,
            'sentiment_score': sentiment_score,
            'volume_score': volume_score
        }
        
        response = client.table('sentiment_data').insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    async def get_sentiment_summary(cls, symbol: str, hours: int = 24) -> Dict[str, Any]:
        """Get sentiment summary for a symbol over specified hours."""
        client = cls.get_client()
        
        # This would ideally be a PostgreSQL function for better performance
        # For now, fetch recent data and compute in Python
        response = (client.table('sentiment_data')
                   .select("*")
                   .eq('symbol', symbol)
                   .gte('timestamp', f'now() - interval \'{hours} hours\'')
                   .execute())
        
        data = response.data or []
        
        if not data:
            return {'avg_sentiment': 0, 'total_volume': 0, 'data_points': 0}
        
        avg_sentiment = sum(d['sentiment_score'] for d in data) / len(data)
        total_volume = sum(d['volume_score'] for d in data)
        
        return {
            'avg_sentiment': avg_sentiment,
            'total_volume': total_volume,
            'data_points': len(data)
        }
    
    # Investment research operations
    @classmethod
    async def create_research(cls, symbol: str, thesis_summary: str, 
                            target_price: float, confidence_level: str,
                            fundamental_score: float, technical_score: float,
                            sentiment_score: float) -> Dict[str, Any]:
        """Create investment research entry."""
        client = cls.get_client()
        
        # Ensure all numeric values are properly typed
        def safe_float(value, default=0.0):
            """Safely convert value to float."""
            if value is None:
                return default
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                if value.lower() in ['n/a', 'na', 'none', '']:
                    return default
                try:
                    return float(value.replace('$', '').replace(',', '').replace('%', ''))
                except ValueError:
                    return default
            return default
            
        data = {
            'symbol': symbol,
            'thesis_summary': thesis_summary,
            'target_price': safe_float(target_price),
            'confidence_level': confidence_level,
            'fundamental_score': safe_float(fundamental_score, 0.5),
            'technical_score': safe_float(technical_score, 0.5),
            'sentiment_score': safe_float(sentiment_score, 0.0)
        }
        
        response = client.table('investment_research').insert(data).execute()
        return response.data[0] if response.data else None
    
    @classmethod
    async def get_latest_research(cls, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest research for a symbol."""
        client = cls.get_client()
        
        response = (client.table('investment_research')
                   .select("*")
                   .eq('symbol', symbol)
                   .order('created_at', desc=True)
                   .limit(1)
                   .execute())
        
        return response.data[0] if response.data else None
    
    # Risk metrics operations
    @classmethod
    async def create_risk_metrics(cls, portfolio_id: str, var_95: float,
                                sharpe_ratio: float, max_drawdown: float,
                                correlation_score: float) -> Dict[str, Any]:
        """Create risk metrics entry."""
        client = cls.get_client()
        
        data = {
            'portfolio_id': portfolio_id,
            'var_95': var_95,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'correlation_score': correlation_score
        }
        
        response = client.table('risk_metrics').insert(data).execute()
        return response.data[0] if response.data else None