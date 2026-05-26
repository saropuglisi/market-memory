# FINDINGS — Second Real-Data Run (N=500)

Date: 2026-05-25. Dataset: 500 eventi 8-K Item 2.02 dal S&P 500, 2018-2025.
Train/test split 70/30 stratificato per settore (346 / 154), seed=42.

---

## Changes vs first run

1. **Text cleaning module** (`real_data/ingestion/text_cleaning.py`): rimuove
   header `EX-99.x [filename]`, Item 2.02 cover boilerplate, conference call /
   webcast trailer (con numeri di telefono), contacts blocks,
   forward-looking statements + safe harbor disclaimers. Pattern hit aggregato
   su 500 eventi: header_ex99 ~80%, conf_call_trailer ~30%, item_202 cover ~5%.
2. **Guidance regex riscritta** (`semantic_features.py`): da 1 pattern per direzione
   a 7 raise / 7 lower / 5 neutral. Coverage di "we expect/anticipate/forecast",
   forme passive ("guidance is X"), quantificatori direzionali, "at the high/low
   end of midpoint", "exceed/miss expectations".
3. **Text cap** alzato da 5000 → 15000 char post-cleaning. Mean clean_len=9671,
   cap raramente vincolante ma include ora guidance/outlook sections che prima
   erano oltre limite.
4. **Filtro min_text_len=500** post-cleaning: scarta candidati con press release
   vuoto/troppo corto (era ~20% del primo sample).

## Dataset N=500

- 500 eventi accettati su 2310 candidati (success rate 21.6%; 332 falliti,
  principalmente per testo cleaned <500 chars o macro/micro/reaction mancante).
- **8 anni**: 2018=41, 2019=66, 2020=77, 2021=67, 2022=79, 2023=70, 2024=86, 2025=14
- **11 settori GICS** (target era ≥12 — uno mancante perché Telecom è
  classificato dentro Communication Services):
  Consumer Staples=58, Health Care=57, Consumer Disc=51, Industrials=50,
  Real Estate=48, Financials=46, Materials=45, Energy=43, IT=40, Utilities=32,
  Comm Svcs=30
- Per-sector mean ~45 events (target era ~40). **Sotto target** solo
  Comm Services (30) e Utilities (32).
- VIX 10.85-41.38 (mean 20.1), yield_10y 0.52-4.98, credit_spread 1.40-3.37
- Cleaning: mean 4.5% chars rimossi (range 0-97%), mean clean_len 9671 (range 503-126153)
- Guidance distribution: 73% zero, 23% +1 (raise), 4% -1 (lower) — vs primo run
  96% / 4% / 0%

## Tabella metriche comparativa N=50 vs N=500 (k=5)

| Approach | Metric | N=50 | N=500 | Δ |
|---|---|---|---|---|
| **concat_eq** | SelfCons Lift | 0.245 | **0.509** | +0.264 |
| concat_eq | ReactCorr | 0.094 | 0.051 | **−0.043** |
| concat_eq | Util@5 | 0.095 | −0.071 | −0.166 |
| concat_eq | CondQual | 0.448 | 0.488 | +0.040 |
| concat_eq | TempDiv(d) | 349 | 299 | −50 |
| concat_eq | Fail | 0 | 0 | — |
| **contrastive_v2** | SelfCons Lift | 0.443 | 0.592 | +0.149 |
| contrastive_v2 | ReactCorr | 0.072 | **0.318** | **+0.246** |
| contrastive_v2 | Util@5 | 0.005 | −0.022 | −0.027 |
| contrastive_v2 | CondQual | 0.400 | 0.496 | +0.096 |
| contrastive_v2 | TempDiv(d) | 587 | 618 | +31 |
| contrastive_v2 | Fail | 0 | 0 | — |
| **llm_v3** | SelfCons Lift | 0.260 | 0.470 | +0.210 |
| llm_v3 | ReactCorr | 0.124 | 0.052 | **−0.072** |
| llm_v3 | Util@5 | 0.195 | −0.045 | **−0.240** |
| llm_v3 | CondQual | 0.362 | 0.473 | +0.111 |
| llm_v3 | TempDiv(d) | 364 | 283 | −81 |
| llm_v3 | **Fail rate** | 10% (5/50) | **23% (115/500)** | **+13pt** |

## Risposte alle domande della sessione

### Le metriche migliorano con scaling + text cleaning?

**Mista, con un winner netto e due regressioni inaspettate.**

- **Contrastive_v2 esplode**: ReactCorr 0.07→0.32 è il delta più grande
  osservato nell'intero progetto. Su N=346 train il modello smette di
  collassare. Conferma diretta della lezione #8: contrastive richiede N≥500.
  Loss training scende a 0.0009 (ancora bassa) ma stavolta generalizza — il
  SelfCons Lift sale a 0.59 e ReactCorr in proporzione. **Best ReactCorr +
  best Lift + best CondQual + miglior diversità temporale.**
