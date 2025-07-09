-- AI Solopreneur System Database Schema
-- Comprehensive schema for all solopreneur-specific data

-- Drop existing tables if they exist
DROP TABLE IF EXISTS task_dependencies;
DROP TABLE IF EXISTS learning_resources;
DROP TABLE IF EXISTS learning_sessions;
DROP TABLE IF EXISTS skill_progress;
DROP TABLE IF EXISTS personal_metrics;
DROP TABLE IF EXISTS technical_intelligence;
DROP TABLE IF EXISTS knowledge_items;
DROP TABLE IF EXISTS research_papers;
DROP TABLE IF EXISTS code_repositories;
DROP TABLE IF EXISTS project_tasks;
DROP TABLE IF EXISTS energy_patterns;
DROP TABLE IF EXISTS focus_sessions;
DROP TABLE IF EXISTS workflow_optimizations;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS agent_interactions;

-- User preferences and profile
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value TEXT,
    category VARCHAR(50), -- 'technical', 'personal', 'learning', 'workflow'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, preference_key)
);

-- Personal optimization metrics
CREATE TABLE personal_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- 'energy', 'focus', 'productivity', 'stress'
    value FLOAT NOT NULL,
    context JSON, -- Additional context like task complexity, environment
    tags TEXT, -- Comma-separated tags
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_metric_type (metric_type)
);

-- Energy patterns and circadian rhythm tracking
CREATE TABLE energy_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    hour INTEGER NOT NULL CHECK (hour >= 0 AND hour <= 23),
    energy_level FLOAT CHECK (energy_level >= 0 AND energy_level <= 10),
    cognitive_capacity FLOAT CHECK (cognitive_capacity >= 0 AND cognitive_capacity <= 10),
    optimal_task_types TEXT, -- JSON array of task types
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date, hour)
);

-- Focus session tracking
CREATE TABLE focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    focus_score FLOAT,
    task_description TEXT,
    interruptions INTEGER DEFAULT 0,
    environment_factors JSON, -- noise level, lighting, temperature
    productivity_rating FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Technical intelligence and research tracking
CREATE TABLE technical_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source VARCHAR(100) NOT NULL, -- 'arxiv', 'github', 'hackernews', 'reddit'
    source_id VARCHAR(255), -- External ID from source
    title TEXT NOT NULL,
    summary TEXT,
    relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
    implementation_priority INTEGER CHECK (implementation_priority >= 1 AND implementation_priority <= 5),
    research_area VARCHAR(100),
    tags TEXT, -- Comma-separated tags
    url TEXT,
    published_date DATETIME,
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    INDEX idx_source_relevance (source, relevance_score),
    INDEX idx_research_area (research_area)
);

-- Research papers specific tracking
CREATE TABLE research_papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    arxiv_id VARCHAR(50) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT, -- JSON array
    abstract TEXT,
    categories TEXT, -- JSON array
    primary_category VARCHAR(50),
    published_date DATETIME,
    updated_date DATETIME,
    relevance_score FLOAT,
    implementation_potential FLOAT,
    reading_status VARCHAR(20) DEFAULT 'unread', -- 'unread', 'reading', 'completed'
    notes TEXT,
    key_insights TEXT, -- JSON array
    related_projects TEXT, -- JSON array of project IDs
    downloaded BOOLEAN DEFAULT FALSE,
    file_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Code repositories and GitHub tracking
CREATE TABLE code_repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_id INTEGER UNIQUE,
    full_name VARCHAR(255) NOT NULL, -- owner/repo
    description TEXT,
    language VARCHAR(50),
    stars INTEGER,
    forks INTEGER,
    open_issues INTEGER,
    topics TEXT, -- JSON array
    relevance_score FLOAT,
    monitoring BOOLEAN DEFAULT FALSE,
    last_commit_date DATETIME,
    last_release_date DATETIME,
    last_checked DATETIME,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge graph items
CREATE TABLE knowledge_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR(100) NOT NULL, -- 'technical', 'personal', 'learning', 'project'
    item_type VARCHAR(50) NOT NULL, -- 'concept', 'pattern', 'insight', 'connection'
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50), -- 'research', 'experience', 'analysis'
    source_id VARCHAR(255), -- Reference to source
    relevance_score FLOAT,
    confidence_score FLOAT,
    tags TEXT,
    connections JSON, -- Array of related knowledge item IDs
    metadata JSON, -- Additional structured data
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_domain_type (domain, item_type)
);

-- Learning and skill development
CREATE TABLE skill_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    skill_category VARCHAR(50), -- 'language', 'framework', 'concept', 'tool'
    current_level INTEGER CHECK (current_level >= 1 AND current_level <= 10),
    target_level INTEGER CHECK (target_level >= 1 AND target_level <= 10),
    hours_invested FLOAT DEFAULT 0,
    last_practice_date DATETIME,
    proficiency_score FLOAT,
    learning_resources TEXT, -- JSON array
    milestones JSON, -- Array of achieved milestones
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_name)
);

