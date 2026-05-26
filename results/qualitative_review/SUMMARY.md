# Qualitative review — SUMMARY (L2 v2)

Selezione di 10 eventi test (2/cluster × 4 + 2 noise), retrieval top-5 da
`llm_v3` + `contrastive_v2` + `concat_eq`. Vedere
[selected_events.json](selected_events.json),
[retrievals.md](retrievals.md),
[overlap_analysis.md](overlap_analysis.md),
[case_studies.md](case_studies.md),
[smart_vs_stupid.md](smart_vs_stupid.md).

---

## Risposte alle 5 domande

### 1) Gli analoghi sono sensati per un analista umano?

**Su 10 query**, miei verdetti di "analista accetterebbe i top-3":

| Encoder | Accept (top-3) | Reject | Note |
|---|---|---|---|
| llm_v3 | 7/10 | 3/10 | sviato dal testo su evt_0071 (B con testo C); ottimo su A/C/NOISE |
| contrastive_v2 | 4/10 | 6/10 | rifiutato quando cambia cluster nei casi "easy" (es. evt_0038); accettato quando reaction-pattern è il segnale reale (B hard, D hard) |
| concat_eq | 6/10 | 4/10 | molto simile a llm_v3 ma più vulnerabile a quirk numerici |

Il giudizio dipende fortemente dal task: **se l'analista chiede "famiglia narrativa"**, llm_v3 vince; **se chiede "outcome simili"**, contrastive_v2. Su 6/10 query gli encoder text-based sono "umanamente sensati"; contrastive_v2 lo è quando i numeri raccontano una storia diversa dal testo.

### 2) Sbagliano in modo informativo o random?

**Informativo** — sempre, in modi diversi.

- **llm_v3/concat_eq** sbagliano lungo l'asse "testo simile, numeri/outcome
  diverso". Es. evt_0071 (cluster B con testo C): retrieve 5/5 C eventi.
  Sbagliano coerentemente sul template, non a caso.
- **contrastive_v2** sbaglia lungo l'asse "reazione simile, cluster diverso".
  Es. evt_0038 (A easy): retrieve 4/5 C eventi con reazione vicina. Cluster
  sbagliato ma outcome corretto.

Nessun encoder produce hit "random". Ogni sbaglio è **leggibile** lungo una
dimensione: testo, reaction, o feature numerica. Su dati reali questo è
prezioso — un'analista può capire **perché** un sistema ha proposto un
analogo apparentemente strano.

### 3) Stupid hits sistematici?

**Sì, due pattern**:

a) **Template lookup banale su NOISE.** Tutti i 3 encoder hanno P@5=1.0 sui
noise event, ma è perché il generator usa **un solo template testuale per
i noise**. In dati reali nessun gruppo "noise" avrebbe testo identico →
questa precisione **non generalizza**.

b) **Intro/closer matching artificiale.** Il generator aggiunge variazioni
"Looking at the quarter just ended,..." e closer "We will provide more
color in Q&A." Tre query diverse possono avere lo stesso intro, e LLM v3
+ concat_eq talvolta li accoppiano per quel motivo. Sentence-embedding
ne è particolarmente sensibile. In dati reali (testi più lunghi e diversi)
questo artefatto sparisce, ma su L2 v2 lo vediamo.

c) **Stessa famiglia narrativa ma reazioni disperse** (vedi Stupid #S2 in
   smart_vs_stupid.md). LLM v3 prende 5 eventi narrativamente coerenti con
   la query ma le loro reazioni sono ai percentili 5-62 → non sono garantiti
   come "stesso outcome".

### 4) C'è valore nell'unione dei top-5 dei 3 approcci?

**Sì, valore alto**. Statistiche:

- Overlap medio LLM ∩ contrastive_v2 = **0.1 di 5** (4.9 disagreement)
- Overlap medio contrastive ∩ concat_eq = **0.4 di 5** (4.6 disagreement)
- Overlap medio LLM ∩ concat_eq = **3.4 di 5** (1.6 disagreement)

Quindi:
- LLM v3 e concat_eq sono **largamente ridondanti** → tenerne uno solo.
- contrastive_v2 è **fortemente complementare** → aggiunge informazione.

Unendo top-5 di {llm_v3, contrastive_v2} → set di ~8-9 eventi unici per query
con **due viste diverse**: famiglia narrativa + outcome similari. Per un
sistema di analoghi in produzione, è la combinazione naturale.

### 5) Quando il sistema è affidabile?

