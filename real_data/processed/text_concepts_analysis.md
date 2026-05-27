# Narrative-tag candidate analysis from full text

corpus: 500 8-K events  |  cap 12000 chars  |  n-grams 1-4  |  min_df=25  max_df=50%  |  vocab=1221

## Seed taxonomy — estimated tag frequencies

Each seed = OR of hand-crafted regex patterns matched against cleaned text.
Frequency = fraction of docs where at least one pattern fires.

| seed | freq | count | acceptable (5-45%) |
|---|---|---|---|
| guidance_raise |  37.6% | 188 | ✓ |
| capital_return |  30.6% | 153 | ✓ |
| MA_activity |  17.6% | 88 | ✓ |
| restructuring |  16.6% | 83 | ✓ |
| record_results |  15.4% | 77 | ✓ |
| margin_pressure |  13.2% | 66 | ✓ |
| guidance_cut |  12.4% | 62 | ✓ |
| supply_constraint |  12.2% | 61 | ✓ |
| margin_expansion |  11.0% | 55 | ✓ |
| demand_strength |  10.6% | 53 | ✓ |
| pricing_action |   8.4% | 42 | ✓ |
| ESG_sustainability |   7.4% | 37 | ✓ |
| cost_inflation |   7.0% | 35 | ✓ |
| FX_headwind |   6.8% | 34 | ✓ |
| capex_investment |   4.8% | 24 | low |
| guidance_reaffirm |   2.8% | 14 | low |
| AI_narrative |   2.0% | 10 | low |
| consumer_weakness |   1.0% | 5 | low |
| enterprise_strength |   0.6% | 3 | low |
| demand_weakness |   0.4% | 2 | low |

## Top 50 n-grams by document frequency

| n-gram | doc_freq | tfidf_sum |
|---|---|---|
| guidance |  50.0% | 16.11 |
| revenue |  49.4% | 20.82 |
| tax |  49.2% | 13.98 |
| costs |  48.4% | 13.46 |
| driven |  46.4% | 12.41 |
| measures |  46.2% | 12.82 |
| offset |  45.8% | 12.81 |
| eps |  45.6% | 17.80 |
| com |  45.6% | 12.43 |
| rate |  45.6% | 12.60 |
| months |  45.2% | 15.04 |
| highlights |  45.0% | 9.89 |
| document |  44.8% | 9.12 |
| higher |  44.6% | 14.63 |
| continue |  43.8% | 9.34 |
| margin |  43.6% | 16.15 |
| flow |  43.4% | 14.00 |
| cash flow |  43.0% | 13.92 |
| expense |  42.6% | 12.60 |
| president |  42.6% | 8.82 |
| shareholders |  42.4% | 10.86 |
| lower |  40.6% | 13.10 |
| items |  40.0% | 11.85 |
| market |  39.4% | 10.06 |
| segment |  39.2% | 14.53 |
| value |  39.0% | 9.24 |
| outlook |  38.8% | 11.59 |
| non-gaap measures |  38.6% | 10.22 |
| excluding |  38.6% | 12.42 |
| global |  38.4% | 11.21 |
| expenses |  38.4% | 12.14 |
| cost |  38.0% | 10.28 |
| change |  37.4% | 11.49 |
| customers |  37.2% | 10.60 |
| average |  37.0% | 11.15 |
| end |  37.0% | 9.97 |
| partially |  36.8% | 10.69 |
| investments |  35.8% | 9.61 |
| partially offset |  35.6% | 10.57 |
| certain |  35.4% | 9.08 |
| provided |  34.8% | 8.92 |
| exchange |  34.8% | 12.06 |
| debt |  34.0% | 10.06 |
| record |  34.0% | 9.66 |
| following |  33.8% | 8.23 |
| price |  33.8% | 9.63 |
| management |  33.4% | 9.34 |
| time |  33.2% | 8.86 |
| significant |  32.8% | 7.52 |
| revenues |  32.6% | 14.32 |

## Top 50 n-grams by TF-IDF sum

