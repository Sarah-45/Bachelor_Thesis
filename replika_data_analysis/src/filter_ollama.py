import csv
import json
import random
import time
from pathlib import Path

from ollama import ChatResponse, chat

from src.config import (
    OLLAMA_INPUT_FILE,
    OLLAMA_PILOT_MODE,
    OLLAMA_PROGRESS_FILE,
    OLLAMA_RELEVANT_POSTS_FILE,
    PILOT_POSTS_FILE,
    PROCESSED_DATA_DIR,
)
from src.constants import (
    OLLAMA_DELAY,
    OLLAMA_FILTER_SYSTEM_PROMPT,
    OLLAMA_MODEL,
    OLLAMA_PILOT_SEED,
    PILOT_SIZE,
    SAVE_EVERY_N_POSTS,
)
from src.models import PostRelevance


def collect_reddit_posts(csv_path: Path = OLLAMA_INPUT_FILE) -> list[dict]:
    posts: list[dict] = []
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(dict(row))
    return posts


def classify_post(title: str, text: str) -> dict:
    prompt = f"Title: {title}\n\n{text[:2000]}"

    try:
        response: ChatResponse = chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": OLLAMA_FILTER_SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            format=PostRelevance.model_json_schema(),
        )
        result = PostRelevance.model_validate_json(response.message.content)
        return result.model_dump()

    except Exception as e:
        print(f"Error: {e}")
        return {"is_relevant": False, "confidence": "Low"}


def build_entry(rp: dict, idx: int, result: dict) -> dict:
    return {
        "id":               rp.get("post_id", idx),
        "title":            rp.get("title", ""),
        "reddit_post_text": rp.get("selftext", ""),
        "theme":            rp.get("theme", ""),
        "keyword":          rp.get("keyword", ""),
        "url":              rp.get("url", ""),
        "created_utc":      rp.get("created_utc", ""),
        "confidence":       result.get("confidence", ""),
    }


def _save_progress(idx: int) -> None:
    OLLAMA_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OLLAMA_PROGRESS_FILE, "w") as f:
        json.dump({"last_processed_idx": idx}, f)


def _save_results(relevant_posts: list[dict], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["id", "title", "reddit_post_text", "theme",
                      "keyword", "url", "created_utc", "confidence"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relevant_posts)


def run_filter_ollama(pilot_mode: bool = False) -> dict:
    reddit_posts = collect_reddit_posts()
    print(f"Total posts loaded: {len(reddit_posts)}")

    cleaned: list[dict] = []
    for rp in reddit_posts:
        text = rp.get("selftext", "")
        if not text or text.strip() in ("[removed]", "[deleted]", "") or len(text) < 100:
            continue
        cleaned.append(rp)

    print(f"Posts after cleaning: {len(cleaned)}")

    if pilot_mode:
        print(f"\n--- PILOT MODE: running on {PILOT_SIZE} random posts ---")
        print(f"--- After pilot, check quality manually, then run with pilot_mode=False ---\n")

        random.seed(OLLAMA_PILOT_SEED)
        pilot_posts = random.sample(cleaned, min(PILOT_SIZE, len(cleaned)))

        relevant_posts: list[dict] = []
        not_relevant = 0

        for idx, rp in enumerate(pilot_posts):
            result = classify_post(title=rp.get("title", ""), text=rp.get("selftext", ""))

            if result["is_relevant"]:
                entry = build_entry(rp, idx, result)
                relevant_posts.append(entry)
                print(f"[{idx+1}/{PILOT_SIZE}] RELEVANT ({result['confidence']}) — total: {len(relevant_posts)}")
            else:
                not_relevant += 1
                print(f"[{idx+1}/{PILOT_SIZE}] not relevant ({result['confidence']})")

            time.sleep(OLLAMA_DELAY)

        _save_results(relevant_posts, PILOT_POSTS_FILE)

        print(f"\n{'='*50}")
        print(f"PILOT DONE")
        print(f"Processed:     {PILOT_SIZE}")
        print(f"Relevant:      {len(relevant_posts)}")
        print(f"Not relevant:  {not_relevant}")
        print(f"Precision:     {len(relevant_posts)/PILOT_SIZE*100:.1f}%")
        print(f"Saved to:      {PILOT_POSTS_FILE}")
        print(f"{'='*50}")
        print(f"\nNext step: review pilot_posts.csv manually.")
        print(f"If quality is good, run again with pilot_mode=False.")

        return {"status": "pilot_done", "relevant": len(relevant_posts)}

    start_idx = 0
    relevant_posts = []

    if OLLAMA_PROGRESS_FILE.exists():
        with open(OLLAMA_PROGRESS_FILE, "r") as f:
            progress  = json.load(f)
            start_idx = progress.get("last_processed_idx", 0) + 1
            print(f"Resuming from post {start_idx}")
    else:
        print("Starting fresh run")

    if OLLAMA_RELEVANT_POSTS_FILE.exists() and OLLAMA_RELEVANT_POSTS_FILE.stat().st_size > 0:
        with open(OLLAMA_RELEVANT_POSTS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            relevant_posts = list(reader)
        print(f"Loaded {len(relevant_posts)} previously found relevant posts")

    not_relevant = 0

    for idx in range(start_idx, len(cleaned)):
        rp    = cleaned[idx]
        result = classify_post(title=rp.get("title", ""), text=rp.get("selftext", ""))

        if result["is_relevant"]:
            entry = build_entry(rp, idx, result)
            relevant_posts.append(entry)
            print(f"[{idx}] RELEVANT ({result['confidence']}) — total: {len(relevant_posts)}")
        else:
            not_relevant += 1

        if (idx + 1) % SAVE_EVERY_N_POSTS == 0:
            total_done = idx + 1
            precision  = len(relevant_posts) / total_done * 100
            print(f"--- [{total_done}/{len(cleaned)}] relevant: {len(relevant_posts)} ({precision:.1f}%) ---")
            _save_progress(idx)
            _save_results(relevant_posts, OLLAMA_RELEVANT_POSTS_FILE)

        time.sleep(OLLAMA_DELAY)

    _save_progress(len(cleaned) - 1)
    _save_results(relevant_posts, OLLAMA_RELEVANT_POSTS_FILE)

    total_done = len(cleaned) - start_idx
    print(f"\n{'='*50}")
    print(f"DONE")
    print(f"Total processed: {total_done}")
    print(f"Relevant:        {len(relevant_posts)}")
    print(f"Not relevant:    {not_relevant}")
    if total_done > 0:
        print(f"Precision:       {len(relevant_posts)/total_done*100:.1f}%")
    print(f"Saved to:        {OLLAMA_RELEVANT_POSTS_FILE}")
    print(f"{'='*50}")

    return {"status": "ok", "relevant": len(relevant_posts)}


if __name__ == "__main__":
    run_filter_ollama()
