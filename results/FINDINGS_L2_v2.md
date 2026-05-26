# FINDINGS — Level 2 v2 (regenerated)

Dataset: `data/mock_events_L2.json` (v2), 200 eventi (150 train / 50 test).
Modifiche vs L2 v1:
- 25 template per cluster × 6 intro × 6 closer = pool ricco → **160 testi unici**.
- Sector cross-pollination (≈25-30% off-primary) → ogni cluster ha **4 settori**.
- Mean-shrink 35% verso grand mean su tutte le dim macro/micro/semantic.
- Std × 1.5 mantenuto.

Sanity check (z-scored feature distance, train cluster events):

| | L1 | L2 v1 (vecchio) | **L2 v2 (nuovo)** |
|---|---|---|---|
| unique texts | 17 | 17 | **160** |
| sectors / cluster | 2-3 | 2-3 | **4 ciascuno** |
| intra-cluster dist | 2.56 | 3.46 | 4.14 |
| inter-cluster dist | 5.82 | 5.99 | 5.70 |
| **gap (inter - intra)** | 3.26 | 2.53 | **1.56** |

Gap del 52% inferiore a L1, vicino al target 1.0–1.5.

## Tabella metriche

| Approach | P@5 | P@10 | ReactCorr | CondQual | **Util@5** | Wall(s) | Note |
|---|---|---|---|---|---|---|---|
| concat_raw | 0.750 | 0.715 | 0.355 | 0.635 | 0.460 | 6.6 | |
| concat_eq | 0.765 | 0.735 | 0.382 | 0.595 | 0.455 | 0.2 | |
| factorized | 0.720 | 0.618 | 0.377 | **1.00** | 0.485 | 0.1 | |
| contrastive v1 | 0.565 | 0.533 | 0.187 | 0.530 | 0.370 | 0.9 | v1 broken (atteso) |
| contrastive v2 | 0.620 | 0.583 | 0.362 | 0.640 | 0.400 | 1.8 | |
| graph_experimental | 0.830 | 0.758 | 0.286 | 0.655 | 0.515 | 0.2 | experimental |
| llm_structured v1 | 0.820 | 0.765 | 0.375 | 0.625 | 0.490 | 530 | 12 fail |
| **llm_structured v2** | **0.850** | **0.803** | **0.395** | 0.660 | **0.535** | 525 | 4 fail |

Plots: [bars_L2_20260525_102456.png](bars_L2_20260525_102456.png),
[umap_L2_20260525_102456.png](umap_L2_20260525_102456.png).

## Verifica predizioni

| # | Predizione | Esito |
|---|---|---|
| 1 | concat_eq P@5 ∈ [0.70, 0.85] | **CONFERMATO** — 0.765 (vs L2v1: 0.950) |
| 2 | graph_exp P@5 < 0.95 | **CONFERMATO** — 0.830 (vs L2v1: 0.995). Cross-pollination ha rotto il leakage strutturale. |
| 3 | contrastive v2 mantiene ReactCorr lead E migliora Util@5 | **SMENTITO** — ReactCorr 0.362 vs concat_eq 0.382 (perde il primato); Util@5 0.400 vs concat_eq 0.455. **Su dataset più difficile contrastive v2 peggiora**, non migliora. |
| 4 | competitive/operational/late emergono | **CONFERMATO** — v2 ora produce `operational=12`, `competitive=5`, `late_cycle=22`. Era artefatto dei testi, non bias del modello. (cache cumulativa n=352, mix L1+L2v1+L2v2) |
| 5 | cycle_phase mid sotto 50% | **PARZIALE** — mid scende da 72% (L1) a 67% (236/352). Spostamento reale ma non sotto soglia 50%. Bias del modello verso "mid" persiste oltre il livello dei testi. |

## Insight nuovi

### a) **LLM v2 è il vincitore complessivo** su L2 difficile.
Su 5 metriche (P@5, P@10, ReactCorr, CondQual, Util@5), v2 è primo o secondo in tutte:
- P@5 = **0.850** (best)
- ReactCorr = **0.395** (best dopo concat_eq di pochissimo)
- Util@5 = **0.535** (best)
- CondQual = 0.660 (secondo dopo factorized=1.00)

