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
