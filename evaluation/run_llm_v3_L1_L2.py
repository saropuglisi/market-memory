"""Run LLM v3 on L1 and L2 v2 to complete the degradation table."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evaluation.run_llm_v3 import evaluate
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
for L in ["L1", "L2"]:
    path = os.path.join(ROOT, "data", f"mock_events_{L}.json")
    print(f"\n=== {L} ===")
    r = evaluate(path)
    out[L] = r
    cy = r["distribution"]["cycle_phase"]
    t = sum(cy.values()) or 1
    print(f"  P@5={r['precision_at_5']} RC={r['reaction_corr']} U@5={r['utility_at_5']} "
          f"fail={r['fail_count']}/{r['n_unique_texts']} ({r['fail_rate']:.1%})")
    print(f"  cycle: " + ", ".join(f"{k}={v}({v/t:.0%})" for k, v in cy.items()))

path = os.path.join(ROOT, "results", f"llm_v3_L1_L2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
json.dump(out, open(path, "w"), indent=2)
print(f"saved: {path}")
