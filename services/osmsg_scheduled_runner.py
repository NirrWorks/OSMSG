from __future__ import annotations

import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd

from api.db_writer import (
    create_pipeline_run,
    mark_pipeline_run_completed,
    mark_pipeline_run_failed,
    insert_user_stats,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def format_osmsg_datetime(value: datetime) -> str:
    return value.strftime("%Y-%m-%d %H:%M:%S%z")


def run_osmsg_to_postgres(
    start_date: datetime,
    end_date: datetime,
    hashtag: str | None = None,
):
    run_id = create_pipeline_run(
        start_date=start_date,
        end_date=end_date,
        hashtag=hashtag or "",
        run_type="scheduled",
        status="running",
    )

    output_name = f"scheduled_run_{run_id}"
    output_csv = PROJECT_ROOT / f"{output_name}.csv"

    command = [
        "uv",
        "run",
        "python",
        "-m",
        "osmsg.app",
        "--start_date",
        format_osmsg_datetime(start_date),
        "--end_date",
        format_osmsg_datetime(end_date),
        "--name",
        output_name,
        "--format",
        "csv",
    ]

    if hashtag:
        command.extend(["--hashtags", hashtag, "--changeset"])

    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        df = pd.read_csv(output_csv)

        users_rows = insert_user_stats(
            run_id=run_id,
            df=df,
            stat_date=start_date.date(),
            hashtag=hashtag or "",
        )

        mark_pipeline_run_completed(
            run_id=run_id,
            users_rows=users_rows,
            summary_rows=0,
            notes="Scheduled OSMSG run completed",
        )

        print(result.stdout)
        print(f"Inserted {users_rows} user rows into PostgreSQL")

    except Exception as ex:
        mark_pipeline_run_failed(run_id, str(ex))
        raise


if __name__ == "__main__":
    run_osmsg_to_postgres(
        start_date=datetime.fromisoformat("2026-04-25T00:00:00+00:00"),
        end_date=datetime.fromisoformat("2026-04-26T00:00:00+00:00"),
        hashtag=None,
    )