# Financial Episode Representation

> Sistema di retrieval strutturato per analoghi finanziari basato su regimi macro-temporali. Dato un evento finanziario (es. un earnings 8-K), trova precedenti storici che condividono lo stesso contesto macro, lo stesso tipo di sorpresa e la stessa fase di mercato.

---

## Cos'è questo progetto

Questo non è un trading bot. Non è un AI stock picker. Non è un sistema che impara "rappresentazioni profonde" di analogie finanziarie attraverso deep learning.

È uno **strumento di retrieval cross-temporale** che ancora ogni evento al regime macro-temporale in cui è avvenuto, e che usa quell'ancoraggio per recuperare precedenti utili. Il valore del sistema sta nel *regime anchoring*, non nel learning di latent semantics.

La domanda iniziale del progetto era: *"come costruire uno spazio di rappresentazione degli eventi finanziari che produca analogie utili?"*. Dopo un ciclo completo di validazione (mock → real → blind A/B con baseline random + ground truth umana) la risposta che è emersa è meno entusiasmante e più onesta: **i mercati hanno regimi macro-temporali ricorrenti, non manifold semantici profondi universali**. Catturare i regimi è sufficiente — e fattibile con architetture semplici.

## Perché esiste

Gli LLM generalisti (Claude, GPT, Gemini) sono stateless rispetto ai mercati. I sistemi commerciali (Bloomberg, FactSet) hanno i dati ma non fanno retrieval semantico-contestuale. I progetti accademici tipo FinGPT si concentrano sul fine-tuning su task accademici (sentiment, forecasting) che producono poco valore reale.

Lo spazio vuoto: **eventi finanziari come oggetti di prima classe**, ancorati al loro contesto macro, recuperabili come precedenti per ragionamento analogico. Un layer di memoria episodica per analisti, non un sostituto.

Durante lo sviluppo abbiamo scoperto qualcosa di importante: non esiste una "latent semantic structure" universale che, una volta appresa, generalizzi cross-regime. Gli approcci sofisticati (contrastive learning su reazioni di prezzo) imparano *qualcosa di reale* (reactional geometry: eventi con reazioni simili finiscono vicini nello spazio appreso) ma quella proprietà non corrisponde a "utile per ragionamento analogico umano". Vedi [`evaluation/FINDINGS_DISCOVERY_PHASE.md`](evaluation/FINDINGS_DISCOVERY_PHASE.md) per la storia completa.

## Obiettivi

### Obiettivo primario

Costruire un sistema di **retrieval strutturato di analoghi finanziari** che ancori ogni evento a un regime macro-temporale (VIX, yield curve, credit spread, settore, tipo di sorpresa) e recuperi precedenti storici con regime simile.

### Obiettivi specifici della prossima fase

1. **`concat_eq+` con narrative tags sparse** — estendere il primary engine con feature simboliche estratte dai testi (sorpresa beat/miss/in-line, direzione guidance, narrative dominante).
2. **Scaling N=500 → N=1500** — un universo più ricco rende il regime anchoring più discriminante.
3. **Eventuale UI per analisti** — interfaccia di esplorazione cross-temporale dei precedenti.

### Principi metodologici (invariati)

- **Onestà sopra spettacolo.** Documentiamo cosa funziona e cosa no. Il pivot da contrastive_v2 a concat_eq è il risultato di un blind test con ground truth umana — è ricerca seria, non fallimento.
- **Ground truth o niente.** Ogni claim quantitativo va misurato contro una metrica fissata in anticipo, su uno split mai visto.
- **Validazione umana qualitativa con baseline random è obbligatoria**, non un nice-to-have. Le metriche proxy possono ingannare.
- **Confronti, non assoluti.** Nessun approccio è "il migliore" in astratto.
- **Hardware ragionevole.** Tutto gira su un MacBook M3 Pro. Nessuna dipendenza da servizi cloud o API a pagamento.

### Cosa NON è un obiettivo

- **Non è apprendimento di rappresentazioni profonde.** È retrieval strutturato basato su feature interpretabili.
- **Non è learning di latent semantics complessi.** Il dominio non ha la struttura latente che approcci come contrastive assumono.
- **Non è un sistema di deep learning per finance.** È un layer di memoria contestuale, non un modello predittivo.
- **Non predice prezzi.** Recupera precedenti; l'interpretazione resta a un umano.
- **Non sostituisce l'analista.** Amplifica il suo giudizio attraverso il retrieval di analoghi macro-temporali.
- **Non è un prodotto commerciale.** È ricerca aperta.

