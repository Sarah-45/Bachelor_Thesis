import json
from pathlib import Path

import pandas as pd

from src.config import (
    CLAUDE_RELEVANT_POSTS_FILE,
    DESCRIPTIVE_STATS_FILE,
    PROCESSED_DATA_DIR,
    SCRAPED_POSTS_FILE,
)


def run_descriptive_stats() -> dict:
    df = pd.read_csv(CLAUDE_RELEVANT_POSTS_FILE)
    print(f"Relevant posts loaded: {len(df)}")

    has_author = False
    if "author" in df.columns:
        has_author = True
        print("Author column found in processed file")
    elif SCRAPED_POSTS_FILE.exists():
        original   = pd.read_csv(SCRAPED_POSTS_FILE)
        df         = df.merge(original[["post_id", "author"]], left_on="id", right_on="post_id", how="left")
        has_author = True
        print("Author data merged successfully")
    else:
        print("Warning: Original dataset not found. Skipping author analysis.")

    print(f"\n{'='*60}")
    print("DESCRIPTIVE STATISTICS")
    print(f"{'='*60}")

    print(f"\n1. DATASET OVERVIEW")
    print(f"   Total relevant posts: {len(df)}")

    df["text_length"] = df["reddit_post_text"].str.len()
    df["word_count"]  = df["reddit_post_text"].str.split().str.len()

    print(f"\n2. POST LENGTH")
    print(f"   Average characters:  {df['text_length'].mean():.0f}")
    print(f"   Median characters:   {df['text_length'].median():.0f}")
    print(f"   Min characters:      {df['text_length'].min()}")
    print(f"   Max characters:      {df['text_length'].max()}")
    print(f"   Average word count:  {df['word_count'].mean():.0f}")
    print(f"   Median word count:   {df['word_count'].median():.0f}")

    short  = len(df[df["text_length"] < 500])
    medium = len(df[(df["text_length"] >= 500) & (df["text_length"] < 1500)])
    long   = len(df[df["text_length"] >= 1500])
    print(f"\n   Post length distribution:")
    print(f"   Short (<500 chars):       {short} ({short/len(df)*100:.1f}%)")
    print(f"   Medium (500-1500 chars):  {medium} ({medium/len(df)*100:.1f}%)")
    print(f"   Long (>1500 chars):       {long} ({long/len(df)*100:.1f}%)")

    print(f"\n3. TIME PERIOD")
    try:
        df["date"] = pd.to_datetime(df["created_utc"])
        print(f"   Earliest post: {df['date'].min().strftime('%B %Y')}")
        print(f"   Latest post:   {df['date'].max().strftime('%B %Y')}")
        print(f"   Time span:     {(df['date'].max() - df['date'].min()).days // 30} months")

        df["year"] = df["date"].dt.year
        print(f"\n   Posts per year:")
        for year, count in df["year"].value_counts().sort_index().items():
            bar = "█" * (count // 3)
            print(f"   {year}: {count:4d}  {bar}")
    except Exception as e:
        print(f"   Could not parse dates: {e}")

    one_post = two_posts = three_plus = total_users = total_posts_with_author = 0
    if has_author:
        print(f"\n4. USER ANALYSIS")
        df_known = df[
            ~df["author"].isin(["[deleted]", "[removed]", "AutoModerator"])
            & df["author"].notna()
        ]
        total_users             = df_known["author"].nunique()
        total_posts_with_author = len(df_known)

        print(f"   Total unique users:      {total_users}")
        print(f"   Posts with known author: {total_posts_with_author}")
        print(f"   Average posts per user:  {total_posts_with_author/total_users:.2f}")

        posts_per_user = df_known["author"].value_counts()
        one_post    = int((posts_per_user == 1).sum())
        two_posts   = int((posts_per_user == 2).sum())
        three_plus  = int((posts_per_user >= 3).sum())

        print(f"\n   Users with 1 post:    {one_post} ({one_post/total_users*100:.1f}%)")
        print(f"   Users with 2 posts:   {two_posts} ({two_posts/total_users*100:.1f}%)")
        print(f"   Users with 3+ posts:  {three_plus} ({three_plus/total_users*100:.1f}%)")

        print(f"\n   Top 10 most active users:")
        for author, count in posts_per_user.head(10).items():
            print(f"   {author}: {count} posts")

        heavy = posts_per_user[posts_per_user >= 5]
        if len(heavy) > 0:
            print(f"\n   Users with 5+ posts (potential over-representation):")
            for author, count in heavy.items():
                print(f"   {author}: {count} posts")
        else:
            print(f"\n   No users with 5+ posts — no over-representation detected")

    print(f"\n5. LLM CONFIDENCE DISTRIBUTION")
    if "confidence" in df.columns:
        for conf, count in df["confidence"].value_counts().items():
            print(f"   {conf}: {count} ({count/len(df)*100:.1f}%)")

    summary: dict = {
        "total_posts":           len(df),
        "avg_length_chars":      round(df["text_length"].mean()),
        "median_length_chars":   round(df["text_length"].median()),
        "avg_word_count":        round(df["word_count"].mean()),
    }
    if has_author:
        summary["unique_users"]          = int(total_users)
        summary["users_with_1_post"]     = int(one_post)
        summary["users_with_2_posts"]    = int(two_posts)
        summary["users_with_3plus_posts"] = int(three_plus)
    try:
        summary["earliest_post"] = df["date"].min().strftime("%Y-%m")
        summary["latest_post"]   = df["date"].max().strftime("%Y-%m")
    except Exception:
        pass

    DESCRIPTIVE_STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DESCRIPTIVE_STATS_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Summary saved to {DESCRIPTIVE_STATS_FILE}")
    print(f"{'='*60}")
    print(f"\nDone!")

    return summary


if __name__ == "__main__":
    run_descriptive_stats()