- **Concat_eq peggiora su ReactCorr** (0.094→0.051). Plausibile: in N=50
  pochi cluster naturali (settori×anni) producevano coincidenze fortunate;
  con N=500 il rumore sentence-emb domina. Concat_eq è baseline
  non-parametrico, non *impara* dai dati. SelfCons Lift sale solo perché
  random baseline cresce.
- **LLM v3 peggiora su tutto tranne Lift e CondQual**: ReactCorr 0.124→0.052,
  Util@5 0.195→−0.045 (dramma). E fail rate raddoppia.

### LLM fail rate scende sotto 3% come predetto?

**No, raddoppia: 10%→23% (115/500).** Predizione invalidata.

Cause probabili (da investigare in prossima sessione):
- **Cap 15000 vs 5000**: testi 3x più lunghi sovraccaricano context del modello
  e producono più output malformato o timeout.
- **Forward-looking statements rimosso**: paradossalmente potrebbe aver tolto
  language di tipo che il modello sa parsare ("we anticipate", "outlook") —
  ironia perché era anche il signal per guidance_direction.
- **Variabilità lessicale reale**: il vocabolario chiuso v3 (cycle_phase,
  driver, surprise) è tarato sul mock; molti press release reali non
  contengono i termini-target → output fuori schema → fail.

Pattern timeout: 11 sui primi ~250 sono `Read timed out (read timeout=120)`
— ollama satura su testi lunghi (>10K char). Soluzioni candidate: chunking del
testo, prompt che chiede risposta su prima sezione, modello quantizzato più
piccolo.

### Cross-sector retrieval funziona meglio con coverage maggiore?

**Sì per contrastive_v2, no per gli altri due.** Vedi case study JNJ COVID
sotto — contrastive trova PFE (sector peer corretto) mentre concat e LLM
collassano sullo stesso set di consumer staples 2020.

### Ci sono pattern nuovi visibili che N=50 nascondeva?

1. **Contrastive_v2 era artificialmente debole** per dataset-size, non per
   limitazione intrinseca. Su N=500 è il chiaro leader. Smentita parziale
   della lezione #8 (vale ancora per N<200, ma ≥500 supera).
2. **LLM v3 è fragile su testi lunghi reali.** Su mock con testi 200-400
   token lavorava. Su real con 10K+ char il fail rate diventa proibitivo.
3. **Util@5 negativo per tutti i 3 approcci**: indica che la metrica non
   discrimina su distribuzione reale di reazioni. Probabilmente serve
   re-calibrazione (P25 invece di P50 threshold).
4. **Convergenza concat_eq ≈ llm_v3** su molti retrieval (vedi JNJ sotto:
   4/5 overlap). LLM aggiunge marginalità sulle metriche aggregate ma raramente
   cambia il set di analoghi.
5. **Contrastive_v2 retrieve più temporalmente diversi** (618 giorni di
   spread vs 283-299 per gli altri). Implica: contrastive trova
   "stesso tipo di reazione" indipendentemente da quando; concat/LLM trovano
   "stesso periodo" — privilegiano vicinanza temporale.

---

## Case study 1 — JNJ Q1 2020 (Health Care, COVID stress)

Query: Johnson & Johnson, 14 aprile 2020. VIX 37.8 (massimo COVID), reaction
30d = −0.001 (neutro nonostante macro stress).

| Encoder | Top-5 (ticker / sec / reaction / date) | TempDiv | Sector match |
|---|---|---|---|
| concat_eq | TSCO/CD +0.289 2020-04, AAPL/IT +0.156 2020-04, CL/CS +0.064 2020-05, LIN/Mat +0.131 2020-05, CLX/CS +0.079 2020-05 | tight (1 mese) | 0/5 HC |
| llm_v3    | TSCO/CD +0.289 2020-04, LIN/Mat +0.131 2020-05, AAPL/IT +0.156 2020-04, CL/CS +0.064 2020-05, CLX/CS +0.079 2020-05 | tight (1 mese) | 0/5 HC |
| contrastive_v2 | ETR/Util +0.180 2022-02, **PFE/HC +0.144 2022-11**, MNST/CS +0.116 2021-02, COST/CS +0.112 2020-09, FAST/Ind +0.060 2021-04 | wide (~2 anni) | **1/5 HC** |

**Verdetto**: concat e llm retrievono **4/5 stessi eventi** (TSCO, AAPL, CL, CLX) —
classico cluster "COVID-era safe assets". Sensato come "cosa stava succedendo
intorno" ma zero analoghi HC. Contrastive trova **PFE in 2022**, primo
sector-peer rilevante in tutti i top-5, e diversifica temporalmente. Per la
domanda "a cosa assomiglia JNJ Q1 2020 dal punto di vista del *playbook di
reazione*?" contrastive vince. Per "cosa succedeva nell'aria intorno a quel
trimestre?" concat/LLM rispondono meglio. **Conferma complementarietà.**

## Case study 2 — IT Q1 2022 (Gartner, IT in macro stress)

Query: Gartner, 3 maggio 2022. VIX 29.3 (post Fed rate-hike), reaction 30d =
−0.161 (calo significativo).

