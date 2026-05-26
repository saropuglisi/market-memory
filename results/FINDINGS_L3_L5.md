# FINDINGS — Batch L3, L4, L5 (LLM esclusi)

Run timestamp: 2026-05-25 10:40–10:44.
Vedere [DEGRADATION_TABLE.md](DEGRADATION_TABLE.md) per la tabella completa
e [degradation_plots/](degradation_plots/) per i plot per metrica.

Sanity check pre-run (gap intra/inter feature, z-scored):

| Level | n train/test | gap macro+micro+sem | gap macro+micro | gap semantic | gap reaction |
|---|---|---|---|---|---|
| L1 | 132/44 | 3.19 | 2.72 | 1.66 | 1.15 |
| L2 v2 | 150/50 | 1.50 | 1.25 | 0.82 | 0.84 |
| L3 | 200/67 | 0.67 | 0.55 | 0.36 | 0.60 |
| L4 | 140/47 | 0.79 | **-0.03** | **1.73** | 1.24 |
| L5 | 170/57 | 0.82 | 0.68 | 0.45 | **2.06** |

L4 ha macro+micro pooled (gap ≈ 0), semantic ben separato. L5 ha reaction
ben separato, features overlap.

## Sintesi tabella metriche

P@5 per encoder × livello:

| Approach | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| concat_raw | 0.985 | 0.750 | 0.495 | 0.570 | 0.560 |
| concat_eq | 1.000 | 0.765 | 0.510 | 0.630 | 0.545 |
| factorized | 0.980 | 0.720 | 0.375 | 0.370 | 0.485 |
| contrastive (v1) | 0.985 | 0.565 | 0.385 | 0.415 | 0.545 |
| contrastive_v2 | 0.890 | 0.620 | 0.520 | **0.715** | **0.790** |
| contrastive_v3 | 0.830 | 0.695 | 0.450 | 0.665 | 0.735 |
| graph_experimental | **1.000** | **0.830** | **0.600** | 0.685 | 0.715 |

## Risposte alle 5 domande

### 1) Quale approccio degrada in modo più "graceful"?

Tutti gli encoder mostrano un drop forte L1→L3 (atteso, dataset si fa difficile).
Il pattern interessante è la **forma del declino** e l'eventuale recupero su L4/L5.

- **graph_experimental** = miglior graceful su P@5. Curva: 1.00 → 0.83 → 0.60 → 0.69 → 0.72.
  Cala dolcemente, recupera leggermente sui livelli "structural" (L4, L5). Il segnale
  settore + features standardizzate è robusto a manipolazioni diverse.
- **contrastive_v2** = graceful su Util@5 (stable) e improving su ReactCorr. P@5
  ha forma a U: 0.89 → 0.62 (L3) → 0.79 (L5). Recupera in modo netto quando il
  task allinea reaction-similarity con cluster (L4, L5).
- **factorized** = cliff senza recupero su P@5 (0.98 → 0.37). Su CondQual resta
  perfetto (1.00 ovunque) per design.
- **concat_eq** = cliff su P@5 (1.00 → 0.51). Stable su ReactCorr (0.55 → 0.30 → 0.53).
- **contrastive v1** = cliff catastrofico, atteso (overfit + bad pair definition).

Vincitore qualitativo: **graph + contrastive_v2** mostrano profili più stabili
attraverso i livelli, ognuno su metriche diverse.

### 2) Contrastive v3 vs v2: il fix anti-overfitting funziona?

Risultato **misto**:

| Metrica | Livello | v2 | v3 | Delta |
|---|---|---|---|---|
| P@5 | L1 | 0.890 | 0.830 | -0.060 |
| P@5 | L2 | 0.620 | 0.695 | **+0.075** |
| P@5 | L3 | 0.520 | 0.450 | -0.070 |
| P@5 | L4 | 0.715 | 0.665 | -0.050 |
| P@5 | L5 | 0.790 | 0.735 | -0.055 |
| ReactCorr | L1 | 0.517 | 0.602 | **+0.085** |
| ReactCorr | L2 | 0.362 | 0.361 | ~0 |
| ReactCorr | L3 | 0.298 | 0.259 | -0.039 |
| ReactCorr | L4 | 0.548 | 0.549 | ~0 |
| ReactCorr | L5 | 0.702 | 0.700 | ~0 |

**Risposta**: v3 **batte v2 dove v2 overfittava** (L1 ReactCorr +0.085) e **dove
v2 perdeva su P@5** (L2 +0.075). Su L3-L5 v3 peggiora leggermente perché
l'early stop (loss<0.05 → 11-26 epoche) gli toglie capacità su task complessi.

Loss curves di v3 dal log:
- L1: 100 epoche, no early stop → fit completo, batte v2 su ReactCorr
- L2: 26 epoche (loss<0.05) → ok
- L3: 44 epoche (no improve 10) → struttura difficile
- L4: 26 epoche (loss<0.05) → ok
- L5: 11 epoche (loss<0.05) → forse troppo early

Il fix funziona **come anti-overfitting**, non come boost universale. Per L3-L5
serve calibrare early-stop più tollerante (es. loss<0.02 invece di 0.05).

### 3) Graph performance su L4 (macro/micro pooled): regge o crolla?

**Ipotesi smentita**: graph **regge** (P@5 = 0.685, Util@5 = 0.565). 

