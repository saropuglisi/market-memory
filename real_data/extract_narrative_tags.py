"""Extract 12 binary narrative tags from each event summary via Qwen 2.5-7B.

Reads:  real_data/processed/sample_500_summaries.json
Writes: real_data/processed/sample_500_narrative_tags.json
        real_data/processed/sample_500_narrative_tags_failures.log

For events with no/unavailable summary, all 12 tags = 0 (logged separately).

Usage:
  python -m real_data.extract_narrative_tags [--limit N] [--model qwen2.5:7b]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
import re

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags import NARRATIVE_TAGS, TAG_KEYS, N_TAGS

PROCESSED = os.path.join(ROOT, "real_data", "processed")
SUMMARIES_PATH = os.path.join(PROCESSED, "sample_500_summaries.json")
OUT_PATH = os.path.join(PROCESSED, "sample_500_narrative_tags.json")
FAIL_LOG = os.path.join(PROCESSED, "sample_500_narrative_tags_failures.log")
MISSING_LOG = os.path.join(PROCESSED, "sample_500_narrative_tags_missing_summaries.log")

EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = "qwen2.5:7b"
TIMEOUT = 120
MAX_RETRIES = 2
FULLTEXT_CAP = 6000
UNAVAIL = "[summary unavailable]"

YES_RE = re.compile(r"\bYES\b", re.IGNORECASE)
NO_RE  = re.compile(r"\bNO\b",  re.IGNORECASE)
LINE_RE = re.compile(r"^\s*(\d+)\.\s*(.+?)\s*$")


def build_prompt(summary: str) -> str:
    numbered = "\n".join(f"{i+1}. {k}: {NARRATIVE_TAGS[k]}" for i, k in enumerate(TAG_KEYS))
    return (
        "You are a financial analyst. Read this earnings summary and answer "
        "with YES or NO for each of the 12 tags below. Be strict: only YES "
        "if the tag is explicitly supported by the summary.\n\n"
        "Tags to evaluate:\n"
        f"{numbered}\n\n"
        f"Summary:\n{summary}\n\n"
        "Output format (exactly 12 lines, no preamble):\n"
        "1. YES/NO\n2. YES/NO\n3. YES/NO\n... etc\n\n"
        "Output:\n"
    )


def parse_response(raw: str) -> tuple[dict, list[str]]:
    """Return (tags_dict, warnings). Missing/garbage answers default 0."""
    tags = {k: 0 for k in TAG_KEYS}
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
        if not (0 <= idx < N_TAGS):
            continue
        ans = m.group(2)
        if YES_RE.search(ans):
            found[idx] = 1
        elif NO_RE.search(ans):
            found[idx] = 0
        else:
            warns.append(f"line {idx+1} unparsable: {ans!r}")
            found[idx] = 0
    if len(found) != N_TAGS:
        warns.append(f"only {len(found)}/{N_TAGS} lines parsed")
    for i, k in enumerate(TAG_KEYS):
        tags[k] = int(found.get(i, 0))
    return tags, warns


def call_ollama(summary: str, model: str) -> tuple[dict | None, str]:
    prompt = build_prompt(summary)
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.0, "num_predict": 200}},
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


def zero_tags():
    return {k: 0 for k in TAG_KEYS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--save-every", type=int, default=15)
    ap.add_argument("--source", choices=["summary", "full_text"], default="summary",
                    help="summary uses sample_500_summaries.json; full_text uses sample_500.json text field (capped 6000)")
    args = ap.parse_args()

    if args.source == "summary":
        if not os.path.exists(SUMMARIES_PATH):
            print(f"Missing {SUMMARIES_PATH}"); sys.exit(1)
        with open(SUMMARIES_PATH) as f:
            summaries = json.load(f)
    else:
        if not os.path.exists(EVENTS_PATH):
            print(f"Missing {EVENTS_PATH}"); sys.exit(1)
        with open(EVENTS_PATH) as f:
            events = json.load(f)
        summaries = {}
        for e in events:
            t = (e.get("text") or "").strip()
            summaries[e["id"]] = t[:FULLTEXT_CAP] if t else UNAVAIL

    ids = list(summaries.keys())
    if args.limit:
        ids = ids[:args.limit]

    cache = load_cache()
    todo = [i for i in ids if i not in cache]
    print(f"summaries={len(ids)} cached={len(cache)} todo={len(todo)}")

    missing_summary_ids = []
    n_ok = n_zero = 0
    t0 = time.time()

    with open(FAIL_LOG, "a") as flog:
        flog.write(f"\n=== run @ {time.strftime('%Y-%m-%d %H:%M:%S')} model={args.model} ===\n")
        for i, eid in enumerate(todo, start=1):
            summary = summaries[eid]
            if summary == UNAVAIL or not summary.strip():
                cache[eid] = zero_tags()
                cache[eid]["_status"] = "no_summary"
                n_zero += 1
                missing_summary_ids.append(eid)
            else:
                tags, warns = call_ollama(summary, args.model)
                if tags is None:
                    cache[eid] = zero_tags()
                    cache[eid]["_status"] = "parsing_failed"
                    flog.write(f"{eid}\tFAIL\t{warns}\n"); flog.flush()
                    n_zero += 1
                else:
                    cache[eid] = tags
                    cache[eid]["_status"] = "ok" if not warns else "partial"
                    if warns:
                        flog.write(f"{eid}\tPARTIAL\t{warns}\n"); flog.flush()
                    n_ok += 1
            if i % args.save_every == 0:
                save_cache(cache)
                elapsed = time.time() - t0
                eta = elapsed / i * (len(todo) - i)
                active = sum(v.get(k, 0) for v in cache.values() for k in TAG_KEYS) / max(len(cache), 1)
                print(f"  [{i}/{len(todo)}] ok={n_ok} zero={n_zero}  avg_active_tags={active:.2f}"
                      f"  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")
        save_cache(cache)

    if missing_summary_ids:
        with open(MISSING_LOG, "w") as f:
            f.write("\n".join(missing_summary_ids))

    total = len(cache)
    okc = sum(1 for v in cache.values() if v.get("_status") in ("ok", "partial"))
    print(f"\nDONE. total={total} extracted_ok={okc} zero={total-okc}")
    print(f"out={OUT_PATH}")
    if missing_summary_ids:
        print(f"missing-summary events: {len(missing_summary_ids)} -> {MISSING_LOG}")


if __name__ == "__main__":
    main()
