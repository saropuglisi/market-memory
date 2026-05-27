"""Compare Qwen v2 tag extraction against manual annotations on 25 events.

Reads:
  real_data/processed/manual_tags_validation.json     (ground truth)
  real_data/processed/sample_500_narrative_tags_v2.json (Qwen v2)

Writes:
  real_data/processed/qwen_vs_manual_comparison.md

Reports per tag: precision, recall, F1, TP/FP/FN counts, and the specific
events where Qwen disagrees with manual. Also flags overall mean F1 and
which tags are below the 0.4 / 0.6 thresholds.
"""
from __future__ import annotations
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags_v2 import TAG_KEYS_V2

PROCESSED = os.path.join(ROOT, "real_data", "processed")
MANUAL_PATH = os.path.join(PROCESSED, "manual_tags_validation.json")
QWEN_PATH   = os.path.join(PROCESSED, "sample_500_narrative_tags_v2.json")
OUT_PATH    = os.path.join(PROCESSED, "qwen_vs_manual_comparison.md")


def prf(tp, fp, fn):
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def main():
    with open(MANUAL_PATH) as f:
        manual = json.load(f)["annotations"]
    with open(QWEN_PATH) as f:
        qwen = json.load(f)

    ids = sorted(manual.keys())
    print(f"comparing {len(ids)} events × {len(TAG_KEYS_V2)} tags")

    per_tag = {}
    disagreements_by_tag = {k: [] for k in TAG_KEYS_V2}

    for tag in TAG_KEYS_V2:
        tp = fp = fn = tn = 0
        for eid in ids:
            m_v = int(manual[eid].get(tag, 0))
            q_v = int(qwen.get(eid, {}).get(tag, 0))
            if m_v == 1 and q_v == 1: tp += 1
            elif m_v == 0 and q_v == 1: fp += 1; disagreements_by_tag[tag].append(("FP", eid, manual[eid].get("_ticker"), manual[eid].get("_date")))
            elif m_v == 1 and q_v == 0: fn += 1; disagreements_by_tag[tag].append(("FN", eid, manual[eid].get("_ticker"), manual[eid].get("_date")))
            else: tn += 1
        p, r, f1 = prf(tp, fp, fn)
        per_tag[tag] = {"tp":tp, "fp":fp, "fn":fn, "tn":tn,
                        "precision":p, "recall":r, "f1":f1,
                        "n_manual_yes": tp+fn, "n_qwen_yes": tp+fp}

    # Mean F1 (macro; skip tags with no positives in manual)
    f1s = [v["f1"] for k, v in per_tag.items() if v["n_manual_yes"] > 0]
    macro_f1 = sum(f1s) / len(f1s) if f1s else 0.0

    # ── report ──
    lines = ["# Qwen v2 vs manual annotations — 25-event validation", ""]
    lines.append(f"manual annotator: Claude (ground truth proxy)  |  N events: {len(ids)}  |  tags: {len(TAG_KEYS_V2)}")
    lines.append(f"**Macro mean F1 (across tags with ≥1 positive in manual): {macro_f1:.3f}**")
    lines.append("")

    # Acceptance criteria check
    bad = [k for k, v in per_tag.items() if v["n_manual_yes"] > 0 and v["f1"] < 0.4]
    moderate = [k for k, v in per_tag.items() if v["n_manual_yes"] > 0 and 0.4 <= v["f1"] < 0.6]
    if macro_f1 < 0.6 or len(bad) >= 3:
        lines.append("## ⚠️  REVIEW NEEDED  (per spec: macro F1 < 0.6 OR ≥3 tags with F1 < 0.4)")
        lines.append(f"- macro F1 = {macro_f1:.3f}")
        lines.append(f"- tags with F1 < 0.4 (count {len(bad)}): {', '.join(bad) or 'none'}")
        lines.append("")
    else:
        lines.append("✓ acceptance criteria met (macro F1 ≥ 0.6, fewer than 3 tags below F1=0.4).")
        lines.append("")

    lines.append("## Per-tag scores")
    lines.append("")
    lines.append("| tag | manual+ | qwen+ | TP | FP | FN | precision | recall | F1 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    sorted_tags = sorted(per_tag.items(), key=lambda x: -x[1]["f1"])
    for k, v in sorted_tags:
        lines.append(f"| {k} | {v['n_manual_yes']} | {v['n_qwen_yes']} | "
                     f"{v['tp']} | {v['fp']} | {v['fn']} | "
                     f"{v['precision']:.2f} | {v['recall']:.2f} | {v['f1']:.2f} |")
    lines.append("")

    # Overall confusion
    total_active_manual = sum(sum(int(manual[i].get(k,0)) for k in TAG_KEYS_V2) for i in ids)
    total_active_qwen   = sum(sum(int(qwen.get(i,{}).get(k,0)) for k in TAG_KEYS_V2) for i in ids)
    lines.append(f"- mean active tags / event — manual: {total_active_manual/len(ids):.2f}  qwen: {total_active_qwen/len(ids):.2f}")
    lines.append("")

    lines.append("## Disagreements per tag (FP = qwen false alarm, FN = qwen miss)")
    lines.append("")
    for k in TAG_KEYS_V2:
        d = disagreements_by_tag[k]
        if not d:
            continue
        lines.append(f"### {k} — {len(d)} disagreements")
        for kind, eid, tk, dt in d:
            lines.append(f"- **{kind}** {tk} {dt}  (`{eid}`)")
        lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    keep = [k for k, v in per_tag.items() if v["f1"] >= 0.6 or v["n_manual_yes"] == 0]
    review = moderate
    drop = bad
    lines.append(f"- **KEEP** (F1 ≥ 0.6 or no positives to evaluate): {', '.join(keep) or 'none'}")
    lines.append(f"- **REVIEW** (0.4 ≤ F1 < 0.6 — tune prompt or accept noise): {', '.join(review) or 'none'}")
    lines.append(f"- **DROP** (F1 < 0.4 — Qwen unreliable, consider removing): {', '.join(drop) or 'none'}")

    report = "\n".join(lines)
    with open(OUT_PATH, "w") as f:
        f.write(report)
    print(report[:3000])
    print("...")
    print(f"\nfull report: {OUT_PATH}")


if __name__ == "__main__":
    main()
