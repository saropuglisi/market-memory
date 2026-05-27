# Qwen v2 vs manual annotations — 25-event validation

manual annotator: Claude (ground truth proxy)  |  N events: 25  |  tags: 14
**Macro mean F1 (across tags with ≥1 positive in manual): 0.290**

## ⚠️  REVIEW NEEDED  (per spec: macro F1 < 0.6 OR ≥3 tags with F1 < 0.4)
- macro F1 = 0.290
- tags with F1 < 0.4 (count 8): guidance_cut, margin_expansion, margin_pressure, pricing_action, MA_activity, restructuring, supply_constraint, FX_headwind

## Per-tag scores

| tag | manual+ | qwen+ | TP | FP | FN | precision | recall | F1 |
|---|---|---|---|---|---|---|---|---|
| ESG_sustainability | 3 | 2 | 2 | 0 | 1 | 1.00 | 0.67 | 0.80 |
| record_results | 5 | 3 | 3 | 0 | 2 | 1.00 | 0.60 | 0.75 |
| capital_return | 11 | 8 | 7 | 1 | 4 | 0.88 | 0.64 | 0.74 |
| guidance_raise | 7 | 3 | 3 | 0 | 4 | 1.00 | 0.43 | 0.60 |
| demand_strength | 13 | 5 | 5 | 0 | 8 | 1.00 | 0.38 | 0.56 |
| cost_inflation | 4 | 1 | 1 | 0 | 3 | 1.00 | 0.25 | 0.40 |
| margin_expansion | 8 | 1 | 1 | 0 | 7 | 1.00 | 0.12 | 0.22 |
| guidance_cut | 1 | 0 | 0 | 0 | 1 | 0.00 | 0.00 | 0.00 |
| margin_pressure | 5 | 0 | 0 | 0 | 5 | 0.00 | 0.00 | 0.00 |
| pricing_action | 2 | 0 | 0 | 0 | 2 | 0.00 | 0.00 | 0.00 |
| MA_activity | 8 | 0 | 0 | 0 | 8 | 0.00 | 0.00 | 0.00 |
| restructuring | 6 | 0 | 0 | 0 | 6 | 0.00 | 0.00 | 0.00 |
| supply_constraint | 3 | 0 | 0 | 0 | 3 | 0.00 | 0.00 | 0.00 |
| FX_headwind | 6 | 0 | 0 | 0 | 6 | 0.00 | 0.00 | 0.00 |

- mean active tags / event — manual: 3.28  qwen: 0.92

## Disagreements per tag (FP = qwen false alarm, FN = qwen miss)

### guidance_raise — 4 disagreements
- **FN** DE 2021-02-19  (`DE_2020Q4_8K_20210219`)
- **FN** FANG 2018-11-06  (`FANG_2018Q3_8K_20181106`)
- **FN** PODD 2021-11-04  (`PODD_2021Q3_8K_20211104`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)

### guidance_cut — 1 disagreements
- **FN** HD 2019-08-20  (`HD_2019Q2_8K_20190820`)

### record_results — 2 disagreements
- **FN** PLTR 2024-08-05  (`PLTR_2024Q2_8K_20240805`)
- **FN** PODD 2021-11-04  (`PODD_2021Q3_8K_20211104`)

### demand_strength — 8 disagreements
- **FN** AIZ 2019-08-06  (`AIZ_2019Q2_8K_20190806`)
- **FN** AKAM 2023-11-07  (`AKAM_2023Q3_8K_20231107`)
- **FN** AVY 2025-01-30  (`AVY_2024Q4_8K_20250130`)
- **FN** DRI 2023-03-23  (`DRI_2023Q1_8K_20230323`)
- **FN** FANG 2018-11-06  (`FANG_2018Q3_8K_20181106`)
- **FN** PLTR 2024-08-05  (`PLTR_2024Q2_8K_20240805`)
- **FN** PODD 2021-11-04  (`PODD_2021Q3_8K_20211104`)
- **FN** TRGP 2024-08-01  (`TRGP_2024Q2_8K_20240801`)

### margin_expansion — 7 disagreements
- **FN** AKAM 2023-11-07  (`AKAM_2023Q3_8K_20231107`)
- **FN** AVY 2025-01-30  (`AVY_2024Q4_8K_20250130`)
- **FN** DE 2021-02-19  (`DE_2020Q4_8K_20210219`)
- **FN** FANG 2018-11-06  (`FANG_2018Q3_8K_20181106`)
- **FN** JCI 2021-01-29  (`JCI_2020Q4_8K_20210129`)
- **FN** MA 2020-01-29  (`MA_2019Q4_8K_20200129`)
- **FN** PLTR 2024-08-05  (`PLTR_2024Q2_8K_20240805`)

