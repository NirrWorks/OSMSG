import pandas as pd
from osmsg.osmsg_pipeline import run_processing_pipeline
from api.db_writer import (
    create_pipeline_run,
    insert_user_stats,
    insert_summary_stats,
    mark_pipeline_run_completed,
    mark_pipeline_run_failed,
    pipeline_run_exists,
)


def build_output_dataframes(users, summary_interval, summary_enabled):
    df = pd.DataFrame()

    if users:
        df = pd.json_normalize(list(users.values()))

        for col in [
            "nodes.create", "nodes.modify", "nodes.delete",
            "ways.create", "ways.modify", "ways.delete",
            "relations.create", "relations.modify", "relations.delete",
            "poi.create", "poi.modify",
        ]:
            if col not in df.columns:
                df[col] = 0

        df["map_changes"] = (
            df["nodes.create"] + df["nodes.modify"] + df["nodes.delete"] +
            df["ways.create"] + df["ways.modify"] + df["ways.delete"] +
            df["relations.create"] + df["relations.modify"] + df["relations.delete"]
        )

        df = df.sort_values("map_changes", ascending=False).reset_index(drop=True).copy()
        df.insert(0, "rank", range(1, len(df) + 1))

    summary_df = pd.DataFrame()

    if summary_enabled and summary_interval:
        summary_df = pd.json_normalize(list(summary_interval.values()))

        for col in [
            "nodes.create", "nodes.modify", "nodes.delete",
            "ways.create", "ways.modify", "ways.delete",
            "relations.create", "relations.modify", "relations.delete",
            "poi.create", "poi.modify",
        ]:
            if col not in summary_df.columns:
                summary_df[col] = 0

        summary_df["map_changes"] = (
            summary_df["nodes.create"] + summary_df["nodes.modify"] + summary_df["nodes.delete"] +
            summary_df["ways.create"] + summary_df["ways.modify"] + summary_df["ways.delete"] +
            summary_df["relations.create"] + summary_df["relations.modify"] + summary_df["relations.delete"]
        )

        if "timestamp" in summary_df.columns:
            summary_df = summary_df.sort_values("timestamp").reset_index(drop=True).copy()

    return df, summary_df


def run_osmsg_job(start_date, end_date, hashtag=None, summary=True):
    class Args:
        pass

    args = Args()
    args.start_date = start_date
    args.end_date = end_date
    args.summary = summary
    args.hashtags = [hashtag] if hashtag else None

    if pipeline_run_exists(start_date, end_date, hashtag or ""):
        print("Pipeline run already exists for this date range. Skipping.")
        return pd.DataFrame(), pd.DataFrame()
    
    run_id = create_pipeline_run(
        start_date=start_date,
        end_date=end_date,
        hashtag=hashtag or "",
        run_type="manual",
        status="running",
    )

    try:
        users, summary_interval = run_processing_pipeline(args)

        df, summary_df = build_output_dataframes(
            users=users,
            summary_interval=summary_interval,
            summary_enabled=summary,
        )

        users_rows = insert_user_stats(
            run_id=run_id,
            df=df,
            stat_date=start_date.date(),
            hashtag=hashtag or "",
        )

        summary_rows = insert_summary_stats(
            run_id=run_id,
            summary_df=summary_df,
            hashtag=hashtag or "",
        )

        mark_pipeline_run_completed(
            run_id=run_id,
            users_rows=users_rows,
            summary_rows=summary_rows,
            notes="Run completed successfully",
        )

        return df, summary_df

    except Exception as exc:
        mark_pipeline_run_failed(run_id=run_id, notes=str(exc))
        raise