-- Learning sessions
CREATE TABLE learning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    skill_id INTEGER REFERENCES skill_progress(id),
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_minutes INTEGER,
    focus_score FLOAT,
    productivity_score FLOAT,
    topics_covered JSON, -- Array of topics
    resources_used JSON, -- Array of resources
    key_learnings TEXT,
    next_steps TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Learning resources
CREATE TABLE learning_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_type VARCHAR(50) NOT NULL, -- 'course', 'book', 'tutorial', 'documentation'
    title TEXT NOT NULL,
    url TEXT,
    platform VARCHAR(50), -- 'coursera', 'udemy', 'youtube', 'official_docs'
    skill_categories TEXT, -- JSON array
    difficulty_level INTEGER CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    estimated_hours FLOAT,
    completion_status VARCHAR(20) DEFAULT 'not_started',
    progress_percentage FLOAT DEFAULT 0,
    rating FLOAT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Project and task management
CREATE TABLE project_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    project_name VARCHAR(100),
    task_title TEXT NOT NULL,
    task_description TEXT,
    task_type VARCHAR(50), -- 'feature', 'bugfix', 'research', 'learning'
    complexity_score INTEGER CHECK (complexity_score >= 1 AND complexity_score <= 5),
    estimated_hours FLOAT,
    actual_hours FLOAT,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER CHECK (priority >= 1 AND priority <= 5),
    energy_requirement VARCHAR(20), -- 'high', 'medium', 'low'
    optimal_time_slots JSON, -- Array of optimal time slots
    dependencies JSON, -- Array of task IDs
    assigned_date DATETIME,
    start_date DATETIME,
    completion_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Task dependencies
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER REFERENCES project_tasks(id),
    depends_on_task_id INTEGER REFERENCES project_tasks(id),
    dependency_type VARCHAR(20), -- 'blocks', 'requires', 'related'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id)
);

-- Workflow optimizations and patterns
CREATE TABLE workflow_optimizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    optimization_type VARCHAR(50), -- 'schedule', 'task_order', 'tool_config', 'environment'
    title TEXT NOT NULL,
    description TEXT,
    impact_score FLOAT, -- Measured improvement
    confidence_score FLOAT,
    implementation_status VARCHAR(20) DEFAULT 'proposed',
    context JSON, -- Conditions when optimization applies
    metrics_before JSON,
    metrics_after JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agent interaction logs
CREATE TABLE agent_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) NOT NULL, -- 'orchestrator', 'technical', 'personal', 'learning'
    request_type VARCHAR(50),
    request_content TEXT,
    response_content TEXT,
    confidence_scores JSON, -- Array of confidence scores by domain
    execution_time_ms INTEGER,
    tokens_used INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_agent (user_id, agent_type),
    INDEX idx_created (created_at)
);

-- Create indexes for performance
CREATE INDEX idx_personal_metrics_user_time ON personal_metrics(user_id, timestamp);
CREATE INDEX idx_technical_intelligence_relevance ON technical_intelligence(relevance_score DESC);
CREATE INDEX idx_knowledge_items_domain ON knowledge_items(domain);
CREATE INDEX idx_skill_progress_user ON skill_progress(user_id);
CREATE INDEX idx_project_tasks_status ON project_tasks(status);
CREATE INDEX idx_agent_interactions_user ON agent_interactions(user_id);

-- Create views for common queries
CREATE VIEW daily_energy_summary AS
SELECT 
    user_id,
    date,
    AVG(energy_level) as avg_energy,
    AVG(cognitive_capacity) as avg_cognitive,
    MAX(energy_level) as peak_energy_hour,
    MIN(energy_level) as low_energy_hour
FROM energy_patterns
GROUP BY user_id, date;

CREATE VIEW skill_learning_progress AS
SELECT 
    sp.user_id,
    sp.skill_name,
    sp.current_level,
    sp.target_level,
    sp.hours_invested,
    COUNT(ls.id) as total_sessions,
    AVG(ls.productivity_score) as avg_productivity
FROM skill_progress sp
LEFT JOIN learning_sessions ls ON sp.id = ls.skill_id
GROUP BY sp.id;

CREATE VIEW active_technical_intelligence AS
SELECT 
    ti.*,
    COUNT(ki.id) as knowledge_connections
FROM technical_intelligence ti
LEFT JOIN knowledge_items ki ON ti.id = ki.source_id AND ki.source_type = 'research'
WHERE ti.relevance_score > 0.7 
    AND ti.reviewed = FALSE
GROUP BY ti.id
ORDER BY ti.relevance_score DESC;

-- Trigger to update timestamps
CREATE TRIGGER update_user_preferences_timestamp 
AFTER UPDATE ON user_preferences
FOR EACH ROW
BEGIN
    UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_skill_progress_timestamp 
AFTER UPDATE ON skill_progress
FOR EACH ROW
BEGIN
    UPDATE skill_progress SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_knowledge_items_timestamp 
AFTER UPDATE ON knowledge_items
FOR EACH ROW
BEGIN
    UPDATE knowledge_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;