### margin_pressure — 5 disagreements
- **FN** CPT 2021-02-04  (`CPT_2020Q4_8K_20210204`)
- **FN** DHI 2025-01-21  (`DHI_2024Q4_8K_20250121`)
- **FN** LYB 2019-04-26  (`LYB_2019Q1_8K_20190426`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)
- **FN** SYY 2020-11-03  (`SYY_2020Q3_8K_20201103`)

### cost_inflation — 3 disagreements
- **FN** AVY 2025-01-30  (`AVY_2024Q4_8K_20250130`)
- **FN** DRI 2023-03-23  (`DRI_2023Q1_8K_20230323`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)

### pricing_action — 2 disagreements
- **FN** DE 2021-02-19  (`DE_2020Q4_8K_20210219`)
- **FN** DRI 2023-03-23  (`DRI_2023Q1_8K_20230323`)

### capital_return — 5 disagreements
- **FN** FANG 2018-11-06  (`FANG_2018Q3_8K_20181106`)
- **FN** JCI 2021-01-29  (`JCI_2020Q4_8K_20210129`)
- **FP** MA 2020-01-29  (`MA_2019Q4_8K_20200129`)
- **FN** MCK 2019-05-08  (`MCK_2019Q1_8K_20190508`)
- **FN** PPL 2021-11-04  (`PPL_2021Q3_8K_20211104`)

### MA_activity — 8 disagreements
- **FN** AIZ 2019-08-06  (`AIZ_2019Q2_8K_20190806`)
- **FN** AKAM 2023-11-07  (`AKAM_2023Q3_8K_20231107`)
- **FN** FANG 2018-11-06  (`FANG_2018Q3_8K_20181106`)
- **FN** LYB 2019-04-26  (`LYB_2019Q1_8K_20190426`)
- **FN** MA 2020-01-29  (`MA_2019Q4_8K_20200129`)
- **FN** PPL 2021-11-04  (`PPL_2021Q3_8K_20211104`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)
- **FN** SYY 2020-11-03  (`SYY_2020Q3_8K_20201103`)

### restructuring — 6 disagreements
- **FN** AKAM 2023-11-07  (`AKAM_2023Q3_8K_20231107`)
- **FN** AVY 2025-01-30  (`AVY_2024Q4_8K_20250130`)
- **FN** DE 2021-02-19  (`DE_2020Q4_8K_20210219`)
- **FN** JCI 2021-01-29  (`JCI_2020Q4_8K_20210129`)
- **FN** MCK 2019-05-08  (`MCK_2019Q1_8K_20190508`)
- **FN** SYY 2020-11-03  (`SYY_2020Q3_8K_20201103`)

### supply_constraint — 3 disagreements
- **FN** DHI 2025-01-21  (`DHI_2024Q4_8K_20250121`)
- **FN** MNST 2021-02-25  (`MNST_2020Q4_8K_20210225`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)

### FX_headwind — 6 disagreements
- **FN** AKAM 2023-11-07  (`AKAM_2023Q3_8K_20231107`)
- **FN** DE 2021-02-19  (`DE_2020Q4_8K_20210219`)
- **FN** MA 2020-01-29  (`MA_2019Q4_8K_20200129`)
- **FN** MCK 2019-05-08  (`MCK_2019Q1_8K_20190508`)
- **FN** MNST 2021-02-25  (`MNST_2020Q4_8K_20210225`)
- **FN** ROK 2022-01-27  (`ROK_2021Q4_8K_20220127`)

### ESG_sustainability — 1 disagreements
- **FN** PPL 2021-11-04  (`PPL_2021Q3_8K_20211104`)

## Recommendations

- **KEEP** (F1 ≥ 0.6 or no positives to evaluate): guidance_raise, record_results, capital_return, ESG_sustainability
- **REVIEW** (0.4 ≤ F1 < 0.6 — tune prompt or accept noise): demand_strength, cost_inflation
- **DROP** (F1 < 0.4 — Qwen unreliable, consider removing): guidance_cut, margin_expansion, margin_pressure, pricing_action, MA_activity, restructuring, supply_constraint, FX_headwind