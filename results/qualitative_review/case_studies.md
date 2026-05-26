# Case studies — letture ravvicinate

Tre casi scelti dalle 10 query in [retrievals.md](retrievals.md):

---

## Caso A — Successo (relativo) — `evt_0038`, cluster A, easy, STX/tech

**Query**: "Capacity expansion is tracking ahead of schedule operationally.
Our competitive position in advanced packaging is a key differentiator..."

Vicino al centroide A (dist=1.38), reazione moderatamente positiva
(return=0.16, vol=0.29). Caso "facile".

### Esiti per encoder

| Encoder | same-cluster | mean react-dist | nota |
|---|---|---|---|
| llm_v3 | **5/5** A | 2.16 | tutti tech tranne TGT (consumer cross-pollinated) e ZION (financial) |
| concat_eq | **5/5** A | 1.85 | identico a llm_v3 sui primi 4 ID, ANET vs AMD al 5° |
| contrastive_v2 | 1/5 A | **1.60** | 4 eventi cluster C (recovery surprise); reazioni più vicine |

### Cosa rende questo caso "facile"?

- **Testo molto template-coerente**: la stringa "Capacity expansion is tracking
  ahead of schedule operationally" appare letteralmente in **evt_0008** (top-1
  di llm_v3 e concat_eq). È **lo stesso template**, solo intro/closer diversi.
  Hit per matching testuale puro.
- **Cross-pollination dei settori** non confonde: gli encoder semantici trovano
  TGT/consumer e ZION/financial nei top-5 di A perché i loro testi
  appartengono al pool A (vocabolario "competitive moat / operational excellence").
- **Contrastive diverge interamente**: trova 4 eventi cluster C con reazione
  più simile (return moderato positivo, vol simile) ma testo molto diverso
  ("Recovery in end-market demand…"). Per contrastive, una reazione
  return=0.13 in un evento di recovery vale più di una reazione return=0.16
  in un evento A "puro".

### Lettura

Su cluster A "puro" con testo template, **llm_v3 e concat_eq sono praticamente
intercambiabili**. Una analista umana userebbe entrambi i risultati come
"famiglie di analoghi AI/growth euphoria". Il contrastive presenta un **lens
alternativo**: "stesso outcome quantitativo anche se narrativa diversa". Non è
sbagliato — è un'altra domanda.

**Il caso non è davvero unanime** tra i 3 encoder: è unanime tra i 2 text-based,
con contrastive che fa volutamente altro. La distinzione utile è già visibile
qui.

---

## Caso B — Fallimento istruttivo — `evt_0071`, cluster B, easy, HON/industrial

**Query**: "We are observing positive inflection signals across multiple
leading indicators. Bookings, customer engagement, and pipeline conversion are
all firming. We will provide more color in Q&A."

Aspetto interessante: il testo è **un template del cluster C** ("positive
inflection… bookings firming") ma è stato sampled per un evento ground-truth
**cluster B** (probabilmente artefatto del generator: il pool semantic di B
ha occasionalmente confidence>0.5 nelle estremi, e il TEXTS[B] contiene
template misti). Il sample finale ha:

- Macro: VIX=24.3, yield=5.16, slope=-0.42 → tipico cluster B
- Micro: ret60d=-0.08, vol=0.34 → ancora cluster B
- Semantic: conf=0.66, hedging=4, guide=0 → ambiguo
- Reaction: return=-0.18, vol=0.45 → cluster B

Quindi **testo da cluster C, ma numeri+reazione cluster B**.

### Esiti

| Encoder | same-cluster (B) | mean react-dist | scelte |
|---|---|---|---|
| llm_v3 | **0/5** | 2.66 | tutti C (recovery) — segue il testo |
| concat_eq | 2/5 | 1.96 | mix B+C — testo trascina ma numeri tirano via |
| contrastive_v2 | **3/5** | **1.24** | macchina di B+1HYBRID con reazioni simili |

### Cosa hanno in comune gli analoghi sbagliati?

Sono **eventi cluster C** che condividono **lo stesso template testuale**.
Llm_v3 e concat_eq seguono il testo → sbagliano cluster. Non è "random":
è un pattern parziale (testo) che maschera la verità.

Contrastive_v2 non guarda il testo direttamente (lo eredita dal backbone
concat ma il MLP "appiattisce" verso reaction-geometry). Vede macro+micro
da B + reaction da B → top-5 a maggioranza B.

### Lettura

Caso istruttivo: la query è **dell'evento "rumoroso"** del generator (testo
da un cluster ma resto da un altro). Gli encoder text-driven sono ingannati
dal testo; il contrastive recupera la reaction-pattern reale.

