# Smart hits vs Stupid hits

Esempi concreti dalle 10 query. Fonte: [retrievals.md](retrievals.md) +
[retrievals.json](retrievals.json).

---

## Stupid hits

### S1 — concat_eq su `evt_0192` (NOISE) → trova 5/5 noise per **template lookup banale**
Query è un evento NOISE con il template:
> "Quarterly results were broadly in line with expectations. We continue to
> execute on our strategic priorities..."

Tutti gli eventi NOISE nel training condividono **esattamente lo stesso testo
base** (solo intro/closer variano). concat_eq fa 5/5 cosine ≈ 1.0 perché
sentence-emb è quasi identico. Il P@5=1.00 è ingannevole: non è "intelligenza"
del modello, è **pattern matching su un template unico**. In dati reali
nessun "noise event" ha lo stesso testo dei suoi vicini → questa precisione
non generalizza.

### S2 — llm_v3 su `evt_0038` (A) → 5/5 stesso cluster ma **react-dist medio in p42-p57**
Pull di 5 eventi A con simile narrativa "competitive moat / operational scale".
Same-cluster perfetto, ma le **reazioni effettive sono distanti** (rank
percentili 5/15/32/57/62 nei pair training): la "famiglia narrativa" è
giusta ma gli outcome non sono garantiti. Un analista che usa questi top-5
per "what happened next" sarebbe **sviato**.

### S3 — llm_v3 su `evt_0071` (B easy) → 0/5 same cluster perché trascinato dal testo
Query è cluster B ma con un testo dal pool C (artefatto generator-noise). LLM
fa 0/5: trova 5 eventi C con stesso template. Statisticamente sembrano vicini
(sim 0.8+ in embedding), narrativamente sono **opposti** (recovery vs late-cycle
compression). Questo è il fallimento più puro di "vedere solo le parole".

### S4 — concat_eq su `evt_0037` (A hard) → react-dist top-1 = 1.34 (p14), ma 2° = 1.93 (p31)
Il top-1 evt_0018 (A, INTC) ha reaction-dist p14 — ok. Ma da rank 2 in poi
le distanze salgono a p31, p17, p56, p22. Cinque eventi della stessa famiglia
narrativa ma con reazioni dispersé. Sembrano analoghi solo finché non guardi
i numeri di reazione.

---

## Smart hits

### Sm1 — llm_v3 su `evt_0037` (A hard) → **evt_0028 GM/consumer, reaction-dist p0**
Cross-sector (GM consumer, ma cluster A grazie a cross-pollination + testo
AI), **reazione quasi identica** alla query (return e dd allineati). Smart
hit perfetto: testo riconosciuto, cross-sector accettato, outcome verificato.

### Sm2 — contrastive_v2 su `evt_0038` (A easy) → **evt_0102 C/QCOM, reaction-dist p3**
Cluster diverso (C non A), testo "recovery" diverso dalla query "AI moat",
ma **reazione vicinissima** (return moderato, vol simile, drawdown simile).
Per un analista che cerca "stesso outcome anche se contesto diverso", questo
è oro. Contrastive_v2 fa la cosa che nessun altro encoder fa.

### Sm3 — contrastive_v2 su `evt_0071` (B easy) → **evt_0146 D/MMM, reaction-dist p5**
Query B (margin compression) → contrastive trova eventi D (liquidity stress)
con **reazioni distruttive simili**. Cluster diversi (B vs D) ma stessa
"forma" di outcome (return negativo, vol alta, drawdown grande). Per la
domanda "se la reazione è così, dove abbiamo già visto questo?", risposta
ottima.

### Sm4 — llm_v3 su `evt_0118` (C hard) → 5/5 same cluster + react-dist mean 1.65
Query è un C "hard" (centroid dist 3.02). LLM v3 trova 5 eventi C con
**reazioni tutte vicine** (mean rank ~14). Caso in cui il prompt direttivo
fa pesare la giusta combinazione di markers ("stabilizing", "improving
trends") senza farsi sviare dal noise.

### Sm5 — contrastive_v2 su `evt_0152` (D hard) → 4/5 same cluster + react-dist 2.59
Query D hard, vicino ai bordi (centroid dist 5.31, outlier). Contrastive
sale a 4/5 same-cluster (vs concat 3/5, LLM 1/5). La reaction-geometry
appresa è abbastanza robusta da identificare comunque la famiglia "liquidity
stress" anche al limite. Smart perché **non si lascia ingannare dal testo
specifico**.

---

## Pattern

- **Stupid hits** vengono prevalentemente da **template matching superficiale**
  (text che ripete o lo stesso intro+closer) → llm_v3 e concat_eq.
- **Smart hits** vengono prevalentemente da **cross-sector / cross-cluster
  con outcome simile** → contrastive_v2 (per reaction), llm_v3 (per
  narrativa coerente in events tra settori).
- Il rumore strutturato del generator (testo da X + numeri da Y) **espone
  in modo netto** la differenza tra i due tipi di encoder.
