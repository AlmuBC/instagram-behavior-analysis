import os
import json
import pandas as pd

def load_messages_df(inbox_path="data/raw/Inbox/", my_name="Almu"):
    rows = []

    for folder in os.listdir(inbox_path):
        folder_path = os.path.join(inbox_path, folder)
        if not os.path.isdir(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if not filename.startswith("message_") or not filename.endswith(".json"):
                continue

            try:
                with open(os.path.join(folder_path, filename), encoding="utf-8") as f:
                    data = json.load(f)
                    for msg in data.get("messages", []):
                        sender = msg.get("sender_name")
                        timestamp = msg.get("timestamp_ms")
                        if not sender or not timestamp:
                            continue
                        rows.append({
                            "timestamp": pd.to_datetime(timestamp, unit="ms"),
                            "sender_name": sender,
                            "is_sent_by_me": sender == my_name
                        })
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    df["hour"] = df["timestamp"].dt.hour

    return df
def load_advertisers(path="data/raw/instagram_ads_and_businesses/advertisers_using_your_activity_or_information.json"):
    """Load the advertisers that use your activity for custom audiences."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["ig_custom_audiences_all_types"]
    return pd.DataFrame(data)

def load_ads_view_authors(path="data/raw/ads_and_topics/ads_viewed.json"):
    """Load ad authors from ads_viewed.json and count views per author."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["impressions_history_ads_seen"]
    records = []
    for entry in data:
        author = entry["string_map_data"]["Author"]["value"]
        records.append(author)
    # Count how many times each author appears
    df = pd.DataFrame(records, columns=["author"])
    df["normalized_author"] = df["author"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    count_df = df.groupby(["normalized_author", "author"]).size().reset_index(name="count")
    return count_df

def load_story_likes(path="data/raw/story_interactions/story_likes.json"):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["story_activities_story_likes"]

    rows = []
    for entry in data:
        ts = pd.to_datetime(entry["string_list_data"][0]["timestamp"], unit="s")
        rows.append({"timestamp": ts})

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Añadimos columnas necesarias
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)
    df["day"] = df["timestamp"].dt.day_name()
    df["hour"] = df["timestamp"].dt.hour

    return df

def filter_by_date(df, date_col, start_date, end_date):
    return df[
        (df[date_col] >= pd.to_datetime(start_date)) &
        (df[date_col] <= pd.to_datetime(end_date))
    ]