In dati reali, questo equivale a CEO che usa retorica positiva mentre i
numeri sotto sono negativi. Un analogo "intelligente" dovrebbe pesare i
fondamentali, non solo la retorica. **Contrastive_v2 fa la cosa giusta qui;
LLM e concat_eq vengono sviati**.

Generalizzando: quando testo e numeri disaccordano (eventi "rumore strutturato"),
LLM e concat_eq sono pericolosi. Il prompt LLM non ha modo di "vedere oltre
le parole".

---

## Caso C — Disagreement netto — `evt_0037`, cluster A, hard, AMD/tech

**Query**: "Average selling prices expanded again this quarter on richer mix.
We are not seeing any pricing pressure across the AI portfolio. Demand-supply
imbalance persists."

Vicino al limite del cluster A (centroid dist 3.60). Numeri:
- Macro: VIX=16, yield=4.1, spread=3.5 → cluster A coerente
- Micro: ret60d=**0.32** (estremo positivo), vol=**0.13** (estremo basso) → A outlier
- Reaction: return=0.07, vol=0.36, dd=-0.14, persist=0.37 → atipica per A (return basso, drawdown grande, persistenza bassa)

Quindi: testo+macro=A, reazione atipica (più simile a recovery o noise).

### Esiti

| Encoder | same-cluster (A) | mean react-dist | scelte |
|---|---|---|---|
| llm_v3 | **5/5** A | **1.35** | tutti tech-A, semantica/text coerente |
| concat_eq | **5/5** A | 1.82 | identico a llm_v3 sui primi 3 |
| contrastive_v2 | **0/5** A | 2.04 | tutti C (recovery) |

### Quale ha "ragione"?

Domanda non banale. Dipende dall'obiettivo:

- **Se cerchi "altri eventi narrativi simili"**: llm_v3 e concat_eq.
  L'evento è un AI euphoria con micro outlier; gli analoghi narrativi
  giusti sono altri eventi A.
- **Se cerchi "altri eventi con reazione simile"**: contrastive_v2.
  return=0.07 + persist=0.37 + dd=-0.14 sono atipici per A pieno
  (return=0.10 medio, persist=0.55, dd=-0.06). Sono più tipici di
  recovery. Contrastive trova eventi C con reazioni simili a quelle
  osservate.

Il top-1 di llm_v3 (**evt_0028**, A/GM consumer) ha **reaction-dist=0.41
rank p0** — la reazione più vicina in tutto il training set, e same cluster.
**Smart hit emblematico**: cross-sector (GM/consumer in cluster A grazie a
cross-pollination), reaction quasi identica, narrativa coerente.

Contrastive_v2 NON trova questo perché il suo MLP-space è dominato dalla
reaction-geometry e GM/consumer evt_0028 ha ranking minore nello spazio
contrastive (probabilmente perché il MLP ha mappato GM più vicino a recovery
nella sua geometria appresa).

**Mia interpretazione**: per un analista umano leggere "demand-supply imbalance
persists" è un segnale forte di AI euphoria. La reazione atipica è un
"second-order" (forse l'azione era già pricedin pre-announcement). I top-5
giusti sono gli A, non i C. **llm_v3 vince**.

Ma contrastive_v2 non è "stupido": ha colto un secondo pattern legittimo
(reaction shape simile a recovery surprise events). Un sistema più maturo
dovrebbe mostrare **entrambe le viste** insieme.
