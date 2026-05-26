# SITUATION REPORT — Discovery Phase Final

**Data**: 2026-05-26
**Stato**: Discovery Phase completata. Pivot strategico effettuato.

Questo documento sostituisce gli update precedenti come stato corrente del progetto per consultazioni future.

---

## Sintesi in una frase

Il progetto si riposiziona da *"deep representation learning for financial analogies"* a *"structured macro-contextual retrieval based on regime anchoring"*, dopo che il blind A/B test v2 con baseline random e ground truth umana ha invalidato la narrativa "contrastive_v2 vincitore basato su ReactCorr".

## Primary engine

**`concat_eq`** (regime anchoring via concatenazione standardizzata di feature macro, micro, semantiche + embedding testuale MiniLM).

- Vincitore blind A/B v2 su tutte e 4 le metriche umane (same_dynamic, same_regime, same_surprise, mental_precedent).
- Statisticamente significativo vs random su tutte e 4 le metriche (Mann-Whitney p<0.05).
- 15/20 top performers (vs contrastive_v2 5/20, random 0/20).
- 4/45 hard failures (vs contrastive_v2 16/45, random 26/45).

## Approcci archiviati

| Branch | Versioni | Status | Motivo |
|---|---|---|---|
| Contrastive learning | v1, v2, v3 | Archived 2026-05-26 | Optimize "reactional geometry" — proprietà reale ma cognitivamente non utile. ReactCorr 0.318 (top statistico) → 16/45 hard failures umani. |
| LLM structured | v1, v2, v3 | Archived 2026-05-25 | Fail rate 23% su N=500 real. Mismatch generativo↔discriminativo. |

Entrambe le branch sono mantenute come case study di failure modes — non eliminate. Vedi `approaches/archived/README_CONTRASTIVE_ARCHIVE.md` e `README_LLM_ARCHIVE.md`.

## Lezione centrale

**ReactCorr era *optimizing the wrong ontology*.** Misurava una proprietà reale (coerenza nelle reazioni di prezzo tra eventi vicini nello spazio appreso) ma quella proprietà non corrisponde a "utilità per ragionamento analogico umano". Optimizing the wrong ontology è il failure mode più pericoloso perché passa inosservato: produce numeri belli su metriche tecnicamente corrette e ti convinci di avere un vincitore.

**Antidoto**: validazione qualitativa umana con baseline random come metodologia obbligatoria. Lezioni metodologiche complete #14 e #15 in `PROGRESS.md`.

## Cosa fa il sistema (definizione corrente)

Dato un evento finanziario (es. un earnings 8-K), recupera precedenti storici che condividono:

- Stesso regime macro (VIX, yield curve, credit spread, dxy)
- Stesso settore GICS o settore correlato
- Stesso tipo di sorpresa rispetto alle aspettative
- Tono semantico vicino (Loughran-McDonald)
- Fase di mercato compatibile

I mercati hanno regimi macro-temporali ricorrenti (le combinazioni VIX-yields-credit-settore-narrative-sorpresa si ripetono perché il ciclo economico si ripete). Catturare questi regimi è sufficiente — e fattibile con feature engineering attento e standardizzazione corretta. Non serve deep learning.

## Cosa NON fa il sistema

- Non predice prezzi
- Non impara rappresentazioni latenti profonde
- Non sostituisce l'analista (è un layer di memoria episodica)
- Non è un sistema commerciale

## Next phase

**Implementazione `concat_eq+` con narrative tags sparse.**

Estendere il primary engine con feature simboliche estratte dai testi:

- Sorpresa: beat / miss / in-line
- Direzione guidance: raise / cut / maintain
- Narrative dominante: competitive / operational / cycle / regulatory

Feature concatenate al vettore esistente. Mantiene interpretabilità e logica del regime anchoring. Architettonicamente minimale.

Parallelamente: scaling dataset N=500 → N=1500 (più precedenti per ogni regime → regime anchoring più discriminante).

## Documenti chiave

- [`README.md`](README.md) — narrativa pubblica aggiornata
- [`PROGRESS.md`](PROGRESS.md) — log cronologico completo + lezioni metodologiche
- [`evaluation/FINDINGS_DISCOVERY_PHASE.md`](evaluation/FINDINGS_DISCOVERY_PHASE.md) — documento principale della scoperta
- [`evaluation/qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md`](evaluation/qualitative/reviews/blind_test_v2_20260525_213305_REPORT.md) — output completo dell'analisi blind v2
- [`approaches/archived/README_CONTRASTIVE_ARCHIVE.md`](approaches/archived/README_CONTRASTIVE_ARCHIVE.md) — motivazione archiviazione contrastive
- [`approaches/archived/README_LLM_ARCHIVE.md`](approaches/archived/README_LLM_ARCHIVE.md) — motivazione archiviazione LLM
