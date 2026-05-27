"""Mine candidate narrative tags from 8-K full text via n-gram statistics.

Pipeline:
  1. Load sample_500.json full text + light cleaning (lowercase, strip
     boilerplate that survives ingestion pipeline).
  2. TF-IDF on 1-4 grams. Domain-specific stoplist (months, weekdays,
     filler corp speak).
  3. Filter candidate n-grams: doc_freq ∈ [5%, 50%] (Step 1 spec).
  4. Group by hand-curated semantic seeds (capital_return, guidance_raise,
     cost_inflation, …). Each n-gram matched to one or more seeds via
     keyword regex; un-matched but high-TF-IDF n-grams listed separately
     so the human can spot missed clusters.
  5. Emit text_concepts_analysis.md with top-50 by freq, top-50 by TF-IDF,
     proposed 12-15 tags with estimated frequencies.

Output: real_data/processed/text_concepts_analysis.md
"""
from __future__ import annotations
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PROCESSED = os.path.join(ROOT, "real_data", "processed")
EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
OUT_PATH = os.path.join(PROCESSED, "text_concepts_analysis.md")

TEXT_CAP = 12000

# Generic finance/legal boilerplate to keep out of the n-gram pool.
STOP_EXTRA = {
    "company", "companies", "quarter", "quarterly", "fiscal", "year",
    "years", "ended", "approximately", "approximately", "results",
    "financial", "press", "release", "today", "announced", "reported",
    "report", "reports", "reporting", "stated", "said", "noted",
    "respectively", "compared", "versus", "vs", "prior", "previous",
    "current", "period", "periods", "well", "also", "however",
    "including", "include", "includes", "included", "approximately",
    "due", "primarily", "across", "based", "remain", "continues",
    "continued", "continuing", "expects", "expected", "expect",
    "forward", "looking", "statements", "non", "gaap", "reconciliation",
    "shares", "share", "common", "outstanding", "additional", "available",
    "information", "see", "table", "tables", "see", "page", "appendix",
    "see", "section", "ex", "exhibit", "edgar", "sec",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "monday", "tuesday", "wednesday", "thursday", "friday",
    "us", "u.s.", "usa", "united", "states", "york", "new",
    "inc", "corp", "corporation", "incorporated", "ltd", "llc",
    "approximately", "approximate", "approximately",
    "use", "uses", "used", "using",
    "first", "second", "third", "fourth",
    "q1", "q2", "q3", "q4", "1q", "2q", "3q", "4q",
    "million", "millions", "billion", "billions", "thousand",
    "ceo", "cfo", "coo", "chief", "executive", "officer",
    "investor", "investors", "conference", "call", "webcast",
    "earnings", "per", "diluted", "basic",
}

