from api.db_async import get_pool


async def fetch_users_async(start_date, end_date, hashtag=None, limit=100, offset=0):
    sql = """
        SELECT
            stat_date,
            uid,
            username,
            changesets,
            map_changes,
            nodes_create,
            nodes_modify,
            nodes_delete,
            ways_create,
            ways_modify,
            ways_delete,
            relations_create,
            relations_modify,
            relations_delete,
            poi_create,
            poi_modify,
            hashtag
        FROM user_stats
        WHERE stat_date BETWEEN $1 AND $2
          AND ($3 = '' OR hashtag = $4)
        ORDER BY map_changes DESC, uid ASC
        LIMIT $5 OFFSET $6
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, start_date, end_date, hashtag or "", hashtag or "", limit, offset,)
        return [dict(row) for row in rows]


async def fetch_summary_async(start_date, end_date, hashtag=None):
    sql = """
        SELECT
            COUNT(DISTINCT uid) AS users,
            COALESCE(SUM(changesets), 0) AS changesets,
            COALESCE(SUM(map_changes), 0) AS map_changes,
            COALESCE(SUM(nodes_create), 0) AS nodes_create,
            COALESCE(SUM(nodes_modify), 0) AS nodes_modify,
            COALESCE(SUM(nodes_delete), 0) AS nodes_delete,
            COALESCE(SUM(ways_create), 0) AS ways_create,
            COALESCE(SUM(ways_modify), 0) AS ways_modify,
            COALESCE(SUM(ways_delete), 0) AS ways_delete,
            COALESCE(SUM(relations_create), 0) AS relations_create,
            COALESCE(SUM(relations_modify), 0) AS relations_modify,
            COALESCE(SUM(relations_delete), 0) AS relations_delete,
            COALESCE(SUM(poi_create), 0) AS poi_create,
            COALESCE(SUM(poi_modify), 0) AS poi_modify
        FROM user_stats
        WHERE stat_date BETWEEN $1 AND $2
          AND ($3 = '' OR hashtag = $4)
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql, start_date, end_date, hashtag or "", hashtag or "")
        return dict(row) if row else {}


async def fetch_timeseries_async(start_date, end_date, hashtag=None):
    sql = """
        SELECT
            stat_date,
            COUNT(DISTINCT uid) AS users,
            COALESCE(SUM(changesets), 0) AS changesets,
            COALESCE(SUM(map_changes), 0) AS map_changes,
            COALESCE(SUM(nodes_create), 0) AS nodes_create,
            COALESCE(SUM(nodes_modify), 0) AS nodes_modify,
            COALESCE(SUM(nodes_delete), 0) AS nodes_delete,
            COALESCE(SUM(ways_create), 0) AS ways_create,
            COALESCE(SUM(ways_modify), 0) AS ways_modify,
            COALESCE(SUM(ways_delete), 0) AS ways_delete,
            COALESCE(SUM(relations_create), 0) AS relations_create,
            COALESCE(SUM(relations_modify), 0) AS relations_modify,
            COALESCE(SUM(relations_delete), 0) AS relations_delete,
            COALESCE(SUM(poi_create), 0) AS poi_create,
            COALESCE(SUM(poi_modify), 0) AS poi_modify
        FROM user_stats
        WHERE stat_date BETWEEN $1 AND $2
          AND ($3 = '' OR hashtag = $4)
        GROUP BY stat_date
        ORDER BY stat_date ASC
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            sql,
            start_date,
            end_date,
            hashtag or "",
            hashtag or "",
        )
        return [dict(row) for row in rows]