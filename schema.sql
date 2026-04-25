-- PostgreSQL schema for a learning URL shortener

CREATE TABLE IF NOT EXISTS links (
    id UUID PRIMARY KEY,
    short_code VARCHAR(16) NOT NULL UNIQUE,
    long_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NULL,
    owner_id UUID NULL,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_links_created_at ON links (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_links_expires_at ON links (expires_at);

CREATE TABLE IF NOT EXISTS click_events (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(16) NOT NULL,
    clicked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_hash VARCHAR(128) NULL,
    user_agent TEXT NULL,
    referer TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_click_events_short_code_clicked_at
    ON click_events (short_code, clicked_at DESC);
