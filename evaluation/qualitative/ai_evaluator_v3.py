"""AI evaluator for blind test v3 — Claude as evaluator proxy.

Calls Claude (via Anthropic SDK) on each (query, candidate) pair from the
blind_test_v3 data file. Uses the SAME 4 metrics + tooltips presented to
the human evaluator in static/index.html.

Each evaluation is independent (one API call per candidate) — Claude
does not see other queries or other candidates. This mirrors how the
human evaluator works: one candidate at a time.

Output: <reviews_dir>/<review_id>_AI_responses.json — same schema as the
human responses file, so analyze_blind_results_v2.py works as-is. Tag:
"evaluator": "ai" added to top-level meta.

Usage:
  python -m evaluation.qualitative.ai_evaluator_v3 \
      [--data path/to/blind_test_v3_*_data.json] \
      [--model claude-sonnet-4-5] [--limit N] [--resume]

Env var ANTHROPIC_API_KEY required.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import re
import sys
import time
from datetime import datetime

import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

REVIEWS_DIR = os.path.join(ROOT, "evaluation", "qualitative", "reviews")

# ── Exact same tooltip text as static/index.html ───────────────────────
METRICS = [
    {
        "key": "same_dynamic",
        "label": "Stessa storia",
        "question": "Sta succedendo la stessa cosa all'azienda, per le stesse ragioni?",
        "tips": [
            "Per niente. Stanno succedendo cose totalmente diverse.",
            "Poco. Solo una vaga somiglianza superficiale.",
            "In parte. Alcuni elementi in comune ma molti diversi.",
            "Molto. Dinamica simile con piccole differenze.",
            "Esattamente la stessa cosa, stesse cause.",
        ],
    },
    {
        "key": "same_regime",
        "label": "Stesso clima di mercato",
        "question": "Il mercato era nello stesso stato d'animo? (VIX, tassi simili)",
        "tips": [
            "Totalmente diverso (es. mercato calmo vs crisi).",
            "Molto diverso.",
            "Parzialmente simile.",
            "Molto simile.",
            "Praticamente identico (VIX, tassi, sentiment).",
        ],
    },
    {
        "key": "same_surprise",
        "label": "Stesso tipo di notizia",
        "question": "Era una buona/cattiva notizia dello stesso tipo? (es. beat+raise vs miss+cut)",
        "tips": [
            "Opposto (es. buona vs cattiva notizia).",
            "Molto diverso.",
            "Stessa direzione (entrambe buone o cattive) ma intensità diversa.",
            "Stesso tipo con piccole differenze.",
            "Identico (es. entrambi beat+raise, entrambi miss+cut).",
        ],
    },
    {
        "key": "mental_precedent",
        "label": "Utile come esempio storico",
        "question": "Mi servirebbe come precedente per ragionare sulla query?",
        "tips": [
            "Non mi aiuta per niente a capire la query.",
            "Aiuta poco.",
            "Qualche spunto utile ma contesto diverso.",
            "Buon precedente, mi aiuta a ragionare.",
            "Esempio perfetto, lo userei subito come paragone.",
        ],
    },
]

DEFAULT_MODEL = os.environ.get("AI_EVALUATOR_MODEL", "")  # empty = CLI default (Claude Code)
MAX_TEXT_CHARS = 4000   # cap per side to keep prompts reasonable
RATE_RE = re.compile(r"\b([1-5])\b")
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", "claude")
CALL_TIMEOUT = 120


def build_prompt(query: dict, candidate: dict) -> str:
    """One self-contained evaluation prompt for one (query, candidate) pair."""
    qe = query["event"]
    qm = qe.get("macro", {})
    qr = qe.get("reaction_30d", {})
    cm = candidate.get("macro", {})
    cr = candidate.get("reaction_30d", {})

    q_text = (qe.get("text_full") or "").strip()[:MAX_TEXT_CHARS]
    c_text = (candidate.get("text_full") or "").strip()[:MAX_TEXT_CHARS]

    metrics_block = ""
    for i, m in enumerate(METRICS, start=1):
        tips = "\n".join(f"    {v}. {m['tips'][v-1]}" for v in range(1, 6))
        metrics_block += (
            f"\n{i}. {m['label']}\n"
            f"   Question: {m['question']}\n"
            f"   Scale (1-5):\n{tips}\n"
        )

    rule = ("Practical rule: if torn between two scores, pick the LOWER one. "
            "A 3 means 'kinda — partial match'.")

    return f"""You are a financial analyst evaluating whether a CANDIDATE earnings
event is a good analog for a QUERY earnings event, for the purpose of
analogical reasoning by a human analyst.

Score the candidate on 4 metrics, each on a 1-5 integer scale.

{metrics_block}
{rule}

═══════════ QUERY ═══════════
Ticker: {qe['ticker']}  ·  Date: {qe['date']}  ·  Sector: {qe['sector_gics']}
Macro: VIX={qm.get('vix','?')}  yield_10y={qm.get('yield_10y','?')}  credit={qm.get('credit_spread','?')}
Reaction 30d: ret={qr.get('return','?')}  vol={qr.get('vol','?')}  max_dd={qr.get('max_dd','?')}

Narrative summary:
{qe.get('narrative_summary','')}

Full text (first {MAX_TEXT_CHARS} chars):
{q_text}

═══════════ CANDIDATE ═══════════
Ticker: {candidate['ticker']}  ·  Date: {candidate['date']}  ·  Sector: {candidate['sector_gics']}
Macro: VIX={cm.get('vix','?')}  yield_10y={cm.get('yield_10y','?')}  credit={cm.get('credit_spread','?')}
Reaction 30d: ret={cr.get('return','?')}  vol={cr.get('vol','?')}  max_dd={cr.get('max_dd','?')}