Il guadagno emerge solo quando i testi hanno informazione discriminativa che le feature numeriche non catturano già. Su L1/L2v1 non si vedeva.

Costo: 525s wall time (vs 0.2s di concat_eq). ROI economico marginale ma reale.

### b) **Contrastive v2 collassa dal best su ReactCorr al peggio dei "buoni".**
Su L1 e L2v1 contrastive v2 vinceva ReactCorr (+0.10 vs concat_eq).
Su L2 v2 perde (-0.02). Loss training pulita (2.33 → 0.001), 145/150 valid anchors,
pair distribution sana. Quindi non è collapse né training broken — è **mismatch
train/test**.

Ipotesi: con shrink delle medie del 35%, train e test set hanno più overlap geometrico
tra cluster. I positivi del training set (quantile 20% di reaction-distance) sono
una nuvola che si sovrappone parzialmente ad altri cluster nel test. Il modello impara
una struttura di reazioni che non generalizza più bene.

Possibili fix da provare:
- Pesare i pair con confidence basata su quanto i due eventi appartengono allo stesso cluster (ma usa label → leak).
- Aumentare regolarizzazione (weight decay) per ridurre overfitting.
- Stop early (loss < 0.05 invece di 0.001).

### c) **Factorized continua a essere l'unico vero specialist** per condizionamento.
CondQual = 1.00 vs 0.53–0.66 per tutti gli altri. È il caso d'uso che giustifica
da solo il design multi-stage.

### d) **Graph perde leakage ma resta sopra concat su Util@5** (0.515 vs 0.455).
Cross-pollination ha tagliato P@5 da 0.995 → 0.830 ma il segnale sector resta
informativo. Continua a essere un encoder credibile, non solo un artefatto.

### e) **LLM v1 ancora produce out-of-vocab** (12 failures su L2 v2 vs 0 su L1).
Sui nuovi testi più ricchi che includono linguaggio competitive/operational/late-cycle,
v1 confonde di nuovo i campi. Conferma che lo schema di v2 è strutturalmente
più robusto.

### f) **Cycle_phase bias verso "mid"** rimane ~67% anche su testi che menzionano
esplicitamente "late cycle". L'LLM riconosce la parola ma resta cauto nell'assegnare.
Probabilmente serve un prompt più direttivo ("se il testo menziona late cycle o
cycle maturity, assegna 'late'").

## Lessons learned

1. **Texture del dataset conta più della scala dei numeri.** Std×1.5 da solo non basta
   a rompere la separabilità. Servono testi diversi e ticker non-bijettivi.
2. **L2 ora discrimina davvero.** P@5 spread: 0.565 (contrastive v1) → 0.850 (LLM v2).
   Differenze visibili e ordinabili.
3. **Trade-off contrastive emerge solo su data hard.** Su L1 era invisibile, su L2 v1
   marginale, su L2 v2 evidente. Suggerisce che il fix `v2` aiuta nel definire pair
   thresholds sensate ma non risolve la generalizzazione train→test su distribuzioni
   sovrapposte.
4. **LLM costoso ma utile** quando i testi portano segnale incrementale. Il break-even
   col costo (525s vs 0.2s) deve essere giustificato dal valore della discriminazione
   testuale. Su L2 v2 sì; su L1/L2v1 no.

## Output

- Tabella: [results/run_L2_20260525_102456.md](run_L2_20260525_102456.md)
- JSON: [results/run_L2_20260525_102456.json](run_L2_20260525_102456.json)
- Bar chart: [results/bars_L2_20260525_102456.png](bars_L2_20260525_102456.png)
- UMAP: [results/umap_L2_20260525_102456.png](umap_L2_20260525_102456.png)
- Dataset archivio: [data/mock_events_L2_v1_archived.json](../data/mock_events_L2_v1_archived.json)
- Sanity script: [diagnostics/sanity_L2v2.py](../diagnostics/sanity_L2v2.py)
- Loss/pair log contrastive v2: [cache/contrastive_v2_distlog.txt](../cache/contrastive_v2_distlog.txt)
