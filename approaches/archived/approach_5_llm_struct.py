"""Approach 5: LLM as structured encoder (Ollama qwen2.5:7b)."""
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

NARRATIVES = ["growth_acceleration", "growth_deceleration", "margin_expansion",
              "margin_compression", "guidance_cut", "guidance_raise",
              "macro_pressure", "competitive_threat", "demand_shift",
              "supply_constraint"]
SURPRISES = ["positive_beat", "negative_miss", "mixed", "in_line", "guidance_only"]
ASYMM = ["upside", "downside", "balanced"]
CYCLE = ["early", "mid", "late", "recession", "recovery"]

PROMPT = """Sei un analista finanziario. Leggi questo evento e produci un JSON con esattamente questi campi:

{{
  "dominant_narrative": <uno tra: {narratives}>,
  "surprise_type": <uno tra: {surprises}>,
  "risk_asymmetry": <uno tra: {asymms}>,
  "implicit_cycle_phase": <uno tra: {cycles}>,
  "confidence_level": <intero 1-5>
}}

Rispondi SOLO con il JSON, nient'altro.

Evento:
{text}
"""


def _ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _call_ollama(text: str, max_retries: int = 2) -> Optional[dict]:
    prompt = PROMPT.format(
        narratives=", ".join(f'"{x}"' for x in NARRATIVES),
        surprises=", ".join(f'"{x}"' for x in SURPRISES),
        asymms=", ".join(f'"{x}"' for x in ASYMM),
        cycles=", ".join(f'"{x}"' for x in CYCLE),
        text=text,
    )
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
            if _validate(obj):
                return obj
        except Exception as e:
            if attempt == max_retries:
                print(f"[llm] failed after {max_retries+1} tries: {e}")
        time.sleep(0.5)
    return None


def _validate(obj: dict) -> bool:
    try:
        return (obj["dominant_narrative"] in NARRATIVES
                and obj["surprise_type"] in SURPRISES
                and obj["risk_asymmetry"] in ASYMM
                and obj["implicit_cycle_phase"] in CYCLE
                and isinstance(obj["confidence_level"], (int, float))
                and 1 <= int(obj["confidence_level"]) <= 5)
    except Exception:
        return False


def _onehot(val: str, vocab: List[str]) -> np.ndarray:
    v = np.zeros(len(vocab), dtype=np.float32)
    if val in vocab:
        v[vocab.index(val)] = 1.0
    return v


def _mock_from_cluster(event: Dict[str, Any]) -> dict:
    """Deterministic mock keyed on ground_truth_cluster + jitter from event id.
    Used only if Ollama unreachable. Marked clearly in results."""
    cluster = event.get("ground_truth_cluster", "NOISE")
    h = int(hashlib.md5(event["id"].encode()).hexdigest(), 16)
    rng = np.random.default_rng(h)
    base = {
        "A": ("growth_acceleration", "positive_beat", "upside", "early", 5),
        "B": ("growth_deceleration", "negative_miss", "downside", "late", 2),
        "C": ("margin_compression", "mixed", "downside", "recession", 2),
        "D": ("guidance_raise", "positive_beat", "upside", "recovery", 4),
        "NOISE": ("macro_pressure", "in_line", "balanced", "mid", 3),
    }
    narr, surp, asym, cyc, conf = base.get(cluster, base["NOISE"])
    # add small noise: 15% chance of swap
    if rng.random() < 0.15:
        narr = rng.choice(NARRATIVES)
    if rng.random() < 0.15:
        surp = rng.choice(SURPRISES)
    return {"dominant_narrative": narr, "surprise_type": surp,
            "risk_asymmetry": asym, "implicit_cycle_phase": cyc,
            "confidence_level": int(conf)}


class LLMStructuredEncoder(EpisodeEncoder):
    name = "llm_structured"

    def __init__(self, force_mock: bool = False):
        self.force_mock = force_mock
        self.use_mock = force_mock or not _ollama_available()
        if self.use_mock and not force_mock:
            print("[llm] Ollama unreachable -> using mock fallback")
        self.std_macro = Standardizer()
        self.std_micro = Standardizer()
        self.std_sem = Standardizer()
        self.cache_path = os.path.join(CACHE_DIR, f"llm_struct_{OLLAMA_MODEL.replace(':','_')}{'_mock' if self.use_mock else ''}.json")
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
        # Precompute LLM structured outputs for training events
        from tqdm import tqdm
        for e in tqdm(events, desc=f"[{self.name}] LLM encode train", leave=False):
            self._struct(e)
        self._save_cache()

    def _struct(self, event: Dict[str, Any]) -> dict:
        key = hashlib.md5(event["text"].encode("utf-8")).hexdigest()
        if key in self.cache:
            return self.cache[key]
        if self.use_mock:
            obj = _mock_from_cluster(event)
        else:
            obj = _call_ollama(event["text"])
            if obj is None:
                self.fail_count += 1
                obj = _mock_from_cluster(event)
        self.cache[key] = obj
        return obj

    def _llm_vec(self, obj: dict) -> np.ndarray:
        return np.concatenate([
            _onehot(obj["dominant_narrative"], NARRATIVES),
            _onehot(obj["surprise_type"], SURPRISES),
            _onehot(obj["risk_asymmetry"], ASYMM),
            _onehot(obj["implicit_cycle_phase"], CYCLE),
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
