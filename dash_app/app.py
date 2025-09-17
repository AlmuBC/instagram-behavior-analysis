import dash
import plotly.express as px
import pandas as pd
import json

from layout import serve_layout  # import layout function


# Helper function to parse Instagram JSON structure (follows/unfollows)
def load_instagram_json(path, key):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)[key]
    rows = []
    for item in data:
        entry = item["string_list_data"][0]
        rows.append({
            "username": entry["value"],
            "timestamp": pd.to_datetime(entry["timestamp"], unit="s")
        })
    return pd.DataFrame(rows)

# Helper function to parse Instagram JSON structure (likes)
def load_likes_json(path, key):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)[key]
    rows = []
    for item in data:
        entry = item["string_list_data"][0]
        rows.append({
            "user": item["title"],
            "url": entry["href"],
            "timestamp": pd.to_datetime(entry["timestamp"], unit="s")
        })
    return pd.DataFrame(rows)


# --- FOLLOW DATA ---
# Load data from raw folder
df_following = load_instagram_json("data/raw/followers_and_following/following.json", "relationships_following")
df_unfollow = load_instagram_json("data/raw/followers_and_following/recently_unfollowed_profiles.json", "relationships_unfollowed_users")

# Extract month as string (avoids Period objects)
df_following["month"] = df_following["timestamp"].dt.to_period("M").astype(str)

# Aggregate counts by month
follows_per_month = df_following.groupby("month").size().reset_index(name="new_follows")

# Create charts
fig_follows = px.line(follows_per_month, x="month", y="new_follows", title="New follows per month")

# --- LIKES DATA ---
df_liked_posts = load_likes_json("data/raw/likes/liked_posts.json", "likes_media_likes")
df_liked_comments = load_likes_json("data/raw/likes/liked_comments.json", "likes_comment_likes")

# Add month column
for df in [df_liked_posts, df_liked_comments]:
    df["month"] = df["timestamp"].dt.to_period("M").astype(str)

# Aggregate counts
likes_posts_per_month = df_liked_posts.groupby("month").size().reset_index(name="likes_posts")
likes_comments_per_month = df_liked_comments.groupby("month").size().reset_index(name="likes_comments")

# Merge both
likes_per_month = pd.merge(likes_posts_per_month, likes_comments_per_month, on="month", how="outer").fillna(0)

# Chart: likes (posts vs comments)
fig_likes = px.bar(
    likes_per_month,
    x="month",
    y=["likes_posts", "likes_comments"],
    barmode="group",
    title="Likes given per month (Posts vs Comments)"
)

# --- DASH APP ---
app = dash.Dash(__name__)
app.layout = serve_layout(fig_follows, fig_likes)


if __name__ == "__main__":
    app.run(debug=True)
