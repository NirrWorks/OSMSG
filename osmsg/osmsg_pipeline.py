import datetime as dt
import os

import osmium

from osmsg.changefiles import get_download_urls_changefiles
from osmsg.utils import download_osm_files, get_file_path_from_url

# --------------------------------------------------
# Runtime state used during one pipeline run
# --------------------------------------------------
users = {}
users_temp = {}
summary_interval = {}
summary_interval_temp = {}
processed_changesets = {}

start_date_utc = None
end_date_utc = None

# --------------------------------------------------
# Config defaults
# --------------------------------------------------
summary = True
hashtags = None
changeset_meta = False
all_tags = False
key_value = False
collect_field_mappers_stats = False
geom_boundary = False
whitelisted_users = []
additional_tags = None
length = None

remove_temp_files = False


def reset_runtime_state():
    global users
    global users_temp
    global summary_interval
    global summary_interval_temp
    global processed_changesets
    global start_date_utc
    global end_date_utc

    users = {}
    users_temp = {}
    summary_interval = {}
    summary_interval_temp = {}
    processed_changesets = {}

    start_date_utc = None
    end_date_utc = None


def apply_args_config(args):
    """
    Load the settings needed by the processing pipeline.
    """
    global summary
    global hashtags
    global changeset_meta
    global all_tags
    global key_value
    global collect_field_mappers_stats
    global geom_boundary
    global whitelisted_users
    global additional_tags
    global length
    global remove_temp_files

    summary = getattr(args, "summary", True)
    hashtags = getattr(args, "hashtags", None)

    changeset_meta = getattr(args, "changeset_meta", False)
    all_tags = getattr(args, "all_tags", False)
    key_value = getattr(args, "key_value", False)
    collect_field_mappers_stats = getattr(args, "collect_field_mappers_stats", False)
    geom_boundary = getattr(args, "geom_boundary", False)
    whitelisted_users = getattr(args, "whitelisted_users", [])
    additional_tags = getattr(args, "additional_tags", None)
    length = getattr(args, "length", None)
    remove_temp_files = getattr(args, "remove_temp_files", False)


def collect_changefile_stats(
    user, uname, changeset, version, tags, osm_type, timestamp, osm_obj_nodes=None
):
    tags_to_collect = list(additional_tags) if additional_tags else None

    if version == 1:
        action = "create"
    elif version > 1:
        action = "modify"
    else:
        action = "delete"

    timestamp = timestamp.strftime("%Y-%m-%d")
    len_feature = 0

    if length and osm_obj_nodes:
        try:
            len_feature = osmium.geom.haversine_distance(osm_obj_nodes)
        except Exception:
            pass

    users.setdefault(
        user,
        {
            "name": uname,
            "uid": user,
            "changesets": 0,
            "nodes": {"create": 0, "modify": 0, "delete": 0},
            "ways": {"create": 0, "modify": 0, "delete": 0},
            "relations": {"create": 0, "modify": 0, "delete": 0},
            "poi": {"create": 0, "modify": 0},
        },
    )

    users_temp.setdefault(user, {"changesets": []})

    if summary:
        summary_interval.setdefault(
            timestamp,
            {
                "timestamp": timestamp,
                "users": 0,
                "changesets": 0,
                "nodes": {"create": 0, "modify": 0, "delete": 0},
                "ways": {"create": 0, "modify": 0, "delete": 0},
                "relations": {"create": 0, "modify": 0, "delete": 0},
                "poi": {"create": 0, "modify": 0},
            },
        )
        summary_interval_temp.setdefault(timestamp, {"changesets": [], "users": []})

        if changeset not in summary_interval_temp[timestamp]["changesets"]:
            summary_interval_temp[timestamp]["changesets"].append(changeset)
        summary_interval[timestamp]["changesets"] = len(
            summary_interval_temp[timestamp]["changesets"]
        )

        if user not in summary_interval_temp[timestamp]["users"]:
            summary_interval_temp[timestamp]["users"].append(user)
        summary_interval[timestamp]["users"] = len(
            summary_interval_temp[timestamp]["users"]
        )

    if changeset not in users_temp[user]["changesets"]:
        users_temp[user]["changesets"].append(changeset)
    users[user]["changesets"] = len(users_temp[user]["changesets"])

    if hashtags or changeset_meta:
        users[user].setdefault("countries", [])
        users[user].setdefault("hashtags", [])
        users[user].setdefault("editors", [])

        if summary:
            summary_interval[timestamp].setdefault("editors", {})

        if changeset in processed_changesets:
            try:
                users[user]["countries"] += [
                    ctry
                    for ctry in processed_changesets[changeset].get("countries", [])
                    if ctry not in users[user]["countries"]
                ]
                users[user]["hashtags"] += [
                    hstg
                    for hstg in processed_changesets[changeset].get("hashtags", [])
                    if hstg not in users[user]["hashtags"]
                ]

                for editor in processed_changesets[changeset].get("editors", []):
                    if editor not in users[user]["editors"]:
                        users[user]["editors"].append(editor)

                    if summary:
                        summary_interval[timestamp]["editors"].setdefault(editor, 0)
                        summary_interval[timestamp]["editors"][editor] += 1
            except Exception:
                pass

    users[user][osm_type][action] += 1
    if summary:
        summary_interval[timestamp][osm_type][action] += 1

    if osm_type == "nodes" and tags and action != "delete":
        users[user]["poi"][action] += 1
        if summary:
            summary_interval[timestamp]["poi"][action] += 1

    if all_tags:
        users[user].setdefault("tags_create", {})
        users[user].setdefault("tags_modify", {})

        if summary:
            summary_interval[timestamp].setdefault("tags_create", {})
            summary_interval[timestamp].setdefault("tags_modify", {})

        if tags:
            for key, value in tags:
                if action != "delete":
                    if key_value:
                        users[user][f"tags_{action}"].setdefault(f"{key}={value}", 0)
                        users[user][f"tags_{action}"][f"{key}={value}"] += 1

                    users[user][f"tags_{action}"].setdefault(key, 0)
                    users[user][f"tags_{action}"][key] += 1

                    if summary:
                        if key_value:
                            summary_interval[timestamp][f"tags_{action}"].setdefault(
                                f"{key}={value}", 0
                            )
                            summary_interval[timestamp][f"tags_{action}"][
                                f"{key}={value}"
                            ] += 1

                        summary_interval[timestamp][f"tags_{action}"].setdefault(key, 0)
                        summary_interval[timestamp][f"tags_{action}"][key] += 1

    if tags_to_collect and action != "delete" and tags:
        for tag in tags_to_collect:
            if summary:
                summary_interval[timestamp].setdefault(tag, {"create": 0, "modify": 0})
            users[user].setdefault(tag, {"create": 0, "modify": 0})

            if tag in tags:
                if summary:
                    summary_interval[timestamp][tag][action] += 1
                users[user][tag][action] += 1

    if length:
        for t in length:
            users[user].setdefault(f"{t}_len_m", 0)
            if summary:
                summary_interval[timestamp].setdefault(f"{t}_len_m", 0)

            if tags:
                if (
                    t in tags
                    and action != "modify"
                    and action != "delete"
                    and len_feature > 0
                ):
                    if summary:
                        summary_interval[timestamp][f"{t}_len_m"] += round(len_feature)
                    users[user][f"{t}_len_m"] += round(len_feature)