Spiegazione: graph_experimental concatena `[macro_z, micro_z, semantic_z, ticker_emb, sector_emb]`.
In L4, macro_z e micro_z portano gap ≈ 0 (non informativi) ma:
- **semantic_z** rimane forte (gap = 1.73)
- **sector_emb** cross-pollinated ma ancora correlato (70% primary sector)
- **ticker_emb** legato a settore via random projection

Quindi graph "scarta" implicitamente macro/micro (z-score li uniforma) e usa il
resto. Il segnale semantic è abbastanza forte da tenere up P@5.

**Interpretazione**: graph non è un "macro/micro encoder" come supposto.
È un encoder multi-block che si adatta a quale blocco porta segnale.

### 4) L5 reaction-driven: quale approccio cattura meglio struttura su sole reazioni?

**Ipotesi confermata**: contrastive_v2 (e v3) brillano su L5.

| Encoder | L5 P@5 | L5 ReactCorr | L5 Util@5 |
|---|---|---|---|
| concat_eq | 0.545 | 0.528 | 0.540 |
| **contrastive_v2** | **0.790** | **0.702** | **0.775** |
| contrastive_v3 | 0.735 | 0.700 | 0.715 |
| graph_experimental | 0.715 | 0.527 | 0.715 |

Differenza tra contrastive e baseline: +0.245 su P@5, +0.174 su ReactCorr.
Contrastive impara da pair-similarità su reaction → quando reaction è il segnale
dominante e features sono rumore, le pair-similarities riflettono la struttura
vera dei cluster. Concat_eq vede solo features e tira random.

v3 leggermente sotto v2 perché early-stop a epoca 11 lo lascia "verde". Iperparametro
da rivedere.

### 5) Quale livello è il più discriminante?

Standard deviation di P@5 attraverso encoder (escluso v1 broken):

| Livello | std P@5 | encoder range |
|---|---|---|
| L1 | 0.07 | 0.83–1.00 |
| L2 | 0.07 | 0.62–0.83 |
| L3 | 0.07 | 0.38–0.60 |
| **L4** | **0.12** | 0.37–0.72 |
| L5 | 0.10 | 0.48–0.79 |

**L4 è il più discriminante.** Il setup (macro/micro pooled) costringe gli
encoder a usare blocchi diversi, e li separa molto: factorized fallisce
(0.37, il suo macro-filter non discrimina), contrastive_v2 vince (0.715),
concat_eq sta in mezzo (0.63), graph regge (0.685).

L5 secondo: 0.79 (contrastive_v2) vs 0.485 (factorized).

**Suggerimento metodologico**: L4 e L5 sono i livelli più utili per il
benchmarking finale. L3 è "troppo difficile per tutti" (P@5 ≤ 0.60 per tutti),
quindi discrimina meno.

## Insight aggiuntivi

### a) Profili di encoder
- **concat_eq** = "general purpose stable": ReactCorr abbastanza costante,
  P@5 cala ma non collassa.
- **factorized** = "specialista CondQual": vince ovunque su filtri macro,
  perde tutto il resto su L3+.
- **graph** = "robust adapt": più stabile attraverso difficoltà diverse.
- **contrastive_v2** = "reaction-aware learner": eccelle quando il task
  premia la reaction-geometry (L4, L5). Overfit su L1.
- **contrastive_v3** = "anti-overfit contrastive": vince dove v2 overfit,
  perde dove early-stop è troppo aggressivo. Va tunato.

### b) CondQual cresce con la difficoltà per tutti
Pattern strano: tutti gli encoder migliorano CondQual passando da L1 (0.56) a
L3+ (0.65-0.74). Spiegazione probabile: con più overlap tra cluster, il filtro
macro (VIX > 18) seleziona un sottoinsieme dove le distribuzioni si confondono
di meno → P@5 condizionato sale.

### c) Trend "improving" su ReactCorr per contrastive
contrastive_v2 e v3 sono gli unici con trend improving su ReactCorr
attraverso L1→L5. La loro architettura beneficia di dataset più sfidanti
dove il segnale reaction è discriminativo. Conferma il valore strategico di
questo approccio man mano che ci avviciniamo a dati reali (con segnale rumoroso).

## Decisione LLM

Aspetto go-ahead esplicito su quali livelli attivare LLM v3 (e magari v2 per
comparazione). Setup pronto: cache disco già popolata su L2 v2 (160 testi).
L3 ha 200 testi unici, L4 160, L5 158 → totali nuovi ~520 testi unici (alcuni
overlap con L2). Tempo stimato totale: ~30 min per L3+L4+L5 con LLM v2+v3
in parallelo (se possibile) o sequenziale.

## Output files

- Tabella: [results/DEGRADATION_TABLE.md](DEGRADATION_TABLE.md)
- Plot: [results/degradation_plots/](degradation_plots/)
  - [precision_at_5.png](degradation_plots/precision_at_5.png)
  - [reaction_corr.png](degradation_plots/reaction_corr.png)
  - [utility_at_5.png](degradation_plots/utility_at_5.png)
  - [conditional_quality.png](degradation_plots/conditional_quality.png)
- JSON per livello: `run_L<n>_*.json` (timestamp 20260525_1043-1044)
- Loss curves contrastive_v3: [cache/contrastive_v3_loss_curve.json](../cache/contrastive_v3_loss_curve.json)
