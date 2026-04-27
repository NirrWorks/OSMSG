CREATE TABLE IF NOT EXISTS pipeline_runs (
    id SERIAL PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL DEFAULT 'manual',
    start_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ NOT NULL,
    hashtag VARCHAR(255) NOT NULL DEFAULT '',
    status VARCHAR(50) NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    users_rows INTEGER NOT NULL DEFAULT 0,
    summary_rows INTEGER NOT NULL DEFAULT 0,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_status
    ON pipeline_runs(status);

CREATE INDEX IF NOT EXISTS idx_pipeline_runs_dates
    ON pipeline_runs(start_date, end_date);


CREATE TABLE IF NOT EXISTS user_stats (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    uid BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    hashtag VARCHAR(255) NOT NULL DEFAULT '',

    changesets INTEGER NOT NULL DEFAULT 0,
    nodes_create INTEGER NOT NULL DEFAULT 0,
    nodes_modify INTEGER NOT NULL DEFAULT 0,
    nodes_delete INTEGER NOT NULL DEFAULT 0,
    ways_create INTEGER NOT NULL DEFAULT 0,
    ways_modify INTEGER NOT NULL DEFAULT 0,
    ways_delete INTEGER NOT NULL DEFAULT 0,
    relations_create INTEGER NOT NULL DEFAULT 0,
    relations_modify INTEGER NOT NULL DEFAULT 0,
    relations_delete INTEGER NOT NULL DEFAULT 0,
    poi_create INTEGER NOT NULL DEFAULT 0,
    poi_modify INTEGER NOT NULL DEFAULT 0,
    map_changes INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uq_user_stats UNIQUE (run_id, stat_date, uid, hashtag)
);

CREATE INDEX IF NOT EXISTS idx_user_stats_stat_date
    ON user_stats(stat_date);

CREATE INDEX IF NOT EXISTS idx_user_stats_uid
    ON user_stats(uid);

CREATE INDEX IF NOT EXISTS idx_user_stats_username
    ON user_stats(username);

CREATE INDEX IF NOT EXISTS idx_user_stats_hashtag
    ON user_stats(hashtag);

CREATE INDEX IF NOT EXISTS idx_user_stats_date_hashtag
    ON user_stats(stat_date, hashtag);

CREATE INDEX IF NOT EXISTS idx_user_stats_uid_date
    ON user_stats(uid, stat_date);


CREATE TABLE IF NOT EXISTS summary_stats (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES pipeline_runs(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    hashtag VARCHAR(255) NOT NULL DEFAULT '',

    users INTEGER NOT NULL DEFAULT 0,
    changesets INTEGER NOT NULL DEFAULT 0,
    nodes_create INTEGER NOT NULL DEFAULT 0,
    nodes_modify INTEGER NOT NULL DEFAULT 0,
    nodes_delete INTEGER NOT NULL DEFAULT 0,
    ways_create INTEGER NOT NULL DEFAULT 0,
    ways_modify INTEGER NOT NULL DEFAULT 0,
    ways_delete INTEGER NOT NULL DEFAULT 0,
    relations_create INTEGER NOT NULL DEFAULT 0,
    relations_modify INTEGER NOT NULL DEFAULT 0,
    relations_delete INTEGER NOT NULL DEFAULT 0,
    poi_create INTEGER NOT NULL DEFAULT 0,
    poi_modify INTEGER NOT NULL DEFAULT 0,
    map_changes INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uq_summary_stats UNIQUE (run_id, stat_date, hashtag)
);

CREATE INDEX IF NOT EXISTS idx_summary_stats_stat_date
    ON summary_stats(stat_date);

CREATE INDEX IF NOT EXISTS idx_summary_stats_hashtag
    ON summary_stats(hashtag);

CREATE INDEX IF NOT EXISTS idx_summary_stats_date_hashtag
    ON summary_stats(stat_date, hashtag);