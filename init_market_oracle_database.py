#!/usr/bin/env python3
"""Initialize the Market Oracle investment database with schema and sample data."""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_FILE = 'market_oracle.db'

def init_database():
    """Create and populate the market oracle database."""
    
    # Remove existing database if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    # Create new database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            total_value DECIMAL(15,2),
            cash_balance DECIMAL(15,2),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            symbol TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            entry_price DECIMAL(10,4),
            current_price DECIMAL(10,4),
            entry_date TIMESTAMP,
            exit_date TIMESTAMP,
            exit_price DECIMAL(10,4),
            profit_loss DECIMAL(10,2),
            position_type TEXT DEFAULT 'long',
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE trading_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            signal_type TEXT NOT NULL,
            confidence_score DECIMAL(3,2),
            agent_name TEXT NOT NULL,
            reasoning TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE sentiment_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            source TEXT NOT NULL,
            sentiment_score DECIMAL(3,2),
            volume_score INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE risk_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            var_95 DECIMAL(10,2),
            sharpe_ratio DECIMAL(5,2),
            max_drawdown DECIMAL(5,2),
            correlation_score DECIMAL(3,2),
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE investment_research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            thesis_summary TEXT,
            target_price DECIMAL(10,2),
            confidence_level TEXT,
            fundamental_score DECIMAL(3,2),
            technical_score DECIMAL(3,2),
            sentiment_score DECIMAL(3,2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE market_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            search_term TEXT NOT NULL,
            trend_score INTEGER,
            correlation_coefficient DECIMAL(3,2),
            lead_lag_days INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE audio_briefings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER,
            briefing_type TEXT NOT NULL,
            audio_url TEXT,
            transcript TEXT,
            duration_seconds INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
        )
    ''')
    
    # Insert sample data
    
    # Sample portfolios
    portfolios_data = [
        ('user_001', 100000.00, 50000.00),
        ('user_002', 250000.00, 75000.00),
        ('demo_user', 50000.00, 25000.00)
    ]
    
    cursor.executemany(
        'INSERT INTO portfolios (user_id, total_value, cash_balance) VALUES (?, ?, ?)',
        portfolios_data
    )
    
    # Sample positions
    positions_data = [
        (1, 'AAPL', 100, 150.00, 175.00, datetime.now() - timedelta(days=30), None, None, 2500.00, 'long'),
        (1, 'TSLA', 50, 200.00, 180.00, datetime.now() - timedelta(days=15), None, None, -1000.00, 'long'),
        (2, 'GOOGL', 75, 100.00, 120.00, datetime.now() - timedelta(days=60), None, None, 1500.00, 'long'),
        (2, 'MSFT', 200, 300.00, 350.00, datetime.now() - timedelta(days=45), None, None, 10000.00, 'long'),
        (2, 'NVDA', 30, 400.00, 450.00, datetime.now() - timedelta(days=20), None, None, 1500.00, 'long')
    ]
    
    for pos in positions_data:
        cursor.execute(
            '''INSERT INTO positions (portfolio_id, symbol, quantity, entry_price, 
               current_price, entry_date, exit_date, exit_price, profit_loss, position_type) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            pos
        )
    
    # Sample trading signals
    symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'META', 'AMZN']
    agents = ['sentiment_seeker', 'fundamental_analyst', 'technical_prophet', 'trend_correlator']
    signal_types = ['buy', 'sell', 'hold']
    
    for _ in range(20):
        symbol = random.choice(symbols)
        agent = random.choice(agents)
        signal = random.choice(signal_types)
        confidence = round(random.uniform(0.5, 0.95), 2)
        reasoning = f"Strong {signal} signal based on {agent} analysis"
        
        cursor.execute(
            '''INSERT INTO trading_signals (symbol, signal_type, confidence_score, 
               agent_name, reasoning) VALUES (?, ?, ?, ?, ?)''',
            (symbol, signal, confidence, agent, reasoning)
        )
    
    # Sample sentiment data
    sources = ['reddit', 'twitter', 'news']
    for symbol in symbols:
        for source in sources:
            sentiment = round(random.uniform(-0.5, 0.8), 2)
            volume = random.randint(50, 500)
            cursor.execute(
                '''INSERT INTO sentiment_data (symbol, source, sentiment_score, volume_score) 
                   VALUES (?, ?, ?, ?)''',
                (symbol, source, sentiment, volume)
            )
    
    # Sample risk metrics
    for portfolio_id in [1, 2, 3]:
        var_95 = round(random.uniform(1000, 5000), 2)
        sharpe = round(random.uniform(0.5, 2.5), 2)
        drawdown = round(random.uniform(0.05, 0.15), 2)
        correlation = round(random.uniform(0.2, 0.6), 2)
        
        cursor.execute(
            '''INSERT INTO risk_metrics (portfolio_id, var_95, sharpe_ratio, 
               max_drawdown, correlation_score) VALUES (?, ?, ?, ?, ?)''',
            (portfolio_id, var_95, sharpe, drawdown, correlation)
        )
    
    # Sample investment research
    research_data = [
        ('AAPL', 'Strong buy based on services growth and margin expansion', 200.00, 'high', 0.85, 0.75, 0.80),
        ('TSLA', 'Hold pending clarity on margin pressures and competition', 250.00, 'medium', 0.70, 0.65, 0.85),
        ('GOOGL', 'Buy on AI leadership and cloud growth acceleration', 150.00, 'high', 0.90, 0.80, 0.70),
        ('MSFT', 'Strong buy on enterprise AI adoption and Azure momentum', 400.00, 'high', 0.95, 0.85, 0.75),
        ('NVDA', 'Buy but monitor valuation after massive run-up', 550.00, 'medium', 0.80, 0.70, 0.90)
    ]
    
    for research in research_data:
        cursor.execute(
            '''INSERT INTO investment_research (symbol, thesis_summary, target_price, 
               confidence_level, fundamental_score, technical_score, sentiment_score) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            research
        )
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Database '{DB_FILE}' initialized successfully!")
    
    # Verify data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM portfolios")
    portfolio_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM positions")
    position_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM trading_signals")
    signal_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sentiment_data")
    sentiment_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM investment_research")
    research_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"Inserted {portfolio_count} portfolios, {position_count} positions")
    print(f"Inserted {signal_count} trading signals, {sentiment_count} sentiment records")
    print(f"Inserted {research_count} investment research records")


if __name__ == "__main__":
    init_database()