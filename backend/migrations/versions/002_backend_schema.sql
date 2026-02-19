-- Backend schema for chatbot and AI services

CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS conversation_turns (
    turn_id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    query VARCHAR(1000) NOT NULL
        CHECK (LENGTH(query) >= 1 AND LENGTH(query) <= 1000),
    response TEXT NOT NULL,
    retrieved_chunks JSONB DEFAULT '[]'::jsonb
        CHECK (jsonb_array_length(retrieved_chunks) <= 5),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    page_context VARCHAR(500),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS rate_limit_records (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    query_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Personalization tables
CREATE TABLE IF NOT EXISTS personalized_content (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    chapter_slug TEXT NOT NULL,
    personalized_markdown TEXT NOT NULL,
    user_profile_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
    content_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, chapter_slug)
);

CREATE TABLE IF NOT EXISTS urdu_translations (
    id SERIAL PRIMARY KEY,
    chapter_slug TEXT NOT NULL UNIQUE,
    urdu_markdown TEXT NOT NULL,
    content_version TEXT NOT NULL,
    prompt_version TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- AI generation rate limiting
CREATE TABLE IF NOT EXISTS ai_generation_rate_limits (
    id SERIAL PRIMARY KEY,
    identifier TEXT NOT NULL,
    request_type TEXT NOT NULL,
    request_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Agent execution logging
CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id SERIAL PRIMARY KEY,
    agent_type TEXT NOT NULL,
    grounding_policy TEXT NOT NULL,
    skills_used TEXT[] NOT NULL,
    skills_detail JSONB NOT NULL DEFAULT '[]'::jsonb,
    token_count INTEGER,
    model TEXT NOT NULL,
    latency_ms INTEGER NOT NULL,
    cached BOOLEAN NOT NULL DEFAULT FALSE,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_logs_created
    ON agent_execution_logs (created_at);
CREATE INDEX IF NOT EXISTS idx_agent_logs_type
    ON agent_execution_logs (agent_type);
CREATE INDEX IF NOT EXISTS idx_conversations_session
    ON conversation_turns (session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp
    ON conversation_turns (timestamp);
CREATE INDEX IF NOT EXISTS idx_rate_limit_session_time
    ON rate_limit_records (session_id, query_timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_rate_limits_id_type_time
    ON ai_generation_rate_limits (identifier, request_type, request_timestamp);

-- Auto-cleanup functions (can be called by background tasks)
CREATE OR REPLACE FUNCTION cleanup_old_conversations(p_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM conversation_turns
    WHERE timestamp < NOW() - (p_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_old_rate_limit_records(p_hours INTEGER DEFAULT 24)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM rate_limit_records
    WHERE query_timestamp < NOW() - (p_hours || ' hours')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION cleanup_agent_execution_logs(p_days INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_execution_logs
    WHERE created_at < NOW() - (p_days || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Grant basic permissions (if not already granted)
GRANT USAGE ON SCHEMA public TO postgres;

--DOWN--
-- This is a simplified rollback - in production you'd need to handle dependencies carefully
-- Drop tables in reverse dependency order
DROP FUNCTION IF EXISTS cleanup_agent_execution_logs(INTEGER);
DROP FUNCTION IF EXISTS cleanup_old_rate_limit_records(INTEGER);
DROP FUNCTION IF EXISTS cleanup_old_conversations(INTEGER);

DROP INDEX IF EXISTS idx_ai_rate_limits_id_type_time;
DROP INDEX IF EXISTS idx_rate_limit_session_time;
DROP INDEX IF EXISTS idx_conversations_timestamp;
DROP INDEX IF EXISTS idx_conversations_session;
DROP INDEX IF EXISTS idx_agent_logs_type;
DROP INDEX IF EXISTS idx_agent_logs_created;

DROP TABLE IF EXISTS agent_execution_logs;
DROP TABLE IF EXISTS ai_generation_rate_limits;
DROP TABLE IF EXISTS urdu_translations;
DROP TABLE IF EXISTS personalized_content;
DROP TABLE IF EXISTS rate_limit_records;
DROP TABLE IF EXISTS conversation_turns;
DROP TABLE IF EXISTS chat_sessions;