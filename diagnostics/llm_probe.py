"""Probe Ollama on the full dataset, capture raw responses, classify failure modes.

Bypasses the validation-then-cache pipeline of approach_5 so we see the raw text.
"""
from __future__ import annotations
import json
import os
import sys
import time
from collections import Counter

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from approaches.approach_5_llm_struct import (
    NARRATIVES, SURPRISES, ASYMM, CYCLE, PROMPT, OLLAMA_URL, OLLAMA_MODEL,
)

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "mock_events.json")
OUT_DIR = os.path.dirname(__file__)
os.makedirs(OUT_DIR, exist_ok=True)


def call_raw(text: str, force_json_mode: bool = True) -> dict:
    prompt = PROMPT.format(
        narratives=", ".join(f'"{x}"' for x in NARRATIVES),
        surprises=", ".join(f'"{x}"' for x in SURPRISES),
        asymms=", ".join(f'"{x}"' for x in ASYMM),
        cycles=", ".join(f'"{x}"' for x in CYCLE),
        text=text,
    )
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
               "options": {"temperature": 0.0, "seed": 42}}
    if force_json_mode:
        payload["format"] = "json"
    t0 = time.time()
    r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120)
    r.raise_for_status()
    raw = r.json().get("response", "")
    return {"raw": raw, "t": time.time() - t0}


def classify(raw: str):
    """Return (status, parsed_or_None, reason)."""
    try:
        obj = json.loads(raw)
    except Exception as e:
        return ("json_parse_error", None, str(e)[:120])
    issues = []
    if obj.get("dominant_narrative") not in NARRATIVES:
        issues.append(f"narrative={obj.get('dominant_narrative')!r}")
    if obj.get("surprise_type") not in SURPRISES:
        issues.append(f"surprise={obj.get('surprise_type')!r}")
    if obj.get("risk_asymmetry") not in ASYMM:
        issues.append(f"asym={obj.get('risk_asymmetry')!r}")
    if obj.get("implicit_cycle_phase") not in CYCLE:
        issues.append(f"cycle={obj.get('implicit_cycle_phase')!r}")
    conf = obj.get("confidence_level")
    try:
        ci = int(conf)
        if not (1 <= ci <= 5):
            issues.append(f"conf_oor={conf!r}")
    except Exception:
        issues.append(f"conf_type={type(conf).__name__}={conf!r}")
    if issues:
        return ("vocab_violation", obj, "; ".join(issues))
    return ("ok", obj, "")


def main(limit=None, force_json_mode=True):
    events = json.load(open(DATA))
    if limit:
        events = events[:limit]
    results = []
    counters = Counter()
    field_violations = Counter()
    for i, e in enumerate(events):
        try:
            out = call_raw(e["text"], force_json_mode=force_json_mode)
        except Exception as ex:
            results.append({"id": e["id"], "status": "http_error",
                            "reason": str(ex)[:200], "raw": None,
                            "cluster": e["ground_truth_cluster"]})
            counters["http_error"] += 1
            continue
        status, obj, reason = classify(out["raw"])
        counters[status] += 1
        if status == "vocab_violation":
            for part in reason.split(";"):
                key = part.strip().split("=")[0]
                field_violations[key] += 1
        results.append({
            "id": e["id"], "cluster": e["ground_truth_cluster"],
            "status": status, "reason": reason, "raw": out["raw"],
            "parsed": obj, "t": out["t"],
        })
        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{len(events)}] counters={dict(counters)}")

    mode_tag = "jsonmode" if force_json_mode else "plain"
    out_path = os.path.join(OUT_DIR, f"llm_probe_{mode_tag}.json")
    with open(out_path, "w") as f:
        json.dump({"counters": dict(counters),
                   "field_violations": dict(field_violations),
                   "results": results}, f, indent=2)
    print("\n=== SUMMARY ===")
    print("status counts:", dict(counters))
    print("field violations:", dict(field_violations))
    print("saved:", out_path)
    return counters, field_violations, results


if __name__ == "__main__":
    main()
