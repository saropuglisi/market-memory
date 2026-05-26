"""Build degradation table + per-metric line plots across L1..L5."""
from __future__ import annotations
import json
import os
import sys
import glob
from datetime import datetime

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(ROOT, "results")
PLOTS_DIR = os.path.join(RESULTS_DIR, "degradation_plots")
os.makedirs(PLOTS_DIR, exist_ok=True)


def latest_run(level: str) -> str:
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, f"run_{level}_*.json")))
    if not files:
        raise FileNotFoundError(f"no run_{level}_*.json in {RESULTS_DIR}")
    return files[-1]


def load_per_level(levels) -> dict:
    out = {}
    for L in levels:
        path = latest_run(L)
        with open(path) as f:
            data = json.load(f)
        per_enc = {r["name"]: r for r in data["results"]}
        out[L] = {"path": path, "results": per_enc, "n_train": data.get("n_train"),
                  "n_test": data.get("n_test")}
        print(f"{L}: {os.path.basename(path)}  ({data.get('n_train')}/{data.get('n_test')})")
    return out


def trend_label(vals):
    arr = np.array(vals, dtype=float)
    if np.all(np.isnan(arr)):
        return "—"
    # Drop NaNs for trend assessment
    a = arr[~np.isnan(arr)]
    if len(a) < 2:
        return "—"
    diff = np.diff(a)
    total = a[-1] - a[0]
    if a[-1] > a[0] + 0.05:
        return "improving"
    # max single-step drop
    max_drop = float(diff.min()) if len(diff) > 0 else 0.0
    if abs(total) < 0.05:
        return "stable"
    if max_drop < -0.15:
        return "cliff"
    return "graceful"


def build_table(per_level, metric_key: str, levels, encoders) -> str:
    headers = ["Approach"] + [f"{L} {metric_key}" for L in levels] + ["Trend"]
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(["---"] * len(headers)) + "|"]
    for enc in encoders:
        row = [enc]
        vals = []
        for L in levels:
            r = per_level[L]["results"].get(enc)
            if r is None:
                row.append("—"); vals.append(float("nan"))
            else:
                v = r.get(metric_key)
                row.append(f"{v:.3f}" if v is not None else "—")
                vals.append(v if v is not None else float("nan"))
        row.append(trend_label(vals))
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def make_plots(per_level, levels, encoders, metric_keys: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = plt.get_cmap("tab10")
    for metric_key, pretty in metric_keys.items():
        fig, ax = plt.subplots(figsize=(10, 6))
        for i, enc in enumerate(encoders):
            ys = []
            for L in levels:
                r = per_level[L]["results"].get(enc)
                ys.append(r.get(metric_key) if r else None)
            ax.plot(levels, ys, "o-", label=enc, color=colors(i), linewidth=2, markersize=8)
        ax.set_xlabel("Difficulty level")
        ax.set_ylabel(pretty)
        ax.set_title(f"{pretty} across L1..L5")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", fontsize=9)
        out = os.path.join(PLOTS_DIR, f"{metric_key}.png")
        plt.tight_layout()
        plt.savefig(out, dpi=120)
        plt.close()
        print(f"  saved {out}")


def load_llm_v3(per_level: dict, levels):
    """Inject llm_structured_v3 rows from saved llm_v3_*.json files."""
    files = sorted(glob.glob(os.path.join(RESULTS_DIR, "llm_v3_*.json")))
    if not files:
        print("no llm_v3 results found")
        return
    combined = {}
    for f in files:
        d = json.load(open(f))
        combined.update(d)
    for L in levels:
        r = combined.get(L)
        if not r:
            continue
        per_level[L]["results"]["llm_structured_v3"] = {
            "name": "llm_structured_v3",
            "precision_at_5": r["precision_at_5"],
            "precision_at_10": r["precision_at_10"],
            "reaction_corr": r["reaction_corr"],
            "utility_at_5": r["utility_at_5"],
            "conditional_quality": r["conditional_quality"],
            "fail_count": r.get("fail_count", 0),
            "distribution": r.get("distribution", {}),
        }


def main():
    levels = ["L1", "L2", "L3", "L4", "L5"]
    encoders = ["concat_raw", "concat_eq", "factorized", "contrastive",
                "contrastive_v2", "contrastive_v3", "graph_experimental",
                "llm_structured_v3"]
    metrics = {
        "precision_at_5": "P@5",
        "reaction_corr": "ReactCorr",
        "utility_at_5": "Util@5",
        "conditional_quality": "CondQual",
    }
    per_level = load_per_level(levels)
    load_llm_v3(per_level, levels)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_md = os.path.join(RESULTS_DIR, "DEGRADATION_TABLE.md")
    sections = [f"# Degradation table — L1 to L5\n",
                f"Generated {ts}.",
                f"n_train/n_test per level:",
                "\n".join(f"- {L}: {per_level[L]['n_train']}/{per_level[L]['n_test']}" for L in levels),
                ""]
    for key, pretty in metrics.items():
        sections.append(f"## {pretty}\n")
        sections.append(build_table(per_level, key, levels, encoders))
        sections.append("")

    # Head-to-head v3 vs contrastive_v2
    sections.append("## LLM v3 vs contrastive_v2 — head-to-head\n")
    sections.append("Delta = v3 − contrastive_v2.")
    sections.append("")
    h2h_rows = ["| Level | metric | contrastive_v2 | llm_v3 | Δ |",
                "|---|---|---|---|---|"]
    for L in levels:
        v2 = per_level[L]["results"].get("contrastive_v2", {})
        v3 = per_level[L]["results"].get("llm_structured_v3", {})
        for mkey, mpretty in [("precision_at_5", "P@5"),
                              ("reaction_corr", "RC"),
                              ("utility_at_5", "Util@5")]:
            a = v2.get(mkey); b = v3.get(mkey)
            if a is None or b is None:
                continue
            d = b - a
            mark = "**" if abs(d) > 0.05 else ""
            h2h_rows.append(f"| {L} | {mpretty} | {a:.3f} | {b:.3f} | {mark}{d:+.3f}{mark} |")
    sections.append("\n".join(h2h_rows))
    sections.append("")

    # Cycle_phase distributions for v3
    sections.append("## Cycle_phase distribution — LLM v3 per livello\n")
    cy_rows = ["| Level | mid | late | recovery | early | recession | n |",
               "|---|---|---|---|---|---|---|"]
    for L in levels:
        v3 = per_level[L]["results"].get("llm_structured_v3", {})
        dist = v3.get("distribution", {}).get("cycle_phase", {})
        if not dist:
            continue
        total = sum(dist.values()) or 1
        def pct(k): return f"{dist.get(k,0)} ({dist.get(k,0)/total:.0%})"
        cy_rows.append(f"| {L} | {pct('mid')} | {pct('late')} | {pct('recovery')} | {pct('early')} | {pct('recession')} | {total} |")
    sections.append("\n".join(cy_rows))
    sections.append("")
    sections.append("Per riferimento — v2 cache su L2 v2 mostrava mid=72%, late=11%.")
    sections.append("Il prompt direttivo v3 raddoppia/triplica la frequenza di `late` ma azzera `early`/`recession`.")

    with open(out_md, "w") as f:
        f.write("\n".join(sections))
    print(f"saved: {out_md}")

    print("\nplots:")
    make_plots(per_level, levels, encoders, metrics)


if __name__ == "__main__":
    main()
