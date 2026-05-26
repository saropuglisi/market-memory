# Degradation table — L1 to L5

Generated 20260525_113027.
n_train/n_test per level:
- L1: 132/44
- L2: 150/50
- L3: 200/67
- L4: 140/47
- L5: 170/57

## P@5

| Approach | L1 precision_at_5 | L2 precision_at_5 | L3 precision_at_5 | L4 precision_at_5 | L5 precision_at_5 | Trend |
|---|---|---|---|---|---|---|
| concat_raw | 0.985 | 0.750 | 0.495 | 0.570 | 0.560 | cliff |
| concat_eq | 1.000 | 0.765 | 0.510 | 0.630 | 0.545 | cliff |
| factorized | 0.980 | 0.720 | 0.375 | 0.370 | 0.485 | cliff |
| contrastive | 0.985 | 0.565 | 0.385 | 0.415 | 0.545 | cliff |
| contrastive_v2 | 0.890 | 0.620 | 0.520 | 0.715 | 0.790 | cliff |
| contrastive_v3 | 0.830 | 0.695 | 0.450 | 0.665 | 0.735 | cliff |
| graph_experimental | 1.000 | 0.830 | 0.600 | 0.685 | 0.715 | cliff |
| llm_structured_v3 | 0.990 | 0.815 | 0.560 | 0.600 | 0.645 | cliff |

## ReactCorr

| Approach | L1 reaction_corr | L2 reaction_corr | L3 reaction_corr | L4 reaction_corr | L5 reaction_corr | Trend |
|---|---|---|---|---|---|---|
| concat_raw | 0.547 | 0.355 | 0.237 | 0.441 | 0.466 | cliff |
| concat_eq | 0.546 | 0.382 | 0.297 | 0.492 | 0.528 | stable |
| factorized | 0.550 | 0.377 | 0.287 | 0.482 | 0.493 | cliff |
| contrastive | 0.360 | 0.187 | 0.313 | 0.266 | 0.593 | improving |
| contrastive_v2 | 0.517 | 0.362 | 0.298 | 0.548 | 0.702 | improving |
| contrastive_v3 | 0.602 | 0.361 | 0.259 | 0.549 | 0.700 | improving |
| graph_experimental | 0.494 | 0.286 | 0.199 | 0.378 | 0.527 | stable |
| llm_structured_v3 | 0.547 | 0.395 | 0.303 | 0.492 | 0.531 | stable |

## Util@5

| Approach | L1 utility_at_5 | L2 utility_at_5 | L3 utility_at_5 | L4 utility_at_5 | L5 utility_at_5 | Trend |
|---|---|---|---|---|---|---|
| concat_raw | 0.845 | 0.460 | 0.240 | 0.505 | 0.550 | cliff |
| concat_eq | 0.855 | 0.455 | 0.230 | 0.535 | 0.540 | cliff |
| factorized | 0.825 | 0.485 | 0.185 | 0.330 | 0.480 | cliff |
| contrastive | 0.835 | 0.370 | 0.195 | 0.335 | 0.535 | cliff |
| contrastive_v2 | 0.800 | 0.400 | 0.290 | 0.625 | 0.775 | stable |
| contrastive_v3 | 0.735 | 0.440 | 0.250 | 0.585 | 0.715 | stable |
| graph_experimental | 0.865 | 0.515 | 0.290 | 0.565 | 0.715 | cliff |
| llm_structured_v3 | 0.840 | 0.525 | 0.280 | 0.515 | 0.640 | cliff |

## CondQual

| Approach | L1 conditional_quality | L2 conditional_quality | L3 conditional_quality | L4 conditional_quality | L5 conditional_quality | Trend |
|---|---|---|---|---|---|---|
| concat_raw | 0.570 | 0.635 | 0.700 | 0.660 | 0.670 | improving |
| concat_eq | 0.565 | 0.595 | 0.680 | 0.680 | 0.670 | improving |
| factorized | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | stable |
| contrastive | 0.570 | 0.530 | 0.680 | 0.670 | 0.675 | improving |
| contrastive_v2 | 0.605 | 0.640 | 0.640 | 0.755 | 0.740 | improving |
| contrastive_v3 | 0.620 | 0.675 | 0.675 | 0.680 | 0.710 | improving |
| graph_experimental | 0.560 | 0.655 | 0.710 | 0.730 | 0.730 | improving |
| llm_structured_v3 | 0.570 | 0.620 | 0.705 | 0.620 | 0.710 | improving |

## LLM v3 vs contrastive_v2 — head-to-head

Delta = v3 − contrastive_v2.

| Level | metric | contrastive_v2 | llm_v3 | Δ |
|---|---|---|---|---|
| L1 | P@5 | 0.890 | 0.990 | **+0.100** |
| L1 | RC | 0.517 | 0.547 | +0.030 |
| L1 | Util@5 | 0.800 | 0.840 | +0.040 |
| L2 | P@5 | 0.620 | 0.815 | **+0.195** |
| L2 | RC | 0.362 | 0.395 | +0.033 |
| L2 | Util@5 | 0.400 | 0.525 | **+0.125** |
| L3 | P@5 | 0.520 | 0.560 | +0.040 |
| L3 | RC | 0.298 | 0.303 | +0.005 |
| L3 | Util@5 | 0.290 | 0.280 | -0.010 |
| L4 | P@5 | 0.715 | 0.600 | **-0.115** |
| L4 | RC | 0.548 | 0.492 | **-0.056** |
| L4 | Util@5 | 0.625 | 0.515 | **-0.110** |
| L5 | P@5 | 0.790 | 0.645 | **-0.145** |
| L5 | RC | 0.702 | 0.531 | **-0.171** |
| L5 | Util@5 | 0.775 | 0.640 | **-0.135** |

## Cycle_phase distribution — LLM v3 per livello

| Level | mid | late | recovery | early | recession | n |
|---|---|---|---|---|---|---|
| L1 | 11 (65%) | 5 (29%) | 0 (0%) | 1 (6%) | 0 (0%) | 17 |
| L2 | 109 (68%) | 36 (22%) | 15 (9%) | 0 (0%) | 0 (0%) | 160 |
| L3 | 133 (66%) | 52 (26%) | 15 (8%) | 0 (0%) | 0 (0%) | 200 |
| L4 | 109 (68%) | 36 (22%) | 15 (9%) | 0 (0%) | 0 (0%) | 160 |
| L5 | 92 (58%) | 57 (36%) | 9 (6%) | 0 (0%) | 0 (0%) | 158 |

Per riferimento — v2 cache su L2 v2 mostrava mid=72%, late=11%.
Il prompt direttivo v3 raddoppia/triplica la frequenza di `late` ma azzera `early`/`recession`.