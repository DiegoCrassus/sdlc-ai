-- Provider request tracking for market data observability

CREATE TABLE IF NOT EXISTS provider_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name VARCHAR(64) NOT NULL,
    source_type VARCHAR(16) NOT NULL,
    endpoint_or_url VARCHAR(512),
    symbol VARCHAR(64),
    asset_type VARCHAR(16),
    status VARCHAR(32) NOT NULL,
    http_status INTEGER,
    response_time_ms INTEGER,
    cache_hit BOOLEAN NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_provider_requests_created_at ON provider_requests (created_at);
CREATE INDEX IF NOT EXISTS idx_provider_requests_provider ON provider_requests (provider_name, status);
