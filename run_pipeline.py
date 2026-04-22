from datetime import datetime, timedelta, timezone
from services.osmsg_runner import run_osmsg_job


def get_previous_day_window():
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    start_date = today_start - timedelta(days=1)
    end_date = today_start
    return start_date, end_date


if __name__ == "__main__":
    start_date, end_date = get_previous_day_window()

    print("Running pipeline")
    print("Start:", start_date.isoformat())
    print("End:", end_date.isoformat())

    df, summary_df = run_osmsg_job(
        start_date=start_date,
        end_date=end_date,
        hashtag=None,
        summary=True,
    )

    print("Pipeline completed")
    print("Users rows:", len(df))
    print("Summary rows:", len(summary_df))

    print(f"Run started: {start_date} → {end_date}")
    print(f"Run completed. Users: {len(df)}, Summary: {len(summary_df)}")