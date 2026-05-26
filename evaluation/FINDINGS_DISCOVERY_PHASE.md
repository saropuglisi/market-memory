# Discovery Phase — Findings

> Come abbiamo scoperto, attraverso un blind A/B test con baseline random e
> ground truth umana, che il nostro vincitore statistico era in realtà inutile —
> e cosa abbiamo imparato sul dominio.

**Periodo**: maggio 2026. **Stato finale**: pivot strategico verso `concat_eq` come primary engine; archiviazione della branch contrastive.

---

## 1. Il punto di partenza

Il progetto è partito con una domanda concreta: *come costruire uno spazio di rappresentazione degli eventi finanziari che produca analogie utili?*. L'idea era confrontare rigorosamente più approcci di encoding — dai più semplici (concatenazione di feature numeriche con embedding testuali) ai più sofisticati (contrastive learning addestrato sulla similarità delle reazioni di prezzo, LLM strutturato come estrattore di feature categoriche, encoder grafico basato su settore/temporal edges).

Abbiamo implementato 8 encoder e 3 varianti, costruito una pipeline di valutazione end-to-end (mock data L1-L5 con ground truth cluster nota, poi real data N=500 da SEC EDGAR + FRED + yfinance), e definito 5 metriche statistiche: precision@K, ReactCorr (Spearman tra similarità di encoding e similarità di reazione 30g), Util@K (frazione di analoghi con reaction-distance ≤ P25 train), CondQual (qualità conditional retrieval), TempDiv (diversità temporale).

Tutto il framework era costruito intorno all'idea che un buon encoder dovesse organizzare lo spazio in modo che eventi "analoghi" finissero vicini — dove "analoghi" inizialmente significava "stesso cluster" su mock e "stessa reaction-shape" su real.

## 2. Le metriche ci dicevano una cosa

Sulla fase mock (L1 → L5, difficoltà crescente da cluster perfettamente separabili a reaction-driven con feature overlap), `contrastive_v2` ha mostrato performance progressivamente più convincenti man mano che il dataset diventava più difficile. Su L5 — il livello disegnato per privilegiare la reaction-shape — `contrastive_v2` raggiungeva P@5 0.79 mentre `concat_eq` si fermava a 0.55.

Sulla fase real (N=50 → N=500), il pattern si è amplificato:

| Metrica | concat_eq | contrastive_v2 | llm_v3 |
|---|---|---|---|
| ReactCorr | 0.051 | **0.318** | 0.052 |
| SelfCons Lift | 0.509 | **0.592** | 0.470 |
| Util@5 P25 lift | +0.067 | **+0.142** | +0.059 |

Su N=50 contrastive aveva ReactCorr 0.07, su N=500 è esploso a 0.32 — il delta più grande del progetto. Sembrava una storia classica di success: contrastive learning ha bisogno di scala per non collassare, una volta superata la soglia (~500 sample) sblocca il segnale, batte i baseline non-parametrici.

Abbiamo anche raccolto qualche case study qualitativo notevole: contrastive trovava cross-sector smart hits (JNJ Q1 2020 → PFE Q3 2022 come HC peer; IT Q1 2022 → LRCX come semi peer) che concat/llm perdevano. Sembrava che contrastive avesse imparato qualcosa di non banale — una sorta di "reaction-similarity cross-sector" che gli encoder strutturali non vedevano.

La narrativa era pronta: *contrastive_v2 è il vincitore. Si paga con maggior complessità e meno interpretabilità, ma il segnale c'è.*

## 3. Il primo segnale di crepa

A questo punto siamo passati alla validazione qualitativa umana. Primo blind A/B test (2026-05-25): 15 query stratificate per macro-settore, top-3 da `concat_eq` e top-3 da `contrastive_v2` mescolati con label A-F, evaluator (lo sviluppatore stesso) in cieco. Tre scale 1-5: utility, insight non-banale, transferability.

Il risultato è stato sorprendentemente piatto. Mann-Whitney U cross-encoder su tutte e tre le metriche restituiva p-value > 0.7 — nessuna differenza statisticamente significativa tra i due gruppi. L'evaluator non era in grado di distinguere `contrastive_v2` da `concat_eq`.

Tre interpretazioni possibili erano sul tavolo:

1. **Gli encoder sono effettivamente equivalenti** dal punto di vista qualitativo — le differenze statistiche su ReactCorr non si traducono in differenza percepibile.
2. **Le metriche di valutazione erano sbagliate** — utility/insight/transferability sono proxy intuitivi ma sovrapposti e ancorati alla similarità visiva dei grafici di reazione. L'evaluator collassa su una singola intuizione visiva.
3. **Manca un punto di riferimento** — senza una baseline random, non sappiamo se *qualunque* gruppo (incluso concat_eq) sta facendo meglio del puro caso.

