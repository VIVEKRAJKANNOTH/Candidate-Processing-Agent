-- TraqCheck CandidateVerify Database Schema (SQLite)
-- This schema supports the candidate verification workflow

-- Main candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY,  -- UUID as TEXT (will be generated in application)
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    company TEXT,
    designation TEXT,
    skills TEXT,  -- JSON stored as TEXT
    experience_years INTEGER,
    resume_path TEXT NOT NULL,
    confidence_scores TEXT,  -- JSON stored as TEXT
    status TEXT DEFAULT 'PARSED',
    document_status TEXT DEFAULT 'NOT_REQUESTED',
    documents_requested_at TEXT,  -- ISO 8601 datetime string
    documents_submitted_at TEXT,  -- ISO 8601 datetime string
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Documents table
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,  -- UUID as TEXT
    candidate_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_size INTEGER,  -- File size in bytes
    uploaded_at TEXT DEFAULT (datetime('now')),
    verification_status TEXT DEFAULT 'PENDING',
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- Agent activity logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id TEXT PRIMARY KEY,  -- UUID as TEXT
    candidate_id TEXT NOT NULL,
    action TEXT NOT NULL,
    tool_used TEXT,
    input TEXT,  -- JSON stored as TEXT
    output TEXT,  -- JSON stored as TEXT
    timestamp TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_documents_candidate ON documents(candidate_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_candidate ON agent_logs(candidate_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);
