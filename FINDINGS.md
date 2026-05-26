# FINDINGS — primo run, 2026-05-24

## Risultati (n_train=132, n_test=44, 4 cluster + NOISE)

| Approach           | P@5   | P@10  | ReactCorr | CondQual | Wall(s) |
|--------------------|-------|-------|-----------|----------|---------|
| concat_raw         | 0.985 | 0.960 | 0.547     | 0.57     | 0.12    |
| concat_eq          | 1.000 | 0.985 | 0.546     | 0.57     | 0.11    |
| factorized         | 0.980 | 0.935 | 0.550     | **1.00** | 0.08    |
| contrastive        | 0.985 | 0.895 | **0.360** | 0.57     | 1.47    |
| graph_experimental | 1.000 | 1.000 | 0.494     | 0.56     | 0.14    |
| llm_structured     | 0.995 | 0.975 | 0.543     | 0.57     | 783     |

## Osservazioni qualitative

### 1. Il dataset mock è troppo facile (saturazione P@5)
Tutti gli approcci superano P@5 ≥ 0.98. I cluster A/B/C/D sono linearmente
separabili dalle feature numeriche grezze (macro+micro+semantic). Il generator
del mock dataset codifica il cluster troppo direttamente nelle feature.
**Implicazione:** la metrica P@K non discrimina gli approcci finché non
introduciamo: (a) rumore strutturato, (b) overlap fra cluster, (c) eventi
di "regime" che oscurano l'appartenenza al cluster, oppure (d) un task
fuori-distribuzione (eventi test con feature mix non visto in training).

### 2. Reaction correlation è la metrica più informativa qui
Spearman ~0.55 per tutti tranne contrastive. Significa che lo spazio cattura
struttura predittiva al di là del cluster label.
**Sospetto:** è alto perché il generator del dataset accoppia reaction_30d
alle feature → di nuovo, struttura "iniettata". Su dati reali non aspettarsi
0.5+.

### 3. Contrastive sta peggiorando, non migliorando
Loss appiattita a ~3.05 ≈ ln(20–32) → InfoNCE non distingue positivi da negativi
in-batch. ReactCorr scende a 0.36 (peggio del backbone equalize che fa 0.55).
**Cause probabili:**
- In-batch negatives sono spesso anch'essi positivi (positivi abbondanti, dato
  che reaction_cos > 0.7 è frequente nel mock) → segnale ambiguo.
- Loss collassa perché output normalizzato + temperature 0.1 + segnale debole.
**Fix da provare:**
- Triplet loss con margin invece di InfoNCE.
- Hard-negative mining (sample esplicito di negativi con reaction_cos < 0).
- Pre-train del backbone freezzato, solo fine-tune testa.
- Aumentare temperature (0.3–0.5) per ammorbidire la softmax.

### 4. Factorized vince solo sul condizionamento
P@5/ReactCorr indistinguibili dal concat. Ma CondQual = 1.0 vs 0.57 perché
applica il filtro macro hard prima del ranking. **Insight chiave:** se l'API
prevede query condizionate ("trova analoghi solo in regime VIX > 18"),
factorized è strutturalmente l'unico approccio adatto — non puoi facilmente
condizionare un encoder monolitico. Tenere.

### 5. LLM structured: costo enorme, segnale marginale
601s fit + 181s eval = 13 minuti, contro 0.1s degli altri. Performance
in linea con concat_eq. Inoltre 36/176 chiamate (~20%) hanno fallito
validazione JSON nonostante `format=json` + temperature 0 → il modello
qwen2.5:7b in italiano segue il vocabolario chiuso solo parzialmente.
**Decisione provvisoria:** rimandare LLM finché non abbiamo (a) un dataset
in cui il testo conta davvero, (b) un modello più affidabile sul vocabolario
chiuso (qwen2.5-coder:14b? o function-calling esplicito invece di JSON mode).

### 6. Graph (placeholder) tira inaspettatamente
P@5=1.0, P@10=1.0. Sospetto: la mia random projection per sector è correlata
col cluster perché nel mock dataset settore→cluster è quasi deterministico.
**Non leggere come segnale reale.** Su dati veri ticker/settore varieranno
ortogonalmente al cluster.

## Cose che farei nel prossimo iteration

1. **Dataset generator v2:** introdurre rumore strutturato (10–20% di eventi
   con feature da cluster A ma reaction da cluster B), eventi di transizione
   di regime, eventi NOISE più rumorosi. Far scendere il P@5 floor sotto 0.7
   così le metriche discriminano.
2. **Fix contrastive:** triplet + hard negatives + temperature più alta.
3. **Misure aggiuntive:** Recall@K per cluster minoritari, ablation che
   rimuove un blocco alla volta (text-only, macro-only…) per attribuire
   quanto contribuisce ciascuna modalità.
4. **LLM:** valutare function-calling invece di JSON mode, o passare a
   un modello locale più stabile sul vocabolario chiuso.
5. **Conditional query realistici:** non solo VIX > 18, ma regimi
   compositi (yield-curve invertita + credit_spread > X) per stressare
   factorized.
6. **Stability check:** ri-eseguire con seeds 0/1/2/3/4 per stimare la
   varianza delle metriche — sospetto sia alta su n_test=44.