# Hand-curated seed taxonomy. Each seed has regex patterns that match
# n-grams or phrases. Multi-pattern OR.
SEEDS = {
    # Tightened: must contain an explicit "raise/raised/increased/updated higher"
    # within 4 words of "guidance/outlook/forecast/range".
    "guidance_raise":      [r"\b(raised|raises|increasing|increased|updated|narrowed|narrowing)\s+(?:its\s+|the\s+|our\s+|full[- ]year\s+|fiscal[- ]year\s+)?\b(guidance|outlook|forecast|range)\b",
                            r"\b(guidance|outlook|forecast)\b.*\b(raised|increased|now expects higher|moved higher)\b"],
    "guidance_cut":        [r"\b(lowered|lowering|cut|reduced|reducing|withdraw|withdrew|withdrawn|suspended|suspending)\s+(?:its\s+|the\s+|our\s+|full[- ]year\s+|fiscal[- ]year\s+)?\b(guidance|outlook|forecast)\b",
                            r"\b(guidance|outlook|forecast)\b.*\b(lowered|reduced|cut|withdrawn|suspended)\b"],
    "guidance_reaffirm":   [r"\b(reaffirm|reaffirmed|reaffirming|maintain|maintained|maintaining|reiterat)\w*\b\s+(?:its\s+|the\s+|our\s+|full[- ]year\s+|fiscal[- ]year\s+)?\b(guidance|outlook|forecast|range)\b"],
    # Tightened: explicit collocations only.
    "demand_strength":     [r"\b(strong|robust|record|broad-?based|healthy)\s+(demand|orders?|backlog|bookings|pipeline|adoption)\b",
                            r"\b(demand)\s+(remains?|continues?|was|is)\s+(strong|robust|healthy|broad)\b",
                            r"\b(accelerating|surging)\s+(demand|orders|sales|adoption)\b"],
    "demand_weakness":     [r"\b(soft|weak|declining|deteriorating|sluggish|moderating)\s+(demand|orders?|sales|volume|environment)\b",
                            r"\b(demand)\s+(remained?|continues?|was|is)\s+(soft|weak|cautious|sluggish)\b"],
    "cost_inflation":      [r"\b(inflationary|input cost|raw material|wage|labor|freight|fuel|energy|commodity)\b.{0,30}\b(pressure|headwind|increase|cost|inflation)\b",
                            r"\b(cost|cogs)\b.{0,20}\b(headwind|inflation|pressure|escalation|rising|rose)\b"],
    "pricing_action":      [r"\b(price increase|price actions?|pricing action|pricing initiative|list price|price hike|higher pricing|price realization)\b",
                            r"\bpricing\b.{0,25}\b(power|strength|benefit|tailwind|contribution|favorable|positive)\b",
                            r"\b(took|implemented|realized|raised)\s+(prices?|pricing)\b"],
    "margin_expansion":    [r"\b(gross margin|operating margin|ebitda margin|margins?)\b.{0,30}\b(expand|expanded|expanding|improve|improved|improvement|strengthen|widen|widened|up\s+\d|increased\s+\d)\b",
                            r"\b(expand|expanded|expanding|widening)\b.{0,15}\bmargin"],
    "margin_pressure":     [r"\b(gross margin|operating margin|ebitda margin|margins?)\b.{0,40}\b(pressure|compress|compressed|decline|declined|contract|contracted|narrow|narrowed|lower|down|decreased|softer|headwind)\b",
                            r"\b(compress|compressed|compressing|squeezed)\b.{0,15}\bmargin",
                            r"\b(margin)\b.{0,15}\b(headwind|deleverag)\b"],
    # Tightened: must include a return-of-capital verb, not just "dividend".
    "capital_return":      [r"\b(share repurchase|share buyback|repurchased?\s+(?:shares|common stock)|stock repurchase|increased? (?:its )?(?:quarterly )?dividend|raised (?:its )?dividend|special dividend|dividend increase|tender offer)\b",
                            r"\b(authoriz|approved)\w*\b.{0,30}\b(repurchas|buyback)\b",
                            r"\breturned\b.{0,20}\b(shareholders?)\b"],
    # Tightened: explicit terms only.
    "capex_investment":    [r"\b(capital expenditure|capital expenditures|capex)\b.{0,40}\b(increas|higher|expand|investment|plan|guidance)\b",
                            r"\b(new (manufacturing )?(plant|facility|factory|site|line)|capacity expansion|capacity addition|breaking ground|broke ground|opened (a )?new)\b",
                            r"\binvesting\b.{0,15}\b(capacity|infrastructure|new plant|gigafactory)\b"],
    # Tightened: must reference actual M&A event, not vague "combined".
    "MA_activity":         [r"\b(completed (the )?acquisition|announced (the )?acquisition|definitive agreement|to acquire|acquired\s+[A-Z]|merger with|merger of equals|divestiture|divested|spin-?off|spun off|sold (its )?(business|division|segment))\b",
                            r"\bm&a\b"],
    "restructuring":       [r"\b(restructuring|reorganization|workforce reduction|cost reduction program|cost savings program|headcount reduction|layoff)s?\b",
                            r"\b(announced|initiating|launching)\b.{0,15}\b(restructuring|simplification|optimization|cost (reduction|savings)) program\b"],
    "supply_constraint":   [r"\b(supply chain)\b",
                            r"\b(chip|component|semiconductor)\s+shortage\b",
                            r"\b(supply|inventory|capacity|logistics)\s+(constraint|constrain|shortage|tightness|disrupt)\w*"],
    "AI_narrative":        [r"\b(artificial intelligence|generative ai|gen ?ai|machine learning|llm|large language model|ai-?powered|ai capabilit|ai solution|ai platform|copilot|gpt|neural network)\b",
                            r"\b(ai)\b.{0,30}\b(adopt|opportunity|investment|platform|capability|customer|workload|infrastructure|tailwind|monet)\w*"],
    "record_results":      [r"\b(record|all-?time high|highest ever|best ever|all-?time record)\b.{0,25}\b(revenue|sales|profit|earnings|margin|quarter|year|orders|backlog|bookings)\b"],
    "ESG_sustainability":  [r"\b(esg|sustainability initiative|carbon neutral|net zero|emissions reduction|renewable energy|green energy|decarbonization)\b"],
    "FX_headwind":         [r"\b(currency|fx|foreign exchange|exchange rate)\b.{0,20}\b(headwind|pressure|impact|unfavorable|adverse|hurt)\b",
                            r"\b(strong dollar|stronger dollar|dollar strength|usd strength)\b"],
    "consumer_weakness":   [r"\b(consumer)\b.{0,15}\b(weakness|cautious|pressured|softening|stretched|trade[- ]?down|pulled back)\b",
                            r"\b(discretionary)\b.{0,15}\b(spend|spending|weakness|cautious|pullback)\b"],
    "enterprise_strength": [r"\b(enterprise|commercial|b2b)\b.{0,15}\b(strong|robust|momentum|acceleration|expansion|broad-based)\b"],
}


