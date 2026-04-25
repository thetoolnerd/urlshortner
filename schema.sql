-- PostgreSQL schema for the FastAPI URL shortener

CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY,
    short_code VARCHAR(16) NOT NULL UNIQUE,
    long_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NULL,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    redirect_status_code INTEGER NOT NULL DEFAULT 302,
    click_count INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_links_created_at ON links (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_links_expires_at ON links (expires_at);
