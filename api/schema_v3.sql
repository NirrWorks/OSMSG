-- OSMSG PostgreSQL Schema v3
-- Normalized beta-next schema

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    hashtag VARCHAR(255) DEFAULT '',
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    users_rows INTEGER DEFAULT 0,
    summary_rows INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS users (
    uid BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS daily_user_stats (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    uid BIGINT NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    hashtag VARCHAR(255) DEFAULT '',
    changesets INTEGER DEFAULT 0,
    map_changes INTEGER DEFAULT 0,
    poi_create INTEGER DEFAULT 0,
    poi_modify INTEGER DEFAULT 0,

    UNIQUE (run_id, stat_date, uid, hashtag)
);

CREATE TABLE IF NOT EXISTS element_stats (
    id SERIAL PRIMARY KEY,
    daily_user_stat_id INTEGER NOT NULL REFERENCES daily_user_stats(id) ON DELETE CASCADE,
    element_type VARCHAR(20) NOT NULL,
    action VARCHAR(20) NOT NULL,
    count INTEGER DEFAULT 0,

    CONSTRAINT valid_element_type CHECK (
        element_type IN ('node', 'way', 'relation')
    ),
    CONSTRAINT valid_action CHECK (
        action IN ('create', 'modify', 'delete')
    ),
    UNIQUE (daily_user_stat_id, element_type, action)
);

CREATE TABLE IF NOT EXISTS tag_stats (
    id SERIAL PRIMARY KEY,
    daily_user_stat_id INTEGER NOT NULL REFERENCES daily_user_stats(id) ON DELETE CASCADE,
    tag_key TEXT NOT NULL,
    tag_value TEXT,
    action VARCHAR(20) NOT NULL,
    count INTEGER DEFAULT 0,
    length_m DOUBLE PRECISION,

    CONSTRAINT valid_tag_action CHECK (
        action IN ('create', 'modify')
    )
);

CREATE TABLE IF NOT EXISTS summary_stats (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    hashtag VARCHAR(255) DEFAULT '',
    users INTEGER DEFAULT 0,
    changesets INTEGER DEFAULT 0,
    map_changes INTEGER DEFAULT 0,
    poi_create INTEGER DEFAULT 0,
    poi_modify INTEGER DEFAULT 0,

    UNIQUE (run_id, stat_date, hashtag)
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_date
ON pipeline_runs (start_date, end_date);

CREATE INDEX IF NOT EXISTS idx_daily_user_stats_date
ON daily_user_stats (stat_date);

CREATE INDEX IF NOT EXISTS idx_daily_user_stats_uid
ON daily_user_stats (uid);

CREATE INDEX IF NOT EXISTS idx_daily_user_stats_hashtag
ON daily_user_stats (hashtag);

CREATE INDEX IF NOT EXISTS idx_element_stats_type_action
ON element_stats (element_type, action);

CREATE INDEX IF NOT EXISTS idx_summary_stats_date
ON summary_stats (stat_date);