Dopo consultazione esterna con tre advisor, il consenso è stato chiaro: il primo test non era abbastanza rigoroso per distinguere queste tre ipotesi. Servivano (a) una baseline random, (b) metriche di valutazione disegnate per il task analitico specifico (non proxy generici), (c) un setup che riducesse il bias visuale dei grafici (includere i testi narrativi nella valutazione, non solo le reazioni).

## 4. Il test decisivo

Blind A/B test v2 (2026-05-26):

- **Tre gruppi invece di due**: `contrastive_v2` top-3 + `concat_eq` top-3 + 3 candidati random dal training pool (esclusi solo ticker della query e id già scelti dagli encoder). Nessun filtro temporale sul random.
- **Permutazione X/Y/Z** dei tre gruppi per ogni query, in modo che l'evaluator non potesse memorizzare "X = contrastive" attraverso il test.
- **Summaries narrative obbligatori**: per ogni candidato e per la query, una sintesi 2-3 frasi (cosa è successo, perché, tono) generata via Qwen 2.5-7B/Ollama, mostrata prominently nell'UI prima dei grafici. Testo completo disponibile on-demand in modal.
- **Quattro nuove metriche** invece di tre, ridisegnate per il task analitico:
  - *Stessa storia* — stessa dinamica economica sottostante?
  - *Stesso clima di mercato* — stesso regime macro (VIX, tassi, sentiment)?
  - *Stesso tipo di notizia* — stesso tipo di sorpresa (beat/miss/raise/cut)?
  - *Utile come esempio storico* — precedente mentale utile per la query?
- **UI "tinder mode"** con un candidato alla volta, tooltip operativo per ogni voto 1-5, navigazione da tastiera, autosave incrementale, supporto cannot-evaluate per dati mancanti.

15 query × ~9 candidati (alcune query con 8 per dedup di candidati picked by both encoder) = 133 candidati valutati. Una sola valutazione marcata cannot_evaluate.

### Risultati netti

| Encoder | same_dynamic | same_regime | same_surprise | mental_precedent |
|---|---|---|---|---|
| **concat_eq** | 2.13 | **4.18** | **3.93** | **2.80** |
| contrastive_v2 | 1.59 | 3.16 | 3.52 | 2.07 |
| random | 1.24 | 2.38 | 3.02 | 1.56 |

Kruskal-Wallis 3-way per metrica: p<0.05 su tutte e quattro (p≤0.0083). Le differenze tra i tre gruppi sono statisticamente reali, non rumore.

Mann-Whitney pairwise (le righe che contano):

| Confronto | same_dynamic | same_regime | same_surprise | mental_precedent |
|---|---|---|---|---|
| concat_eq vs random | **p=0.0007** | **p<0.0001** | **p=0.0025** | **p<0.0001** |
| contrastive vs random | p=0.092 | **p=0.0072** | p=0.120 | **p=0.022** |
| contrastive vs concat_eq | p=0.064 | **p=0.0005** | p=0.10 | **p=0.011** |

`concat_eq` batte random su **tutte e quattro** le metriche con p<0.05. `contrastive_v2` invece **pareggia con random** su same_dynamic e same_surprise (p≥0.09), e quando viene confrontato direttamente con concat_eq perde su tutte e quattro le metriche (significativo su due, trend su altre due).

### Distribuzione hard failures / top performers

Estraendo i candidati con mean(4 metriche) ≤ 2 (hard failures) e ≥ 4 (top performers):

| Encoder | Hard failures | Top performers |
|---|---|---|
| **concat_eq** | **4/45** | **15/20** |
| contrastive_v2 | 16/45 | 5/20 |
| random | 26/45 | 0/20 |

`concat_eq` produce quattro volte meno hard failures di `contrastive_v2` e tre volte più top performers. La distribuzione di `contrastive_v2` è sbilanciata verso il basso: la metà delle sue hard failures sono valutazioni medie ≤ 1.75, indicando che quando sbaglia, sbaglia in modo radicale (non parzialmente). I top performers di contrastive_v2 sono concentrati su Q4 (ALGN) e Q2 (HPE, peer covid CAT/CPAY) — pattern di reaction-similarity che genuinamente coincide con regime anchoring. Ma è l'eccezione, non la regola.

## 5. La scoperta

Cosa abbiamo imparato concretamente, oltre il "concat_eq vince":

