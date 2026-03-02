-- Initial schema for V1.1 (Transcript-Link + Slack Job layer)
-- Run this once against a PostgreSQL database.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_integrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    provider TEXT NOT NULL,
    api_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS user_external_identities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    provider TEXT NOT NULL,
    external_user_id TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transcript_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    source_link TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transcript_request_id UUID NOT NULL REFERENCES transcript_requests(id),
    source TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    cleaned_text TEXT,
    fetched_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    transcript_request_id UUID NOT NULL REFERENCES transcript_requests(id),
    google_doc_id TEXT NOT NULL,
    doc_type TEXT NOT NULL DEFAULT 'BRD',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id),
    section_key TEXT NOT NULL,
    heading_id TEXT,
    content TEXT NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS job_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_type TEXT NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    trigger_source TEXT NOT NULL,
    trigger_event_id TEXT,
    arguments JSONB,
    external_user_id TEXT,
    provider TEXT,
    status TEXT NOT NULL,
    workflow_execution_id UUID,
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_type TEXT NOT NULL DEFAULT 'GenerateBRDFromTranscriptLink',
    transcript_request_id UUID NOT NULL REFERENCES transcript_requests(id),
    user_id UUID NOT NULL REFERENCES users(id),
    trigger_type TEXT NOT NULL DEFAULT 'UI',
    status TEXT NOT NULL DEFAULT 'PENDING',
    current_step TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    context JSONB,
    started_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);
