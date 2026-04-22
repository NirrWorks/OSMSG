from datetime import datetime
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.db_async import init_db_pool, close_db_pool
from api.queries_async import (
    fetch_users_async,
    fetch_summary_async,
    fetch_timeseries_async,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool()
    yield
    await close_db_pool()


app = FastAPI(
    title="OSMSG Stats API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/stats/users")
async def get_users(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    hashtag: str | None = Query(None),
):
    users = await fetch_users_async(
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
        "users": users,
    }


@app.get("/api/v1/stats/summary")
async def get_summary(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    hashtag: str | None = Query(None),
):
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


@app.get("/api/v1/stats/timeseries")
async def get_timeseries(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    hashtag: str | None = Query(None),
):
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