**ReactCorr misurava una proprietà reale ma cognitivamente non utile.** La metrica calcola correttamente la Spearman correlation tra similarità di encoding e similarità di reazione 30g. Su `contrastive_v2` raggiunge 0.318, il valore più alto del progetto. È un numero corretto — il modello impara *davvero* a organizzare lo spazio in modo che eventi vicini abbiano reazioni vicine. Ma "reazioni vicine" non implica "analoghi utili": due eventi possono avere reazioni a 30g molto simili (entrambe +5% con bassa vol) per ragioni totalmente diverse (uno per un beat+raise in regime risk-on, l'altro per un dividend announcement in regime difensivo). Il modello li mette vicini; l'analista li scarta. *Reactional geometry* è una proprietà reale ma è quella sbagliata.

**`concat_eq` fa regime anchoring.** Non impara nulla — è una concatenazione standardizzata di feature macro, micro, semantiche e un embedding testuale MiniLM. Ma proprio perché lavora su feature interpretabili e non comprime in uno spazio appreso, conserva l'informazione che conta: VIX, yield curve, credit spread, settore GICS, tono semantico Loughran-McDonald. Due eventi con VIX simile, stessa fase del ciclo dei tassi, stesso settore e tono semantico vicino finiscono vicini perché *condividono il regime macro-temporale*, non perché un modello ha trovato un pattern latente. Sui top performers del blind test, l'evaluator ha annotato ripetutamente cose come "stesso settore e settimana", "stessa macro nel 2020", "stesso ciclo manifatturiero 2019" — il sistema fa precisamente quello che dice di fare.

**`contrastive_v2` optimizza reactional geometry, non regime anchoring.** Quando ha successo (5/20 top performers) lo fa perché *occasionalmente* reactional similarity coincide con regime similarity (es. CAT 2020-04-28 → HPE 2020-05-21: stesso shock covid, reazioni allineate, regime allineato). Quando fallisce (16/45 hard failures) lo fa perché ha trovato eventi con reaction-shape simile ma in regimi totalmente diversi — es. ROK 2022-01-27 (rate-hike, beat+raise) → CPB 2021-09-01 (consumer staples, inflation guidance cut): grafici simili a 30g ma significato cognitivo opposto.

**I mercati hanno regimi, non manifold.** Questa è la conclusione più importante. L'ipotesi implicita di tutti gli approcci deep — contrastive, LLM structured, eventualmente graph — era che esistesse una *struttura semantica latente universale* nei mercati finanziari, una che, se opportunamente appresa, permettesse a un encoder di metterci dentro tutto e ritrovare analogie "profonde". L'evidenza empirica dice di no: i mercati hanno regimi macro-temporali ricorrenti (le combinazioni VIX-yields-credit-settore-narrative-sorpresa si ripetono perché il ciclo economico si ripete) e queste sono il segnale che conta. Catturarle non richiede deep learning, richiede feature engineering attento e standardizzazione corretta.

## 6. Implicazioni per il futuro

**Pivot tecnico**: da "deep representation learning for financial analogies" a "structured macro-contextual retrieval based on regime anchoring". La prossima fase implementativa è `concat_eq+` con narrative tags sparse — feature simboliche estratte dai testi (sorpresa beat/miss/in-line, direzione guidance raise/cut/maintain, narrative dominante: competitive/operational/cycle/regulatory) concatenate al vettore esistente. Estensione minima, allineata alla logica del primary engine, mantiene interpretabilità.

**Scaling N=500 → N=1500**: un universo più ricco rende il regime anchoring più discriminante (più precedenti per ogni regime). Non serve cambiare architettura.

**Direzione metodologica**: validazione qualitativa umana con baseline random come metodologia obbligatoria per ogni run a scala. Le metriche statistiche da sole non bastano — il caso `contrastive_v2` lo dimostra: ReactCorr 0.318 (top del progetto) si traduce in 16/45 hard failures su valutazione umana.

**Direzione filosofica**: accettare che alcuni domini richiedono approcci semplici e interpretabili, non sofisticati. La sofisticazione architettonica si paga con perdita di interpretabilità *e* con il rischio di apprendere proprietà cognitivamente inutili. In domini senza struttura latente vera, il deep learning non aggiunge valore — aggiunge solo rischio di optimize the wrong ontology.

**Cosa potrebbe sbloccare contrastive in futuro** (non roadmap immediata, solo ricerca pura): training loss diversa che NON sia similarità reazioni 30g, target di apprendimento allineato al regime anchoring (es. coppie positive = "stesso regime VIX/yields/sector"), hard negative mining strutturato per coppie "same regime opposite reaction". Eventualmente un encoder ibrido che combini regime features (alla concat_eq) con rappresentazioni apprese in modo subordinato.

## 7. Lezioni metodologiche

Le tre lezioni più importanti da portare via:

**1. Le metriche proxy possono ingannare.** ReactCorr era tecnicamente corretta — misurava esattamente quello che diceva di misurare. Ma misurava la cosa sbagliata rispetto al task target ("analogo utile per ragionamento umano"). *Optimizing the wrong ontology* è il failure mode più pericoloso perché passa inosservato per molto tempo: produce numeri belli su metriche valide, confronti credibili, narrative convincenti. L'unico antidoto è ground truth umana presto.

**2. Validazione umana qualitativa con baseline random è obbligatoria, non opzionale.** Il primo blind test, senza baseline random, produceva risultati ambigui che potevano essere letti come "gli encoder sono equivalenti" o "le metriche sono sbagliate". Solo con il random come terzo gruppo si distinguono i tre regimi possibili: tutti random-level (sistema rotto), tutti sopra random ma equivalenti (encoder ridondanti), differenza concreta tra encoder e random (segnale reale). Senza random non si può chiudere il dubbio.

**3. In domini con struttura non latente, approcci semplici battono approcci complessi.** I mercati finanziari hanno regimi ricorrenti, non manifold semantici profondi universali. Approcci che assumono il secondo (contrastive learning su reazioni, LLM strutturato) sotto-performano approcci che catturano il primo (concatenazione di feature interpretabili). Architettura semplice + feature engineering attento batte architettura complessa + feature minimi. Non è un risultato anti-deep-learning generale: è un risultato sulla *struttura del dominio* finanziario. In altri domini con struttura latente reale (es. linguaggio naturale, immagini) il pattern sarebbe diverso.

## 8. Onestà sul percorso

Il pivot da contrastive_v2 a concat_eq non è una sconfitta. È il risultato che dà valore al progetto.

Il sistema è passato attraverso un ciclo completo:

1. Implementazione (5 approcci, infrastruttura di valutazione end-to-end)
2. Sviluppo iterativo (cinque diagnostici, due rewrite del generator mock, due versioni di contrastive con regularization, tre versioni di LLM con prompt fix)
3. Validazione statistica multipla (mock L1-L5, real N=50, real N=500, util@K recalibration)
4. Apparente convergenza su un vincitore (contrastive_v2 con ReactCorr 0.318, lift Util@5 P25 +0.142)
5. Validazione qualitativa con ground truth umana (blind v1 ambiguo, blind v2 decisivo)
6. Invalidazione della narrativa precedente, pivot strategico, archiviazione branch

Il progetto avrebbe potuto fermarsi al punto 4. Lì c'era un "vincitore" pubblicabile, una storia coerente, numeri convincenti, case study notevoli. Quello che molti progetti di ML applicato fanno: si fermano al primo risultato statistico significativo e non lo testano contro ground truth umana con baseline random. Pubblicano il "vincitore", costruiscono prodotto sopra, e scoprono out-of-distribution che il vincitore non vince — ma allora è troppo tardi.

Andare al punto 5 ha richiesto dieci ore di lavoro infrastrutturale (summaries Qwen, blind v2 generator a 3 gruppi, UI tinder-mode, 4 nuove metriche, analyze script) e una sessione di valutazione manuale. Il costo è basso in confronto al rischio evitato.

Il risultato di questo ciclo non è "abbiamo fallito su contrastive". È "abbiamo scoperto che il dominio è diverso da quello che assumevamo, e ora sappiamo come costruire valore reale". La ricerca seria fa precisamente questo: passa attraverso cicli di validazione e ne esce con knowledge calibrata sull'evidenza, non con un sistema sovrapposto e una narrativa di successo non testata.

Concat_eq fa regime anchoring. Funziona. La prossima fase lo estende con narrative tags sparse e lo scala a N=1500. Da qui in avanti, il progetto sa cosa è — e cosa non è.

---

**Riferimenti**:

- [`PROGRESS.md`](../PROGRESS.md) — log cronologico completo
- [`SITUATION_REPORT_FINAL_DISCOVERY.md`](../SITUATION_REPORT_FINAL_DISCOVERY.md) — stato finale Discovery Phase
- [`evaluation/qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md`](qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md) — output completo dell'analisi blind v2
- [`approaches/archived/README_CONTRASTIVE_ARCHIVE.md`](../approaches/archived/README_CONTRASTIVE_ARCHIVE.md) — motivazione archiviazione contrastive
- [`approaches/archived/README_LLM_ARCHIVE.md`](../approaches/archived/README_LLM_ARCHIVE.md) — motivazione archiviazione LLM