## Approcci

| Encoder | Stato | Note |
|---|---|---|
| **concat_eq** | **Primary engine** | Vincitore del blind A/B v2 su tutte e 4 le metriche umane. Statisticamente significativo vs random su tutte. 15/20 top performers. |
| factorized | Specialist | Utilità mirata su query condizionate (es. "stesso regime macro"). CondQual=1.00 su mock. |
| graph_experimental | Sperimentale | Conserva valore post cross-pollination ticker; usa semantic+sector come segnale. |
| concat_raw | Baseline numerico | Riferimento. |
| contrastive v1, v2, v3 | **Archived** | Vedi [`approaches/archived/README_CONTRASTIVE_ARCHIVE.md`](approaches/archived/README_CONTRASTIVE_ARCHIVE.md). Optimize "reactional geometry" — proprietà reale ma cognitivamente non utile. 16/45 hard failures nel blind v2. |
| llm_structured v1, v2, v3 | **Archived** | Vedi [`approaches/archived/README_LLM_ARCHIVE.md`](approaches/archived/README_LLM_ARCHIVE.md). Fail rate 23% su N=500 real, mismatch generativo↔discriminativo. |

Gli approcci archiviati sono mantenuti come case study di failure modes — non eliminati.

## Dataset

**Real data (current focus)**: `real_data/processed/sample_500.json` — 500 eventi 8-K Item 2.02 (Results of Operations) da SEC EDGAR (2018-2025), 11 settori GICS, stratificati per anno + settore. Macro features da FRED (VIX, yields, credit spread), prezzi da yfinance, semantic features da Loughran-McDonald.

**Mock data (legacy, per regression testing)**: `data/mock_events_L1.json`-`L5.json` — dataset sintetici a 5 livelli di difficoltà con ground truth cluster nota. Usati per validare la metodologia prima del passaggio a dati reali.

**Narrative summaries**: `real_data/processed/sample_500_summaries.json` — sintesi narrative 2-3 frasi generate via Qwen 2.5-7B (Ollama), usate per la valutazione qualitativa umana (non come feature di encoding).

## Metriche di valutazione

### Metriche quantitative (su retrieval)

1. **SelfCons Lift** — coerenza nelle reazioni dei top-K vs random baseline.
2. **ReactCorr** — Spearman tra similarità di encoding e similarità di reazione 30g. *Caveat critico*: misura una proprietà reale ma non corrisponde a utilità analogica. Vedi lezione metodologica #14.
3. **Util@K P25** — frazione di analoghi con reaction-distance ≤ P25 del training pool; lift vs random baseline.
4. **CondQual** — qualità conditional retrieval su filtri macro (es. VIX>18).
5. **TempDiv** — diversità temporale media (giorni) dei top-K.

### Metriche qualitative (blind A/B con ground truth umana)

Dal blind test v2: 4 metriche su scala 1-5 valutate da umano in cieco (gruppi X/Y/Z permutati per query, baseline random come terzo gruppo):

1. **Same dynamic** — stessa dinamica economica sottostante?
2. **Same regime** — stesso clima di mercato (VIX, tassi, sentiment)?
3. **Same surprise** — stesso tipo di sorpresa rispetto alle aspettative?
4. **Mental precedent** — utile come precedente mentale per ragionare sulla query?

**La validazione qualitativa con baseline random è metodologia obbligatoria** per il progetto da qui in avanti.

## Risultati chiave

Dal blind A/B test v2 (N=15 query × ~9 candidati, valutazione umana single-blind):

| Encoder | same_dynamic | same_regime | same_surprise | mental_precedent | Hard failures | Top performers |
|---|---|---|---|---|---|---|
| **concat_eq** | 2.13 | **4.18** | **3.93** | **2.80** | **4/45** | **15/20** |
| contrastive_v2 | 1.59 | 3.16 | 3.52 | 2.07 | 16/45 | 5/20 |
| random baseline | 1.24 | 2.38 | 3.02 | 1.56 | 26/45 | 0/20 |

