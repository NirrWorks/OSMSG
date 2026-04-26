# OSMSG API starter

This starter is for learning the API flow before wiring PostgreSQL.

## Run

```bash
pip install -r requirements_api.txt
uvicorn api.main:app --reload
```

Then open:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Example requests

```bash
curl "http://127.0.0.1:8000/api/v1/stats/users?start_date=2026-03-01T00:00:00&end_date=2026-03-10T23:59:59&hashtag=%23mapathon"
```

```bash
curl "http://127.0.0.1:8000/api/v1/stats/summary?start_date=2026-03-01T00:00:00&end_date=2026-03-10T23:59:59&hashtag=%23mapathon"
```

```bash
curl "http://127.0.0.1:8000/api/v1/stats/timeseries?start_date=2026-03-01T00:00:00&end_date=2026-03-10T23:59:59&hashtag=%23mapathon"
```

## What is mock right now?

The API currently reads from `api/mock_data.py`.
Later you will replace that with PostgreSQL queries.

## What is already designed?

- `user_stats` table: one row per user per filter window
- `stats_summary` table: one row per timestamp bucket per filter window
- v1 filters: `start_date`, `end_date`, `hashtag`
