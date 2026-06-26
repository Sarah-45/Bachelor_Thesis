import argparse
import sys


def cmd_scrape(_args) -> None:
    from src.scraper import run_scraper
    run_scraper()


def cmd_filter_pilot(_args) -> None:
    from src.filter_pilot import run_filter_pilot
    run_filter_pilot()


def cmd_filter(args) -> None:
    from src.filter_full import run_filter_full
    run_filter_full(limit=getattr(args, "limit", None))


def cmd_stats(_args) -> None:
    from src.descriptive_stats import run_descriptive_stats
    run_descriptive_stats()


def cmd_code(args) -> None:
    from src.qualitative_analysis.llm_coding import run_llm_coding
    run_llm_coding(limit=getattr(args, "limit", None))


def cmd_validate(_args) -> None:
    from src.qualitative_analysis.validation import run_validation
    run_validation()


def cmd_analyze(_args) -> None:
    from src.qualitative_analysis.analysis import run_analysis
    run_analysis()


def cmd_pipeline(args) -> None:
    print("=" * 60)
    print("RUNNING FULL PIPELINE")
    print("=" * 60)

    steps = [
        ("filter",   cmd_filter),
        ("stats",    cmd_stats),
        ("code",     cmd_code),
        ("validate", cmd_validate),
        ("analyze",  cmd_analyze),
    ]

    for name, fn in steps:
        print(f"\n{'─'*60}")
        print(f"STEP: {name.upper()}")
        print(f"{'─'*60}")
        fn(args)

    print(f"\n{'='*60}")
    print("PIPELINE COMPLETE")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Replika data analysis pipeline",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    subparsers.add_parser("scrape",       help="Scrape posts from r/Replika")
    subparsers.add_parser("filter-pilot", help="Claude pilot filter on 100 random posts")

    p_filter = subparsers.add_parser("filter", help="Claude relevance filter over full dataset")
    p_filter.add_argument("--limit", type=int, default=None, metavar="N",
                          help="Process at most N posts (overrides auto-skip)")

    subparsers.add_parser("stats",    help="Compute descriptive statistics")

    p_code = subparsers.add_parser("code", help="Qualitative LLM coding of relevant posts")
    p_code.add_argument("--limit", type=int, default=None, metavar="N",
                        help="Code at most N new posts this run")

    subparsers.add_parser("validate", help="Inter-rater agreement: LLM vs manual coding")
    subparsers.add_parser("analyze",  help="Quantitative analysis → Excel output")

    p_pipeline = subparsers.add_parser("pipeline", help="Run filter → stats → code → validate → analyze")
    p_pipeline.add_argument("--limit", type=int, default=None, metavar="N",
                            help="Limit API calls per step (1 = test with a single post per step)")

    args = parser.parse_args()

    dispatch = {
        "scrape":       cmd_scrape,
        "filter-pilot": cmd_filter_pilot,
        "filter":       cmd_filter,
        "stats":        cmd_stats,
        "code":         cmd_code,
        "validate":     cmd_validate,
        "analyze":      cmd_analyze,
        "pipeline":     cmd_pipeline,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
