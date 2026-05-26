"""Generate narrative 2-3 sentence summaries for every event in sample_500.

Uses Qwen 2.5-7B via Ollama as a *summarization* tool (not as an encoder —
that role was archived; this is a separate task). Output drives the new
blind-test UI: the human evaluator reads the summary before scoring.

Cache: every successful summary is persisted to processed/sample_500_summaries.json.
Re-runs only fill the missing keys (resume-friendly). Failures are logged to
processed/sample_500_summaries_failures.log and marked '[summary unavailable]'
in the JSON. ~5-10% failure tolerated.

Usage:
  python -m real_data.narrative_summaries [--limit N] [--model qwen2.5:7b]
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PROCESSED = os.path.join(ROOT, "real_data", "processed")
EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
OUT_PATH = os.path.join(PROCESSED, "sample_500_summaries.json")
FAIL_LOG = os.path.join(PROCESSED, "sample_500_summaries_failures.log")

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = "qwen2.5:7b"
TEXT_CAP = 6000          # chars sent to LLM (keep prompt < ~8k tok)
TIMEOUT = 90
MAX_RETRIES = 2
UNAVAIL = "[summary unavailable]"

PROMPT = """You are a financial analyst. Read this earnings press release and produce a 2-3 sentence summary that captures:
1. What happened (the event)
2. Why it happened (the cause/driver mentioned)
3. The tone (confident, cautious, defensive, optimistic)
Be specific. Do NOT use generic phrases like "company reported earnings".
Output: 2-3 sentences, no preamble, no markdown formatting.

Event text:
{text}"""


def call_ollama(text: str, model: str) -> str | None:
    prompt = PROMPT.format(text=text[:TEXT_CAP])
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0, "num_predict": 200},
                },
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            out = (r.json().get("response") or "").strip()
            if out:
                return out
        except Exception as e:
            if attempt == MAX_RETRIES:
                return f"__ERR__{e.__class__.__name__}: {e}"
            time.sleep(1.0)
    return None


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
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--save-every", type=int, default=10)
    args = ap.parse_args()

    with open(EVENTS_PATH) as f:
        events = json.load(f)
    if args.limit:
        events = events[:args.limit]

    cache = load_cache()
    todo = [e for e in events if e["id"] not in cache or cache[e["id"]] == UNAVAIL]
    print(f"events={len(events)}  cached_ok={len(cache) - sum(1 for v in cache.values() if v == UNAVAIL)}  todo={len(todo)}")

    n_ok = n_fail = 0
    t0 = time.time()
    with open(FAIL_LOG, "a") as flog:
        flog.write(f"\n=== run @ {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        for i, e in enumerate(todo, start=1):
            out = call_ollama(e["text"], args.model)
            if out and not out.startswith("__ERR__"):
                cache[e["id"]] = out
                n_ok += 1
            else:
                cache[e["id"]] = UNAVAIL
                n_fail += 1
                flog.write(f"{e['id']}\t{out or 'empty'}\n")
                flog.flush()
            if i % args.save_every == 0:
                save_cache(cache)
                elapsed = time.time() - t0
                eta = elapsed / i * (len(todo) - i)
                print(f"  [{i}/{len(todo)}] ok={n_ok} fail={n_fail}  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")
        save_cache(cache)

    total_ok = sum(1 for v in cache.values() if v != UNAVAIL)
    total_fail = sum(1 for v in cache.values() if v == UNAVAIL)
    print(f"\nDONE. cache: ok={total_ok} fail={total_fail}  out={OUT_PATH}")
    if total_fail:
        print(f"failures logged: {FAIL_LOG}")


if __name__ == "__main__":
    main()