Kruskal-Wallis a 3 gruppi: significativo (p<0.05) su tutte e 4 le metriche. concat_eq batte random su tutte e 4. contrastive_v2 pareggia con random su same_dynamic e same_surprise.

Riferimento completo: [`evaluation/qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md`](evaluation/qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md).

## Struttura del progetto

```
market-memory/
├── README.md                            # questo file
├── PROGRESS.md                          # log cronologico delle decisioni
├── SITUATION_REPORT_FINAL_DISCOVERY.md  # stato finale Discovery Phase
├── approaches/
│   ├── base.py                          # EpisodeEncoder ABC
│   ├── approach_1_concat.py             # Primary engine: concat_eq
│   ├── approach_2_factorized.py
│   ├── approach_4_graph.py
│   └── archived/                        # contrastive v1/v2/v3, LLM v1/v2/v3
├── real_data/
│   ├── ingestion/                       # SEC + FRED + yfinance + cleaning
│   ├── processed/                       # sample_500.json + summaries
│   ├── metrics_real.py
│   ├── run_approaches.py
│   └── narrative_summaries.py           # generatore Qwen via Ollama
├── evaluation/
│   ├── metrics.py
│   ├── FINDINGS_DISCOVERY_PHASE.md      # documento principale della scoperta
│   └── qualitative/
│       ├── blind_test_v2_generator.py   # 3-way blind test generator
│       ├── analyze_blind_results_v2.py  # Kruskal-Wallis + Mann-Whitney
│       ├── serve_review.py              # Flask UI server
│       └── static/index.html            # UI tinder-mode
├── data/                                # mock datasets L1-L5
└── results/                             # output dei run
```

## Stack tecnico

- **Linguaggio**: Python 3.11+
- **Hardware target**: MacBook Pro M3 Pro (no GPU dedicata richiesta)
- **ML**: scikit-learn, sentence-transformers (MiniLM), PyTorch (CPU/MPS) per architetture archiviate
- **LLM locali**: Ollama + Qwen2.5-7B per generazione narrative summaries (NON come encoder)
- **Web UI valutazione**: Flask + Chart.js
- **Statistica**: scipy (Kruskal-Wallis, Mann-Whitney)

Nessuna API esterna a pagamento. Nessuna dipendenza da servizi cloud.

## Come riprodurre

```bash
# Setup
python3 -m venv .venv
.venv/bin/pip install numpy pandas scikit-learn scipy sentence-transformers torch \
                     requests tqdm flask yfinance pysentiment2 fredapi

# Ollama (per narrative summaries, opzionale)
ollama pull qwen2.5:7b

# Ingestione real data (richiede FRED API key)
python -m real_data.ingestion.run_pipeline   # → real_data/processed/sample_500.json

# Run retrieval su tutti gli encoder attivi
python -m real_data.run_approaches            # → real_data/results/run_500_<ts>.json

# Generazione summaries narrative (~20 min su M-series)
python -m real_data.narrative_summaries

# Generazione blind test v2
python -m evaluation.qualitative.blind_test_v2_generator

# UI valutazione (porta 5050 se 5000 occupata da AirPlay macOS)
python -m evaluation.qualitative.serve_review --port 5050

# Analisi post-valutazione
python -m evaluation.qualitative.analyze_blind_results_v2
```

Seeds fissati a 42 ovunque.

## Filosofia

Il problema dei mercati non è la mancanza di informazione. È la mancanza di **memoria strutturata** che permetta di metterla in prospettiva. Un sistema che dice "questa configurazione di VIX, settore e tipo di sorpresa assomiglia a Q1 2020, Q3 2022 e Q4 2023 per queste ragioni specifiche" è infinitamente più utile di uno che dice "compra X".

Il sistema amplifica il giudizio dell'analista attraverso retrieval di precedenti macro-temporali. Non attraverso "comprensione AI" del mercato: i mercati non hanno una struttura semantica latente universale da comprendere. Hanno regimi ricorrenti da riconoscere.

Architetture semplici e interpretabili sono la risposta giusta quando il dominio non ha la struttura latente che approcci complessi assumono.

## Licenza e contributi

Progetto di ricerca aperta. Codice e findings pubblicati per trasparenza e replicabilità. Feedback, repliche e critiche metodologiche benvenute.

---

*"Make it work, make it right, make it fast — in that order."* — Kent Beck
