"""Approach 5 v3: LLM structured with directive prompt.

Same orthogonal vocabularies as v2; adds an INSTRUCTIONS block to force the
model toward decisive, text-grounded choices rather than defaults (mid, etc.).
"""
from __future__ import annotations
from typing import Dict, Any
import json
import os
import time
import hashlib

import numpy as np
import requests

from .approach_5_llm_struct_v2 import (
    POLARITY, SURPRISE_MAG, DRIVER, ASYMM, CYCLE, DEFINITIONS,
    _format_vocab, _ollama_available, _validate_v2, _onehot, _mock_v2,
    OLLAMA_URL, OLLAMA_MODEL,
)
from ..base import (EpisodeEncoder, Standardizer, vec_from, CACHE_DIR, SEED)


PROMPT_TEMPLATE_V3 = """Sei un analista finanziario. Classifica l'evento sottostante producendo un JSON con esattamente i seguenti campi. Ogni campo ha una definizione operativa e un vocabolario chiuso: usa SOLO i valori indicati per quel campo.

Campi:
- "event_polarity" ({def_polarity}). Valori ammessi: {v_polarity}.
- "surprise_magnitude" ({def_surprise}). Valori ammessi: {v_surprise}.
- "dominant_driver" ({def_driver}). Valori ammessi: {v_driver}.
- "risk_asymmetry" ({def_asym}). Valori ammessi: {v_asym}.
- "cycle_phase" ({def_cycle}). Valori ammessi: {v_cycle}.
- "confidence_level" ({def_conf}). Valori ammessi: intero in 1..5.

INSTRUCTIONS FOR CLASSIFICATION:
- Be decisive. Choose the most specific value supported by the text, not the safest one.
- For cycle_phase: if the text explicitly mentions "late cycle", "cycle maturity", "late-stage", "extended cycle", classify as "late". Do not default to "mid" when clear markers of other phases are present.
- For dominant_driver: if multiple drivers are present, choose the primary one based on emphasis and detail in the text.
- For confidence_level: reserve 4-5 only when language is unambiguous; use 2-3 for typical earnings calls; use 1 for highly hedged or uncertain content.

Restituisci SOLO il JSON, nient'altro.

Evento:
{text}
"""


def _build_prompt_v3(text: str) -> str:
    return PROMPT_TEMPLATE_V3.format(
        def_polarity=DEFINITIONS["event_polarity"],
        v_polarity=_format_vocab(POLARITY),
        def_surprise=DEFINITIONS["surprise_magnitude"],
        v_surprise=_format_vocab(SURPRISE_MAG),
        def_driver=DEFINITIONS["dominant_driver"],
        v_driver=_format_vocab(DRIVER),
        def_asym=DEFINITIONS["risk_asymmetry"],
        v_asym=_format_vocab(ASYMM),
        def_cycle=DEFINITIONS["cycle_phase"],
        v_cycle=_format_vocab(CYCLE),
        def_conf=DEFINITIONS["confidence_level"],
        text=text,
    )


def _call_ollama_v3(text: str, max_retries: int = 2):
    prompt = _build_prompt_v3(text)
    for attempt in range(max_retries + 1):
        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                      "options": {"temperature": 0.0, "seed": SEED},
                      "format": "json"},
                timeout=120,
            )
            r.raise_for_status()
            raw = r.json().get("response", "")
            obj = json.loads(raw)
            if _validate_v2(obj):
                return obj
        except Exception as e:
            if attempt == max_retries:
                print(f"[llm_v3] failed after {max_retries+1} tries: {e}")
        time.sleep(0.5)
    return None


class LLMStructuredEncoderV3(EpisodeEncoder):
    name = "llm_structured_v3"

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.use_mock = force_mock or not _ollama_available()
        if self.use_mock and not force_mock:
            print("[llm_v3] Ollama unreachable -> using mock fallback")
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()
        suffix = "_mock" if self.use_mock else ""
        self.cache_path = os.path.join(
            CACHE_DIR, f"llm_struct_v3_{OLLAMA_MODEL.replace(':','_')}{suffix}.json")
        self.cache: Dict[str, dict] = {}
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as f:
                self.cache = json.load(f)
        self.fail_count = 0

    def _save_cache(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def fit(self, events) -> None:
        self.std_macro.fit(np.stack([vec_from(e, "macro") for e in events]))
        self.std_micro.fit(np.stack([vec_from(e, "micro") for e in events]))
        self.std_sem.fit(np.stack([vec_from(e, "semantic") for e in events]))
        from tqdm import tqdm
        for e in tqdm(events, desc=f"[{self.name}] LLM encode train", leave=False):
            self._struct(e)
        self._save_cache()

    def _struct(self, event):
        key = hashlib.md5(event["text"].encode("utf-8")).hexdigest()
        if key in self.cache:
            return self.cache[key]
        if self.use_mock:
            obj = _mock_v2(event)
        else:
            obj = _call_ollama_v3(event["text"])
            if obj is None:
                self.fail_count += 1
                obj = _mock_v2(event)
        self.cache[key] = obj
        return obj

    def _llm_vec(self, obj):
        return np.concatenate([
            _onehot(obj["event_polarity"], POLARITY),
            _onehot(obj["surprise_magnitude"], SURPRISE_MAG),
            _onehot(obj["dominant_driver"], DRIVER),
            _onehot(obj["risk_asymmetry"], ASYMM),
            _onehot(obj["cycle_phase"], CYCLE),
            np.array([float(obj["confidence_level"]) / 5.0], dtype=np.float32),
        ])

    def encode(self, event):
        obj = self._struct(event)
        llm = self._llm_vec(obj)
        macro = self.std_macro.transform(vec_from(event, "macro")[None, :])[0]
        micro = self.std_micro.transform(vec_from(event, "micro")[None, :])[0]
        sem = self.std_sem.transform(vec_from(event, "semantic")[None, :])[0]
        return np.concatenate([llm, macro, micro, sem]).astype(np.float32)

    def encode_batch(self, events):
        from tqdm import tqdm
        out = []
        any_new = False
        for e in tqdm(events, desc=f"[{self.name}] encode", leave=False):
            key = hashlib.md5(e["text"].encode("utf-8")).hexdigest()
            had = key in self.cache
            out.append(self.encode(e))
            if not had:
                any_new = True
        if any_new:
            self._save_cache()
        return np.stack(out)
