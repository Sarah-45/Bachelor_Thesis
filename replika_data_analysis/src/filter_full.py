import csv
import json
import time

import requests

from src.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_FILTER_PROGRESS_FILE,
    CLAUDE_RELEVANT_POSTS_FILE,
    PROCESSED_DATA_DIR,
    SCRAPED_POSTS_FILE,
)
from src.constants import (
    ANTHROPIC_API_URL,
    ANTHROPIC_API_VERSION,
    CLASSIFICATION_DELAY,
    CLAUDE_FILTER_SYSTEM_PROMPT,
    CLAUDE_MODEL,
    MIN_POST_LENGTH,
    SAVE_EVERY_N_POSTS,
)


def load_and_clean_posts(csv_path=SCRAPED_POSTS_FILE) -> list[dict]:
    posts: list[dict] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("selftext", "")
            if text and len(text) >= MIN_POST_LENGTH:
                posts.append(row)
    return posts


def classify_post(title: str, text: str) -> dict:
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

    prompt = f"Title: {title}\n\n{text[:2000]}"
    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type":      "application/json",
    }
    payload = {
        "model":      CLAUDE_MODEL,
        "max_tokens": 150,
        "system":     CLAUDE_FILTER_SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": prompt}],
    }

    try:
        r = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        content = r.json()["content"][0]["text"].strip()
        start = content.find("{")
        end   = content.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(content[start:end])
            return {
                "is_relevant": result.get("is_relevant", False),
                "confidence":  result.get("confidence", "Low"),
                "reason":      result.get("reason", ""),
            }
    except Exception as e:
        print(f"  Error: {e}")

    return {"is_relevant": False, "confidence": "Low", "reason": "error"}


def save_progress(idx: int) -> None:
    CLAUDE_FILTER_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CLAUDE_FILTER_PROGRESS_FILE, "w") as f:
        json.dump({"last_idx": idx}, f)


def save_results(relevant_posts: list[dict]) -> None:
    CLAUDE_RELEVANT_POSTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CLAUDE_RELEVANT_POSTS_FILE, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["id", "title", "reddit_post_text", "theme", "keyword",
                      "url", "created_utc", "author", "confidence", "reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relevant_posts)


def run_filter_full(limit: int | None = None) -> dict:
    if CLAUDE_RELEVANT_POSTS_FILE.exists() and CLAUDE_RELEVANT_POSTS_FILE.stat().st_size > 0 and limit is None:
        with open(CLAUDE_RELEVANT_POSTS_FILE, "r", encoding="utf-8-sig") as f:
            n = sum(1 for _ in f) - 1
        print(f"Filter output already exists ({n} relevant posts). Skipping. Pass --limit to override.")
        return {"total": 0, "relevant": n, "precision": 0.0, "skipped": True}

    print(f"Loading posts from {SCRAPED_POSTS_FILE}...")
    posts = load_and_clean_posts()
    print(f"Total posts loaded: {len(posts)}")

    start_idx = 0
    relevant_posts: list[dict] = []

    if CLAUDE_FILTER_PROGRESS_FILE.exists():
        with open(CLAUDE_FILTER_PROGRESS_FILE, "r") as f:
            progress = json.load(f)
            start_idx = progress.get("last_idx", 0) + 1
            print(f"Resuming from post {start_idx}")
    else:
        print("Starting fresh run")

    if CLAUDE_RELEVANT_POSTS_FILE.exists() and CLAUDE_RELEVANT_POSTS_FILE.stat().st_size > 0:
        with open(CLAUDE_RELEVANT_POSTS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            relevant_posts = list(reader)
        print(f"Loaded {len(relevant_posts)} previously found relevant posts")

    not_relevant = 0
    print(f"\nProcessing {len(posts) - start_idx} posts...\n")

    for idx in range(start_idx, len(posts)):
        if limit is not None and (idx - start_idx) >= limit:
            print(f"Limit of {limit} post(s) reached.")
            break

        post  = posts[idx]
        title = post.get("title", "")
        text  = post.get("selftext", "")

        result = classify_post(title=title, text=text)

        if result["is_relevant"]:
            relevant_posts.append({
                "id":               post.get("post_id", ""),
                "title":            title,
                "reddit_post_text": text,
                "theme":            post.get("theme", ""),
                "keyword":          post.get("keyword", ""),
                "url":              post.get("url", ""),
                "created_utc":      post.get("created_utc", ""),
                "author":           post.get("author", ""),
                "confidence":       result["confidence"],
                "reason":           result["reason"],
            })
            print(f"[{idx+1}/{len(posts)}] RELEVANT ({result['confidence']}) — total: {len(relevant_posts)}")
        else:
            not_relevant += 1

        if (idx + 1) % SAVE_EVERY_N_POSTS == 0:
            total_done = idx + 1
            precision  = len(relevant_posts) / total_done * 100
            print(f"--- [{total_done}/{len(posts)}] relevant: {len(relevant_posts)} ({precision:.1f}%) ---")
            save_progress(idx)
            save_results(relevant_posts)

        time.sleep(CLASSIFICATION_DELAY)

    save_progress(len(posts) - 1)
    save_results(relevant_posts)

    total_done = len(posts) - start_idx
    precision  = len(relevant_posts) / total_done * 100 if total_done > 0 else 0.0

    print(f"\n{'='*50}")
    print(f"DONE")
    print(f"Total processed: {total_done}")
    print(f"Relevant:        {len(relevant_posts)}")
    print(f"Not relevant:    {not_relevant}")
    if total_done > 0:
        print(f"Precision:       {precision:.1f}%")
    print(f"Saved to:        {CLAUDE_RELEVANT_POSTS_FILE}")
    print(f"{'='*50}")

    return {"total": total_done, "relevant": len(relevant_posts), "precision": precision}


if __name__ == "__main__":
    run_filter_full()
