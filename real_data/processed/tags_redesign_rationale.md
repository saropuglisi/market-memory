# Narrative tags v2 — redesign rationale

## Why v1 needed redesign

The v1 extraction (12 tags via Qwen 2.5-7B on full-text, strict YES/NO,
temperature 0) produced structurally weak vectors on sample_500:

- **55% of events had a zero tag vector** → Jaccard similarity = 0 with
  every other event, neutralizing the entire tag block in concat_eq+.
- **5 of 12 tags had freq < 2%**: `capex_increase` (0.0%),
  `beat_and_raise` (0.4%), `supply_chain_issue` (0.4%), `miss_or_cut`
  (0.8%), `restructuring_or_layoffs` (1.4%). Tags this rare cannot
  discriminate.
- **mean active tags / event = 0.56** (target: 1.5-4).
- Distribution was skewed: `demand_strength` 33% in the summary-based v1,
  while several conceptually distinct tags shared the same low band.

Root cause: v1 tags were chosen *before* looking at the data. Several
labels did not map to vocabulary that 8-K press releases actually use
(`capex_increase` is rarely phrased that way; the corpus says "capacity
expansion", "new facility", "investment in plant"). Strict YES/NO Qwen
amplifies this mismatch.

## Approach for v2

1. **Mine candidate concepts from the data itself.** Built
   `real_data/analyze_text_concepts.py`: TF-IDF on 1–4 grams (vocab
   1221 terms after stoplist + 5% min_df + 50% max_df cap), plus 20
   hand-curated regex seeds. Each seed has 2–4 OR'd regex patterns
   tuned against the corpus.
2. **Iterate on regex specificity** until each candidate's corpus
   frequency lands in the acceptable band [5%, 45%]. Tightening was
   needed for `guidance_raise` (66% → 38% after requiring explicit
   "raised/increased X guidance"), `MA_activity` (54% → 18% after
   requiring a real M&A verb), `capital_return` (35%), and others.
   Loosening was needed for `supply_constraint`, `pricing_action`,
   `margin_pressure`.
3. **Drop candidates that stayed outside the band** even after tuning:
   `capex_investment` (4.8% — wording too variable), `guidance_reaffirm`
   (2.8% — rare in 8-Ks; usually implicit), `AI_narrative` (2.0% — corpus
   is 2018-2024, mostly pre-Gen-AI; not a discriminative signal at this
   scale), `consumer_weakness` (1.0%), `enterprise_strength` (0.6%).

## Final list — 14 tags in 4 categories

Estimated corpus frequency from regex seed analysis (full text, cap 12000):

| tag | est. freq | category |
|---|---|---|
| guidance_raise | 37.6% | A outcome |
| capital_return | 30.6% | C capital |
| MA_activity | 17.6% | C capital |
| restructuring | 16.6% | C capital |
| record_results | 15.4% | A outcome |
| margin_pressure | 13.2% | B drivers |
| guidance_cut | 12.4% | A outcome |
| supply_constraint | 12.2% | D thematic |
| margin_expansion | 11.0% | B drivers |
| demand_strength | 10.6% | B drivers |
| pricing_action | 8.4% | B drivers |
| ESG_sustainability | 7.4% | D thematic |
| cost_inflation | 7.0% | B drivers |
| FX_headwind | 6.8% | D thematic |

All 14 tags are inside [5%, 45%]. All 4 categories have ≥3 tags.
Total: 14, within the 12-15 target.

## Mapping v1 → v2

| v1 tag | v1 Qwen freq | v2 status | note |
|---|---|---|---|
| beat_and_raise | 0.4% | renamed → `guidance_raise` | broader, more frequent in actual text |
| miss_or_cut | 0.8% | renamed → `guidance_cut` | explicit verb-noun pair |
| inline_results | 11.2% | **dropped** | weak signal for analogical retrieval |
| demand_strength | 10.0% | kept | tightened regex |
| demand_weakness | 1.8% | **dropped** | freq too low in this corpus |
| margin_pressure | 6.6% | kept | regex broadened |
| margin_expansion | 10.8% | kept | tightened |
| capex_increase | 0.0% | **dropped** | wording too variable; replaced by `MA_activity` and `restructuring` in category C |
| buyback_or_dividend | 9.6% | renamed → `capital_return` | broader umbrella |
| restructuring_or_layoffs | 1.4% | renamed → `restructuring` | regex broadened |
| supply_chain_issue | 0.4% | renamed → `supply_constraint` | regex broadened |
| AI_or_tech_narrative | 2.8% | **dropped** | <5% in corpus; not discriminative at this scale |

**Net change**: -4 tags dropped (inline_results, demand_weakness,
capex_increase, AI_or_tech_narrative), +6 added (record_results,
cost_inflation, pricing_action, MA_activity, ESG_sustainability,
FX_headwind), 2 renamed. 12 → 14 tags total.

## Expected gains over v1

| metric | v1 (full-text) | v2 (estimated) |
|---|---|---|
| events with all-zero vector | 55% | ≤ 20% (est.) |
| mean active tags/event | 0.56 | ≈ 1.9 (sum of freqs / 14 × …) |
| useless tags (freq <2%) | 5 of 12 | 0 of 14 (by construction) |
| coverage of all 4 categories | yes but unbalanced | yes, ≥3 tags each |

The v2 *estimate* assumes Qwen recovers 50-80% of the regex-seed
frequencies (Qwen's strict YES/NO is more conservative than regex). The
*real* validation will come from the manual annotation comparison in
Step 4.

## Open questions for the user

- **Drop AI_narrative entirely, or keep at <5% as a stretch tag?** It is
  conceptually important post-2023 but the corpus (2018-2024 mix) is
  dominated by pre-Gen-AI events. Currently dropped.
- **Add `consumer_weakness` despite freq <2%?** Could matter for
  consumer-discretionary events specifically. Currently dropped.
- **Pair-wise contradictions** — keep `guidance_raise` ↔ `guidance_cut`
  and `margin_expansion` ↔ `margin_pressure` as mutually exclusive in
  validation? A single 8-K typically lands on one side, but earnings
  releases can describe mixed dynamics (e.g. one segment expanding while
  another compresses) — should we allow both = 1 without flagging?
