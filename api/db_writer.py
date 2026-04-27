from __future__ import annotations

import pandas as pd
from psycopg import connect

DATABASE_URL = "postgresql://postgres:1234@localhost:5432/osmsg"


def get_connection():
    return connect(DATABASE_URL)


def create_pipeline_run(start_date, end_date, hashtag="", run_type="manual", status="running"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO pipeline_runs (run_type, start_date, end_date, hashtag, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (run_type, start_date, end_date, hashtag or "", status),
            )
            run_id = cur.fetchone()[0]
        conn.commit()
    return run_id


def mark_pipeline_run_completed(run_id: int, users_rows: int, summary_rows: int, notes=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pipeline_runs
                SET status = %s,
                    finished_at = NOW(),
                    users_rows = %s,
                    summary_rows = %s,
                    notes = %s
                WHERE id = %s
                """,
                ("completed", users_rows, summary_rows, notes, run_id),
            )
        conn.commit()


def mark_pipeline_run_failed(run_id: int, notes: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE pipeline_runs
                SET status = %s,
                    finished_at = NOW(),
                    notes = %s
                WHERE id = %s
                """,
                ("failed", notes, run_id),
            )
        conn.commit()


def insert_user_stats(run_id: int, df: pd.DataFrame, stat_date, hashtag=""):
    if df.empty:
        return 0

    records = []
    for _, row in df.iterrows():
        records.append(
            (
                run_id,
                stat_date,
                int(row["uid"]),
                str(row["name"]),
                hashtag or "",
                int(row.get("changesets", 0)),
                int(row.get("nodes_create", 0)),
                int(row.get("nodes_modify", 0)),
                int(row.get("nodes_delete", 0)),
                int(row.get("ways_create", 0)),
                int(row.get("ways_modify", 0)),
                int(row.get("ways_delete", 0)),
                int(row.get("rels_create", 0)),
                int(row.get("rels_modify", 0)),
                int(row.get("rels_delete", 0)),
                int(row.get("poi_create", 0)),
                int(row.get("poi_modify", 0)),
                int(row.get("map_changes", 0)),
            )
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO user_stats (
                    run_id, stat_date, uid, username, hashtag,
                    changesets,
                    nodes_create, nodes_modify, nodes_delete,
                    ways_create, ways_modify, ways_delete,
                    relations_create, relations_modify, relations_delete,
                    poi_create, poi_modify, map_changes
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                """,
                records,
            )
        conn.commit()

    return len(records)


def insert_summary_stats(run_id: int, summary_df: pd.DataFrame, hashtag=""):
    if summary_df.empty:
        return 0

    records = []
    for _, row in summary_df.iterrows():
        records.append(
            (
                run_id,
                row["timestamp"],
                hashtag or "",
                int(row.get("users", 0)),
                int(row.get("changesets", 0)),
                int(row.get("nodes.create", 0)),
                int(row.get("nodes.modify", 0)),
                int(row.get("nodes.delete", 0)),
                int(row.get("ways.create", 0)),
                int(row.get("ways.modify", 0)),
                int(row.get("ways.delete", 0)),
                int(row.get("relations.create", 0)),
                int(row.get("relations.modify", 0)),
                int(row.get("relations.delete", 0)),
                int(row.get("poi.create", 0)),
                int(row.get("poi.modify", 0)),
                int(row.get("map_changes", 0)),
            )
        )

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO summary_stats (
                    run_id, stat_date, hashtag,
                    users, changesets,
                    nodes_create, nodes_modify, nodes_delete,
                    ways_create, ways_modify, ways_delete,
                    relations_create, relations_modify, relations_delete,
                    poi_create, poi_modify, map_changes
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                """,
                records,
            )
        conn.commit()

    return len(records)

def pipeline_run_exists(start_date, end_date, hashtag=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM pipeline_runs
                WHERE start_date = %s
                  AND end_date = %s
                  AND hashtag = %s
                  AND status = 'completed'
                LIMIT 1
                """,
                (start_date, end_date, hashtag or ""),
            )
            return cur.fetchone() is not None