# Diagnostic findings — Level 1

## 1. Contrastive collapse (v1) — confermato

`diagnostics/contrastive_diag.py` su `data/mock_events.json`:

- **Distribuzione cos(reaction)**: 99.0% delle coppie ha `cos > 0.7`, 0% ha `cos < 0`.
  Tutti i vettori reaction vivono in un cono angolare stretto (tutte le componenti
  positivamente correlate). Le soglie pos/neg di v1 (0.7 / 0.0) non producono
  insiemi distinti.
- **Conseguenza InfoNCE**: con `batch_size=32`, in media ~30/31 dei "negativi in-batch"
  sono in realtà coppie positive. Segnale di training nullo → loss appiattita a
  `ln(K) ≈ 3.05`.
- **Mode collapse**: dopo 80 epoche tutti gli embedding test convergono al
  ~singolo punto. Within-cluster cosine sim = 1.000, cross-cluster sim = 0.998,
  gap = **0.001**. P@5 rimane alto (0.985) solo per tie-breaking via noise
  numerico, ma ReactCorr crolla a 0.36.

### Fix in v2 (`approach_3_contrastive_v2.py`)

1. Reaction similarity = euclidean su reaction z-scored (Standardizer fit su
   training).
2. Soglie pos/neg sui quantili 20/80 della distribuzione effettiva.
3. Negativi esplicitamente campionati (non in-batch).

**Esito v2 su Level 1**:
- Loss 3.05 → **0.04** in 40 epoche.
- ReactCorr 0.36 → **0.52** (vicino al backbone 0.55).
- Pair split bilanciato 20/20, 132/132 anchor validi.
- Mode collapse risolto.
- Trade-off: P@5 cala a 0.89 (training non più cluster-preserving by accident).

## 2. LLM JSON failures — root cause: vocabularies semanticamente sovrapposti

`diagnostics/llm_probe.py` (qwen2.5:7b, format=json, T=0, full dataset n=176):

| status | count |
|---|---|
| ok | 140 |
| json_parse_error | 0 |
| vocab_violation | 36 |

**Tutte e 36** le violazioni sono **cross-field swaps** fra due campi:

| token errato | osservato in | dovrebbe stare in | conteggio |
|---|---|---|---|
| `in_line` | `dominant_narrative` | `surprise_type` | 16 |
| `guidance_cut` | `surprise_type` | `dominant_narrative` | 11 |
| `guidance_raise` | `surprise_type` | `dominant_narrative` | 9 |

Nessuna violazione sui campi `risk_asymmetry`, `implicit_cycle_phase`,
`confidence_level` (vocabolari semanticamente disgiunti dagli altri).

### Conseguenza

`format=json` di Ollama valida la sintassi JSON ma non l'enum. Il modello
sceglie il token per significato semantico, non per appartenenza al campo
dichiarato. Su un dataset più rumoroso questo errore esploderà perché la
ambiguità tra "narrative di guidance" e "tipo di sorpresa di guidance" è
strutturale al vocabolario, non al dataset.

### Fix proposti (in ordine di costo crescente)

1. **Rinomina i token per disambiguare il campo**:
   - `narrative.guidance_raise` → `narrative.guidance_raised_outlook`
   - `narrative.guidance_cut` → `narrative.guidance_lowered_outlook`
   - `surprise.in_line` → `surprise.in_line_result`
   - `surprise.guidance_only` → `surprise.no_eps_only_guidance`
   Costo: solo prompt + one-hot vocab.
2. **JSON schema con enum stretti** via `/api/chat` + `tools=[{...}]`
   (function calling). Ollama supporta strict mode su alcuni modelli — verificare
   per qwen2.5:7b.
3. **Decomposizione in chiamate per-campo**: una chiamata per `narrative`,
   una per `surprise`, etc. Costo: 5× wall time per evento (~3000s su 176 eventi).
4. **Repair pass**: se un token è out-of-vocab nel suo campo ma in-vocab in un altro,
   swap automaticamente. Cheapest. Soluzione tattica buona per ora.

Su Level 1 il repair pass recupererebbe **tutti 36** i fallimenti senza una sola
chiamata aggiuntiva al modello.

## 3. Implicazioni per Level 2

- Contrastive v2 dovrebbe scalare meglio: la definizione di positives ora
  riflette struttura vera del reaction-space, non un threshold arbitrario.
- LLM: applicare almeno il fix 1 (rinomina) prima del prossimo run, altrimenti
  i ~20% di fallimenti corrente diventeranno 40–60% con segnali ambigui.
