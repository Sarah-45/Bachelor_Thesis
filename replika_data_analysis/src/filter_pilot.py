import csv
import json
import random
import time

import requests

from src.config import (
    ANTHROPIC_API_KEY,
    CLAUDE_PILOT_RESULTS_FILE,
    PROCESSED_DATA_DIR,
    SCRAPED_POSTS_FILE,
)
from src.constants import (
    ANTHROPIC_API_URL,
    ANTHROPIC_API_VERSION,
    CLASSIFICATION_DELAY,
    CLAUDE_FILTER_SYSTEM_PROMPT,
    CLAUDE_MODEL,
    CLAUDE_PILOT_SEED,
    MIN_POST_LENGTH,
    PILOT_SIZE,
)


def load_posts(csv_path=SCRAPED_POSTS_FILE) -> list[dict]:
    posts: list[dict] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get("selftext", "")
            if text and len(text) >= MIN_POST_LENGTH and text not in ("[removed]", "[deleted]"):
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
        "max_tokens": 200,
        "system":     CLAUDE_FILTER_SYSTEM_PROMPT,
        "messages":   [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        content = response.json()["content"][0]["text"].strip()

        start = content.find("{")
        end   = content.rfind("}") + 1
        if start >= 0 and end > start:
            result = json.loads(content[start:end])
            return {
                "is_relevant": result.get("is_relevant", False),
                "confidence":  result.get("confidence", "Low"),
                "reason":      result.get("reason", ""),
            }
        return {"is_relevant": False, "confidence": "Low", "reason": "Could not parse response"}

    except Exception as e:
        print(f"  Error: {e}")
        return {"is_relevant": False, "confidence": "Low", "reason": f"Error: {e}"}


def save_results(results: list[dict], output_path=CLAUDE_PILOT_RESULTS_FILE) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["id", "title", "reddit_post_text", "theme", "keyword",
                      "url", "created_utc", "is_relevant", "confidence", "reason"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def run_filter_pilot() -> dict:
    print(f"Loading posts from {SCRAPED_POSTS_FILE}...")
    posts = load_posts()
    print(f"Total posts loaded: {len(posts)}")

    random.seed(CLAUDE_PILOT_SEED)
    sample = random.sample(posts, min(PILOT_SIZE, len(posts)))
    print(f"Pilot sample size: {len(sample)}")
    print(f"\nRunning Claude API pilot on {len(sample)} posts...")
    print(f"Estimated cost: ~$0.20-0.50\n")

    results: list[dict] = []
    relevant_count = 0
    not_relevant_count = 0

    for idx, post in enumerate(sample):
        title = post.get("title", "")
        text  = post.get("selftext", "")

        result = classify_post(title=title, text=text)

        entry = {
            "id":               post.get("post_id", ""),
            "title":            title,
            "reddit_post_text": text,
            "theme":            post.get("theme", ""),
            "keyword":          post.get("keyword", ""),
            "url":              post.get("url", ""),
            "created_utc":      post.get("created_utc", ""),
            "is_relevant":      result["is_relevant"],
            "confidence":       result["confidence"],
            "reason":           result["reason"],
        }
        results.append(entry)

        if result["is_relevant"]:
            relevant_count += 1
            print(f"[{idx+1}/{len(sample)}] RELEVANT ({result['confidence']}) — total: {relevant_count}")
        else:
            not_relevant_count += 1
            print(f"[{idx+1}/{len(sample)}] not relevant ({result['confidence']})")

        time.sleep(CLASSIFICATION_DELAY)

    save_results(results)
    precision = relevant_count / len(sample) * 100

    print(f"\n{'='*50}")
    print(f"CLAUDE API PILOT DONE")
    print(f"{'='*50}")
    print(f"Total processed:  {len(sample)}")
    print(f"Relevant:         {relevant_count} ({precision:.1f}%)")
    print(f"Not relevant:     {not_relevant_count}")
    print(f"Saved to:         {CLAUDE_PILOT_RESULTS_FILE}")
    print(f"{'='*50}")
    print(f"\nNext step: manually review a sample of the results.")
    print(f"If quality looks good, run: python main.py filter")

    return {"total": len(sample), "relevant": relevant_count, "precision": precision}


if __name__ == "__main__":
    run_filter_pilot()
