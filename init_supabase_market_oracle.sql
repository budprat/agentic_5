-- Market Oracle Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing tables if they exist (be careful in production!)
DROP TABLE IF EXISTS audio_briefings CASCADE;
DROP TABLE IF EXISTS market_trends CASCADE;
DROP TABLE IF EXISTS investment_research CASCADE;
DROP TABLE IF EXISTS risk_metrics CASCADE;
DROP TABLE IF EXISTS sentiment_data CASCADE;
DROP TABLE IF EXISTS trading_signals CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS portfolios CASCADE;

-- Create portfolios table
CREATE TABLE portfolios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    total_value DECIMAL(15,2),
    cash_balance DECIMAL(15,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create positions table
CREATE TABLE positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(10,4),
    current_price DECIMAL(10,4),
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exit_date TIMESTAMP,
    exit_price DECIMAL(10,4),
    profit_loss DECIMAL(10,2),
    position_type TEXT DEFAULT 'long',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trading signals table
CREATE TABLE trading_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL CHECK (signal_type IN ('buy', 'sell', 'hold')),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    agent_name TEXT NOT NULL,
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sentiment data table
CREATE TABLE sentiment_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT NOT NULL,
    source TEXT NOT NULL,
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    volume_score INTEGER CHECK (volume_score >= 0),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create risk metrics table
CREATE TABLE risk_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    var_95 DECIMAL(10,2),
    sharpe_ratio DECIMAL(5,2),
    max_drawdown DECIMAL(5,2),
    correlation_score DECIMAL(3,2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create investment research table
CREATE TABLE investment_research (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT NOT NULL,
    thesis_summary TEXT,
    target_price DECIMAL(10,2),
    confidence_level TEXT CHECK (confidence_level IN ('high', 'medium', 'low')),
    fundamental_score DECIMAL(3,2) CHECK (fundamental_score >= 0 AND fundamental_score <= 1),
    technical_score DECIMAL(3,2) CHECK (technical_score >= 0 AND technical_score <= 1),
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create market trends table
CREATE TABLE market_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol TEXT NOT NULL,
    search_term TEXT NOT NULL,
    trend_score INTEGER,
    correlation_coefficient DECIMAL(3,2),
    lead_lag_days INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audio briefings table
CREATE TABLE audio_briefings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    portfolio_id UUID REFERENCES portfolios(id) ON DELETE CASCADE,
    briefing_type TEXT NOT NULL,
    audio_url TEXT,
    transcript TEXT,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_positions_portfolio ON positions(portfolio_id);
CREATE INDEX idx_positions_symbol ON positions(symbol);
CREATE INDEX idx_trading_signals_symbol ON trading_signals(symbol);
CREATE INDEX idx_trading_signals_created ON trading_signals(created_at DESC);
CREATE INDEX idx_sentiment_symbol_time ON sentiment_data(symbol, timestamp DESC);
CREATE INDEX idx_research_symbol ON investment_research(symbol);
CREATE INDEX idx_trends_symbol ON market_trends(symbol);

-- Enable Row Level Security (RLS)
ALTER TABLE portfolios ENABLE ROW LEVEL SECURITY;
ALTER TABLE positions ENABLE ROW LEVEL SECURITY;
ALTER TABLE trading_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE risk_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE investment_research ENABLE ROW LEVEL SECURITY;
ALTER TABLE market_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE audio_briefings ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (adjust based on your auth strategy)
-- For now, we'll create permissive policies for service role

-- Portfolios: Users can only see their own portfolios
CREATE POLICY "Service role has full access to portfolios" ON portfolios
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Users can view own portfolios" ON portfolios
    FOR SELECT USING (auth.uid()::text = user_id);

-- Positions: Inherit from portfolio access
CREATE POLICY "Service role has full access to positions" ON positions
    FOR ALL USING (auth.role() = 'service_role');

-- Trading signals: Public read, service write
CREATE POLICY "Service role has full access to signals" ON trading_signals
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Anyone can read signals" ON trading_signals
    FOR SELECT USING (true);

-- Sentiment data: Public read, service write
CREATE POLICY "Service role has full access to sentiment" ON sentiment_data
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Anyone can read sentiment" ON sentiment_data
    FOR SELECT USING (true);

-- Research: Public read, service write
CREATE POLICY "Service role has full access to research" ON investment_research
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Anyone can read research" ON investment_research
    FOR SELECT USING (true);

-- Similar policies for other tables
CREATE POLICY "Service role has full access to risk_metrics" ON risk_metrics
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to trends" ON market_trends
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role has full access to briefings" ON audio_briefings
    FOR ALL USING (auth.role() = 'service_role');

-- Create useful views
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT 
    p.id,
    p.user_id,
    p.total_value,
    p.cash_balance,
    COUNT(pos.id) as position_count,
    SUM(pos.profit_loss) as total_pnl,
    p.last_updated
FROM portfolios p
LEFT JOIN positions pos ON p.id = pos.portfolio_id AND pos.exit_date IS NULL
GROUP BY p.id;

-- Create function to calculate portfolio value
CREATE OR REPLACE FUNCTION calculate_portfolio_value(p_portfolio_id UUID)
RETURNS TABLE (
    total_value DECIMAL(15,2),
    positions_value DECIMAL(15,2),
    cash_balance DECIMAL(15,2),
    total_pnl DECIMAL(15,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.cash_balance + COALESCE(SUM(pos.quantity * pos.current_price), 0) as total_value,
        COALESCE(SUM(pos.quantity * pos.current_price), 0) as positions_value,
        p.cash_balance,
        COALESCE(SUM(pos.profit_loss), 0) as total_pnl
    FROM portfolios p
    LEFT JOIN positions pos ON p.id = pos.portfolio_id AND pos.exit_date IS NULL
    WHERE p.id = p_portfolio_id
    GROUP BY p.cash_balance;
END;
$$ LANGUAGE plpgsql;

-- Create function to get latest signals
CREATE OR REPLACE FUNCTION get_latest_signals_for_symbol(p_symbol TEXT, p_limit INTEGER DEFAULT 10)
RETURNS TABLE (
    signal_type TEXT,
    confidence_score DECIMAL(3,2),
    agent_name TEXT,
    reasoning TEXT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ts.signal_type,
        ts.confidence_score,
        ts.agent_name,
        ts.reasoning,
        ts.created_at
    FROM trading_signals ts
    WHERE ts.symbol = p_symbol
    ORDER BY ts.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Insert sample data for testing
INSERT INTO portfolios (user_id, total_value, cash_balance)
VALUES 
    ('demo_user', 100000.00, 50000.00),
    ('test_user', 250000.00, 100000.00);

-- Sample positions
INSERT INTO positions (portfolio_id, symbol, quantity, entry_price, current_price, profit_loss)
SELECT 
    p.id,
    'AAPL',
    100,
    150.00,
    175.00,
    2500.00
FROM portfolios p WHERE p.user_id = 'demo_user';

INSERT INTO positions (portfolio_id, symbol, quantity, entry_price, current_price, profit_loss)
SELECT 
    p.id,
    'TSLA',
    50,
    200.00,
    180.00,
    -1000.00
FROM portfolios p WHERE p.user_id = 'demo_user';

-- Sample trading signals
INSERT INTO trading_signals (symbol, signal_type, confidence_score, agent_name, reasoning)
VALUES 
    ('AAPL', 'buy', 0.85, 'fundamental_analyst', 'Strong earnings growth and expanding margins'),
    ('AAPL', 'buy', 0.75, 'sentiment_seeker', 'Positive Reddit sentiment with high volume'),
    ('TSLA', 'hold', 0.65, 'technical_prophet', 'RSI indicating overbought conditions'),
    ('GOOGL', 'buy', 0.90, 'fundamental_analyst', 'AI leadership position strengthening');

-- Sample sentiment data
INSERT INTO sentiment_data (symbol, source, sentiment_score, volume_score)
VALUES 
    ('AAPL', 'reddit', 0.75, 450),
    ('AAPL', 'twitter', 0.65, 320),
    ('TSLA', 'reddit', 0.85, 890),
    ('TSLA', 'twitter', -0.20, 560);

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;