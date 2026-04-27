from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime

from litestar import Litestar, get
from litestar.params import Parameter

from api.db_async import init_db_pool, close_db_pool
from api.queries_async import (
    fetch_users_async,
    fetch_summary_async,
    fetch_timeseries_async,
)


@asynccontextmanager
async def lifespan(app: Litestar):
    await init_db_pool()
    yield
    await close_db_pool()


@get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@get("/api/v1/stats/users")
async def get_users(
    start_date: datetime,
    end_date: datetime,
    hashtag: str | None = None,
    limit: int = Parameter(default=100, ge=1, le=1000),
    offset: int = Parameter(default=0, ge=0),
) -> dict:
    if start_date > end_date:
        return {"error": "start_date must be before end_date"}

    users = await fetch_users_async(
        start_date.date(),
        end_date.date(),
        hashtag,
        limit,
        offset,
    )

    return {
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hashtag": hashtag,
            "limit": limit,
            "offset": offset,
        },
        "users": users,
    }


@get("/api/v1/stats/summary")
async def get_summary(
    start_date: datetime,
    end_date: datetime,
    hashtag: str | None = None,
) -> dict:
    if start_date > end_date:
        return {"error": "start_date must be before end_date"}

    summary = await fetch_summary_async(
        start_date.date(),
        end_date.date(),
        hashtag,
    )

    return {
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hashtag": hashtag,
        },
        "summary": summary,
    }


@get("/api/v1/stats/timeseries")
async def get_timeseries(
    start_date: datetime,
    end_date: datetime,
    hashtag: str | None = None,
) -> dict:
    if start_date > end_date:
        return {"error": "start_date must be before end_date"}

    timeseries = await fetch_timeseries_async(
        start_date.date(),
        end_date.date(),
        hashtag,
    )

    return {
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hashtag": hashtag,
        },
        "timeseries": timeseries,
    }

from litestar.openapi.config import OpenAPIConfig
app = Litestar(
    route_handlers=[
        health,
        get_users,
        get_summary,
        get_timeseries,
    ],
    lifespan=[lifespan],
    openapi_config=OpenAPIConfig(
        title="OSMSG API",
        version="1.0.0",
        path="/docs", 
    ),
)