| Encoder | Top-5 |
|---|---|
| concat_eq | ABNB/CD, LYV/Comm, EQIX/RE, WSM/CD, CPAY/Fin |
| llm_v3 | ABNB/CD, **HBAN/Fin**, EQIX/RE, MRSH/Fin, MGM/CD |
| contrastive_v2 | ARE/RE, SLB/Energy, VRTX/HC, KIM/RE, **LRCX/IT** |

**Verdetto**: ancora una volta solo contrastive trova un sector-peer
(**LRCX, semiconductor equipment**). Le reazioni dei suoi top-5 vanno da
−0.049 a +0.103 — distribuite, non clusterizzate. Concat/LLM convergono su
real estate + consumer discretionary (settori che hanno sofferto stesso macro
shock 2022). LLM aggiunge HBAN e MRSH (banche, sensibili al rate-hike) — non
sbagliato. Per "a cosa fa pensare Gartner crollo del 16% in macro stress
2022?" tutti e 3 propongono narrative coerenti ma ortogonali:
- **Concat/LLM**: "asset rate-sensitive dello stesso shock"
- **Contrastive**: "altre aziende con pattern reaction simile, anche fuori
  shock specifico"

## Case study 3 — SLB Q2 2022 (Schlumberger, Energy boom)

Query: Schlumberger, 22 luglio 2022. VIX 23, oil price boom, reaction 30d =
+0.086 (positivo, controcorrente vs equity market).

| Encoder | Top-5 |
|---|---|
| concat_eq | FCX/Mat +0.381, BAX/HC −0.097, **SLB/Energy +0.041** (Q1!), CIEN/IT −0.130, **OXY/Energy +0.384** |
| llm_v3 | FCX/Mat +0.381, BAX/HC −0.097, **SLB/Energy +0.041**, VEEV/HC +0.003, XYZ/Fin +0.160 |
| contrastive_v2 | CAT/Ind +0.147, TSLA/CD −0.061, CPAY/Fin −0.128, EIX/Util +0.096, CF/Mat +0.007 |

**Verdetto**: questa volta concat/LLM **vincono qualitativamente** — entrambi
trovano SLB stesso del Q1 precedente (stesso ticker different quarter pattern
già osservato nel primo run) e concat aggiunge OXY (energy peer in stesso
trend +0.384). Contrastive trova reazioni miste con CAT, TSLA, CPAY — più
diversificato per settore ma meno coerente narrativamente. SLB Q2 2022 è un
caso dove la **continuità temporale (own-ticker + sector peer) è il segnale
giusto**. **Contrastive perde questa intuizione** perché non guarda il
testo abbastanza da catturare "stessa azienda".

---

## Sintesi pattern complementare (esteso post-N=500)

| Quando vuoi... | Usa | Perché |
|---|---|---|
| Stesso ticker / sector peer ovvio | concat_eq o llm_v3 | sentence-emb cattura ticker name + sector boilerplate |
| Stessa "stagione" macro | concat_eq | retrieve temporalmente vicini |
| Reazione simile, settore qualunque | contrastive_v2 | euclidean su reaction vector |
| Sector-peer fuori dal trimestre | contrastive_v2 | l'unico che diversifica temporalmente |
| Robust system al fail | concat_eq | 0 fail vs LLM 23% |

LLM v3 in questa run **non emerge come vincitore su nessun asse**: stessa
qualità di concat_eq sui top-5 (overlap 4/5 ricorrente), ReactCorr peggiore
di entrambi gli altri, e fail rate inaccettabile. **Senza fix del fail rate
non è production-ready su dati reali.**

## Problemi aperti / prossime sessioni

1. **LLM v3 fail rate 23%**: investigare campioni falliti, valutare:
   - Chunking del testo prima del prompt (analizzare prime 3000 char invece di 15K)
   - Modello più capace (qwen2.5:14b al posto di 7b)
   - Validation più tolleranti (accept partial outputs)
2. **Util@5 negativo**: ricalibrare metric. P50 reaction-distance threshold
   produce "good analog" troppo stretto per real data.
3. **Stesso-ticker-different-quarter** è il pattern più ricorrente sui top-5
   reali — vale la pena explicitarlo come baseline trivial?
4. **Contrastive_v2 scaling oltre 500**: provare N=1000 per vedere se ReactCorr
   continua a crescere o satura.
5. **Cross-sector retrieval di contrastive**: produce smart hits (JNJ→PFE,
   IT→LRCX) ma anche miss visibili (SLB perde OXY). Studiare in che condizione
   uno vs l'altro.

## Files

- `real_data/processed/sample_500.json` — 500 eventi
- `real_data/processed/sample_500_metadata.json` — distribuzioni e cleaning stats
- `real_data/results/run_500_20260525_162135.json` — risultati run completo
- `real_data/results/run_500_20260525_162135.md` — tabella metriche
- `real_data/ingestion/text_cleaning.py` — nuovo modulo cleaning
- `real_data/ingestion/semantic_features.py` — guidance regex riscritta
- `real_data/ingestion/pipeline.py` — parametri via env (TARGET_N, TEXT_CAP, OUT_NAME)