| n-gram | doc_freq | tfidf_sum |
|---|---|---|
| revenue |  49.4% | 20.82 |
| eps |  45.6% | 17.80 |
| margin |  43.6% | 16.15 |
| guidance |  50.0% | 16.11 |
| percent |  24.6% | 15.12 |
| months |  45.2% | 15.04 |
| higher |  44.6% | 14.63 |
| segment |  39.2% | 14.53 |
| revenues |  32.6% | 14.32 |
| flow |  43.4% | 14.00 |
| tax |  49.2% | 13.98 |
| cash flow |  43.0% | 13.92 |
| costs |  48.4% | 13.46 |
| lower |  40.6% | 13.10 |
| measures |  46.2% | 12.82 |
| offset |  45.8% | 12.81 |
| rate |  45.6% | 12.60 |
| expense |  42.6% | 12.60 |
| currency |  27.8% | 12.55 |
| com |  45.6% | 12.43 |
| excluding |  38.6% | 12.42 |
| driven |  46.4% | 12.41 |
| operating income |  31.0% | 12.37 |
| ebitda |  25.0% | 12.18 |
| expenses |  38.4% | 12.14 |
| exchange |  34.8% | 12.06 |
| items |  40.0% | 11.85 |
| net sales |  19.8% | 11.73 |
| gross |  28.2% | 11.69 |
| outlook |  38.8% | 11.59 |
| change |  37.4% | 11.49 |
| profit |  23.8% | 11.43 |
| loss |  32.4% | 11.42 |
| global |  38.4% | 11.21 |
| decreased |  32.4% | 11.21 |
| average |  37.0% | 11.15 |
| range |  30.2% | 11.13 |
| consolidated |  29.2% | 11.10 |
| attributable |  31.4% | 10.96 |
| free |  30.6% | 10.92 |
| shareholders |  42.4% | 10.86 |
| free cash |  29.4% | 10.85 |
| partially |  36.8% | 10.69 |
| free cash flow |  28.8% | 10.68 |
| customers |  37.2% | 10.60 |
| partially offset |  35.6% | 10.57 |
| points |  27.4% | 10.52 |
| services |  27.0% | 10.44 |
| organic |  18.8% | 10.31 |
| cost |  38.0% | 10.28 |

## Top 30 high-TF-IDF n-grams NOT covered by any seed

Possible missed clusters — review for new tag candidates.

| n-gram | doc_freq | tfidf_sum |
|---|---|---|
| eps |  45.6% | 17.80 |
| percent |  24.6% | 15.12 |
| months |  45.2% | 15.04 |
| revenues |  32.6% | 14.32 |
| flow |  43.4% | 14.00 |
| tax |  49.2% | 13.98 |
| cash flow |  43.0% | 13.92 |
| costs |  48.4% | 13.46 |
| measures |  46.2% | 12.82 |
| offset |  45.8% | 12.81 |
| expense |  42.6% | 12.60 |
| com |  45.6% | 12.43 |
| excluding |  38.6% | 12.42 |
| driven |  46.4% | 12.41 |
| expenses |  38.4% | 12.14 |
| items |  40.0% | 11.85 |
| change |  37.4% | 11.49 |
| loss |  32.4% | 11.42 |
| global |  38.4% | 11.21 |
| average |  37.0% | 11.15 |
| consolidated |  29.2% | 11.10 |
| attributable |  31.4% | 10.96 |
| free |  30.6% | 10.92 |
| free cash |  29.4% | 10.85 |
| partially |  36.8% | 10.69 |
| free cash flow |  28.8% | 10.68 |
| customers |  37.2% | 10.60 |
| partially offset |  35.6% | 10.57 |
| points |  27.4% | 10.52 |
| services |  27.0% | 10.44 |

## Proposed tag list — seeds inside 5-45% acceptable band

Count: 14 of 20 seeds are in band.

| tag | freq |
|---|---|
| guidance_raise |  37.6% |
| capital_return |  30.6% |
| MA_activity |  17.6% |
| restructuring |  16.6% |
| record_results |  15.4% |
| margin_pressure |  13.2% |
| guidance_cut |  12.4% |
| supply_constraint |  12.2% |
| margin_expansion |  11.0% |
| demand_strength |  10.6% |
| pricing_action |   8.4% |
| ESG_sustainability |   7.4% |
| cost_inflation |   7.0% |
| FX_headwind |   6.8% |

Out of band:
- `capex_investment` 4.8% (too rare)
- `guidance_reaffirm` 2.8% (too rare)
- `AI_narrative` 2.0% (too rare)
- `consumer_weakness` 1.0% (too rare)
- `enterprise_strength` 0.6% (too rare)
- `demand_weakness` 0.4% (too rare)
