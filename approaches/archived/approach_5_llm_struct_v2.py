"""Approach 5 v2: orthogonal vocabularies + operational definitions per field.

Changes vs v1:
- Schema redesigned so vocabularies do NOT semantically overlap across fields.
- Each field has a 5-10 word operational definition embedded in the prompt to
  reduce interpretive ambiguity.
- Same JSON-mode call to Ollama, same Standardizer pipeline for numeric blocks.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
import json
import os
import time
import hashlib

import numpy as np
import requests

from ..base import (EpisodeEncoder, Standardizer, vec_from, CACHE_DIR, SEED)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")

# Orthogonal vocabularies — no token reused across fields.
POLARITY = ["positive", "negative", "neutral"]
SURPRISE_MAG = ["large", "moderate", "minimal"]
DRIVER = ["demand", "margins", "guidance", "macro", "competitive", "operational"]
ASYMM = ["upside", "downside", "balanced"]
CYCLE = ["early", "mid", "late", "recession", "recovery"]

DEFINITIONS = {
    "event_polarity": "complessivo segno della news per investitori dell'asset",
    "surprise_magnitude": "ampiezza dello scostamento rispetto alle attese di mercato",
    "dominant_driver": "fattore principale che ha generato il movimento dell'evento",
    "risk_asymmetry": "direzione prevalente del rischio residuo dopo l'evento",
    "cycle_phase": "fase del ciclo economico-mercato implicita nel contesto",
    "confidence_level": "fiducia del management nel proprio outlook (1 bassa, 5 alta)",
}

PROMPT_TEMPLATE = """Sei un analista finanziario. Classifica l'evento sottostante producendo un JSON con esattamente i seguenti campi. Ogni campo ha una definizione operativa e un vocabolario chiuso: usa SOLO i valori indicati per quel campo.

Campi:
- "event_polarity" ({def_polarity}). Valori ammessi: {v_polarity}.
- "surprise_magnitude" ({def_surprise}). Valori ammessi: {v_surprise}.
- "dominant_driver" ({def_driver}). Valori ammessi: {v_driver}.
- "risk_asymmetry" ({def_asym}). Valori ammessi: {v_asym}.
- "cycle_phase" ({def_cycle}). Valori ammessi: {v_cycle}.
- "confidence_level" ({def_conf}). Valori ammessi: intero in 1..5.

Restituisci SOLO il JSON, nient'altro.

Evento:
{text}
"""


def _format_vocab(vals):
    return ", ".join(f'"{v}"' for v in vals)


def _build_prompt(text: str) -> str:
    return PROMPT_TEMPLATE.format(
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


def _ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _call_ollama_v2(text: str, max_retries: int = 2) -> Optional[dict]:
    prompt = _build_prompt(text)
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
                print(f"[llm_v2] failed after {max_retries+1} tries: {e}")
        time.sleep(0.5)
    return None


def _validate_v2(obj: dict) -> bool:
    try:
        return (obj["event_polarity"] in POLARITY
                and obj["surprise_magnitude"] in SURPRISE_MAG
                and obj["dominant_driver"] in DRIVER
                and obj["risk_asymmetry"] in ASYMM
                and obj["cycle_phase"] in CYCLE
                and isinstance(obj["confidence_level"], (int, float))
                and 1 <= int(obj["confidence_level"]) <= 5)
    except Exception:
        return False


def _onehot(val, vocab) -> np.ndarray:
    v = np.zeros(len(vocab), dtype=np.float32)
    if val in vocab:
        v[vocab.index(val)] = 1.0
    return v


def _mock_v2(event: Dict[str, Any]) -> dict:
    cluster = event.get("ground_truth_cluster", "NOISE")
    h = int(hashlib.md5(event["id"].encode()).hexdigest(), 16)
    rng = np.random.default_rng(h)
    base = {
        "A": ("positive", "large",    "demand",      "upside",   "early",    5),
        "B": ("negative", "moderate", "guidance",    "downside", "late",     2),
        "C": ("negative", "large",    "margins",     "downside", "recession",2),
        "D": ("positive", "moderate", "guidance",    "upside",   "recovery", 4),
        "NOISE": ("neutral","minimal","macro",       "balanced", "mid",      3),
    }
    p, sm, d, a, c, cf = base.get(cluster, base["NOISE"])
    if rng.random() < 0.15: p = rng.choice(POLARITY)
    if rng.random() < 0.15: sm = rng.choice(SURPRISE_MAG)
    return {"event_polarity": p, "surprise_magnitude": sm, "dominant_driver": d,
            "risk_asymmetry": a, "cycle_phase": c, "confidence_level": int(cf)}


class LLMStructuredEncoderV2(EpisodeEncoder):
    name = "llm_structured_v2"

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.use_mock = force_mock or not _ollama_available()
        if self.use_mock and not force_mock:
            print("[llm_v2] Ollama unreachable -> using mock fallback")
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()
        suffix = "_mock" if self.use_mock else ""
        self.cache_path = os.path.join(
            CACHE_DIR, f"llm_struct_v2_{OLLAMA_MODEL.replace(':','_')}{suffix}.json")
        self.cache: Dict[str, dict] = {}
        if os.path.exists(self.cache_path):
            with open(self.cache_path) as f:
                self.cache = json.load(f)
        self.fail_count = 0

    def _save_cache(self):
        with open(self.cache_path, "w") as f:
            json.dump(self.cache, f)

    def fit(self, events: List[Dict[str, Any]]) -> None:
        self.std_macro.fit(np.stack([vec_from(e, "macro") for e in events]))
        self.std_micro.fit(np.stack([vec_from(e, "micro") for e in events]))
        self.std_sem.fit(np.stack([vec_from(e, "semantic") for e in events]))
        from tqdm import tqdm
        for e in tqdm(events, desc=f"[{self.name}] LLM encode train", leave=False):
            self._struct(e)
        self._save_cache()

    def _struct(self, event: Dict[str, Any]) -> dict:
        key = hashlib.md5(event["text"].encode("utf-8")).hexdigest()
        if key in self.cache:
            return self.cache[key]
        if self.use_mock:
            obj = _mock_v2(event)
        else:
            obj = _call_ollama_v2(event["text"])
            if obj is None:
                self.fail_count += 1
                obj = _mock_v2(event)
        self.cache[key] = obj
        return obj

    def _llm_vec(self, obj: dict) -> np.ndarray:
        return np.concatenate([
            _onehot(obj["event_polarity"], POLARITY),
            _onehot(obj["surprise_magnitude"], SURPRISE_MAG),
            _onehot(obj["dominant_driver"], DRIVER),
            _onehot(obj["risk_asymmetry"], ASYMM),
            _onehot(obj["cycle_phase"], CYCLE),
            np.array([float(obj["confidence_level"]) / 5.0], dtype=np.float32),
        ])

    def encode(self, event: Dict[str, Any]) -> np.ndarray:
        obj = self._struct(event)
        llm = self._llm_vec(obj)
        macro = self.std_macro.transform(vec_from(event, "macro")[None, :])[0]
        micro = self.std_micro.transform(vec_from(event, "micro")[None, :])[0]
        sem = self.std_sem.transform(vec_from(event, "semantic")[None, :])[0]
        return np.concatenate([llm, macro, micro, sem]).astype(np.float32)

    def encode_batch(self, events: List[Dict[str, Any]]) -> np.ndarray:
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