def calculate_stats(
    user, uname, changeset, version, tags, osm_type, timestamp, osm_obj_nodes=None
):
    if hashtags or collect_field_mappers_stats or geom_boundary:
        if len(processed_changesets) > 0 and changeset in processed_changesets:
            collect_changefile_stats(
                user,
                uname,
                changeset,
                version,
                tags,
                osm_type,
                timestamp,
                osm_obj_nodes,
            )
    elif len(whitelisted_users) > 0:
        if uname in whitelisted_users:
            collect_changefile_stats(
                user,
                uname,
                changeset,
                version,
                tags,
                osm_type,
                timestamp,
                osm_obj_nodes,
            )
    else:
        collect_changefile_stats(
            user,
            uname,
            changeset,
            version,
            tags,
            osm_type,
            timestamp,
            osm_obj_nodes,
        )


class ChangefileHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()

    def node(self, n):
        if n.timestamp >= start_date_utc and n.timestamp < end_date_utc:
            version = 0 if n.deleted else n.version
            calculate_stats(
                n.uid, n.user, n.changeset, version, n.tags, "nodes", n.timestamp
            )

    def way(self, w):
        if w.timestamp >= start_date_utc and w.timestamp < end_date_utc:
            version = 0 if w.deleted else w.version
            calculate_stats(
                w.uid,
                w.user,
                w.changeset,
                version,
                w.tags,
                "ways",
                w.timestamp,
                w.nodes if length else None,
            )

    def relation(self, r):
        if r.timestamp >= start_date_utc and r.timestamp < end_date_utc:
            version = 0 if r.deleted else r.version
            calculate_stats(
                r.uid,
                r.user,
                r.changeset,
                version,
                r.tags,
                "relations",
                r.timestamp,
            )


def process_changefiles(url):
    if "minute" not in url:
        print(f"Processing {url}")

    file_path = get_file_path_from_url(url, "changefiles")
    local_osc_file = file_path[:-3]

    if not os.path.exists(local_osc_file):
        raise FileNotFoundError(f"Expected decompressed file not found: {local_osc_file}")

    handler = ChangefileHandler()
    try:
        if length:
            handler.apply_file(local_osc_file, locations=True)
        else:
            handler.apply_file(local_osc_file)
    except Exception as ex:
        print(f"File may be corrupt: Error at {url}: {ex}")

    if remove_temp_files and os.path.exists(local_osc_file):
        os.remove(local_osc_file)


def run_processing_pipeline(args):
    global start_date_utc
    global end_date_utc

    reset_runtime_state()
    apply_args_config(args)

    start_date_utc = args.start_date.astimezone(dt.timezone.utc)
    end_date_utc = args.end_date.astimezone(dt.timezone.utc)

    print(f"Pipeline UTC window: {start_date_utc} -> {end_date_utc}")

    base_url = getattr(
        args,
        "base_url",
        "https://planet.openstreetmap.org/replication/minute/",
    )
    timezone = getattr(args, "timezone", "UTC")
    cookies = getattr(args, "cookies", None)

    (
        download_urls,
        server_ts,
        start_seq,
        last_seq,
        start_seq_url,
        end_seq_url,
    ) = get_download_urls_changefiles(
        start_date=start_date_utc,
        end_date=end_date_utc,
        base_url=base_url,
        timezone=timezone,
    )

    print(f"Server latest timestamp: {server_ts}")
    print(f"Start sequence: {start_seq}")
    print(f"End sequence: {last_seq}")
    print(f"Start state URL: {start_seq_url}")
    print(f"End state URL: {end_seq_url}")
    print(f"Total changefiles to process: {len(download_urls)}")

    for i, url in enumerate(download_urls, start=1):
        try:
            print(f"[{i}/{len(download_urls)}] Downloading and processing {url}")
            download_osm_files(url, mode="changefiles", cookies=cookies)
            process_changefiles(url)
        except Exception as ex:
            print(f"Failed processing {url}: {ex}")

    return users, summary_interval