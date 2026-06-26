import json
import time

import pandas as pd
import requests

from ..config import (
    ANTHROPIC_API_KEY,
    CLAUDE_RELEVANT_POSTS_FILE,
    CODEBOOK_FILE,
    LLM_CODED_FILE,
    LLM_CODING_PROGRESS_FILE,
    QUALITATIVE_DIR,
)
from src.constants import (
    ANTHROPIC_API_URL,
    ANTHROPIC_API_VERSION,
    CLAUDE_MODEL,
)
from src.qualitative_analysis.models import PostAnalysis


def build_few_shot_string(manual_df: pd.DataFrame, posts_df: pd.DataFrame) -> str:
    col_map = {
        "C1\nSep. Distress":   "C1_separation_distress",
        "C2\nFear Abandon.":   "C2_fear_abandonment",
        "C3\nProx. Seeking":   "C3_proximity_seeking",
        "C4\nReassu. Seeking": "C4_reassurance_seeking",
        "C7\nRom. Dependency": "C5_romantic_dependency",
    }

    posts_lookup = {row["id"]: row for _, row in posts_df.iterrows()}
    examples: list[tuple] = []

    for _, row in manual_df.iterrows():
        post_id = str(row["Post ID"])
        if post_id not in posts_lookup:
            continue

        post  = posts_lookup[post_id]
        text  = post["reddit_post_text"][:1200]
        title = row["Title"]

        codes   = {v: bool(row.get(k) == 1.0) for k, v in col_map.items()}
        relevant = any(codes.values())
        quote   = str(row.get("Best Quote", "")) if pd.notna(row.get("Best Quote")) else None

        output = {
            "relevant": relevant,
            "codes": codes,
            "quotes": {
                "C1": quote if codes.get("C1_separation_distress") else None,
                "C2": quote if codes.get("C2_fear_abandonment") else None,
                "C3": quote if codes.get("C3_proximity_seeking") else None,
                "C4": quote if codes.get("C4_reassurance_seeking") else None,
                "C5": quote if codes.get("C5_romantic_dependency") else None,
            },
            "trauma_context": False,
            "trauma_note": None,
        }
        examples.append((title, text, output))

    result = "\n\nFEW-SHOT EXAMPLES (how to code posts):\n"
    for i, (title, text, output) in enumerate(examples[:8], 1):
        result += f"\nEXAMPLE {i}:\nTitle: {title}\nText: {text}\nOutput: {json.dumps(output)}\n"
    return result


def code_post(title: str, text: str, few_shot_str: str, codebook_system_prompt: str) -> dict | None:
    print("API KEY:", ANTHROPIC_API_KEY)
    print("HALLO HALLO")
    print("HIER")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set. Add it to your .env file.")

    user_message = f"{few_shot_str}\n\nNOW CODE THIS POST:\nTitle: {title}\nText: {text[:2000]}"

    headers = {
        "x-api-key":         ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type":      "application/json",
    }
    payload = {
        "model":      CLAUDE_MODEL,
        "max_tokens": 600,
        "system":     codebook_system_prompt,
        "messages":   [{"role": "user", "content": user_message}],
    }

    for attempt in range(3):
        try:
            r = requests.post(ANTHROPIC_API_URL, headers=headers, json=payload, timeout=30)
            if r.status_code == 429:
                wait = 15 * (attempt + 1)
                print(f"  Rate limit hit, waiting {wait}s...")
                time.sleep(wait)
                continue
            r.raise_for_status()
            content = r.json()["content"][0]["text"].strip()
            start   = content.find("{")
            end     = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(5)

    return None


def save_results(results: list[PostAnalysis], existing_df: pd.DataFrame | None = None) -> None:
    new_rows = pd.DataFrame([r.to_dict() for r in results])
    if existing_df is not None and not existing_df.empty:
        combined = pd.concat([existing_df, new_rows], ignore_index=True)
    else:
        combined = new_rows
    combined.to_csv(LLM_CODED_FILE, index=False)


def save_progress(idx: int) -> None:
    LLM_CODING_PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LLM_CODING_PROGRESS_FILE, "w") as f:
        json.dump({"last_idx": idx}, f)


def run_llm_coding(limit: int | None = None) -> dict:
    from src.constants import QUALITATIVE_CODEBOOK_SYSTEM_PROMPT

    print("Loading data...")
    posts_df  = pd.read_csv(CLAUDE_RELEVANT_POSTS_FILE)
    manual_df = pd.read_excel(CODEBOOK_FILE)

    print(f"Posts to code: {len(posts_df)}")

    few_shot_str = build_few_shot_string(manual_df, posts_df)
    print("Few-shot examples built.")

    start_idx = 0
    results: list[PostAnalysis] = []
    existing_df: pd.DataFrame = pd.DataFrame()

    if LLM_CODING_PROGRESS_FILE.exists():
        with open(LLM_CODING_PROGRESS_FILE) as f:
            progress  = json.load(f)
            start_idx = progress.get("last_idx", 0) + 1
        print(f"Resuming from post {start_idx}")

    if LLM_CODED_FILE.exists() and LLM_CODED_FILE.read_text().strip():
        existing_df = pd.read_csv(LLM_CODED_FILE)
        print(f"Loaded {len(existing_df)} previously coded posts")

    print(f"\nCoding {len(posts_df) - start_idx} posts...\n")

    for idx in range(start_idx, len(posts_df)):
        if limit is not None and (idx - start_idx) >= limit:
            print(f"Limit of {limit} post(s) reached.")
            break

        row     = posts_df.iloc[idx]
        post_id = str(row["id"])
        title   = str(row["title"])
        text    = str(row["reddit_post_text"])

        response = code_post(title, text, few_shot_str, QUALITATIVE_CODEBOOK_SYSTEM_PROMPT)

        if response:
            analysis = PostAnalysis.from_api_response(post_id, title, response)
        else:
            analysis = PostAnalysis(post_id=post_id, title=title, relevant=False, error="api_error")

        results.append(analysis)

        if analysis.relevant:
            codes_on = [k for k, v in analysis.codes.__dict__.items() if v]
            print(f"[{idx+1}/{len(posts_df)}] RELEVANT — {codes_on}")

        if (idx + 1) % 25 == 0:
            relevant_count = sum(1 for r in results if r.relevant)
            print(f"--- [{idx+1}/{len(posts_df)}] relevant so far: {relevant_count} ---")
            save_progress(idx)
            save_results(results, existing_df)

        time.sleep(2)

    save_progress(len(posts_df) - 1)
    save_results(results, existing_df)

    relevant_count = sum(1 for r in results if r.relevant)
    print(f"\nDONE")
    print(f"Total coded:  {len(results)}")
    print(f"Relevant:     {relevant_count}")
    print(f"Saved to:     {LLM_CODED_FILE}")

    return {"total": len(results), "relevant": relevant_count}


if __name__ == "__main__":
    run_llm_coding()
