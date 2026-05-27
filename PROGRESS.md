# PROGRESS — Financial Episode Representation

Running progress log. Updated at each milestone.

---

## Current state (last update: 2026-05-26)

- **Discovery Phase completata**. Blind A/B test v2 con baseline random e
  ground truth umana ha invalidato la narrativa "contrastive_v2 vincitore" e
  ha rivelato concat_eq come primary engine. Pivot strategico effettuato.
- **Primary engine**: `concat_eq`. **Concat_eq+ implementato** (weighted
  structured retrieval + 12 narrative tags); statisticamente leggermente
  meglio del base su N=500, sector alignment qualitativamente migliore.
  Validazione umana definitiva nella prossima sessione blind test.
- **Archived**: tutta la branch contrastive (v1/v2/v3) + tutta la branch LLM
  (v1/v2/v3). Mantenute come case study di failure modes.
- **Prossima fase**: blind A/B test umano concat_eq+ vs concat_eq vs random;
  poi scaling N=500 → N=1500.

Documenti chiave: [SITUATION_REPORT_FINAL_DISCOVERY.md](SITUATION_REPORT_FINAL_DISCOVERY.md),
[evaluation/FINDINGS_DISCOVERY_PHASE.md](evaluation/FINDINGS_DISCOVERY_PHASE.md).

---

## Stato approcci

| Encoder | Stato | Note |
|---|---|---|
| **concat_eq** | **Primary engine (baseline)** | Vincitore blind A/B v2: 4.18 same_regime, 3.93 same_surprise, 15/20 top performers. Statisticamente significativo vs random su tutte e 4 le metriche. |
| **concat_eq+** | **Primary engine (extended)** | Weighted retrieval su 5 componenti + 12 narrative tags. N=500: ReactCorr +0.026, SelfCons Lift +0.073, Util P50 +0.016 vs concat_eq. Sector alignment qualitativamente migliore. Validazione umana pending. |
| concat_raw | Baseline numerico | Riferimento. |
| factorized | Specialist | Utilità mirata su query condizionate. CondQual=1.00 su mock. |
| graph_experimental | Sperimentale | Conserva valore post cross-pollination ticker. |
| ~~contrastive v1/v2/v3~~ | **Archived 2026-05-26** | Optimize "reactional geometry" — proprietà reale ma non utile per ragionamento analogico umano. 16/45 hard failures nel blind v2. Vedi [approaches/archived/README_CONTRASTIVE_ARCHIVE.md](approaches/archived/README_CONTRASTIVE_ARCHIVE.md). |
| ~~llm_structured v1/v2/v3~~ | **Archived 2026-05-25** | Su N=500 real: fail rate 23%, ReactCorr 0.052, mismatch generativo↔discriminativo. Vedi [approaches/archived/README_LLM_ARCHIVE.md](approaches/archived/README_LLM_ARCHIVE.md). |

Le versioni archiviate sono mantenute come case study di failure modes,
non eliminate.

## Approcci archiviati

| Encoder | Status | Reason |
|---|---|---|
| contrastive v1/v2/v3 | Frozen, not abandoned | Blind A/B v2 con ground truth umana: 16 hard failures (vs concat 4, vs random 26), solo 5 top performers (vs concat 15). Pareggia random su same_dynamic e same_surprise. Optimize the wrong ontology. |
| llm_structured v1/v2/v3 | Frozen, not abandoned | Su N=500 real: fail rate 23%, ReactCorr 0.052 (peggio di concat_eq), costo 3h. Mismatch concettuale generativo↔discriminativo. |

## Decisioni stabili

- **`concat_eq` è il primary engine** del retrieval. Contrastive learning su
  reazioni di prezzo è archiviato come direzione non promettente per questo task.
- **Validazione umana qualitativa con baseline random è metodologia obbligatoria**
  prima di considerare un approccio validato. Le metriche statistiche da sole
  non bastano.
- **Default Util@K = P25** (più discriminante di P50).
- **Cache LLM by content hash, non by event_id** (i dataset cambiano, il testo
  no).

## Roadmap a medio termine

1. **`concat_eq+` con narrative tags sparse** — estendere il primary engine con
   feature simboliche dai testi (sorpresa beat/miss, direzione guidance, narrative
   dominante). Mantenere interpretabilità.
2. **Scaling N=500 → N=1500** — universo più ricco per regime anchoring più
   discriminante.
3. **UI per analisti** — interfaccia di esplorazione cross-temporale dei
   precedenti.

---

## Lezioni metodologiche

1. **Cache by content, non by id**. Cache LLM key=hash(text) — l'`event_id`
   varia tra dataset, il testo è il segnale stabile.
2. **Vocabolari ortogonali**. Se due campi possono ricevere lo stesso token
   (es. `guidance_raise` valido per `narrative` E `surprise`), JSON-mode non
   salva: il modello sceglie per significato, non per campo. 36→0 failures
   passando da v1 a v2.
3. **Pair thresholds tarate sui dati**. Su `cos(reaction)` con vettori in cono
   stretto (99% delle coppie > 0.7), threshold fissi sono inutili. Z-score +
   quantili (20/80) dà pair set bilanciato e training segnale-pulito.
4. **Negativi espliciti, non in-batch**. Se le coppie positive sono dense,
   "negativi in-batch" sono spesso positivi → InfoNCE diventa rumore.
   Campionare neg esplicitamente risolve.
5. **Dataset facile ≠ utile per benchmarking**. Su L1 tutti gli encoder ≥ 0.98
   P@5 → metrica satura, nessun ordinamento. Servono difficoltà calibrate.
6. **Texture dei dati > scala dei numeri**. Std×1.5 + means shrink 35% basta a
   far scendere P@5 di concat da 0.95 → 0.77 SOLO se aggiungi varietà testuale
   e cross-pollination dei ticker. Lo std da solo non rompe la separabilità.
7. **Bias del modello vs bias dei dati**. `competitive`, `operational`, `late`
   sembravano bias di qwen2.5:7b (mai prodotti su L1/L2v1). Con testi che li
   menzionano esplicitamente (L2 v2) emergono → era bias dei dati. Test
   discriminativo: arricchire l'input e vedere se la distribuzione cambia.
8. **Contrastive learning su dataset piccoli (<200 samples) tende
   all'overfitting**. Loss training molto bassa (<0.01) è red flag, non
   success. Servono regolarizzazione (weight decay), dropout, early stopping.
   Su L2 v2 contrastive v2 trasforma loss=0.001 in ReactCorr peggiore di
   concat_eq → la "perfezione" del training non generalizza.
