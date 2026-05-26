# Contrastive Learning Branch — Archived

**Status**: Archiviato dopo Discovery Phase (2026-05-26). Non eliminato per valore come case study di failure mode.

## Cosa contiene questo branch

- `approach_3_contrastive.py` (v1) — InfoNCE su pair definiti con cos(reaction) > 0.7. Mode collapse atteso, archiviato come baseline negativo.
- `approach_3_contrastive_v2.py` — z-score + quantili 20/80 sui pair, MLP standard. Versione "principale".
- `approach_3_contrastive_v3.py` — v2 + weight decay + dropout + early stopping + noise augmentation. Tentativo anti-overfit.

## Cosa ha mostrato il branch

Le versioni v2 e v3 hanno superato il bug iniziale di mode collapse di v1 e hanno mostrato ottimi risultati sulle metriche statistiche:

- **Mock L1-L5**: ReactCorr 0.32–0.70 a seconda del livello; vincitore netto su L5 (reaction-driven).
- **Real N=500**: ReactCorr 0.318 (best tra gli encoder, +0.25 vs N=50).
- **Lift Util@5 P25**: +0.142 (best tra gli encoder, 2× vs concat_eq).
- Case study cross-sector smart hits notevoli (JNJ → PFE, IT → LRCX) che concat_eq e LLM perdevano.

Per molti mesi questa è stata la narrativa: *contrastive_v2 è il vincitore basato su ReactCorr*.

## Perché è archiviato

Il blind A/B test v2 (2026-05-26) — con baseline random come terzo gruppo, summaries narrative, 4 metriche allineate al task analitico, ground truth umana in cieco — ha invalidato la narrativa precedente:

| Metrica | contrastive_v2 | concat_eq | random |
|---|---|---|---|
| same_dynamic | 1.59 | 2.13 | 1.24 |
| same_regime | 3.16 | **4.18** | 2.38 |
| same_surprise | 3.52 | 3.93 | 3.02 |
| mental_precedent | 2.07 | **2.80** | 1.56 |
| **Hard failures (≤2)** | **16/45** | 4/45 | 26/45 |
| **Top performers (≥4)** | 5/20 | **15/20** | 0/20 |

Mann-Whitney pairwise:

- contrastive_v2 **pareggia con random** su same_dynamic (p=0.092) e same_surprise (p=0.120).
- contrastive_v2 **perde contro concat_eq** su same_regime (p=0.0005) e mental_precedent (p=0.011).

In termini operativi: il modello produce retrieval qualitativamente instabile (un terzo delle valutazioni umane sotto la soglia di accettabilità, contro un decimo per concat_eq). Quando sbaglia, sbaglia in modo radicale.

## Lesson learned

Il modello impara **reactional geometry** — coerenza nelle reazioni di prezzo tra eventi vicini nello spazio appreso. È una proprietà reale e misurabile (ReactCorr 0.318 è un numero corretto). Ma NON corrisponde a "utilità per ragionamento analogico umano".

Due eventi possono avere reazioni a 30g molto simili per ragioni totalmente diverse: uno per un beat+raise in regime risk-on, l'altro per un dividend announcement in regime difensivo. Il modello li mette vicini; l'analista li scarta come precedente inutile.

**Optimizing the wrong ontology**. Vedi [PROGRESS.md lezione metodologica #14](../../PROGRESS.md).

## Cosa potrebbe sbloccarlo in futuro

Non è obiettivo immediato, ma per ricerca pura:

- Training loss diversa (NON similarità reazioni 30g).
- Target di apprendimento allineato al regime anchoring: coppie positive = "stesso regime macro" (VIX/yields/credit/sector), non "stessa reaction-shape".
- Hard negative mining strutturato per coppie "same regime opposite reaction" (forza il modello a separare regime-similarity da reaction-similarity).
- Eventualmente encoder ibrido che combini regime features (alla concat_eq, come backbone interpretabile) con rappresentazioni apprese in modo subordinato.

## Cosa NON fare

Non riprovare a "sistemare" v2/v3 con piccole modifiche. Il problema è strutturale: il training objective (similarità reazioni 30g) non è allineato al task analitico (analoghi macro-temporali utili). Più regularization, più dati, prompt più direttivi: niente di questo cambia il fatto che il modello impara la cosa sbagliata.

Se vuoi tornare al contrastive learning per questo task, ripensare il training objective da zero — non iterare sull'esistente.
