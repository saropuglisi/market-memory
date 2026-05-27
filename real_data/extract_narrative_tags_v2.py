"""Extract v2 narrative tags from 8-K full text via Qwen 2.5-7B.

Improvements over v1:
- Uses the data-driven 14-tag list (narrative_tags_v2.py)
- Operational prompt with 1-line example per tag (not just description)
- Same strict YES/NO format but examples reduce ambiguity
- Full text source (cap 6000 chars)

Reads:  real_data/processed/sample_500.json
Writes: real_data/processed/sample_500_narrative_tags_v2.json
        failures + missing logs alongside

Usage:
  python -m real_data.extract_narrative_tags_v2 [--limit N] [--ids id1,id2]
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags_v2 import NARRATIVE_TAGS_V2, TAG_KEYS_V2, N_TAGS_V2

PROCESSED = os.path.join(ROOT, "real_data", "processed")
EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
OUT_PATH = os.path.join(PROCESSED, "sample_500_narrative_tags_v2.json")
FAIL_LOG = os.path.join(PROCESSED, "sample_500_narrative_tags_v2_failures.log")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = "qwen2.5:7b"
TIMEOUT = 120
MAX_RETRIES = 2
TEXT_CAP = 6000

# Compact operational examples (added to the prompt to reduce false negatives).
TAG_EXAMPLES = {
    "guidance_raise":      "'raised FY guidance to $X-$Y' or 'narrowed guidance to upper end'",
    "guidance_cut":        "'lowered FY guidance' or 'withdrew prior outlook' or 'reduced forecast'",
    "record_results":      "'record quarterly revenue' or 'all-time high backlog' (must use the word 'record' or equivalent)",
    "demand_strength":     "'strong demand across segments' or 'robust order book' or 'accelerating bookings'",
    "margin_expansion":    "'operating margin expanded 200bps' or 'margins improved' or 'gross margin up'",
    "margin_pressure":     "'margins compressed' or 'gross margin declined' or 'margin headwind'",
    "cost_inflation":      "'input cost inflation' or 'wage pressure' or 'raw material headwind'",
    "pricing_action":      "'price increases' or 'pricing power' or 'realized price' contributing positively",
    "capital_return":      "'share repurchase' or 'increased dividend' or 'returned capital to shareholders'",
    "MA_activity":         "'completed/announced acquisition' or 'divested business' or 'spin-off' (must reference a specific deal)",
    "restructuring":       "'restructuring program' or 'workforce reduction' or 'cost savings program' or 'simplification initiative'",
    "supply_constraint":   "'supply chain constraints' or 'chip shortage' or 'capacity tightness'",
    "FX_headwind":         "'foreign exchange headwind' or 'unfavorable FX impact' or 'stronger dollar hurt revenue'",
    "ESG_sustainability":  "'net zero commitment' or 'renewable energy investments' or 'sustainability initiative' or 'ESG framework'",
}

YES_RE = re.compile(r"\bYES\b", re.IGNORECASE)
NO_RE  = re.compile(r"\bNO\b",  re.IGNORECASE)
LINE_RE = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*$")


def build_prompt(text: str) -> str:
    lines = []
    for i, k in enumerate(TAG_KEYS_V2):
        ex = TAG_EXAMPLES.get(k, "")
        lines.append(f"{i+1}. {k}: {NARRATIVE_TAGS_V2[k]}  EXAMPLE: {ex}")
    numbered = "\n".join(lines)
    return (
        "You are a financial analyst reading an 8-K earnings press release. "
        "For each of the 14 tags below, answer with YES or NO based ONLY on "
        "what the text explicitly states. Do not infer beyond what is written.\n\n"
        "Tags to evaluate:\n"
        f"{numbered}\n\n"
        f"Text:\n{text}\n\n"
        "Output format (exactly 14 lines, no preamble, no commentary):\n"
        "1. YES/NO\n2. YES/NO\n... up to 14.\n\n"
        "Output:\n"
    )


def parse_response(raw: str) -> tuple[dict, list[str]]:
    tags = {k: 0 for k in TAG_KEYS_V2}
    warns = []
    found = {}
    for line in raw.strip().splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        try:
            idx = int(m.group(1)) - 1
        except ValueError:
            continue
        if not (0 <= idx < N_TAGS_V2):
            continue
        ans = m.group(2)
        if YES_RE.search(ans):
            found[idx] = 1
        elif NO_RE.search(ans):
            found[idx] = 0
        else:
            warns.append(f"line {idx+1} unparsable: {ans!r}")
            found[idx] = 0
    if len(found) != N_TAGS_V2:
        warns.append(f"only {len(found)}/{N_TAGS_V2} lines parsed")
    for i, k in enumerate(TAG_KEYS_V2):
        tags[k] = int(found.get(i, 0))
    return tags, warns


def call_ollama(text: str, model: str):
    prompt = build_prompt(text[:TEXT_CAP])
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.0, "num_predict": 220}},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            raw = (r.json().get("response") or "").strip()
            if raw:
                tags, warns = parse_response(raw)
                return tags, "; ".join(warns) if warns else ""
        except Exception as e:
            if attempt == MAX_RETRIES:
                return None, f"{e.__class__.__name__}: {e}"
            time.sleep(1.0)
    return None, "empty"


def load_cache():
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    tmp = OUT_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    os.replace(tmp, OUT_PATH)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--ids", default=None, help="comma-separated event ids to extract")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--save-every", type=int, default=10)
    args = ap.parse_args()

    with open(EVENTS_PATH) as f:
        events = json.load(f)
    by_id = {e["id"]: e for e in events}

    if args.ids:
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
    else:
        ids = [e["id"] for e in events]
        if args.limit:
            ids = ids[:args.limit]

    cache = load_cache()
    todo = [i for i in ids if i not in cache]
    print(f"events_requested={len(ids)} cached={len([i for i in ids if i in cache])} todo={len(todo)}")

    n_ok = n_zero = 0
    t0 = time.time()
    with open(FAIL_LOG, "a") as flog:
        flog.write(f"\n=== run @ {time.strftime('%Y-%m-%d %H:%M:%S')} model={args.model} ===\n")
        for i, eid in enumerate(todo, start=1):
            e = by_id.get(eid)
            if e is None:
                flog.write(f"{eid}\tNOT_FOUND\n"); continue
            text = (e.get("text") or "").strip()
            if not text:
                cache[eid] = {**{k:0 for k in TAG_KEYS_V2}, "_status":"empty_text"}
                n_zero += 1; continue
            tags, warns = call_ollama(text, args.model)
            if tags is None:
                cache[eid] = {**{k:0 for k in TAG_KEYS_V2}, "_status":"parsing_failed"}
                flog.write(f"{eid}\tFAIL\t{warns}\n"); flog.flush(); n_zero += 1
            else:
                cache[eid] = {**tags, "_status": "ok" if not warns else "partial"}
                if warns:
                    flog.write(f"{eid}\tPARTIAL\t{warns}\n"); flog.flush()
                n_ok += 1
            if i % args.save_every == 0:
                save_cache(cache)
                elapsed = time.time() - t0
                eta = elapsed / i * (len(todo) - i)
                active = sum(sum(v.get(k,0) for k in TAG_KEYS_V2) for v in cache.values()) / max(len(cache),1)
                print(f"  [{i}/{len(todo)}] ok={n_ok} zero={n_zero}  avg_active={active:.2f}  elapsed={elapsed:.0f}s ETA={eta:.0f}s")
        save_cache(cache)

    total = len(cache)
    okc = sum(1 for v in cache.values() if v.get("_status") in ("ok","partial"))
    print(f"\nDONE. total={total} ok={okc} zero={total-okc}  out={OUT_PATH}")


if __name__ == "__main__":
    main()
