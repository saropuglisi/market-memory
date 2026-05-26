| Approach | P@5 | P@10 | ReactCorr | CondQual | Fit(s) | Eval(s) | Wall(s) | Notes |
|---|---|---|---|---|---|---|---|---|
| concat_raw | 0.985 | 0.96 | 0.5475 | 0.57 | 0.0 | 0.12 | 0.12 | - |
| concat_eq | 1.0 | 0.985 | 0.5463 | 0.565 | 0.0 | 0.11 | 0.11 | - |
| factorized | 0.98 | 0.935 | 0.5497 | 1.0 | 0.0 | 0.08 | 0.08 | - |
| contrastive | 0.985 | 0.895 | 0.3601 | 0.57 | 1.3 | 0.16 | 1.47 | - |
| graph_experimental | 1.0 | 1.0 | 0.4944 | 0.56 | 0.0 | 0.14 | 0.14 | experimental |
| llm_structured | 0.995 | 0.975 | 0.5432 | 0.57 | 601.83 | 181.35 | 783.19 | 36 LLM failures |
