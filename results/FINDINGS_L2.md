# FINDINGS — Level 2

Dataset: `data/mock_events_L2.json` (200 eventi, 150 train / 50 test, ~20% NOISE,
stds dei cluster × 1.5).

## Tabella metriche

| Approach | P@5 | P@10 | ReactCorr | CondQual | **Util@5** | Wall(s) | Note |
|---|---|---|---|---|---|---|---|
| concat_raw | 0.885 | 0.838 | 0.334 | 0.52 | 0.615 | 0.2 | |
| concat_eq | **0.950** | 0.910 | 0.359 | 0.535 | 0.625 | 0.2 | |
| factorized | 0.840 | 0.710 | 0.363 | **1.00** | 0.610 | 0.1 | |
| contrastive (v1) | 0.875 | 0.798 | 0.365 | 0.56 | 0.615 | 1.4 | |
| **contrastive_v2** | 0.675 | 0.613 | **0.454** | 0.565 | 0.520 | 1.7 | |
| graph_experimental | **0.995** | 0.980 | 0.303 | 0.555 | 0.690 | 0.2 | experimental |
| llm_structured (v1) | **0.980** | 0.930 | 0.360 | 0.530 | 0.650 | 77 | 3 fail |
| llm_structured_v2 | **0.980** | 0.973 | 0.403 | 0.525 | **0.655** | 51 | 0 fail |

Plots: [bars_L2_20260525_002021.png](bars_L2_20260525_002021.png),
[umap_L2_20260525_002021.png](umap_L2_20260525_002021.png).

## Verifica predizioni

| # | Predizione | Esito |
|---|---|---|
| 1 | P@5 scende a 0.65–0.85 per tutti | **PARZIALE** — solo contrastive_v2 (0.675) e factorized (0.84) sono nel range. concat_eq=0.95, graph=0.995, llm v1/v2=0.98. **Mezza tabella satura ancora**. |
| 2 | contrastive_v2 si separa da concat_eq su ReactCorr | **CONFERMATO** — 0.454 vs 0.359, delta +0.095. Il fix sui pair-thresholds tiene anche su L2. |
| 3 | llm_struct_v2 utility@5 > concat_eq | **CONFERMATO** — 0.655 vs 0.625, delta +0.030. Margine piccolo ma persistente. |
| 4 | competitive/operational/late emergono | **SMENTITO** — `competitive=0`, `operational=0` in tutto v2. `late_cycle=0` per v2 cycle_phase. Sono bias del modello (qwen2.5:7b non sceglie mai questi token sui nostri testi), non artefatto del mock. |
| 5 | cycle_phase si sposta da "mid" | **SMENTITO** — mid=72% in v2 (139/193). Stessa percentuale di L1. Bias persistente. |

## Diagnosi: perché L2 non rompe abbastanza il task

P@5 doveva scendere sotto 0.85 per tutti. Invece resta a 0.95–0.995 per metà
degli encoder. Cause:

1. **Solo 17 testi unici nel dataset** (4 template × 4 cluster + 1 noise).
   Ogni testo è categorical-perfect per il cluster. Conseguenza:
   - LLM raggiunge ~0.98 P@5 perché ha visto N copie di ~4 stringhe per cluster
     → la classificazione testo→cluster è banale.
   - Anche concat_eq fa 0.95 perché 384 dim di sentence-embedding
     prendono dominanza sui ~14 dim numerici sporcati.
2. **Sector mapping resta bijettivo con cluster.** Cluster A → {NVDA, AVGO, AMD, ANET, VRT, SMCI} in {semiconductors, datacenter}. Il graph encoder usa proprio
   questo come feature → 0.995 P@5 perché sector→cluster è ~deterministico anche
   con std × 1.5. Non è "intelligenza" del graph, è leakage strutturale.
