# LLM Structured Encoder — Archived Branch

Status: Frozen, not abandoned. Da rivisitare con modello più capace e schema ridisegnato.

## Why archived

Su dati reali N=500, l'approccio LLM structured encoder ha mostrato fallimenti strutturali, non implementativi:

1. **Fail rate 23%** (115/500) — sopra qualsiasi soglia di produzione accettabile
2. **ReactCorr 0.052** — peggio del baseline concat_eq, molto peggio di contrastive_v2 (0.318)
3. **Costo computazionale 3 ore** per processing 500 eventi su M3 Pro con Qwen 7B locale
4. **Mismatch concettuale identificato**: stiamo chiedendo a un modello generativo (ottimizzato per prevedere token) di fare il lavoro di un modello discriminativo (imparare distanze nello spazio). La task non è ben allineata con la natura del tool.

## Cosa funzionerebbe in futuro (non priorità ora)

- Modello più capace: Qwen 32B locale o API a pagamento (GPT-4o mini, Claude Haiku)
- Schema ridisegnato specifico per narrative finanziarie reali (non derivato dal mock)
- Few-shot prompting con esempi reali curati
- LLM usato in fase di feature extraction o presentation, NON come encoder spaziale primario

## Cosa NON fare

Non perdere tempo a sistemare la versione attuale con piccole modifiche. I problemi sono strutturali.
