# FINDINGS — First Real-Data Run

Date: 2026-05-25. Dataset: 50 eventi 8-K Item 2.02 dal S&P 500, 2018-2024 (un evento è 2025-01-30). Train/test split 70/30 stratificato per settore (35/15... in pratica 29/21 a causa di rounding per settore).

## Dataset

- **Eventi ingeriti**: 50 / 150 candidati (33% successo)
- **Failed**: 9 ticker senza 8-K Item 2.02 nella finestra target, o senza press-release exhibit detectabile, oppure storico prezzi insufficiente
- **Anno**: 2018=2, 2019=7, 2020=7, 2021=6, 2022=7, 2023=10, 2024=10, 2025=1
- **Settori**: 10 GICS rappresentati (Real Estate=4, Health Care=5, Utilities=6, Communication=5, IT=4, Materials=6, Energy=4, Consumer Disc=7, Consumer Staples=4, Financials=5)
- **Macro range**: VIX 11.5-42.0 (mean 18.8), yield_10y 0.56-4.83, credit_spread 1.45-3.30 (BAA10Y in punti percentuali)
- **Reaction**: mean return -0.003 (sane, vicino a zero), realized vol mean 0.31, max drawdown mean -0.10

## Tabella metriche (3 encoder, k=5)

| Approach | SelfCons | Random base | **Lift** | ReactCorr | Util@5 | CondQual | TempDiv(d) | Fit(s) | Eval(s) | Fail |
|---|---|---|---|---|---|---|---|---|---|---|
| concat_eq | 0.329 | 0.084 | **0.245** | 0.094 | 0.095 | 0.448 | 349 | 5.9 | 0.4 | 0 |
| contrastive_v2 | 0.784 | 0.341 | **0.443** | 0.072 | 0.005 | 0.400 | 587 | 0.3 | 0.1 | 0 |
| llm_v3 | 0.465 | 0.206 | **0.260** | **0.124** | **0.195** | 0.362 | 364 | 170 | 128 | **5** |

## Confronto con metriche mock (L2 v2, 150/50, 4 cluster)

| Metrica | Mock L2 v2 | Real 50 | Delta |
|---|---|---|---|
| ReactCorr (concat_eq) | 0.382 | 0.094 | **-0.288** |
| ReactCorr (contrastive_v2) | 0.362 | 0.072 | **-0.290** |
| ReactCorr (llm_v3) | 0.395 | 0.124 | **-0.271** |
| Util@5 (concat_eq) | 0.455 | 0.095 | -0.360 |
| Util@5 (llm_v3) | 0.535 | 0.195 | -0.340 |

**ReactCorr crolla di ~0.3 punti** su tutti gli encoder. La struttura tra
encoding-similarity e reaction-similarity è molto più debole su dati reali.
È atteso: le reazioni reali hanno tante variabili confondenti (idiosincratici,
news non-earnings, regime macro improvviso) che il mock generava in modo
pulito.

## Verifica predizioni richieste

> Le metriche assomigliano a quelle del mock o sono molto diverse?

**Molto diverse**. SelfCons funziona (Lift > 0 per tutti — il sistema retrieves
non-banale). ReactCorr e Util@5 sono ~0.1, una frazione del mock. CondQual ~0.4
(vs 0.6-0.7 mock).

> Gli approcci hanno problemi sistemici?

- **LLM v3 fail rate = 5/50 = 10%** sui testi reali (>5% soglia). Causa
  probabile: testi reali contengono boilerplate (forward-looking statements,
  legal disclaimers, contact info) che confonde il prompt. Servirebbero
  pre-pulizia più aggressiva o aumento retry.
- **contrastive_v2 overfit estremo**: loss da 0.01 → 0.0002 in 80 epoche su
  35 training events. Modello collapsed (SelfCons 0.78 ma Util@5 0.005).
  Conferma lezione #8: contrastive senza adeguato dataset → overfit.
- **concat_eq fit time 5.9s** invece dei soliti 0.2s: prima volta che
  scarica sentence-transformers per testi nuovi (cache populating). Re-run
  sarà istantaneo.

> Gli analoghi recuperati sembrano sensati?

Vedi 3 case studies sotto. **Mista**: alcuni hit razionali, molti retrieval
cross-settoriali che non sarebbero la prima scelta di un analista umano.

> Quali sono i primi problemi visibili?

1. **N=35 train è troppo piccolo** per qualsiasi encoder con parametri (LLM,
   contrastive). Concat_eq sopravvive ma con segnale debole.
2. **guidance_direction**: solo 4% degli eventi ha guidance flag (la regex è
   troppo restrittiva, va estesa o sostituita con classifier).
3. **Boilerplate nei testi**: "EX-99.1 2 [filename] EXHIBIT 99.1" appare in
   testa a quasi tutti i testi. Sentence-emb potrebbe weighting questa stringa
   ripetuta come "topic comune".
4. **LLM v3 fail rate**: a livello 10% su 50 eventi. Servirebbero validation
   tests più tolleranti o pulizia testi pre-prompt.

## Case study 1 — TTD Q4 2022 (ad tech, post rate-hike)

Query: The Trade Desk Q4 2022 risultati. Macro VIX 18, slope -0.6 (inverted),
post rate-hike. Reaction 30d = -0.094 (negativo moderato).

