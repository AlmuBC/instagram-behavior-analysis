import dash
import plotly.express as px
import pandas as pd
import json

from layout import serve_layout  # import layout function
from utils import load_messages_df, load_advertisers, load_ads_view_authors, load_story_likes, load_recommended_topics, build_wordcloud_figure
from callbacks import register_callbacks

from plotly_theme import register_plotly_template
register_plotly_template()


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

# --- MESSAGES ---
df_messages = load_messages_df()

# Mensajes por mes
monthly = df_messages.groupby(["month", "is_sent_by_me"]).size().reset_index(name="n_messages")
monthly["type"] = monthly["is_sent_by_me"].map({True: "Sent", False: "Received"})
fig_messages_month = px.line(
    monthly, x="month", y="n_messages", color="type", markers=True,
    title="Messages Sent vs Received per Month"
)

# Mensajes por hora
df_sent = df_messages[df_messages["is_sent_by_me"]].copy()
df_sent["hour_block"] = (df_sent["hour"] // 4) * 4
df_sent["hour_block"] = df_sent["hour_block"].astype(str) + "-" + (df_sent["hour_block"] + 3).astype(str)
# Agrupar por mes y bloque horario
df_grouped = df_sent.groupby(["month", "hour_block"]).size().reset_index(name="n_messages")

# Pivot para stacked bar
df_pivot = df_grouped.pivot(index="month", columns="hour_block", values="n_messages").fillna(0).astype(int)

# Crear figura
hour_block_order = ["0-3", "4-7", "8-11", "12-15", "16-19", "20-23"]

fig_hour_block = px.bar(
    df_grouped,
    x="month",
    y="n_messages",
    color="hour_block",
    title="Messages Sent by Hour Block per Month",
    labels={"n_messages": "Messages", "hour_block": "Hour Block", "month": "Month"},
    barmode="stack",
    category_orders={"hour_block": hour_block_order}
)

# --- HEATMAP: Messages sent by Day of Week and Hour ---

df_messages["weekday"] = df_messages["timestamp"].dt.day_name()
df_messages["hour"] = df_messages["timestamp"].dt.hour

heatmap_data = df_messages[df_messages["is_sent_by_me"]].groupby(["weekday", "hour"]).size().reset_index(name="count")

# Ordenar días manualmente
ordered_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heatmap_data["weekday"] = pd.Categorical(heatmap_data["weekday"], categories=ordered_days, ordered=True)

# Crear matriz para el heatmap
heatmap_matrix = heatmap_data.pivot(index="weekday", columns="hour", values="count").fillna(0)

fig_messages_heatmap = px.imshow(
    heatmap_matrix,
    labels=dict(x="Hour of Day", y="Day of Week", color="Messages"),
    title="Messages Sent by Day and Hour",
    aspect="auto"
)

# --- ADVERTISERS AND VIEWED AUTHORS ---
df_adv = load_advertisers("data/raw/instagram_ads_and_businesses/advertisers_using_your_activity_or_information.json")
df_authors = load_ads_view_authors("data/raw/ads_and_topics/ads_viewed.json")

# Normalizar nombres de anunciantes
df_adv["normalized_name"] = df_adv["advertiser_name"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)

# Cruce entre anunciantes y autores vistos
df_intersect = df_adv.merge(
    df_authors,
    left_on="normalized_name",
    right_on="normalized_author",
    how="inner",
    suffixes=("_adv", "_auth")
)

# Calculamos métricas básicas
total_adv = len(df_adv)
unique_authors = df_authors["normalized_author"].nunique()
advertisers_shown = len(df_intersect)
# Para el gráfico: solo necesitamos nombre y count
df_intersect_graph = df_intersect[["advertiser_name", "count"]].sort_values("count", ascending=False)

# Figura de barras: anunciantes que te impactaron y nº de anuncios vistos
fig_advertisers_intersect = px.bar(
    df_intersect_graph,
    x="advertiser_name",
    y="count",
    title="Advertisers Using Your Data That Actually Showed You Ads",
    labels={"advertiser_name": "Advertiser", "count": "Ads viewed"}
)


# topics wordcloud
words, topic_freqs = load_recommended_topics(project_root="..")
fig_wordcloud = build_wordcloud_figure(topic_freqs)

fig_right_placeholder = px.imshow([[0]])
fig_right_placeholder.update_xaxes(visible=False); fig_right_placeholder.update_yaxes(visible=False)
fig_right_placeholder.add_annotation(
    text="Aquí irá tu segunda visualización",
    xref="paper", yref="paper", showarrow=False, font=dict(size=18)
)
fig_right_placeholder.update_traces(coloraxis=None, showscale=False)

# --- DASH APP ---
app = dash.Dash(__name__)
register_callbacks(app)  
app.layout = serve_layout(fig_follows, fig_likes, fig_messages_month, fig_hour_block,fig_messages_heatmap,
                          fig_advertisers_intersect, fig_wordcloud)


if __name__ == "__main__":
    app.run(debug=True)
