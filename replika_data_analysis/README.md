# Replika Data Analysis

A Python pipeline for collecting, filtering, and qualitatively coding Reddit posts from r/Replika to study anxious attachment patterns in users who form romantic bonds with their AI companion.

**Research question:** How are anxious attachment patterns expressed in the language of Replika users who form romantic emotional bonds with their AI companion?

## What the pipeline does

| Step | Command | Description |
|------|---------|-------------|
| 1 | `scrape` | Collects posts from r/Replika via the Arctic Shift API using keyword-based search |
| 2 | `filter` | Uses the Claude API to classify each post for relevance (romantic emotional bond + anxious attachment marker) |
| 3 | `stats` | Computes descriptive statistics on the filtered dataset |
| 4 | `code` | Uses the Claude API to apply a qualitative codebook (5 attachment codes) to each relevant post |
| 5 | `validate` | Compares LLM coding against manual coding to calculate inter-rater agreement |
| 6 | `analyze` | Runs quantitative analysis (code frequencies, co-occurrence, linguistic markers) and exports to Excel |

An optional `filter-pilot` command runs the Claude filter on 100 randomly sampled posts for quality validation before committing to the full run.

## Prerequisites

- Python 3.11 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- An [Anthropic API key](https://console.anthropic.com/) for the filtering and coding steps
- (Optional) [Ollama](https://ollama.ai/) with `llama3.2` pulled, if using the local Ollama filter (`filter_ollama.py`)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd replika_data_analysis

# Install dependencies via Poetry
poetry install

# Activate the virtual environment
poetry shell
```

## Configuration

Copy `.env.example` to `.env` and fill in your Anthropic API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The pipeline reads this key automatically via `python-dotenv`. No credentials are ever hardcoded.

## Data

Raw data lives in `data/raw/` and processed outputs in `data/processed/`. These directories are gitignored (large files). The only tracked data file is `data/processed/qualitative/codebook_manual_check.xlsx`, which contains the manual coding reference used for few-shot examples and validation.

If you already have the scraped dataset (`replika_posts_10k_20260504_1505.csv`), place it in `data/raw/` before running the filter step.

## Running the pipeline

### Full pipeline (assumes data is already scraped)

```bash
python main.py pipeline
```

This runs: **filter → stats → code → validate → analyze** in sequence. Each step that supports resuming (filter, code) will pick up where it left off if interrupted.

### Individual steps

```bash
# Step 0: Scrape fresh data from Reddit
python main.py scrape

# Optional: validate filter quality on 100 posts before the full run
python main.py filter-pilot

# Step 1: Filter the full dataset
python main.py filter

# Step 2: Descriptive statistics
python main.py stats

# Step 3: Qualitative coding
python main.py code

# Step 4: Inter-rater validation
python main.py validate

# Step 5: Quantitative analysis -> Excel
python main.py analyze
```

### Help

```bash
python main.py --help
python main.py <command> --help
```

## Project structure

```
replika_data_analysis/
├── .env                          # Your secrets (gitignored)
├── .env.example                  # Template -- copy to .env
├── main.py                       # Single CLI entrypoint
├── pyproject.toml                # Poetry dependency manifest
│
├── data/
│   ├── raw/                      # Downloaded scrape outputs (gitignored)
│   └── processed/
│       └── qualitative/
│           └── codebook_manual_check.xlsx   # Manual coding reference (tracked)
│
├── notebooks/
│   └── archive/                  # Archived Jupyter notebooks
│
└── src/
    ├── config.py                 # Env vars + all file paths
    ├── constants.py              # All prompts, keywords, magic values
    ├── models.py                 # Pydantic model (Ollama filter)
    ├── scraper.py                # Reddit scraper
    ├── filter_pilot.py           # Claude pilot filter (100-post sample)
    ├── filter_full.py            # Claude full relevance filter
    ├── filter_ollama.py          # Local Ollama alternative filter
    ├── descriptive_stats.py      # Descriptive statistics
    └── qualitative_analysis/
        ├── models.py             # Dataclass models for coded results
        ├── llm_coding.py         # Qualitative coding via Claude API
        ├── validation.py         # Inter-rater agreement calculation
        └── analysis.py           # Quantitative analysis -> Excel
```

## Outputs

| File | Description |
|------|-------------|
| `data/processed/claude_relevant_posts.csv` | Posts classified as relevant by the Claude filter |
| `data/processed/descriptive_stats.json` | Summary statistics (post count, lengths, dates, users) |
| `data/processed/qualitative/llm_coded_results.csv` | LLM-coded posts with attachment codes |
| `data/processed/qualitative/validation_results.csv` | Per-post agreement between LLM and manual coding |
| `data/processed/qualitative/analysis_results.xlsx` | Full quantitative analysis (8 sheets) |
