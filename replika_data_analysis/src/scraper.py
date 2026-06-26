import time
from datetime import datetime

import pandas as pd
import requests

from src.constants import (
    ARCTIC_SHIFT_BASE_URL,
    SCRAPER_BATCH_SIZE,
    SCRAPER_DELAY,
    SCRAPER_KEYWORDS,
    SCRAPER_MAX_BATCHES,
    SCRAPER_SUBREDDITS,
)
from src.config import RAW_DATA_DIR


def search_posts_paginated(subreddit: str, keyword: str, max_batches: int = SCRAPER_MAX_BATCHES) -> list[dict]:
    all_posts: list[dict] = []
    after = None

    for batch_num in range(max_batches):
        params: dict = {
            "subreddit": subreddit,
            "query":     keyword,
            "limit":     SCRAPER_BATCH_SIZE,
            "sort":      "desc",
        }
        if after:
            params["after"] = after

        try:
            r = requests.get(f"{ARCTIC_SHIFT_BASE_URL}/posts/search", params=params, timeout=20)
            r.raise_for_status()
            data = r.json()
            batch = data.get("data", [])

            if not batch:
                break

            all_posts.extend(batch)

            after = data.get("metadata", {}).get("after")
            if not after:
                break

            time.sleep(0.3)

        except Exception as e:
            print(f" [batch {batch_num + 1} error: {e}]", end="")
            break

    return all_posts


def get_comments(post_id: str, limit: int = 100) -> list[dict]:
    try:
        r = requests.get(
            f"{ARCTIC_SHIFT_BASE_URL}/comments/search",
            params={"link_id": f"t3_{post_id}", "limit": limit},
            timeout=20,
        )
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception:
        return []


def run_scraper() -> dict:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    total_keywords = sum(len(v) for v in SCRAPER_KEYWORDS.values())
    print(f"   Large-scale Replika scraper — target: 10,000+ posts\n")
    print(f"   Subreddits: {', '.join(SCRAPER_SUBREDDITS)}")
    print(f"   Keywords: {total_keywords} total")
    print(f"   Max per keyword: {SCRAPER_BATCH_SIZE * SCRAPER_MAX_BATCHES}\n")

    collected_posts: dict[str, dict] = {}
    collected_comments: dict[str, dict] = {}

    for subreddit in SCRAPER_SUBREDDITS:
        print(f"\n r/{subreddit}")

        for theme, keywords in SCRAPER_KEYWORDS.items():
            print(f"\n   {theme}")

            for keyword in keywords:
                print(f"      '{keyword}'...", end=" ", flush=True)

                posts = search_posts_paginated(subreddit, keyword)
                new = 0

                for post in posts:
                    pid = post.get("id")
                    if not pid or pid in collected_posts:
                        continue

                    collected_posts[pid] = {
                        "post_id":      pid,
                        "subreddit":    subreddit,
                        "title":        post.get("title", ""),
                        "selftext":     post.get("selftext", ""),
                        "score":        post.get("score", 0),
                        "num_comments": post.get("num_comments", 0),
                        "url":          f"https://reddit.com/r/{subreddit}/comments/{pid}",
                        "created_utc":  datetime.fromtimestamp(
                            int(post.get("created_utc", 0))
                        ).strftime("%Y-%m-%d"),
                        "keyword":      keyword,
                        "theme":        theme,
                        "author":       post.get("author", "[deleted]"),
                    }
                    new += 1

                    comments = get_comments(pid)
                    for c in comments:
                        cid = c.get("id")
                        if cid and cid not in collected_comments:
                            collected_comments[cid] = {
                                "comment_id":    cid,
                                "post_id":       pid,
                                "subreddit":     subreddit,
                                "body":          c.get("body", ""),
                                "score":         c.get("score", 0),
                                "created_utc":   datetime.fromtimestamp(
                                    int(c.get("created_utc", 0))
                                ).strftime("%Y-%m-%d"),
                                "keyword_match": keyword,
                                "theme":         theme,
                                "author":        c.get("author", "[deleted]"),
                            }

                print(f"{new} new  (total so far: {len(collected_posts)})")
                time.sleep(SCRAPER_DELAY)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    print(f"\n{'='*50}")
    print(f"FINAL TOTAL: {len(collected_posts)} posts, {len(collected_comments)} comments")
    print(f"{'='*50}")

    posts_file = RAW_DATA_DIR / f"replika_posts_10k_{timestamp}.csv"
    if collected_posts:
        posts_df = pd.DataFrame(list(collected_posts.values()))
        posts_df.to_csv(posts_file, index=False, encoding="utf-8-sig")
        print(f"\n Posts saved: {posts_file}")
        print(f"\n Posts per theme:")
        print(posts_df["theme"].value_counts().to_string())
        print(f"\n Posts per subreddit:")
        print(posts_df["subreddit"].value_counts().to_string())

    if collected_comments:
        comments_file = RAW_DATA_DIR / f"replika_comments_10k_{timestamp}.csv"
        comments_df = pd.DataFrame(list(collected_comments.values()))
        comments_df.to_csv(comments_file, index=False, encoding="utf-8-sig")
        print(f" Comments saved: {comments_file}")

    print("\nDone!")
    return {"posts": len(collected_posts), "comments": len(collected_comments), "file": str(posts_file)}


if __name__ == "__main__":
    run_scraper()