| Tipo evento | Affidabilità | Encoder consigliato |
|---|---|---|
| **NOISE** | Falsa affidabilità (template lookup) | qualsiasi, ma il P@5 alto è artefatto |
| **Cluster A easy** (AI euphoria centrale) | **Alta** | llm_v3 o concat_eq |
| **Cluster A hard** (outlier numerico) | Media | llm_v3 (cattura narrativa); contrastive può sviare |
| **Cluster B easy** (margin compression centrale) | **Bassa** se testo è ambiguo | contrastive_v2 (preferisce numeri); LLM sviato dal testo |
| **Cluster B hard** | Media | contrastive_v2 |
| **Cluster C easy/hard** (recovery) | **Alta** per llm_v3 (testi distintivi) | llm_v3 |
| **Cluster D easy** (liquidity stress centrale) | Media | concat_eq, talvolta llm_v3 |
| **Cluster D hard** (outlier) | Media | contrastive_v2 |

**Affidabile**: A easy, C easy/hard (narrative cleanly recognizable).
**Non affidabile**: B easy quando testo e numeri disaccordano,
D hard outlier (tutti i 3 encoder retrieve parzialmente sbagliato).

---

## Unexpected observations

### a) LLM v3 e concat_eq sono quasi indistinguibili sui top-5 (3.4/5 overlap medio)
Avevamo trattato i due come encoder "diversi" — uno semantico, l'altro
text-embedding numerico. Empiricamente sui top-5 fanno la stessa cosa.
L'overhead di 525s di LLM v3 si paga solo per i marginali (P@5 +0.05 su L2 v2,
ReactCorr +0.013) — sui top-5 specifici raramente fa una scelta diversa
da concat_eq. **Vale la pena tenere entrambi?** Probabilmente no, a meno che
non si voglia il vettore strutturato di v3 per downstream usage.

### b) Contrastive_v2 ha similarità top-5 quasi sature (0.95+)
Le 5 cosine similarity dei top-5 di contrastive_v2 sono spesso 0.95-0.98,
quasi indistinguibili. Suggerisce che lo spazio appreso è **compresso**:
molti eventi finiscono vicini. P@5 e ReactCorr sono buoni ma il ranking
fine all'interno dei top-5 perde informazione. Per cercare il "top-1
analogo" specifico, llm_v3/concat_eq danno separazioni più nette
(differenze 0.78 → 0.84).

### c) Le reazioni "atipiche" rivelano outlier nei cluster
Cluster A "hard" (evt_0037) ha return=0.32 ma persist=0.37 (basso) — un
A "pieno" ha persist medio 0.55. Cluster A "ben costituito" e A outlier
sono mappati nello stesso cluster ma producono analoghi qualitativamente
diversi. Suggerisce che la struttura "cluster" è approssimazione —
servirebbe granularità inferiore (sub-pattern dentro A).

### d) Cross-pollination ha effetti utili in alcuni casi
evt_0028 (A, GM/consumer) è cross-pollinated. Llm_v3 lo trova come top-1 per
evt_0037 con react-dist p0 — perfetto smart hit. Il fatto che GM "in cluster
A" sia counter-intuitivo a livello settoriale ma corretto a livello
narrativo+reazione è uno dei pattern più interessanti dell'esperimento.

### e) Il prompt direttivo del LLM v3 non è visibile sui top-5
Il fix v3 vs v2 (instructions per cycle_phase) ha cambiato la distribuzione
aggregata di cycle_phase, ma sui top-5 retrieval le differenze v3 vs v2 sono
marginali (perché la similarity dipende soprattutto da event_polarity,
dominant_driver, surprise_magnitude, non da cycle_phase).
Conclusione: i prompt directives muovono la distribuzione di un campo ma
hanno **effetto limitato sul retrieval finale** se quel campo non è
discriminativo per la similarity calcolata.

---

## Cosa ho capito (e cosa no)

**Capito**:
- La differenza vera tra encoder non è "P@5 più alto" ma **quale dimensione
  privilegiano**. text vs reaction è la spaccatura concettuale.
- I "vincitori condizionali" (llm_v3 e contrastive_v2) sono complementari
  sul piano dei top-5 specifici, non solo sulle metriche.
- Una grossa parte della "performance" del mock è guidata da template
  matching che **non sopravviverà** ai dati reali (variabilità testuale,
  ticker overlap, regimi mescolati).

**Non capito ancora**:
- Cosa succede quando il numero di template è 1000 invece di 100 (testi reali).
  La superficialità del template matching dovrebbe sparire, ma allora cosa
  fanno LLM e concat_eq nel range "high diversity"?
- Quale frazione delle "smart hits" di contrastive_v2 è davvero generalizzabile
  vs overfitting alla geometria reaction-z-score del training. Senza validation
  cross-fold non lo sappiamo.
- Se la combinazione LLM + contrastive in un encoder ibrido (es. fit
  contrastive sopra LLM v3 features) produce ulteriore segnale o solo overhead.