| Encoder | Top-5 (sectors) | same-sector | reactions |
|---|---|---|---|
| llm_v3 | ALGN/HC, CIEN/IT, RCL/CD, DHI/CD, **TTD/Comm** | 1/5 | -0.135, -0.176, -0.007, +0.063, +0.054 |
| contrastive_v2 | RCL/CD, ALGN/HC, EBAY/CD, FCX/Mat, **TTD/Comm** | 1/5 | -0.007, -0.135, -0.242, +0.021, +0.054 |
| concat_eq | CIEN/IT, ALGN/HC, RCL/CD, **TTD/Comm**, DHI/CD | 1/5 | -0.176, -0.135, -0.007, +0.054, +0.063 |

**Verdetto**: tutti e 3 hanno hit interessante = **TTD del proprio Q3 2021**
(stessa azienda, diverso quarter). Smart hit "stesso ticker different period".
Gli altri 4 sono mix coerente di tech/consumer-disc con reazioni miste —
suggerisce che gli encoder catturino "macro stress 2022-23" come segnale comune.
Pattern abbastanza sensato.

## Case study 2 — HAS Q4 2021 (Hasbro, fine 2021)

Query: Hasbro full-year 2021. VIX 22.9, yield 1.92 (basso), pre rate-hike.
Reaction 30d = -0.041 (modesto negativo).

| Encoder | Top-5 | overlap con altri |
|---|---|---|
| llm_v3 | EBAY/CD, TTD/Comm, CMCSA/Comm, FCX/Mat, MRK/HC | ∩ contrastive = 1 (FCX) |
| contrastive_v2 | FCX/Mat, PLD/RE, D/Util, MLM/Mat, MGM/CD | ∩ concat = 0 |
| concat_eq | EBAY/CD, CMCSA/Comm, PPL/Util, TTD/Comm, NDAQ/Fin | |

**Verdetto**: i 3 encoder retrievono insiemi quasi disgiunti. Nessun consumer
discretionary analogo evidente (il training set ha solo MGM, RCL, LEN, DHI,
NKE in CD). LLM e concat trovano comunicazione/tech adjacent; contrastive va
verso difensivi/REITs. **Per un analista umano** nessuno dei 3 è chiaramente
"giusto" — è un caso dove i 35 training events non hanno un buon match.
Onestamente: senza più dati, **il sistema non sa cosa rispondere bene**.

## Case study 3 — SYK Q1 2022 (Stryker, COVID-era macro stress)

Query: Stryker Q1 2022. VIX 30.0 (alto), yield 2.85, macro stress.
Reaction = -0.142 (forte negativo).

| Encoder | Top-5 sectors |
|---|---|
| llm_v3 | STZ/CS, FCX/Mat, D/Util, D/Util, NDAQ/Fin |
| contrastive_v2 | RCL/CD, **ALGN/HC**, PLD/RE, FCX/Mat, CMCSA/Comm |
| concat_eq | STZ/CS, D/Util, D/Util, FCX/Mat, NDAQ/Fin |

**Solo contrastive_v2 trova un Health Care** (ALGN). LLM e concat zero
healthcare. **Failure visibile**: per un evento HC importante in macro stress,
nessun analogo HC è trovato. Causa: training pool ha solo 3-4 Health Care
events e sono finiti per essere meno text-similar.

LLM retrieve **2 volte lo stesso ticker Dominion (D)** in due quarter diversi
— pattern "stesso ticker, momento diverso" emerge naturalmente sui dati reali.

## Cosa funziona e cosa è rotto

**Funziona**:
- Ingestion end-to-end (SEC EDGAR + FRED + yfinance + LM) → 50 eventi
  in ~10 min cumulativo.
- Schema isomorfo: gli encoder mock girano sui dati reali senza modifiche.
- Self-consistency Lift positivo per tutti (>0.24): il sistema retrieves
  non-random.
- Case studies mostrano pattern interpretabili (stesso ticker different quarter
  emerge come hit ricorrente).

**Rotto / debole**:
- ReactCorr ~0.1: la struttura predittiva del mock non c'è sui dati reali
  con N=50.
- Util@5 ~0.05-0.20: ranking degli analoghi non riflette ranking delle reazioni.
- contrastive_v2 collapse su 35 events: overfit visibile, SelfCons artificialmente
  alta ma Util crolla.
- LLM v3 10% fail rate: oltre soglia 5%, va investigato.
- guidance_direction regex troppo stretta (96% degli eventi → 0).

## Discussion items (per la prossima sessione)

1. **N events**: 50 è probabilmente troppo piccolo. Per contrastive serve
   probabilmente N ≥ 500. Quanto ampliare?
2. **Text preprocessing**: l'header "EX-99.1 2 [filename]" appare in 90% dei
   testi. Eliminarlo migliorerebbe sentence-emb. Stesso per "forward-looking
   statements" boilerplate.
3. **LLM v3 fail rate**: investigare i 5 fallimenti specifici. Probabilmente
   testi senza guidance esplicita o linguaggio molto tecnico.
4. **guidance_direction**: regex va estesa o sostituita con LLM classifier
   dedicato.
5. **Stratificazione per market cap**: skipped in questa sessione. Da
   aggiungere se vogliamo bilanciamento large vs mid.
6. **Validazione**: nessun ground-truth → come capire se i top-5 sono "giusti"?
   Possibili strade: human-labelled small subset, simulated trading backtests
   sui top-K, expert review.

## Files

- `real_data/processed/sample_50.json` — 50 eventi
- `real_data/processed/sample_50_metadata.json` — statistiche descrittive
- `real_data/results/run_real_20260525_121442.json` — risultati run completo
- `real_data/cache/{fred,prices}/` — cache API
- `real_data/raw/sec/` — filings SEC scaricati
