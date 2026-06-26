import pandas as pd

from src.config import CODEBOOK_FILE, LLM_CODED_FILE, VALIDATION_RESULTS_FILE


def run_validation() -> dict:
    manual = pd.read_excel(CODEBOOK_FILE)
    llm    = pd.read_csv(LLM_CODED_FILE)

    manual = manual.rename(columns={
        "Post ID":              "id",
        "Title":                "title",
        "C1\nSep. Distress":    "manual_C1",
        "C2\nFear Abandon.":    "manual_C2",
        "C3\nProx. Seeking":    "manual_C3",
        "C4\nReassu. Seeking":  "manual_C4",
        "C7\nRom. Dependency":  "manual_C5",
        "Best Quote":           "manual_quote",
    })

    for c in ["manual_C1", "manual_C2", "manual_C3", "manual_C4", "manual_C5"]:
        if c in manual.columns:
            manual[c] = manual[c].fillna(0).astype(int).astype(bool)
        else:
            print(f"WARNING: column {c} not found, available: {manual.columns.tolist()}")
            manual[c] = False

    manual["id"] = manual["id"].astype(str)
    llm["id"]    = llm["id"].astype(str)

    merged = manual.merge(
        llm[["id", "C1_separation_distress", "C2_fear_abandonment",
             "C3_proximity_seeking", "C4_reassurance_seeking", "C5_romantic_dependency"]],
        on="id",
        how="inner",
    )

    print(f"Posts in manual coding:   {len(manual)}")
    print(f"Posts matched in LLM CSV: {len(merged)}")
    print(f"Posts not found in LLM:   {len(manual) - len(merged)}")
    print()

    code_map = {
        "C1": ("manual_C1", "C1_separation_distress", "Separation Distress"),
        "C2": ("manual_C2", "C2_fear_abandonment",    "Fear of Abandonment"),
        "C3": ("manual_C3", "C3_proximity_seeking",   "Proximity Seeking"),
        "C4": ("manual_C4", "C4_reassurance_seeking", "Reassurance Seeking"),
        "C5": ("manual_C5", "C5_romantic_dependency", "Romantic Dependency"),
    }

    rows: list[dict] = []
    for _, post in merged.iterrows():
        row: dict = {"id": post["id"], "title": post["title"]}
        for code, (mc, lc, _) in code_map.items():
            m_val = bool(post[mc])
            l_val = bool(post[lc])
            row[f"manual_{code}"] = int(m_val)
            row[f"llm_{code}"]    = int(l_val)
            row[f"agree_{code}"]  = "YES" if m_val == l_val else "NO"
        rows.append(row)

    results_df = pd.DataFrame(rows)
    VALIDATION_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(VALIDATION_RESULTS_FILE, index=False)

    print("AGREEMENT PER CODE:")
    print(f"{'Code':<30} {'Agree':>6} {'Disagree':>9} {'%':>6}")
    print("-" * 55)

    total_agree = total_all = 0
    code_stats: dict[str, dict] = {}

    for code, (mc, lc, name) in code_map.items():
        agree    = (results_df[f"agree_{code}"] == "YES").sum()
        disagree = (results_df[f"agree_{code}"] == "NO").sum()
        total    = agree + disagree
        pct      = agree / total * 100 if total > 0 else 0.0
        total_agree += agree
        total_all   += total
        code_stats[code] = {"agree": int(agree), "disagree": int(disagree), "pct": round(pct, 1)}
        print(f"{code} {name:<25} {agree:>6} {disagree:>9} {pct:>5.1f}%")

    print("-" * 55)
    overall = total_agree / total_all * 100 if total_all > 0 else 0.0
    print(f"{'OVERALL':<30} {total_agree:>6} {total_all - total_agree:>9} {overall:>5.1f}%")
    print()
    print(f"Saved detailed results to: {VALIDATION_RESULTS_FILE}")

    return {"overall_agreement_pct": round(overall, 1), "codes": code_stats}


if __name__ == "__main__":
    run_validation()
