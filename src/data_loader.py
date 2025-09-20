import os
import json
import glob
import pandas as pd
from datetime import datetime


def load_event_timestamps(raw_data_path="data/raw"):
    """
    Walk through all JSON files under raw_data_path and extract timestamps.
    Each event_type is a combination of the parent folder and the JSON filename.
    Returns: pd.DataFrame with columns: event_type, timestamp
    """
    event_rows = []
    json_files = glob.glob(os.path.join(raw_data_path, "*", "*.json"), recursive=True)
    print(f"Scanning {len(json_files)} JSON files...")

    for path in json_files:
        folder = os.path.basename(os.path.dirname(path))
        filename = os.path.splitext(os.path.basename(path))[0]
        event_type = f"{folder}_{filename}"

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Could not load {event_type}: {e}")
            continue

        entries = _get_entries_from_json(data)

        n_found = 0
        for item in entries:
            timestamps = extract_all_timestamps(item)
            for ts in timestamps:
                event_rows.append((event_type, ts))
                n_found += 1

        print(f"{event_type}: {n_found} timestamps extracted")

    df = pd.DataFrame(event_rows, columns=["event_type", "timestamp"])
    df = df[df["timestamp"].apply(lambda x: isinstance(x, (pd.Timestamp, datetime)) and pd.notnull(x))]

    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df.sort_values(by="timestamp").reset_index(drop=True)

    print(f"Final DataFrame shape: {df.shape}")
    return df


def extract_all_timestamps(obj):
    """
    Recursively search for timestamp fields in nested dicts or lists.
    Returns a list of datetime objects.
    """
    timestamps = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                timestamps.extend(extract_all_timestamps(value))
            elif isinstance(value, (int, float)) and "timestamp" in key.lower():
                try:
                    timestamps.append(pd.to_datetime(int(value), unit="s"))
                except Exception:
                    continue
            elif isinstance(value, str) and "timestamp" in key.lower():
                try:
                    timestamps.append(pd.to_datetime(value))
                except Exception:
                    continue

    elif isinstance(obj, list):
        for item in obj:
            timestamps.extend(extract_all_timestamps(item))

    return timestamps


def _get_entries_from_json(data):
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        entries = []
        for v in data.values():
            if isinstance(v, list):
                entries.extend(v)
        return entries
    return []


def load_sent_messages(user_name="Almu", base_path="data/raw/inbox"):
    """
    Extract all timestamps of messages sent by the given user from inbox folders.

    Each folder in `base_path` contains a `message_1.json` file with the conversation.

    Returns:
        pd.DataFrame with columns: event_type, timestamp
    """
    event_rows = []
    inbox_folders = glob.glob(os.path.join(base_path, "*/message_1.json"))

    print(f"Scanning {len(inbox_folders)} message files...")

    for path in inbox_folders:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Could not load {path}: {e}")
            continue

        messages = data.get("messages", [])
        n_found = 0

        for msg in messages:
            if msg.get("sender_name") == user_name and "timestamp_ms" in msg:
                try:
                    ts = pd.to_datetime(int(msg["timestamp_ms"]), unit="ms")
                    event_rows.append(("messages_sent", ts))
                    n_found += 1
                except Exception:
                    continue

        folder_name = os.path.basename(os.path.dirname(path))
        #print(f"{folder_name}: {n_found} messages sent by {user_name}")

    df = pd.DataFrame(event_rows, columns=["event_type", "timestamp"])
    df = df[df["timestamp"].notna()]
    df = df.sort_values(by="timestamp").reset_index(drop=True)

    print(f"Total messages extracted: {len(df)}")
    return df

def load_all_instagram_events(raw_data_path="data/raw", inbox_path="data/raw/inbox", user_name="Almu"):
    """
    Loads both general Instagram events and messages sent by the user.
    Returns: unified DataFrame with event_type and timestamp.
    """
    df_events = load_event_timestamps(raw_data_path=raw_data_path)
    df_messages = load_sent_messages(user_name=user_name, base_path=inbox_path)

    df_all = pd.concat([df_events, df_messages], ignore_index=True)
    df_all = df_all[df_all["timestamp"].notna()]
    df_all = df_all.sort_values(by="timestamp").reset_index(drop=True)

    return df_all
