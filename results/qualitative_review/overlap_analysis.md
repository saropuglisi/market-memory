# Overlap analysis — top-5 across encoders

Per-query top-5 (event_id sets) and overlap counts.

| Query | cluster | kind | all3 | 2of3 | unique | LLM∩contr | LLM∩concat | contr∩concat |
|---|---|---|---|---|---|---|---|---|
| evt_0038 | A | easy | 0 | 4 | 7 | 0 | 4 | 0 |
| evt_0037 | A | hard | 0 | 4 | 7 | 0 | 4 | 0 |
| evt_0071 | B | easy | 0 | 4 | 7 | 0 | 3 | 1 |
| evt_0075 | B | hard | 0 | 2 | 11 | 0 | 2 | 0 |
| evt_0111 | C | easy | 0 | 2 | 11 | 0 | 1 | 1 |
| evt_0118 | C | hard | 0 | 3 | 9 | 0 | 3 | 0 |
| evt_0154 | D | easy | 0 | 4 | 7 | 0 | 4 | 0 |
| evt_0152 | D | hard | 0 | 4 | 7 | 0 | 3 | 1 |
| evt_0192 | NOISE | noise_a | 1 | 4 | 4 | 1 | 5 | 1 |
| evt_0197 | NOISE | noise_b | 0 | 5 | 5 | 0 | 5 | 0 |

## Pair disagreement (total non-overlap across 10 queries, max=50)

- llm_vs_contr: 49 non-overlapping picks (avg 4.9 of 5)
- contr_vs_concat: 46 non-overlapping picks (avg 4.6 of 5)
- llm_vs_concat: 16 non-overlapping picks (avg 1.6 of 5)

## Queries with overlap ≤ 1 per pair
- llm_vs_contr: evt_0038(easy/A), evt_0037(hard/A), evt_0071(easy/B), evt_0075(hard/B), evt_0111(easy/C), evt_0118(hard/C), evt_0154(easy/D), evt_0152(hard/D), evt_0192(noise_a/NOISE), evt_0197(noise_b/NOISE)
- llm_vs_concat: evt_0111(easy/C)
- contr_vs_concat: evt_0038(easy/A), evt_0037(hard/A), evt_0071(easy/B), evt_0075(hard/B), evt_0111(easy/C), evt_0118(hard/C), evt_0154(easy/D), evt_0152(hard/D), evt_0192(noise_a/NOISE), evt_0197(noise_b/NOISE)

## Heavy divergence queries (all3 < 2)

### evt_0038 (A, easy)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=2.16
- **contrastive_v2**: same-cluster=1/5, mean_reaction_dist=1.60
- **concat_eq**: same-cluster=5/5, mean_reaction_dist=1.85
- → looks **closest to ground truth**: concat_eq

### evt_0037 (A, hard)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=1.35
- **contrastive_v2**: same-cluster=0/5, mean_reaction_dist=2.04
- **concat_eq**: same-cluster=5/5, mean_reaction_dist=1.82
- → looks **closest to ground truth**: llm_v3

### evt_0071 (B, easy)
- **llm_v3**: same-cluster=0/5, mean_reaction_dist=2.66
- **contrastive_v2**: same-cluster=3/5, mean_reaction_dist=1.24
- **concat_eq**: same-cluster=2/5, mean_reaction_dist=1.96
- → looks **closest to ground truth**: contrastive_v2

### evt_0075 (B, hard)
- **llm_v3**: same-cluster=3/5, mean_reaction_dist=3.27
- **contrastive_v2**: same-cluster=5/5, mean_reaction_dist=2.31
- **concat_eq**: same-cluster=1/5, mean_reaction_dist=2.81
- → looks **closest to ground truth**: contrastive_v2

### evt_0111 (C, easy)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=1.63
- **contrastive_v2**: same-cluster=4/5, mean_reaction_dist=1.22
- **concat_eq**: same-cluster=4/5, mean_reaction_dist=1.57
- → looks **closest to ground truth**: llm_v3

### evt_0118 (C, hard)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=1.65
- **contrastive_v2**: same-cluster=4/5, mean_reaction_dist=0.99
- **concat_eq**: same-cluster=4/5, mean_reaction_dist=1.85
- → looks **closest to ground truth**: llm_v3

### evt_0154 (D, easy)
- **llm_v3**: same-cluster=3/5, mean_reaction_dist=1.75
- **contrastive_v2**: same-cluster=0/5, mean_reaction_dist=1.05
- **concat_eq**: same-cluster=4/5, mean_reaction_dist=2.18
- → looks **closest to ground truth**: concat_eq

### evt_0152 (D, hard)
- **llm_v3**: same-cluster=1/5, mean_reaction_dist=2.71
- **contrastive_v2**: same-cluster=4/5, mean_reaction_dist=2.59
- **concat_eq**: same-cluster=3/5, mean_reaction_dist=2.71
- → looks **closest to ground truth**: contrastive_v2

### evt_0192 (NOISE, noise_a)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=1.11
- **contrastive_v2**: same-cluster=5/5, mean_reaction_dist=1.25
- **concat_eq**: same-cluster=5/5, mean_reaction_dist=1.11
- → looks **closest to ground truth**: llm_v3

### evt_0197 (NOISE, noise_b)
- **llm_v3**: same-cluster=5/5, mean_reaction_dist=1.45
- **contrastive_v2**: same-cluster=5/5, mean_reaction_dist=0.93
- **concat_eq**: same-cluster=5/5, mean_reaction_dist=1.45
- → looks **closest to ground truth**: contrastive_v2