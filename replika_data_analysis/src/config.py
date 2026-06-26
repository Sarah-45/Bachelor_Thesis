import os
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).parent.parent

load_dotenv(_PROJECT_ROOT, override=True)

ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY", "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")
OLLAMA_PILOT_MODE: bool = os.environ.get("OLLAMA_PILOT_MODE", "false").lower() == "true"

DATA_DIR           = _PROJECT_ROOT / "data"
RAW_DATA_DIR       = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
QUALITATIVE_DIR    = PROCESSED_DATA_DIR / "qualitative"

SCRAPED_POSTS_FILE = RAW_DATA_DIR / "replika_posts_10k_20260504_1505.csv"

OLLAMA_INPUT_FILE = RAW_DATA_DIR / "reddit_posts.csv"

CODEBOOK_FILE = QUALITATIVE_DIR / "codebook_manual_check.xlsx"

PILOT_POSTS_FILE          = PROCESSED_DATA_DIR / "pilot_posts.csv"
CLAUDE_PILOT_RESULTS_FILE = PROCESSED_DATA_DIR / "claude_pilot_results.csv"
CLAUDE_RELEVANT_POSTS_FILE = PROCESSED_DATA_DIR / "claude_relevant_posts.csv"
CLAUDE_FILTER_PROGRESS_FILE = PROCESSED_DATA_DIR / "claude_progress.json"
DESCRIPTIVE_STATS_FILE    = PROCESSED_DATA_DIR / "descriptive_stats.json"

LLM_CODED_FILE          = QUALITATIVE_DIR / "llm_coded_results.csv"
LLM_CODING_PROGRESS_FILE = QUALITATIVE_DIR / "llm_progress.json"
VALIDATION_RESULTS_FILE  = QUALITATIVE_DIR / "validation_results.csv"
ANALYSIS_RESULTS_FILE    = QUALITATIVE_DIR / "analysis_results.xlsx"

OLLAMA_RELEVANT_POSTS_FILE = PROCESSED_DATA_DIR / "ollama_relevant_posts.csv"
OLLAMA_PROGRESS_FILE       = PROCESSED_DATA_DIR / "ollama_progress.json"