def light_clean(t: str) -> str:
    if not t:
        return ""
    t = t[:TEXT_CAP]
    t = re.sub(r"\$[\d.,]+", " ", t)         # strip dollar amounts
    t = re.sub(r"\b\d+(?:\.\d+)?%\b", " ", t) # strip percentages
    t = re.sub(r"\b\d+(?:[.,]\d+)?\b", " ", t)# strip numbers
    t = re.sub(r"[\(\)\[\]\{\}\"]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t.lower().strip()


def main():
    with open(EVENTS_PATH) as f:
        events = json.load(f)
    print(f"loaded {len(events)} events")

    texts = [light_clean(e.get("text") or "") for e in events]
    keep = [(i, t) for i, t in enumerate(texts) if len(t) > 100]
    print(f"usable texts: {len(keep)}")

    docs = [t for _, t in keep]

    # Build extended stoplist
    from sklearn.feature_extraction import text as sk_text
    stop = set(sk_text.ENGLISH_STOP_WORDS) | STOP_EXTRA

    # TF-IDF on 1-4 grams, doc_freq filter 5% - 50%
    n_docs = len(docs)
    min_df = max(2, int(0.05 * n_docs))
    max_df = 0.50
    vect = TfidfVectorizer(
        ngram_range=(1, 4),
        min_df=min_df,
        max_df=max_df,
        stop_words=list(stop),
        sublinear_tf=True,
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-&]{2,}\b",
    )
    X = vect.fit_transform(docs)
    vocab = vect.get_feature_names_out()
    print(f"vocab: {len(vocab)} terms (min_df={min_df} max_df=50%)")

    # Doc frequency per term
    binx = (X > 0).astype(np.int8)
    doc_freq = np.asarray(binx.sum(axis=0)).ravel() / n_docs
    # Sum TF-IDF across docs
    tfidf_sum = np.asarray(X.sum(axis=0)).ravel()

    # Filter further: drop n-grams that are subset of longer high-freq one?
    # Skip — list both anyway.

    # Top 50 by freq, top 50 by TF-IDF
    order_freq = np.argsort(-doc_freq)[:50]
    order_tfidf = np.argsort(-tfidf_sum)[:50]

    # Seed matching: for each seed, count how many DOCS match at least one
    # regex pattern → estimated tag frequency on the corpus.
    seed_hits = {s: 0 for s in SEEDS}
    seed_docs = {s: [] for s in SEEDS}
    for di, doc in enumerate(docs):
        for s, patterns in SEEDS.items():
            for p in patterns:
                if re.search(p, doc):
                    seed_hits[s] += 1
                    seed_docs[s].append(di)
                    break

    seed_freq = sorted(((s, seed_hits[s] / n_docs) for s in SEEDS), key=lambda x: -x[1])

    # Identify high-TF-IDF n-grams NOT explained by any seed (potential
    # missed clusters).
    seed_words = set()
    for ps in SEEDS.values():
        for p in ps:
            for tok in re.findall(r"[a-z\-&]{3,}", p):
                seed_words.add(tok.lower())
    unmatched = []
    for idx in order_tfidf:
        term = vocab[idx]
        toks = term.split()
        if any(t in seed_words for t in toks):
            continue
        unmatched.append((term, doc_freq[idx], tfidf_sum[idx]))
        if len(unmatched) >= 30:
            break

    # ── write report ─────────────────────────────────────────────────────
    out = []
    out.append("# Narrative-tag candidate analysis from full text")
    out.append("")
    out.append(f"corpus: {n_docs} 8-K events  |  cap {TEXT_CAP} chars  |  n-grams 1-4  "
               f"|  min_df={min_df}  max_df=50%  |  vocab={len(vocab)}")
    out.append("")

    out.append("## Seed taxonomy — estimated tag frequencies")
    out.append("")
    out.append("Each seed = OR of hand-crafted regex patterns matched against cleaned text.")
    out.append("Frequency = fraction of docs where at least one pattern fires.")
    out.append("")
    out.append("| seed | freq | count | acceptable (5-45%) |")
    out.append("|---|---|---|---|")
    for s, f in seed_freq:
        flag = "✓" if 0.05 <= f <= 0.45 else ("low" if f < 0.05 else "high")
        out.append(f"| {s} | {f*100:5.1f}% | {seed_hits[s]} | {flag} |")
    out.append("")

    out.append("## Top 50 n-grams by document frequency")
    out.append("")
    out.append("| n-gram | doc_freq | tfidf_sum |")
    out.append("|---|---|---|")
    for idx in order_freq:
        out.append(f"| {vocab[idx]} | {doc_freq[idx]*100:5.1f}% | {tfidf_sum[idx]:.2f} |")
    out.append("")

    out.append("## Top 50 n-grams by TF-IDF sum")
    out.append("")
    out.append("| n-gram | doc_freq | tfidf_sum |")
    out.append("|---|---|---|")
    for idx in order_tfidf:
        out.append(f"| {vocab[idx]} | {doc_freq[idx]*100:5.1f}% | {tfidf_sum[idx]:.2f} |")
    out.append("")

    out.append("## Top 30 high-TF-IDF n-grams NOT covered by any seed")
    out.append("")
    out.append("Possible missed clusters — review for new tag candidates.")
    out.append("")
    out.append("| n-gram | doc_freq | tfidf_sum |")
    out.append("|---|---|---|")
    for term, df, ts in unmatched:
        out.append(f"| {term} | {df*100:5.1f}% | {ts:.2f} |")
    out.append("")

    # ── proposed 12-15 tag list ──────────────────────────────────────────
    # Keep only seeds inside 5-45% band; report what falls outside.
    in_band = [s for s, f in seed_freq if 0.05 <= f <= 0.45]
    out.append("## Proposed tag list — seeds inside 5-45% acceptable band")
    out.append("")
    out.append(f"Count: {len(in_band)} of {len(SEEDS)} seeds are in band.")
    out.append("")
    out.append("| tag | freq |")
    out.append("|---|---|")
    for s, f in seed_freq:
        if 0.05 <= f <= 0.45:
            out.append(f"| {s} | {f*100:5.1f}% |")
    out.append("")
    out.append("Out of band:")
    for s, f in seed_freq:
        if f < 0.05 or f > 0.45:
            tag_state = "too rare" if f < 0.05 else "too common"
            out.append(f"- `{s}` {f*100:.1f}% ({tag_state})")
    out.append("")

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out))
    print(f"saved {OUT_PATH}")
    print(f"\nseeds in band [5,45]: {len(in_band)} / {len(SEEDS)}")


if __name__ == "__main__":
    main()