3. **std × 1.5 sposta solo i marginal, non crea overlap reale.** Le distanze
   cluster-cluster nelle distribuzioni di feature sono ancora >> std intra-cluster
   in molte dimensioni. Vedere: contrastive_v2 distance log mostra distribuzioni
   z-scored che si sovrappongono (quantili 20/50/80 = 1.58/2.47/3.47) ma il modello
   trova comunque positivi puliti.

## Cosa cambiare per L2 "vero"

L2 attuale = "easy noisy". Per ottenere L2 = "medium" servono almeno 2 di:

- **Pool di testi più ricco**: 20-30 template per cluster + variazioni
  generate (parafrasi). Riduce P@5 di LLM e concat di ~0.1–0.2.
- **Decoupling sector↔cluster**: ogni cluster pesca da pool ticker che
  contengono anche tickers di altri cluster (20% cross-pollination).
  Distrugge il vantaggio strutturale del graph.
- **Std × 2.0 invece di 1.5**: forza overlap reale. (Già pianificato in L3.)
- **Aumentare la frazione di NOISE oltre il 20%.**

## Contrastive v2 — diagnostica training su L2

```
RAW reaction euclidean:   mean=0.395 std=0.173, q20/50/80 = 0.244/0.377/0.533
Z-SCORED reaction:        mean=2.592 std=1.156, q20/50/80 = 1.577/2.469/3.471
thresholds: pos<=1.577 neg>=3.471  | 2235 pos pairs / 2235 neg pairs (20/20 ok)
per-anchor: pos 29.8 avg (min 0, max 69) | neg 29.8 avg (min 6, max 142)
valid anchors: 146/150 (4 senza positivi)
loss: 2.50 → 1.19 → 0.65 → 0.35 → 0.23 → 0.11 → 0.06 → 0.029 → ... → 0.003
```

Il training converge bene (loss 1000×). ReactCorr migliore di tutti (0.45).
Il trade-off vs P@5/Util@5 è chiaro: ottimizza esplicitamente la geometria delle
reazioni, **non** la cluster-fidelity. Su un dataset dove cluster ≈ reaction
(Level 1), il trade-off è quasi nullo. Su L2 inizia a vedersi.

## LLM v2 — il `dominant_driver` collassato

Distribuzione v2 (n=193 entries, mix L1+L2 testi):

```
event_polarity:      positive=88, negative=67, neutral=38           ok
surprise_magnitude:  moderate=83, minimal=83, large=27               ok (large under)
dominant_driver:     demand=97, macro=44, guidance=27, margins=25,
                     competitive=0, operational=0                    !!!
risk_asymmetry:      upside=88, downside=76, balanced=29             ok
cycle_phase:         mid=139, recovery=22, recession=21, early=11,
                     late=0                                          !!!
confidence_level:    3=78, 5=55, 4=39, 2=21                          ok
```

- `competitive` e `operational` mai usati: i testi non parlano di competizione
  o problemi operativi, e qwen2.5:7b non li "inventa". Bias dell'input più che
  del modello.
- `late_cycle = 0`: 17 testi unici, nessuno menziona late-cycle in modo esplicito.
  Default del modello → "mid". Da rivedere quando i testi diventano più vari.

## Decisione

Per la regola "Se P@5 rimane sopra 0.95, ferma e capisci prima": **fermo**.
Quattro encoder sopra 0.95 su L2. Necessario discutere se:

(a) accettare che L2 attuale è "easy noisy" e procedere a L3 (che ha std × 2
    e i HYBRID — distruttori naturali del graph leakage e della cluster
    fidelity testuale);

(b) regenerare L2 con i fix sopra (testi più ricchi, ticker cross-pollination)
    per avere uno step di difficoltà intermedio prima di L3.

Mia raccomandazione: **(a) procedere a L3**. Il fix dei testi è grosso (richiede
varianti generate o LLM-based augmentation) e i HYBRID di L3 attaccano già il
problema da angolo diverso (semantica X + macro Y → impossibile per encoder
"text-only" o "macro-only" risolverlo bene). Vediamo cosa succede.
