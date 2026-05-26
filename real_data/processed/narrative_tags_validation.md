# Narrative tags — validation report

## ⚠️  REVIEW NEEDED

- tag `capex_increase` never seen (freq 0%) — useless
- avg active tags per event = 0.56 — under-extracted

events: 500  |  status: {'ok': 500}

## Tag frequency

| tag | freq | count |
|---|---|---|
| inline_results |  11.2% | 56 |
| margin_expansion |  10.8% | 54 |
| demand_strength |  10.0% | 50 |
| buyback_or_dividend |   9.6% | 48 |
| margin_pressure |   6.6% | 33 |
| AI_or_tech_narrative |   2.8% | 14 |
| demand_weakness |   1.8% | 9 |
| restructuring_or_layoffs |   1.4% | 7 |
| miss_or_cut |   0.8% | 4 |
| beat_and_raise |   0.4% | 2 |
| supply_chain_issue |   0.4% | 2 |
| capex_increase |   0.0% | 0 |

## Active tags per event

- mean=0.56  median=0  min=0  max=4
- distribution: 0→276  1→179  2→37  3→6  4→2

## Mutually-exclusive contradictions

| pair | count | % |
|---|---|---|
| beat_and_raise + miss_or_cut | 0 | 0.0% |
| beat_and_raise + inline_results | 0 | 0.0% |
| miss_or_cut + inline_results | 0 | 0.0% |
| demand_strength + demand_weakness | 0 | 0.0% |
| margin_pressure + margin_expansion | 0 | 0.0% |

## Pairwise correlation (φ)

| | beat_and_raise | miss_or_cut | inline_results | demand_strength | demand_weakness | margin_pressure | margin_expansion | capex_increase | buyback_or_dividend | restructuring_or_layoffs | supply_chain_issue | AI_or_tech_narrative |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **beat_and_raise** | +1.00 | -0.01 | -0.02 | -0.02 | -0.01 | -0.02 | -0.02 | +0.00 | -0.02 | -0.01 | -0.00 | -0.01 |
| **miss_or_cut** | -0.01 | +1.00 | -0.03 | -0.03 | +0.16 | +0.16 | -0.03 | +0.00 | +0.05 | +0.18 | +0.35 | -0.02 |
| **inline_results** | -0.02 | -0.03 | +1.00 | -0.03 | -0.05 | -0.04 | -0.10 | +0.00 | +0.14 | +0.01 | -0.02 | -0.02 |
| **demand_strength** | -0.02 | -0.03 | -0.03 | +1.00 | -0.05 | +0.02 | -0.05 | +0.00 | -0.06 | -0.04 | -0.02 | +0.11 |
| **demand_weakness** | -0.01 | +0.16 | -0.05 | -0.05 | +1.00 | +0.02 | +0.05 | +0.00 | +0.01 | +0.24 | +0.47 | +0.07 |
| **margin_pressure** | -0.02 | +0.16 | -0.04 | +0.02 | +0.02 | +1.00 | -0.09 | +0.00 | +0.05 | +0.04 | -0.02 | +0.00 |
| **margin_expansion** | -0.02 | -0.03 | -0.10 | -0.05 | +0.05 | -0.09 | +1.00 | +0.00 | -0.07 | +0.01 | -0.02 | +0.14 |
| **capex_increase** | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 |
| **buyback_or_dividend** | -0.02 | +0.05 | +0.14 | -0.06 | +0.01 | +0.05 | -0.07 | +0.00 | +1.00 | +0.02 | -0.02 | -0.01 |
| **restructuring_or_layoffs** | -0.01 | +0.18 | +0.01 | -0.04 | +0.24 | +0.04 | +0.01 | +0.00 | +0.02 | +1.00 | +0.26 | -0.02 |
| **supply_chain_issue** | -0.00 | +0.35 | -0.02 | -0.02 | +0.47 | -0.02 | -0.02 | +0.00 | -0.02 | +0.26 | +1.00 | -0.01 |
| **AI_or_tech_narrative** | -0.01 | -0.02 | -0.02 | +0.11 | +0.07 | +0.00 | +0.14 | +0.00 | -0.01 | -0.02 | -0.01 | +1.00 |