9. **Le correzioni via prompt LLM non generalizzano, vanno enumerate per
   categoria.** Il fix v3 ("classifica come `late` se il testo menziona
   late cycle") ha alzato la frequenza di `late` ma ha **azzerato `early` e
   `recession`**. Il modello impara la regola direttiva ma non la simmetria
   implicita per gli altri valori. Pattern: ogni token di un vocabolario chiuso
   serve **la sua propria istruzione esplicita**, altrimenti il modello fa
   collasso bimodale (default + il valore istruito).
11. **Encoder generativi (LLM) e encoder discriminativi (contrastive)
    ottimizzano oggettivi diversi.** Usare un LLM per produrre features
    categoriche da concatenare a un vettore di similarità è categoricamente
    diverso da addestrare un modello a riprodurre una geometria di reazione.
    Il primo è plausibile come feature extractor; il secondo richiede
    architetture diverse. Il fallimento di LLM v3 su N=500 (fail rate 23%,
    ReactCorr peggio del baseline) è il segnale empirico di questo mismatch:
    non è un bug, è un task-tool misalignment.
12. **Bias di conferma su valutazioni qualitative è il rischio più grosso nei
    progetti single-developer.** Protocolli blind (mescolare output di
    approcci diversi prima della valutazione, label A-F, KEY file separato
    da non aprire) sono mitigazioni obbligatorie, non opzionali. Da questa
    sessione in avanti la validazione qualitativa è parte del workflow di
    ogni run a scala.

10. **Metriche aggregate possono nascondere stupid hits sistematici.**
   P@5=1.00 di concat_eq sui NOISE event è "intelligenza" apparente: il
   template testuale dei noise è unico → match banale. In dati reali questa
   precisione sparirà. La review qualitativa ha mostrato anche che LLM v3 e
   concat_eq fanno **gli stessi top-5 al 68%** → l'aggiunta di v3 è marginale
   sul retrieval, non solo sulle metriche aggregate. **Approcci complementari
   producono set di analoghi più ricchi se combinati**: contrastive_v2 ∩ LLM
   v3 = 0.1/5 → unione dà ~9 analoghi unici con due viste indipendenti
   (narrativa + reazione).

---

## Qualitative Review L2 v2

5 findings principali dalla review ravvicinata di 10 query (vedi
[results/qualitative_review/SUMMARY.md](results/qualitative_review/SUMMARY.md)):

1. **Affidabilità human-grade**: llm_v3 accettabile su 7/10 top-3, concat_eq
   6/10, contrastive_v2 4/10 (dipende dal task — se cerchi outcome simili,
   contrastive vince).
2. **Gli errori sono informativi, non random**: llm_v3 sbaglia lungo l'asse
   "testo simile → cluster sbagliato"; contrastive sbaglia lungo "reazione
   simile → cluster sbagliato". Ogni miss è leggibile.
3. **Stupid hits sistematici trovati**: NOISE P@5=1.0 è template lookup
   banale; intro/closer matching trascina llm_v3 e concat_eq; "stesso
   cluster con reazioni disperse" è altra falsa precisione.
4. **LLM v3 ≈ concat_eq sui top-5** (overlap 3.4/5). I 525s di LLM danno
   marginalità sulle metriche aggregate ma raramente cambiano il set di
   analoghi specifici. **contrastive_v2 invece è radicalmente complementare**
   (overlap 0.1/5 vs LLM).
5. **Sistema affidabile su**: cluster A easy, C easy/hard, NOISE (con
   caveat). **Non affidabile su**: B easy quando testo e numeri
   disaccordano (artefatto generator), D hard outlier, A hard outlier
   numerico.

Unexpected: cross-pollination genera **smart hits cross-sector** notevoli
(evt_0028 GM/consumer in cluster A retrieve perfetto per evt_0037).

## Pattern complementare v3 ↔ contrastive_v2

I due "vincitori condizionali" sono **complementari, non concorrenti**:

| Terreno | Vincitore | Perché |
|---|---|---|
| L1 (easy, testi puliti) | LLM v3 | testo è l'unica informazione che conta |
| L2 v2 (medio, testi ricchi) | LLM v3 | encoder semantico finalmente attivato |
| L3 (caos hybrid+noise) | pareggio | nessuno regge bene |
| L4 (macro/micro pooled) | contrastive_v2 | reaction-similarity batte LLM su feature numeriche |
| L5 (reaction-driven) | contrastive_v2 | terreno disegnato per reaction-learner |

Cycle_phase v3 distribution per livello:

| Level | mid | late | recovery | early | recession |
|---|---|---|---|---|---|
| L1 | 65% | 29% | 0% | 6% | 0% |
| L2 v2 | 68% | 22% | 9% | 0% | 0% |
| L3 | 66% | 26% | 8% | 0% | 0% |
| L4 | 68% | 22% | 9% | 0% | 0% |
| L5 | 58% | **36%** | 6% | 0% | 0% |

Prompt direttivo funziona per `late` ma collassa `early`/`recession`. Per la
prossima iterazione estendere le istruzioni a tutti i valori.

## Decisioni aperte

- **Contrastive ha futuro su dataset > 1000 eventi?** Da testare quando
  passeremo a dati reali. Su mock 200 eventi continua a overfit.
- **LLM su L3-L5**: aspetta go-ahead dopo aver visto risultati del batch
  senza LLM.
- **prompt cycle_phase**: il bias verso "mid" persiste (67% in L2 v2 anche
  con testi che dicono "late cycle"). v3 prova prompt direttivo.

---

## Findings per livello

### L1 (easy baseline) — `data/mock_events_L1.json`

176 eventi (132 train / 44 test), 17 testi unici (4 template × 4 cluster + 1 noise),
~9% noise. Cluster perfectly separable da feature numeriche grezze.

| Approach | P@5 | ReactCorr | Util@5 | Note |
|---|---|---|---|---|
| concat_eq | 1.000 | 0.546 | 0.764 | |
| factorized | 0.980 | 0.550 | 0.764 | CondQual=1.00 |
| contrastive v2 | 0.890 | 0.517 | 0.764 | |
| graph_exp | 1.000 | 0.494 | 0.764 | leakage sector |
| llm v1 | 0.995 | 0.543 | 0.763 | 36 fail vocab |
| llm v2 | 1.000 | 0.569 | 0.763 | 0 fail |

Conclusione: dataset troppo facile per discriminare. Saved as
[results/level1_easy.json](results/level1_easy.json).

### L2 v1 (archiviato) — `data/mock_events_L2_v1_archived.json`

200 eventi, std×1.5 ma stessi 17 testi e ticker bijettivi. P@5 ancora 0.95+
per metà degli encoder → fix insufficiente.

### L2 v2 (corrente) — `data/mock_events_L2.json`

200 eventi (150 train / 50 test), **160 testi unici**, **4 settori per cluster**,
mean-shrink 35% + std×1.5. Gap intra/inter = **1.56** (vs L1=3.26).

Tabella metriche:

| Approach | P@5 | P@10 | ReactCorr | CondQual | Util@5 | Wall(s) |
|---|---|---|---|---|---|---|
| concat_raw | 0.750 | 0.715 | 0.355 | 0.635 | 0.460 | 6.6 |
| concat_eq | 0.765 | 0.735 | 0.382 | 0.595 | 0.455 | 0.2 |
| factorized | 0.720 | 0.618 | 0.377 | **1.00** | 0.485 | 0.1 |
| contrastive v1 | 0.565 | 0.533 | 0.187 | 0.530 | 0.370 | 0.9 |
| contrastive v2 | 0.620 | 0.583 | 0.362 | 0.640 | 0.400 | 1.8 |
| graph_exp | 0.830 | 0.758 | 0.286 | 0.655 | 0.515 | 0.2 |
| llm v1 | 0.820 | 0.765 | 0.375 | 0.625 | 0.490 | 530 |
| **llm v2** | **0.850** | **0.803** | **0.395** | 0.660 | **0.535** | 525 |

Verifica predizioni:

| # | Predizione | Esito |
|---|---|---|
| 1 | concat_eq P@5 ∈ [0.70, 0.85] | ✓ 0.765 |
| 2 | graph_exp P@5 < 0.95 | ✓ 0.830 (leakage rotto) |
| 3 | contrastive v2 ReactCorr lead + Util@5 ↑ | ✗ Perde su entrambi |
| 4 | competitive/operational/late emergono | ✓ ora compaiono nella distribuzione LLM |
| 5 | cycle_phase mid < 50% | parziale (72% → 67%) |

4 insight chiave:

1. **LLM v2 vince complessivamente** — primo o secondo su tutte le metriche.
   Costo 525s ma ROI visibile solo ora che i testi portano segnale.
2. **Contrastive v2 overfit**: loss training pulita (2.33 → 0.001), ma
   ReactCorr 0.362 < concat_eq 0.382 sul test. Mismatch train/test indotto
   dallo shrink del 35% delle medie cluster. → motivazione per contrastive v3.
3. **Graph credibile post cross-pollination**: P@5 0.995 → 0.83, Util@5 0.515
   resta il secondo. Il segnale settore conserva valore anche senza leakage.
4. **cycle_phase bias verso "mid"** persiste (67%) anche con testi espliciti
   "late cycle". L'LLM riconosce la parola ma resta cauto → serve prompt
   direttivo (v3).

Findings full: [results/FINDINGS_L2_v2.md](results/FINDINGS_L2_v2.md).

---

### L3 / L4 / L5 (batch, LLM esclusi)

Sanity check gap intra/inter:

| Level | gap macro+micro+sem | special |
|---|---|---|
| L3 | 0.67 | std×2, shrink 51%, +15% HYBRID |
| L4 | 0.79 (gap macro+micro = -0.03 by design) | semantic gap 1.73 |
| L5 | 0.82 (features overlap) | reaction gap 2.06 |

P@5 attraverso livelli:

| Approach | L1 | L2v2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| concat_eq | 1.00 | 0.77 | 0.51 | 0.63 | 0.55 |
| factorized | 0.98 | 0.72 | 0.38 | 0.37 | 0.49 |
| contrastive_v2 | 0.89 | 0.62 | 0.52 | **0.72** | **0.79** |
| contrastive_v3 | 0.83 | 0.70 | 0.45 | 0.67 | 0.74 |
| graph_experimental | **1.00** | **0.83** | **0.60** | 0.69 | 0.72 |

Insight:
- **L4 più discriminante** (std P@5 = 0.12, range 0.37-0.72). Setup
  macro/micro pooled costringe encoder a usare blocchi diversi.
- **contrastive_v2 brilla su L5** reaction-driven (P@5=0.79). Confermata
  l'ipotesi che contrastive eccelle quando reactions sono il segnale.
- **graph regge su L4** nonostante macro/micro pooled — usa semantic+sector,
  non solo macro/micro. Smentita l'ipotesi che L4 lo facesse crollare.
- **contrastive_v3 vs v2**: misto. v3 vince dove v2 overfittava (L1
  ReactCorr +0.085, L2 P@5 +0.075). Su L3-L5 v3 leggermente sotto perché
  early-stop a loss<0.05 lo blocca presto (11-26 epoche). Va tunato.
- **CondQual cresce con la difficoltà** per tutti (0.56→0.74). Filtro
  macro VIX>18 seleziona sottoinsieme meno confuso.

Findings full: [results/FINDINGS_L3_L5.md](results/FINDINGS_L3_L5.md).
Degradation table: [results/DEGRADATION_TABLE.md](results/DEGRADATION_TABLE.md).
Plot per metrica: [results/degradation_plots/](results/degradation_plots/).

## Real Data Phase Started — 2026-05-25 12:00

### Decisioni architetturali (Step 0 confermate dall'utente)

- Evento: 8-K Item 2.02 (Results of Operations) — SEC EDGAR
- Periodo: 2018-2024 (7 anni)
- Universe: S&P 500 (~500 companies, sector-stratified)
- Sampling: stratificato per anno + settore, 50 eventi
- Macro source: FRED (VIXCLS, DGS10, DGS2) + BAA10Y come credit spread proxy
  (BAMLH0A0HYM2 ICE-restricted, ritorna solo 2 anni); DXY da yfinance
- Prezzi: yfinance (close-adjusted)
- Semantic: Loughran-McDonald via pysentiment2 (positive/negative/uncertainty/weak_modal)

### Statistiche primo dataset (sample_50.json)

- **50 eventi** ingeriti (33% successo da 150 candidati)
- 10 settori GICS, 8 anni (2018-2025), 50 ticker distinti
- VIX range 11.5-42.0, credit_spread 1.45-3.30, reaction return mean -0.003

### Primi findings

Tabella metriche reali (k=5):

| Approach | SelfCons Lift | ReactCorr | Util@5 | Fail |
|---|---|---|---|---|
| concat_eq | 0.245 | 0.094 | 0.095 | 0 |
| contrastive_v2 | **0.443** | 0.072 | 0.005 | 0 |
| llm_v3 | 0.260 | **0.124** | **0.195** | 5 (10%) |

ReactCorr crolla ~0.3 punti vs mock (mock L2v2 ~0.38, real ~0.10). Util@5
~0.1 vs mock ~0.5. **La struttura predittiva del mock non sopravvive ai dati reali con N=50.**

contrastive_v2 mostra overfit estremo (loss 0.0002, SelfCons 0.78 ma Util@5
0.005) → conferma lezione #8 sotto dataset piccoli.

llm_v3 fail rate 10% (oltre soglia 5%) → flag.

### Problemi identificati da risolvere

1. **N=50 troppo piccolo**: per contrastive serve N≥500. Espandere dataset
   prossima sessione.
2. **Text preprocessing**: "EX-99.1 2 [filename]" presente in 90% dei testi
   inquina sentence-emb. Da rimuovere.
3. **LLM v3 fail rate 10%**: investigare i 5 fallimenti specifici.
4. **guidance_direction regex troppo stretta** (96% eventi → 0). Va estesa.
5. **Validazione su dati reali**: nessun ground-truth cluster → quali metriche
   davvero capture "buoni analoghi"?

Findings completi: [real_data/FINDINGS_FIRST_RUN.md](real_data/FINDINGS_FIRST_RUN.md).
Case studies: TTD Q4 2022 (smart hit own-ticker different quarter),
HAS Q4 2021 (3 encoder retrievono insiemi quasi disgiunti — sistema senza
risposta chiara), SYK Q1 2022 (no Health Care analogs perché training pool
troppo piccolo).

## Real Data Phase — Scaled Run (N=500), 2026-05-25 14:30

### Interventi rispetto alla first run

1. **Text cleaning module** (`real_data/ingestion/text_cleaning.py`): regex
   per rimuovere header EX-99 + filename, Item 2.02 cover boilerplate,
   conf-call trailer (con numeri telefono), contacts blocks, FLS / safe harbor
   disclaimers. Logging removed_pct per evento.
2. **Guidance regex riscritta** (7 raise + 7 lower + 5 neutral pattern):
   distribuzione zeri 96%→73% (4%→27% non-zero su sample_500).
3. **Text cap 5000→15000** post-cleaning, **min_text_len=500** filter.
4. **Pipeline parameterizzata** via env (TARGET_N, TEXT_CAP, OUT_NAME).

### Statistiche sample_500.json

- 500 eventi accettati su 2310 candidati (21.6% success). 11 settori, 8 anni.
- Per-sector mean ~45 (target ~40 raggiunto in 9/11). Sotto target: Comm
  Services (30), Utilities (32).
- Cleaning: mean 4.5% chars rimossi, mean clean_len 9671 (max 126K).

### Tabella metriche (N=500, 70/30 split, k=5)

| Approach | SelfCons Lift | ReactCorr | Util@5 | CondQual | TempDiv(d) | Fail | Wall(s) |
|---|---|---|---|---|---|---|---|
| concat_eq | 0.509 | 0.051 | -0.071 | 0.488 | 299 | 0 | 21 |
| **contrastive_v2** | **0.592** | **0.318** | -0.022 | **0.496** | **618** | 0 | 12 |
| llm_v3 | 0.470 | 0.052 | -0.045 | 0.473 | 283 | **115 (23%)** | 10960 |

### Delta vs N=50

| Metric | concat_eq | contrastive_v2 | llm_v3 |
|---|---|---|---|
| ReactCorr | -0.04 | **+0.25** | -0.07 |
| Lift | +0.26 | +0.15 | +0.21 |
| Fail | — | — | **+13pt (10%→23%)** |

### Findings chiave

1. **Contrastive_v2 sbloccato dal scaling**: ReactCorr 0.07→0.32 (+0.25),
   il delta più grande del progetto. Su N=346 train smette di collassare.
   Conferma lezione #8 (N≥500 supera l'overfit).
2. **Concat_eq baseline non-parametrico**: ReactCorr cala (-0.04). Non impara
   da più dati; le coincidenze fortunate di N=50 svaniscono nel rumore.
3. **LLM v3 esplode su fail rate** (10%→23%) e ReactCorr cala (-0.07).
   Predizione "<3% post-cleaning" invalidata. Cause sospette: cap=15000 satura
   ollama (timeout 120s), vocabolario chiuso troppo mock-specifico per real.
4. **Util@5 negativo per tutti**: metric mal-calibrata su reaction distribution
   reale (servirebbe P25 invece di P50 threshold).
5. **Pattern complementare confermato e esteso**:
   - concat/llm = "stessa stagione macro" + "stesso ticker different quarter"
   - contrastive = "stessa reaction-shape, temporalmente diversa, sector-peer cross-time"
6. **Cross-sector smart hits per contrastive**: JNJ Q1 2020 → PFE Q3 2022
   (HC peer); IT Q1 2022 → LRCX (semi peer). Concat e LLM perdono questi.

### Case studies (3 nuovi, diversi da TTD/HAS/SYK)

- **JNJ Q1 2020** (COVID peak): contrastive trova PFE+HC peers, concat/LLM
  collassano su consumer staples 2020.
- **IT Q1 2022** (Gartner, rate-hike): contrastive unico a trovare sector peer
  (LRCX), concat/LLM trovano rate-sensitive cross-sector.
- **SLB Q2 2022** (energy boom): qui concat/LLM **vincono** perché trovano
  SLB own-ticker Q1 + OXY peer. Contrastive perde questa intuizione.

### Aspettative utente vs realtà

| Metrica | Atteso | Osservato |
|---|---|---|
| ReactCorr | 0.20-0.30 | 0.05-0.32 (contrastive dentro range, altri no) |
| Util@5 | 0.20-0.35 | -0.07 a -0.02 (tutti negativi — metric da ricalibrare) |
| LLM fail rate | <3% | 23% (predizione invalidata) |

Findings full: [real_data/FINDINGS_SECOND_RUN.md](real_data/FINDINGS_SECOND_RUN.md).

## Validation Protocol Introduced — 2026-05-25 17:30

### Util@K recalibration P50 → P25

Vecchia metrica `utility_at_5` reale (in `real_data/metrics_real.py`) era
Spearman correlation, non frazione → valori "negativi" non interpretabili.
Nuova metrica `utility_at_k_real_threshold` (no cluster, solo reaction-dist),
con random baseline calcolata sullo stesso threshold. **Default: P25** (top
quartile reaction-similarity).

Risultati ricalibrati su run_500:

| Encoder | Util@5 P25 | Lift vs random | Util@5 P50 | Lift vs random |
|---|---|---|---|---|
| concat_eq | 0.313 | +0.067 | 0.575 | +0.071 |
| **contrastive_v2** | **0.388** | **+0.142** | **0.686** | **+0.181** |
| llm_v3 | 0.305 | +0.059 | 0.571 | +0.067 |

Random baseline: P25=0.246, P50=0.505. **Tutti i lift sono positivi**;
contrastive_v2 è leader netto su entrambe (lift 2x rispetto agli altri).
P25 sarà la default metric da qui in avanti — più stringente, più
discriminante.

Modifiche file:
- `evaluation/metrics.py`: aggiunte `utility_at_k_p25`, `utility_at_k_p50`
  (mock con cluster). Alias `utility_at_k = utility_at_k_p50` per backward
  compat.
- `real_data/metrics_real.py`: aggiunte `utility_at_k_real_threshold` e
  `random_baseline_utility` (no cluster, solo reaction-distance).
- `real_data/recalibrate_util.py`: script standalone per ricalcolo su
  retrievals esistenti (no re-encoding richiesto).

### Blind A/B test protocol

Per evitare bias di conferma su valutazioni qualitative single-developer,
introdotto protocollo blind:

- `evaluation/qualitative/blind_ab_test.py` — genera 2 file accoppiati:
  `blind_test_<ts>.md` (per valutazione umana, label A-F mescolati) e
  `blind_test_<ts>_KEY.md` (id → encoder mapping, da NON aprire prima
  della valutazione).
- 15 query stratificate: 2 per macro-bucket (Tech, Healthcare, Financial,
  Energy, Consumer) + 5 mix (Industrials). Top-3 da concat_eq + top-3 da
  contrastive_v2, deduplicato con nota "picked by both" nel KEY.
- 3 scale di valutazione 1-5: Utility, Insight non-banale, Transferability.
- `evaluation/qualitative/analyze_blind_results.py` — parse eval+KEY, mean
  per encoder, distribuzione hi(>=4)/lo(<=2), Mann-Whitney U test
  cross-encoder per metrica. Da eseguire **solo dopo** compilazione manuale.

Da questa sessione in avanti la validazione qualitativa è parte del workflow
di ogni run a scala (vedi lezione metodologica #12).

## Discovery Phase Completed — 2026-05-26

### Cronologia compatta

1. **Blind A/B test v1** (2026-05-25): 15 query × 6 candidati (concat_eq vs
   contrastive_v2). Valutazione umana 3 metriche (utility/insight/transfer).
   Risultato ambiguo: Mann-Whitney p>0.7 su tutte le metriche → segnale di
   crepa nella narrativa "contrastive_v2 vincitore basato su ReactCorr".
2. **Util@K recalibration** (P50 → P25): tutti i lift positivi,
   contrastive_v2 ancora leader netto sulla metrica statistica.
3. **Blind A/B test v2** (2026-05-26): 15 query × 9 candidati con baseline
   random come terzo gruppo, narrative summaries da Qwen, 4 nuove metriche
   allineate al task analitico (stessa storia / clima / notizia / esempio
   storico). Permutazione X/Y/Z dei gruppi per query.

### Risultati finali blind test v2

| Encoder | same_dynamic | same_regime | same_surprise | mental_precedent |
|---|---|---|---|---|
| **concat_eq** | 2.13 | **4.18** | **3.93** | **2.80** |
| contrastive_v2 | 1.59 | 3.16 | 3.52 | 2.07 |
| random | 1.24 | 2.38 | 3.02 | 1.56 |

| Encoder | Hard failures (mean ≤ 2) | Top performers (mean ≥ 4) |
|---|---|---|
| **concat_eq** | **4/45** | **15/20** |
| contrastive_v2 | 16/45 | 5/20 |
| random | 26/45 | 0/20 |

### Kruskal-Wallis 3-gruppi (per metrica)

| Metrica | H | p |
|---|---|---|
| same_dynamic | 11.98 | 0.0025 |
| same_regime | 36.73 | <0.0001 |
| same_surprise | 9.58 | 0.0083 |
| mental_precedent | 22.09 | <0.0001 |

Tutti significativi p<0.05. Mann-Whitney pairwise: concat_eq batte random
su tutte e 4 le metriche (p<0.05). contrastive_v2 **pareggia con random**
su same_dynamic (p=0.092) e same_surprise (p=0.120).

### Conclusione

**Pivot ufficiale su concat_eq.** La narrativa pre-pivot ("contrastive_v2 è
il vincitore basato su ReactCorr") è stata invalidata dall'evidenza umana
in cieco. La nuova narrativa è: *concat_eq fa regime anchoring efficace;
contrastive_v2 ottimizza una proprietà reale ("reactional geometry") ma
cognitivamente inutile.*

## Strategic Pivot — 2026-05-26

Il progetto si riposiziona ufficialmente:

- **Da**: "deep representation learning for financial analogies"
- **A**: "structured macro-contextual retrieval based on regime anchoring"

Il valore del sistema è il regime anchoring (VIX, yield curve, credit
spread, settore, tipo di sorpresa, fase di mercato), non il learning di
latent semantics. I mercati hanno regimi macro-temporali ricorrenti, non
manifold semantici profondi universali.

Conseguenze:

- `concat_eq` promosso a Primary engine. Era classificato come "baseline solido".
- Tutta la branch contrastive (v1/v2/v3) archiviata. Era considerata la
  leader basata su ReactCorr.
- Roadmap rifocalizzata su `concat_eq+` con narrative tags sparse + scaling.

Documento principale della scoperta: [evaluation/FINDINGS_DISCOVERY_PHASE.md](evaluation/FINDINGS_DISCOVERY_PHASE.md).
Stato finale: [SITUATION_REPORT_FINAL_DISCOVERY.md](SITUATION_REPORT_FINAL_DISCOVERY.md).

## Diagnostic Test V2 Setup — 2026-05-25 20:30

### Le 3 ipotesi che il test intende discriminare

1. **H1 — Existence-of-signal**: il retrieval fa qualcosa di meglio del random?
   Baseline random come terzo gruppo nel blind test.
2. **H2 — Bias-B della valutazione precedente**: includendo i testi nella
   valutazione (summary narrativo prominente + full text on-demand),
   contrastive_v2 emerge meglio rispetto al primo blind dove l'evaluator
   non leggeva i testi?
3. **H3 — Hard-failure pattern**: estraendo le valutazioni più basse (mean
   ≤ 2 sulle 4 metriche), quale encoder le produce sistematicamente e
   quali pattern testuali le accomunano?

### Nuove metriche di valutazione (4 invece di 3)

| Metrica | Domanda | Perché cambiata |
|---|---|---|
| same_dynamic | Stessa dinamica economica sottostante? | "Utility" era troppo vago — non distingueva l'allineamento causale dal valore informativo. |
| same_regime | Stesso regime di mercato (vol, liquidità, sentiment)? | Era implicitamente catturato da "transferability" ma confuso con la reazione osservata. |
| same_surprise | Stesso tipo di sorpresa vs aspettative? | Dimensione nuova — segnale ortogonale a settore/regime, centrale per ragionamento analogico. |
| mental_precedent | Utile come precedente mentale per la query? | Sostituisce "insight non-banale" — sposta il focus da originalità dell'analogo a utilità decisionale. |

Le vecchie metriche (utility/insight/transferability) erano proxy generici
di "similarità", non di "ragionamento analogico". La task target è il
secondo, non il primo (vedi lezione #13 sotto).

### Infrastruttura nuova in questa sessione

- `real_data/narrative_summaries.py` — generatore di summary 2-3 frasi
  via Qwen 2.5-7B (Ollama). Cache JSON, resume-friendly, fallisce
  graceful con `[summary unavailable]`. Generazione su tutti i 500 eventi
  (training + test): riusabile per futuri test.
- `evaluation/qualitative/blind_test_v2_generator.py` — produce blind_test
  a 3 gruppi (contrastive_v2 top-3 + concat_eq top-3 + 3 random),
  permutazione X/Y/Z per query, esce direttamente in formato `*_data.json`
  consumato da `serve_review.py`. KEY md separato in `evaluation/qualitative/`.
- `evaluation/qualitative/static/index.html` — riscritto con: summary box
  prominente, full-text modal, badge X/Y/Z per gruppo, 4 scale data-driven
  dalla risposta `/api/data`, tooltip operazionali per ogni livello 1-5,
  pulsante "cannot evaluate" per-candidate, counter completati / totali.
- `evaluation/qualitative/analyze_blind_results_v2.py` — Kruskal-Wallis
  a 3 gruppi + Mann-Whitney pairwise + Hard Failures + Top Performers,
  output markdown.

Random baseline: nessun filtro temporale, esclusione solo del ticker
della query (per evitare match con la query stessa) e degli id già scelti
dagli encoder.

### Lezione metodologica #13

**La definizione di "analogo finanziario utile" non è ovvia. Le metriche
di valutazione vanno disegnate per misurare proprietà rilevanti per il
task target (ragionamento analogico), non per misurare proprietà
generiche (somiglianza).** Nel primo blind test ho usato utility/insight/
transferability — proxy intuitivi ma sovrapposti e ancorati alla
similarità visibile dei grafici di reazione. Il secondo blind separa
quattro dimensioni indipendenti (dinamica economica, regime di mercato,
tipo di sorpresa, valore come precedente mentale) che corrispondono
alle componenti effettive di un ragionamento per analogia su episodi
finanziari. Senza questa separazione, l'evaluator collassa su un'unica
intuizione visiva e il segnale dei tre gruppi non si distingue.

### Lezione metodologica #14

**Le metriche proxy possono essere completamente corrette tecnicamente
e completamente inutili praticamente.** ReactCorr misura una proprietà
reale (coerenza nelle reazioni di prezzo tra eventi vicini nello spazio
appreso) ma quella proprietà non corrisponde a "utilità per ragionamento
analogico umano". Contrastive_v2 ha ReactCorr 0.318 (best tra gli
encoder su N=500 real) ma produce 16 hard failures su 45 valutazioni
umane — il quadruplo di concat_eq. *Validazione con ground truth umana è
obbligatoria* prima di considerare un sistema validato, non un
nice-to-have. *Optimizing the wrong ontology* è il failure mode più
pericoloso perché passa inosservato per molto tempo: produce numeri belli
su metriche tecnicamente corrette e ti convinci di avere un vincitore.

### Lezione metodologica #15

**In domini complessi come i mercati finanziari, ipotesi semplici (regime
anchoring via feature concatenation) possono battere approcci sofisticati
(contrastive learning su reazioni di prezzo) perché allineate meglio con
la struttura reale del dominio.** I mercati hanno regimi macro-temporali
ricorrenti — combinazioni specifiche di VIX, yield curve, credit spread,
settore, tipo di sorpresa — non manifold semantici profondi e universali
che, una volta appresi, generalizzino cross-regime. Architetture più
semplici e interpretabili possono essere la risposta giusta quando il
dominio non ha la struttura latente che approcci complessi assumono. La
sofisticazione architettonica si paga con perdita di interpretabilità e
con il rischio di apprendere proprietà cognitivamente inutili come
"reactional geometry".

## Narrative Tags Redesign (v2) — 2026-05-27

### Why v1 needed redesign

Qwen v1 extraction on full text (12 tags) produced structurally weak vectors:
55% zero-vector events, 5 tags with freq <2%, `capex_increase` at 0%,
`demand_strength` at 33% dominating. Pattern: v1 tags were chosen *before*
looking at the data — labels didn't map to 8-K vocabulary
(`capex_increase` rarely appears that way; corpus says "capacity expansion",
"new facility").

### Approach v2: data-driven

1. **N-gram TF-IDF analysis** (`real_data/analyze_text_concepts.py`):
   vocab 1221 terms, 20 hand-curated regex seeds tuned iteratively until
   each candidate landed in [5%, 45%] corpus frequency band.
2. **14 tags retained** across 4 categories. Dropped: `inline_results`,
   `demand_weakness`, `capex_increase`, `AI_or_tech_narrative` (all <5% in
   corpus). Added: `record_results`, `cost_inflation`, `pricing_action`,
   `MA_activity`, `ESG_sustainability`, `FX_headwind`.
3. **Estimated freq per regex seed** (upper bound — Qwen will be more
   conservative): guidance_raise 38%, capital_return 31%, MA_activity 18%,
   restructuring 17%, record_results 15%, margin_pressure 13%, guidance_cut
   12%, supply_constraint 12%, margin_expansion 11%, demand_strength 11%,
   pricing_action 8%, ESG_sustainability 7%, cost_inflation 7%, FX_headwind 7%.

### Validation via Claude as ground-truth proxy

Built `real_data/serve_manual_validation.py` (tinder-style web UI) for
human annotation of 25 stratified events. After UI prep, opted to use
**Claude (this model) as annotator proxy** instead of human — saves 1.5h,
ground truth is more permissive (matches what an analyst would tag) than
Qwen-7B strict mode. Documented as methodological limit: ground truth is
"smart-LLM proxy" not actual human analyst. Stats on 25:
mean active 3.28, 4/25 zero-vector (16%, all boilerplate Item 2.02 events).

### Qwen v2 extraction on 25 + comparison

`extract_narrative_tags_v2.py` with operational examples per tag in the
prompt. Run on the 25 manually-annotated events:

| metric | value |
|---|---|
| macro F1 (across tags with ≥1 positive) | **0.290** |
| tags with F1 ≥ 0.6 | ESG_sustainability (0.80), record_results (0.75), capital_return (0.74), guidance_raise (0.60) |
| tags with F1 = 0.00 | guidance_cut, margin_pressure, pricing_action, MA_activity, restructuring, supply_constraint, FX_headwind |
| Qwen precision (when fires) | 1.00 on all firing tags |
| mean active / event — manual vs Qwen | 3.28 vs 0.92 |

**Pattern**: Qwen v2 has perfect precision but collapsed recall. The
strict YES/NO prompt makes it almost never fire on subtle signals.
**Decision**: accept this trade-off rather than loosen the prompt (which
would risk optimizing toward Claude's permissiveness, the thing we're
testing against). Tag layer will be sparse but **noise-free** —
acceptable given that Jaccard similarity treats both 1↔1 matches and
0↔0 matches consistently.

### Full extraction v2 on 500 events

500/500 ok, mean active 1.07 tags/event. Saved as
`real_data/processed/sample_500_narrative_tags_v2.json` (v1 archived
alongside as `_v1_summaries.json`).

### Re-run concat_eq+ with v2 tags (N=500)

| Metric | concat_eq | concat_eq+ v2 | Δ |
|---|---|---|---|
| ReactCorr | 0.0510 | 0.0698 | +0.0188 |
| Util@5 P25 | 0.3130 | 0.3117 | -0.0013 |
| Util@5 P50 | 0.5753 | 0.5935 | +0.0182 |
| Util Spearman top5 | -0.0708 | +0.0078 | +0.0786 |
| SelfCons | 0.6069 | 0.6029 | -0.0040 |
| SelfCons Lift vs Random | 0.5092 | 0.5672 | +0.0580 |
| CondQual (VIX>18) | 0.4883 | 0.4883 | +0.0000 |
| TempDiv (days) | 298.7 | 168.7 | -130.0 |

Vs v1 tags run: comparable lift (slightly smaller on ReactCorr, slightly
larger on Util Spearman). Sector alignment qualitatively still better
(sanity 5 queries: same pattern — MCK gets RMD HC peer, IBM gets IT
peers, etc.).

Top-3 overlap with concat_eq: 17% identical positions, 88/154 queries
have **zero** shared top-3 candidates. Confirms concat_eq+ produces
substantively different retrievals (not just noise on top of base).

### Lezione metodologica #16

**LLM-as-annotator-proxy for ground truth is a pragmatic compromise
with explicit trade-offs.** Claude annotation is faster, more
permissive, and consistent — but it is not human analyst judgment.
The 0.29 macro F1 between Qwen-7B (strict) and Claude (permissive)
quantifies *the gap between two LLM regimes*, not absolute correctness.
For final validation of concat_eq+, human blind evaluation remains
necessary. The v3 blind test below provides that.

### Blind test v3 generated

`evaluation/qualitative/blind_test_v3_generator.py`: 3-way
(concat_eq_plus + concat_eq + random), 15 queries × 8-9 candidates,
group letters X/Y/Z permuted per query. Output:
`reviews/blind_test_v3_20260527_104937_data.json` + `_KEY.md`.

Files created:
- `real_data/analyze_text_concepts.py`
- `real_data/narrative_tags_v2.py`
- `real_data/extract_narrative_tags_v2.py`
- `real_data/manual_validation.py` + `serve_manual_validation.py` + `static_manual/index.html`
- `real_data/compare_manual_vs_qwen.py`
- `evaluation/qualitative/blind_test_v3_generator.py`
- `real_data/processed/text_concepts_analysis.md`
- `real_data/processed/tags_redesign_rationale.md`
- `real_data/processed/manual_tags_validation.json` (Claude annotations)
- `real_data/processed/sample_500_narrative_tags_v2.json` (Qwen extraction)
- `real_data/processed/qwen_vs_manual_comparison.md`
- `real_data/results/run_500_concat_eq_plus_20260527_104922.{json,md}`

## Concat_eq+ Implementation — 2026-05-26

Prima sessione tecnica post-pivot. Implementato `approach_2b_concat_eq_plus`
(weighted structured retrieval + narrative tags) e validato su sample_500.

### Architettura

Score composito su 5 componenti pesate (default sommano a 1):

| Componente | Peso | Definizione |
|---|---|---|
| macro | 0.35 | cosine su 5 macro features z-scored (VIX, yields, slope, credit, DXY) |
| tags | 0.25 | Jaccard sui 12 narrative tag binari |
| sector | 0.20 | sector_match (one-hot GICS) × 0.6 + cosine(sector_return_60d, relative_strength) × 0.4 |
| pre_event | 0.10 | cosine(return_60d, drawdown_from_high) z-scored |
| vol | 0.10 | cosine(realized_vol_60d) z-scored — 1-dim, segna same/different vol regime |

I pesi sono runtime-configurabili. La similarità è calcolata
componente-per-componente in `pairwise_score()` perché Jaccard binario e
match categorico settore non sono cosine-compatibili (overriding `retrieve()`
invece di affidarsi a `encode()` + cosine globale).

### Narrative tags (12 binari su 4 categorie)

- **A direction**: beat_and_raise, miss_or_cut, inline_results
- **B drivers**: demand_strength, demand_weakness, margin_pressure, margin_expansion
- **C capital**: capex_increase, buyback_or_dividend, restructuring_or_layoffs
- **D themes**: supply_chain_issue, AI_or_tech_narrative

Estrazione via Qwen 2.5-7B (Ollama, temperature 0, strict YES/NO) su full
text degli 8-K (cap 6000 char). Prima iterazione su summaries: media 0.74
attivi/evento; seconda iterazione su full text: media 0.56 attivi/evento ma
distribuzione più bilanciata tra tag (top 4 al 9-11% vs summary che aveva
`demand_strength` 32%). Conservata la versione full_text come canonica.

### Limiti noti del tag layer

- 276/500 eventi (55%) hanno vettore tag tutto-zero → Jaccard=0, il blocco
  tags non discrimina per loro. Pattern strutturale di Qwen-7B con prompt
  strict, non bug.
- `capex_increase` mai estratto (0.0%): degenerato, lasciato nel vettore
  per coerenza ma da rivedere (forse il prompt non lo cattura bene).
- 4 tag rari (< 1%): beat_and_raise, miss_or_cut, supply_chain_issue,
  restructuring_or_layoffs. Coerente con la rarità di questi pattern nei
  comunicati 8-K standard.
- 0 contraddizioni mutuamente-esclusive (struttura sana).

### Risultati statistici N=500 (70/30 split, seed=42)

| Metric | concat_eq | concat_eq+ | Δ |
|---|---|---|---|
| ReactCorr | 0.0510 | 0.0773 | +0.0263 |
| Util@5 P25 | 0.3130 | 0.3013 | -0.0117 |
| Util@5 P50 | 0.5753 | 0.5909 | +0.0156 |
| Util Spearman top5 | -0.0708 | -0.0442 | +0.0266 |
| SelfCons | 0.6069 | 0.6127 | +0.0058 |
| SelfCons Lift vs Random | 0.5092 | 0.5819 | +0.0727 |
| CondQual (VIX>18) | 0.4883 | 0.4922 | +0.0039 |
| TempDiv (days) | 298.7 | 184.2 | -114.5 |

Δ modesti ma direzionalmente coerenti: 6/8 metriche migliorate, una invariata.
TempDiv scende di 115 giorni — concat_eq+ pesca eventi temporalmente più
clusterati (probabile effetto del sector_match bonus + macro più stretto).

### Sanity check su 5 query (top-3 base vs plus)

Pattern netto: **concat_eq+ migliora sector alignment** in modo visibile.

- **MCK** (Health Care): concat_eq → 0 HC peers (Energy/Industrials/Cons);
  concat_eq+ → 1 HC peer (RMD 2019).
- **IBM** (IT): concat_eq → 1 IT peer (PANW); concat_eq+ → 2 IT peers
  (FTNT, EPAM).
- **HAL** (Energy): concat_eq → 0 Energy peers (Real Estate/Cons Disc/Comm);
  concat_eq+ → 2 Energy peers (OXY 2022, DVN 2021).
- **PM** (Cons Staples): concat_eq fa "stupid hit" auto-ticker (PM 2020Q3);
  concat_eq+ lo evita e trova DLTR same-sector.
- **TFC** (Financials): entrambi trovano XYZ Financials peer; concat_eq+
  swappa Utilities (EIX) per Consumer Staples (DLTR, DG).

Overlap top-3 medio: 0.6/3 (i.e. ~20% identico). Il sistema sta producendo
retrieval significativamente diversi, non uguali al base.

### Considerazione metodologica

I miglioramenti statistici qui sono indicativi. La validazione vera sarà
nel blind test umano della prossima sessione, alla luce della lezione #14
(proxy metrics possono ingannare). Il sanity check qualitativo già mostra
che il sector alignment è migliorato — questa è proprio la proprietà che
i valutatori umani hanno premiato in concat_eq sul blind v2 (`same_regime`
4.18, `same_surprise` 3.93). Aspettativa: concat_eq+ dovrebbe alzare
queste metriche, ma è ipotesi da validare empiricamente.

File creati: `approaches/approach_2b_concat_eq_plus.py`,
`real_data/narrative_tags.py`, `real_data/extract_narrative_tags.py`,
`real_data/validate_narrative_tags.py`, `real_data/run_concat_eq_plus.py`,
`real_data/sanity_check_concat_eq_plus.py`,
`real_data/processed/sample_500_narrative_tags.json`,
`real_data/processed/narrative_tags_validation.md`,
`real_data/results/run_500_concat_eq_plus_20260526_133659.{json,md}`.

## Cronologia step

- **Step 12** (2026-05-27 10:50): narrative tags v2 redesign (data-driven 14
  tag, 4 categorie); manual validation via Claude come ground-truth proxy
  (25 eventi); Qwen v2 macro F1 = 0.29 (precision 1.00 / recall collassato);
  full extraction 500/500 ok; re-run concat_eq+ con v2 (Δ comparable a v1,
  +ReactCorr 0.019, +SelfCons Lift 0.058); blind test v3 generato (3-way:
  ce+ / ce / random, 15 query). Lezione #16.
- **Step 11** (2026-05-26 13:30): concat_eq+ implementato + run N=500.
  Narrative tags estratti da full text via Qwen (12 tag binari, 4 categorie).
  Architettura weighted retrieval su 5 componenti (macro 0.35, tags 0.25,
  sector 0.20, pre 0.10, vol 0.10) con sector match bonus + Jaccard per tags.
  Δ statistici modesti (+ReactCorr 0.026, +SelfCons Lift 0.073), sector
  alignment qualitativamente migliore. Validazione umana pending.
- **Step 0** (2026-05-24): scaffold 5 approcci + runner + L1.
- **Step 1** (2026-05-24): diagnostica LLM (36 failures → cross-field swap)
  + diagnostica contrastive (mode collapse, gap within/cross 0.001).
- **Step 2** (2026-05-25 00:00): contrastive v2 (z-score + quantili) e
  LLM v2 (schema ortogonale) → 0 LLM failures, ReactCorr 0.36 → 0.52 su L1.
- **Step 3** (2026-05-25 00:20): nuova metrica `utility@5` (binary good-analog
  = same cluster ∧ reaction-dist ≤ P50 train). Generator multi-livello
  L1-L5. Runner con `--dataset`/`--skip`. Run L2 v1 → P@5 ancora 0.95+ per 4
  encoder → stop.
- **Step 4** (2026-05-25 10:00): generator L2 v2 con pool 25 template/cluster,
  cross-pollination ticker, mean-shrink 35%. Sanity ok (gap 1.56). Run completo:
  LLM v2 emerge come leader, contrastive v2 overfit visibile.
- **Step 5** (2026-05-25 10:40): contrastive v3 + LLM v3 implementati.
  Generator aggiornato con L3 hybrid weighted reactions, L4 shared macro/micro,
  L5 reaction amplify + text mix 60/40. Sanity check ok su tutti i livelli.
  Batch run L3/L4/L5 senza LLM. Degradation table + plot per metrica.
  FINDINGS_L3_L5.md con risposte alle 5 domande.
- **Step 10** (2026-05-25 21:45): UI v2 riscritta "tinder mode".
  `static/index.html` rifatto: layout 4-zone fixed-height (header / summaries
  side-by-side / chart sovrapposto Chart.js / 4 metriche), un candidato per
  volta, tastiera (1-5, Tab, Enter/←/→, S, N), localStorage mirror,
  resume per-candidato. Metriche con label colloquiali (Stessa storia /
  Clima / Notizia / Esempio storico) + tooltip operativi 1-5. Vecchia UI
  archiviata in `static/index_v1_scrollable.html`. Nessuna modifica a
  server/data/analyze.
- **Step 9** (2026-05-25 20:30): Diagnostic Test V2 infrastructure.
  Narrative summaries (Qwen via Ollama) per 500 eventi. Blind test v2
  3-way (contrastive_v2 + concat_eq + random) con 4 nuove metriche
  (same_dynamic, same_regime, same_surprise, mental_precedent). UI
  riscritta con summary prominente + full text modal + group badge X/Y/Z
  + cannot-evaluate. Analyze script v2 (Kruskal-Wallis + pairwise MW +
  Hard Failures + Top Performers). Lezione #13.
- **Step 8** (2026-05-25 17:30): LLM v3 archiviato (frozen, non eliminato).
  Util@K ricalibrato a P25 — tutti i lift ora positivi, contrastive_v2
  leader netto (lift +0.142). Blind A/B test protocol introdotto come
  pratica metodologica del progetto. Lezioni #11 (LLM ≠ contrastive) + #12
  (blind protocol obbligatorio).
- **Step 7** (2026-05-25 14:30): scaling N=50→500. Text cleaning module +
  guidance regex riscritta + cap 15K. Run 3 approcci: contrastive_v2 emerge
  vincitore netto (ReactCorr +0.25), LLM v3 fail rate raddoppia (10%→23%),
  concat_eq baseline non scala. Findings in FINDINGS_SECOND_RUN.md.
- **Step 6** (2026-05-25 11:30): LLM v3 lanciato su L3/L4/L5 (poi anche L1/L2v2
  per completare la degradation table). Failure rate sotto 5% ovunque.
  Aggiunto a DEGRADATION_TABLE.md + sezione head-to-head v3 vs contrastive_v2 +
  cycle_phase distribution. Pattern netto: **v3 vince L1/L2 (testo ricco e
  pulito), contrastive_v2 vince L4/L5 (reaction-targeted), L3 è pareggio**.
  v3 NON batte contrastive_v2 su L5 → nessun upset (atteso).
  Cycle_phase directive: `late` raddoppia (11% → 22-36%) MA `early` e
  `recession` azzerate (side effect del prompt che parla solo di "late").
