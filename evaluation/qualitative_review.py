"""Qualitative review on L2 v2:
1) Select 10 test events: 2 per A/B/C/D (easy=near centroid, hard=far),
   + 2 noise (most diverse reactions).
2) Retrieve top-5 from llm_v3, contrastive_v2, concat_eq.
3) Emit selected_events.json, retrievals.md, overlap_analysis.md.
4) Pre-populate case_studies / smart_vs_stupid scaffolding.
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter

import numpy as np
from numpy.linalg import norm

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches import ConcatBaseline
from approaches.archived.approach_3_contrastive_v2 import ContrastiveEncoderV2
from approaches.archived.approach_5_llm_struct_v3 import LLMStructuredEncoderV3
from approaches.base import vec_from

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "mock_events_L2.json")
OUT = os.path.join(ROOT, "results", "qualitative_review")
os.makedirs(OUT, exist_ok=True)


def _zfeat(events, train_ref):
    """Standardize features using train_ref stats."""
    X = np.stack([np.concatenate([vec_from(e, "macro"),
                                  vec_from(e, "micro"),
                                  vec_from(e, "semantic")]) for e in events])
    X_ref = np.stack([np.concatenate([vec_from(e, "macro"),
                                      vec_from(e, "micro"),
                                      vec_from(e, "semantic")]) for e in train_ref])
    mu = X_ref.mean(axis=0); sd = X_ref.std(axis=0) + 1e-9
    return (X - mu) / sd


def select_events(events):
    train = [e for e in events if e["split"] == "train"]
    test = [e for e in events if e["split"] == "test"]

    Xz_test = _zfeat(test, train)
    test_clusters = [e["ground_truth_cluster"] for e in test]
    # centroids on train z-scored features (per cluster)
    Xz_train = _zfeat(train, train)
    train_clusters = [e["ground_truth_cluster"] for e in train]
    centroids = {}
    for c in set(train_clusters):
        idx = [i for i, cc in enumerate(train_clusters) if cc == c]
        centroids[c] = Xz_train[idx].mean(axis=0) if idx else None

    selected = []
    for c in ["A", "B", "C", "D"]:
        idx = [i for i, cc in enumerate(test_clusters) if cc == c]
        if len(idx) < 2:
            continue
        dists = [(i, float(norm(Xz_test[i] - centroids[c]))) for i in idx]
        dists.sort(key=lambda x: x[1])
        easy_i, easy_d = dists[0]
        hard_i, hard_d = dists[-1]
        selected.append({"event": test[easy_i], "cluster": c, "kind": "easy",
                         "centroid_dist": easy_d,
                         "reason": f"closest to cluster {c} centroid (dist={easy_d:.2f})"})
        selected.append({"event": test[hard_i], "cluster": c, "kind": "hard",
                         "centroid_dist": hard_d,
                         "reason": f"farthest from cluster {c} centroid in test (dist={hard_d:.2f})"})

    # noise: two with most-different reaction
    noise_idx = [i for i, cc in enumerate(test_clusters) if cc == "NOISE"]
    if len(noise_idx) >= 2:
        R = np.stack([vec_from(test[i], "reaction") for i in noise_idx])
        diffs = R[:, None, :] - R[None, :, :]
        d = norm(diffs, axis=-1)
        ii, jj = np.unravel_index(np.argmax(d), d.shape)
        for which, i in [("noise_a", noise_idx[ii]), ("noise_b", noise_idx[jj])]:
            selected.append({"event": test[i], "cluster": "NOISE", "kind": which,
                             "centroid_dist": None,
                             "reason": f"most diverse reaction pair (within noise test set)"})
    return selected, train, test


def fit_encoders(train):
    eq = ConcatBaseline(equalize_blocks=True); eq.fit(train)
    cv2 = ContrastiveEncoderV2(epochs=80); cv2.fit(train)
    llm = LLMStructuredEncoderV3()
    llm.fit(train)  # uses cache
    return {"llm_v3": llm, "contrastive_v2": cv2, "concat_eq": eq}


def train_pair_dist_ranks(train):
    """For each pair (i,j) in train, compute reaction-z-score euclidean,
    return matrix + flat sorted distances for rank lookup."""
    R = np.stack([vec_from(e, "reaction") for e in train])
    mu = R.mean(axis=0); sd = R.std(axis=0) + 1e-9
    Rz = (R - mu) / sd
    diffs = Rz[:, None, :] - Rz[None, :, :]
    d = norm(diffs, axis=-1)
    iu = np.triu_indices(len(train), k=1)
    sorted_pair_d = np.sort(d[iu])
    return Rz, mu, sd, sorted_pair_d


def reaction_dist_rank(r_q_raw, r_t_raw, mu, sd, sorted_pair_d):
    rqz = (r_q_raw - mu) / sd
    rtz = (r_t_raw - mu) / sd
    d = float(norm(rqz - rtz))
    # rank: how many pairs have distance <= d
    rank = int(np.searchsorted(sorted_pair_d, d))
    return d, rank, len(sorted_pair_d)


def main():
    events = json.load(open(DATA))
    selected, train, test = select_events(events)

    # Save selection
    sel_out = []
    for s in selected:
        e = s["event"]
        sel_out.append({
            "id": e["id"], "cluster": e["ground_truth_cluster"],
            "ticker": e["ticker"], "sector": e["sector"], "date": e["date"],
            "kind": s["kind"], "centroid_dist": s["centroid_dist"],
            "reason": s["reason"],
        })
    with open(os.path.join(OUT, "selected_events.json"), "w") as f:
        json.dump(sel_out, f, indent=2)
    print(f"selected: {len(selected)} events")

    encoders = fit_encoders(train)
    Rz, r_mu, r_sd, sorted_pair_d = train_pair_dist_ranks(train)

    # Retrievals
    retr = {}  # query_id -> { encoder: [(idx, sim, train_event), ...] }
    for s in selected:
        q = s["event"]
        per_enc = {}
        for name, enc in encoders.items():
            idx = enc.retrieve(q, train, top_k=5)
            # compute similarities
            qv = enc.encode(q)
            cv = enc.encode_batch([train[i] for i in idx])
            sims = []
            for k in range(len(idx)):
                a = qv; b = cv[k]
                s_v = float(np.dot(a, b) / (norm(a) * norm(b) + 1e-9))
                sims.append(s_v)
            per_enc[name] = list(zip(idx, sims))
        retr[q["id"]] = per_enc

    # Write retrievals.md
    md_lines = ["# Retrievals — qualitative review on L2 v2", ""]
    for s in selected:
        q = s["event"]
        md_lines.append(f"## Query: {q['id']} (cluster {q['ground_truth_cluster']}, {q['ticker']} / {q['sector']}, {q['date']}, kind={s['kind']})")
        text_short = q["text"][:300].replace("\n", " ")
        md_lines.append(f"- **Text** (300 char): {text_short}")
        m = q["macro_features"]
        md_lines.append(f"- **Macro**: VIX={m['vix']:.1f}, yield={m['yield_10y']:.2f}, spread={m['credit_spread']:.2f}, slope={m['yield_curve_slope']:.2f}")
        mi = q["micro_features"]
        md_lines.append(f"- **Micro**: ret60d={mi['return_60d']:.2f}, vol60d={mi['realized_vol_60d']:.2f}, dd={mi['drawdown_from_high']:.2f}, relstr={mi['relative_strength']:.2f}")
        sem = q["semantic_features"]
        md_lines.append(f"- **Semantic**: conf={sem['confidence_score']:.2f}, hedging={sem['hedging_count']}, guide={sem['guidance_direction']}, unc={sem['uncertainty_markers']}")
        r = q["reaction_30d"]
        md_lines.append(f"- **Reaction 30d**: return={r['return']:.3f}, vol={r['realized_vol']:.3f}, dd={r['max_drawdown']:.3f}, persist={r['persistence']:.2f}")
        md_lines.append("")
        for name in ["llm_v3", "contrastive_v2", "concat_eq"]:
            md_lines.append(f"### {name} top-5")
            for rank_k, (idx, sim) in enumerate(retr[q["id"]][name], start=1):
                t = train[idx]
                same = (t["ground_truth_cluster"] == q["ground_truth_cluster"])
                r_q = vec_from(q, "reaction"); r_t = vec_from(t, "reaction")
                rd, rrank, npairs = reaction_dist_rank(r_q, r_t, r_mu, r_sd, sorted_pair_d)
                pct = rrank / npairs
                txt = t["text"][:180].replace("\n", " ")
                md_lines.append(
                    f"{rank_k}. **{t['id']}** ({t['ground_truth_cluster']}, {t['ticker']}/{t['sector']}) sim={sim:.3f}"
                    f" — react-dist={rd:.2f} (rank {rrank}/{npairs}, p{int(pct*100)})"
                    f" — same_cluster={'YES' if same else 'NO'}"
                )
                md_lines.append(f"   > {txt}")
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")

    with open(os.path.join(OUT, "retrievals.md"), "w") as f:
        f.write("\n".join(md_lines))
    print("wrote retrievals.md")

    # Overlap analysis
    lines = ["# Overlap analysis — top-5 across encoders", ""]
    lines.append("Per-query top-5 (event_id sets) and overlap counts.")
    lines.append("")
    overlap_rows = ["| Query | cluster | kind | all3 | 2of3 | unique | LLM∩contr | LLM∩concat | contr∩concat |",
                    "|---|---|---|---|---|---|---|---|---|"]
    pair_div = Counter()
    div_examples = {"llm_vs_contr": [], "llm_vs_concat": [], "contr_vs_concat": []}
    for s in selected:
        q = s["event"]
        sets = {name: set(idx for idx, _ in retr[q["id"]][name])
                for name in ["llm_v3", "contrastive_v2", "concat_eq"]}
        all3 = sets["llm_v3"] & sets["contrastive_v2"] & sets["concat_eq"]
        any2 = ((sets["llm_v3"] & sets["contrastive_v2"]) |
                (sets["llm_v3"] & sets["concat_eq"]) |
                (sets["contrastive_v2"] & sets["concat_eq"])) - all3
        union = sets["llm_v3"] | sets["contrastive_v2"] | sets["concat_eq"]
        unique = union - all3 - any2
        p1 = len(sets["llm_v3"] & sets["contrastive_v2"])
        p2 = len(sets["llm_v3"] & sets["concat_eq"])
        p3 = len(sets["contrastive_v2"] & sets["concat_eq"])
        overlap_rows.append(
            f"| {q['id']} | {q['ground_truth_cluster']} | {s['kind']} | {len(all3)} | {len(any2)} | {len(unique)} | {p1} | {p2} | {p3} |"
        )
        # disagreement totals (low overlap = high disagreement)
        pair_div["llm_vs_contr"] += (5 - p1)
        pair_div["llm_vs_concat"] += (5 - p2)
        pair_div["contr_vs_concat"] += (5 - p3)
        if p1 <= 1:
            div_examples["llm_vs_contr"].append((q["id"], s["kind"], q["ground_truth_cluster"]))
        if p2 <= 1:
            div_examples["llm_vs_concat"].append((q["id"], s["kind"], q["ground_truth_cluster"]))
        if p3 <= 1:
            div_examples["contr_vs_concat"].append((q["id"], s["kind"], q["ground_truth_cluster"]))
    lines += overlap_rows
    lines.append("")
    lines.append("## Pair disagreement (total non-overlap across 10 queries, max=50)")
    lines.append("")
    for k, v in pair_div.most_common():
        lines.append(f"- {k}: {v} non-overlapping picks (avg {v/10:.1f} of 5)")
    lines.append("")
    lines.append("## Queries with overlap ≤ 1 per pair")
    for k, exs in div_examples.items():
        lines.append(f"- {k}: " + (", ".join(f"{eid}({k2}/{cl})" for eid, k2, cl in exs) if exs else "none"))
    lines.append("")

    # For each query with all3 < 2 (heavy divergence), record which encoder seems "right"
    lines.append("## Heavy divergence queries (all3 < 2)")
    for s in selected:
        q = s["event"]
        sets = {name: list(idx for idx, _ in retr[q["id"]][name])
                for name in ["llm_v3", "contrastive_v2", "concat_eq"]}
        all3 = set(sets["llm_v3"]) & set(sets["contrastive_v2"]) & set(sets["concat_eq"])
        if len(all3) >= 2:
            continue
        lines.append(f"\n### {q['id']} ({q['ground_truth_cluster']}, {s['kind']})")
        # per-encoder: precision (same-cluster fraction) and mean reaction-distance
        for name in ["llm_v3", "contrastive_v2", "concat_eq"]:
            idxs = sets[name]
            same = sum(1 for i in idxs if train[i]["ground_truth_cluster"] == q["ground_truth_cluster"])
            r_q = vec_from(q, "reaction")
            ds = []
            for i in idxs:
                r_t = vec_from(train[i], "reaction")
                d, _, _ = reaction_dist_rank(r_q, r_t, r_mu, r_sd, sorted_pair_d)
                ds.append(d)
            lines.append(f"- **{name}**: same-cluster={same}/5, mean_reaction_dist={np.mean(ds):.2f}")
        # "winner" guess
        # Best precision wins ties broken by mean reaction-distance
        scored = []
        for name in ["llm_v3", "contrastive_v2", "concat_eq"]:
            idxs = sets[name]
            same = sum(1 for i in idxs if train[i]["ground_truth_cluster"] == q["ground_truth_cluster"])
            r_q = vec_from(q, "reaction")
            ds = [reaction_dist_rank(r_q, vec_from(train[i], "reaction"), r_mu, r_sd, sorted_pair_d)[0] for i in idxs]
            scored.append((name, same, np.mean(ds)))
        scored.sort(key=lambda x: (-x[1], x[2]))
        lines.append(f"- → looks **closest to ground truth**: {scored[0][0]}")
    with open(os.path.join(OUT, "overlap_analysis.md"), "w") as f:
        f.write("\n".join(lines))
    print("wrote overlap_analysis.md")

    # Dump retrieval indices as JSON for downstream analysis
    retr_json = {}
    for q_id, per_enc in retr.items():
        retr_json[q_id] = {name: [{"train_idx": int(i), "train_id": train[i]["id"],
                                    "train_cluster": train[i]["ground_truth_cluster"],
                                    "train_ticker": train[i]["ticker"],
                                    "train_sector": train[i]["sector"],
                                    "sim": float(s)}
                                   for i, s in pairs]
                           for name, pairs in per_enc.items()}
    with open(os.path.join(OUT, "retrievals.json"), "w") as f:
        json.dump(retr_json, f, indent=2)


if __name__ == "__main__":
    main()