Narrative summary:
{candidate.get('narrative_summary','')}

Full text (first {MAX_TEXT_CHARS} chars):
{c_text}

═══════════ OUTPUT ═══════════
Reply with EXACTLY this JSON object and nothing else:
{{
  "same_dynamic": <1-5>,
  "same_regime": <1-5>,
  "same_surprise": <1-5>,
  "mental_precedent": <1-5>,
  "notes": "<3-8 words optional rationale, or empty string>"
}}
"""


def call_claude_cli(prompt: str, model: str = "", max_retries: int = 2):
    """Call the `claude` CLI in headless mode. Returns (ratings_dict, error)."""
    cmd = [CLAUDE_BIN, "-p", prompt]
    if model:
        cmd += ["--model", model]
    for attempt in range(max_retries + 1):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT)
            raw = (proc.stdout or "").strip()
            if proc.returncode != 0 or not raw:
                err = (proc.stderr or "")[:200] or f"empty stdout (rc={proc.returncode})"
                if attempt == max_retries:
                    return None, f"cli_error: {err}"
                time.sleep(1.5)
                continue
            m = re.search(r"\{[\s\S]*\}", raw)
            if not m:
                if attempt == max_retries:
                    return None, f"no JSON: {raw[:200]!r}"
                time.sleep(1.5)
                continue
            try:
                obj = json.loads(m.group(0))
            except Exception as e:
                if attempt == max_retries:
                    return None, f"json_parse: {e}; raw[:200]={raw[:200]!r}"
                time.sleep(1.5)
                continue
            ratings = {}
            ok = True
            for m_def in METRICS:
                v = obj.get(m_def["key"])
                if v is None or not isinstance(v, (int, float)):
                    ok = False
                    break
                ratings[m_def["key"]] = max(1, min(5, int(v)))
            if ok and len(ratings) == 4:
                notes = str(obj.get("notes") or "")
                return {"ratings": ratings, "notes": notes}, None
            if attempt == max_retries:
                return None, f"missing metrics in: {raw[:200]!r}"
            time.sleep(1.5)
        except subprocess.TimeoutExpired:
            if attempt == max_retries:
                return None, f"timeout after {CALL_TIMEOUT}s"
            time.sleep(2.0)
        except Exception as e:
            if attempt == max_retries:
                return None, f"unexpected: {e}"
            time.sleep(1.5)
    return None, "exhausted retries"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=None, help="path to blind_test_v3_*_data.json")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--limit", type=int, default=None, help="evaluate at most N candidates")
    ap.add_argument("--save-every", type=int, default=5)
    args = ap.parse_args()

    if args.data:
        data_path = args.data
    else:
        cands = sorted(glob.glob(os.path.join(REVIEWS_DIR, "blind_test_v3_*_data.json")))
        if not cands:
            print("No blind_test_v3 data file found.")
            sys.exit(1)
        data_path = cands[-1]

    with open(data_path) as f:
        data = json.load(f)
    review_id = data["review_id"]
    out_path = os.path.join(REVIEWS_DIR, f"{review_id}_AI_responses.json")

    # Build flat work list
    work = []
    for q in data["queries"]:
        for c in q["candidates"]:
            work.append((q, c))
    total = len(work)
    print(f"data: {os.path.basename(data_path)}  candidates: {total}  model: {args.model}")
    print(f"out:  {out_path}")

    # Load existing AI responses to resume
    if os.path.exists(out_path):
        with open(out_path) as f:
            existing = json.load(f)
        done = {(r["query_id"], r["candidate_label"]) for r in existing.get("responses", [])}
        responses = existing.get("responses", [])
        print(f"  resuming, already done: {len(done)}")
    else:
        responses = []
        done = set()
        existing = None

    todo = [(q, c) for q, c in work if (q["query_id"], c["label"]) not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"  todo this run: {len(todo)}")

    n_ok = n_fail = 0
    t0 = time.time()

    def save():
        out = {
            "review_id": review_id,
            "completed_at": datetime.now().isoformat(timespec="seconds"),
            "evaluator": "ai",
            "model": args.model,
            "metric_keys": [m["key"] for m in METRICS],
            "responses": responses,
        }
        tmp = out_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        os.replace(tmp, out_path)

    for i, (q, c) in enumerate(todo, start=1):
        prompt = build_prompt(q, c)
        res, err = call_claude_cli(prompt, model=args.model)
        if res is None:
            responses.append({
                "query_id": q["query_id"],
                "candidate_label": c["label"],
                "cannot_evaluate": True,
                "notes": f"AI evaluator error: {err[:200] if err else 'unknown'}",
            })
            n_fail += 1
        else:
            responses.append({
                "query_id": q["query_id"],
                "candidate_label": c["label"],
                "ratings": res["ratings"],
                "notes": res["notes"][:200],
            })
            n_ok += 1
        if i % args.save_every == 0 or i == len(todo):
            save()
            elapsed = time.time() - t0
            eta = elapsed / i * (len(todo) - i)
            print(f"  [{i}/{len(todo)}] ok={n_ok} fail={n_fail}  elapsed={elapsed:.0f}s ETA={eta:.0f}s")
    print(f"\nDONE. total responses: {len(responses)}  ok={n_ok} fail={n_fail}")
    print(f"out: {out_path}")


if __name__ == "__main__":
    main()
