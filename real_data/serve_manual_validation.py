"""Flask app for tinder-style manual tag annotation.

Serves 25 stratified events. UI: one event at a time, header + summary +
full text scrollable, 14 tag toggle buttons grouped by 4 categories,
keyboard nav. Autosaves to manual_tags_validation.json after each click.

Usage:
  python -m real_data.serve_manual_validation                # auto port 5060
  python -m real_data.serve_manual_validation --port 5061
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import threading
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from real_data.narrative_tags_v2 import (
    NARRATIVE_TAGS_V2, TAG_KEYS_V2, CATEGORIES_V2,
)
from real_data.manual_validation import stratified_pick

PROCESSED = os.path.join(ROOT, "real_data", "processed")
EVENTS_PATH = os.path.join(PROCESSED, "sample_500.json")
SUMMARIES_PATH = os.path.join(PROCESSED, "sample_500_summaries.json")
OUT_PATH = os.path.join(PROCESSED, "manual_tags_validation.json")
STATIC_DIR = os.path.join(ROOT, "real_data", "static_manual")
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)
_state = {"picks": [], "summaries": {}}
_save_lock = threading.Lock()


def _load_annotations():
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            return json.load(f)
    return {"annotations": {}, "meta": {"tag_keys": TAG_KEYS_V2, "n_target": 25}}


def _save_annotations(data):
    with _save_lock:
        tmp = OUT_PATH + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, OUT_PATH)


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/static/<path:fname>")
def static_file(fname):
    return send_from_directory(STATIC_DIR, fname)


@app.route("/api/data")
def api_data():
    out = {
        "tags": NARRATIVE_TAGS_V2,
        "tag_keys": TAG_KEYS_V2,
        "categories": CATEGORIES_V2,
        "events": [],
    }
    for e in _state["picks"]:
        out["events"].append({
            "id": e["id"],
            "ticker": e["ticker"],
            "date": e["date"],
            "sector": e["sector"],
            "macro": {
                "vix": e["macro_features"]["vix"],
                "yield_10y": e["macro_features"]["yield_10y"],
                "credit": e["macro_features"]["credit_spread"],
            },
            "summary": _state["summaries"].get(e["id"], "[no summary available]"),
            "text": e.get("text", ""),
        })
    return jsonify(out)


@app.route("/api/annotations", methods=["GET"])
def api_annot_get():
    return jsonify(_load_annotations())


@app.route("/api/annotations", methods=["POST"])
def api_annot_post():
    """Body: {event_id, tags: {tag_key: 0/1, ...}, ticker, date, sector}.
    Upserts entire annotation for one event."""
    body = request.get_json(force=True)
    eid = body.get("event_id")
    if not eid:
        return jsonify({"error": "event_id required"}), 400
    cur = _load_annotations()
    cur["annotations"][eid] = {
        **{k: int(body["tags"].get(k, 0)) for k in TAG_KEYS_V2},
        "_ticker": body.get("ticker", ""),
        "_date": body.get("date", ""),
        "_sector": body.get("sector", ""),
    }
    _save_annotations(cur)
    return jsonify({"ok": True, "n_annotated": len(cur["annotations"])})


def write_static_html():
    """Write the index.html file (kept inline so the server is one-file)."""
    path = os.path.join(STATIC_DIR, "index.html")
    with open(path, "w") as f:
        f.write(_HTML)


_HTML = r"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Manual Tag Validation</title>
<style>
  :root {
    --bg:#f5f5f7; --fg:#1c1c1e; --muted:#6b7280; --line:#e2e2e6;
    --accent:#2766d6; --ok:#16a34a; --warn:#d65a2d;
    --catA:#7c3aed; --catB:#0891b2; --catC:#d97706; --catD:#16a34a;
  }
  *{box-sizing:border-box;}
  html,body{height:100%;margin:0;}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
       color:var(--fg);background:var(--bg);display:flex;flex-direction:column;
       padding:10px 16px;gap:8px;overflow:hidden;}
  header{display:flex;align-items:center;gap:12px;flex:0 0 auto;}
  header h1{font-size:14px;margin:0;font-weight:600;}
  .progress-track{flex:1;height:8px;background:#e4e6ea;border-radius:4px;overflow:hidden;}
  .progress-fill{height:100%;background:var(--accent);transition:width .2s;}
  .counter{font-size:12px;color:var(--muted);white-space:nowrap;}
  .save-status{font-size:11px;color:var(--muted);}
  .main{flex:1;display:grid;grid-template-columns:1.4fr 1fr;gap:12px;min-height:0;}
  .col{display:flex;flex-direction:column;gap:8px;min-height:0;}
  .card{background:white;border:1px solid var(--line);border-radius:8px;padding:10px 14px;}
  .meta-card{flex:0 0 auto;}
  .meta-card .head{font-size:15px;font-weight:600;}
  .meta-card .sub{font-size:11px;color:var(--muted);margin-top:2px;}
  .summary-card{flex:0 0 auto;background:#eaf0ff;border-left:4px solid var(--accent);}
  .summary-card .label{font-size:10px;font-weight:700;letter-spacing:1px;color:var(--accent);
                       text-transform:uppercase;margin-bottom:4px;}
  .summary-card .text{font-size:13px;line-height:1.45;color:#1d2c4a;}
  .text-card{flex:1 1 auto;min-height:0;display:flex;flex-direction:column;}
  .text-card .label{font-size:10px;font-weight:700;letter-spacing:1px;color:var(--muted);
                    text-transform:uppercase;margin-bottom:4px;flex:0 0 auto;}
  .text-card .body{flex:1;overflow:auto;font:13px ui-monospace,monospace;white-space:pre-wrap;
                   background:#fafafa;padding:8px 10px;border-radius:4px;line-height:1.4;}
  .tags-card{flex:1 1 auto;overflow:auto;}
  .cat{margin-bottom:10px;}
  .cat-label{font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;}
  .cat-A{color:var(--catA);} .cat-B{color:var(--catB);}
  .cat-C{color:var(--catC);} .cat-D{color:var(--catD);}
  .tag-row{display:flex;align-items:center;gap:8px;padding:6px 8px;border-radius:4px;
           cursor:pointer;user-select:none;border:1px solid transparent;margin-bottom:2px;}
  .tag-row:hover{background:#f5f5f7;border-color:var(--line);}
  .tag-row.active{background:#dbeafe;border-color:var(--accent);}
  .tag-row.active .tag-toggle{background:var(--accent);color:white;border-color:var(--accent);}
  .tag-toggle{width:28px;height:24px;border:1.5px solid var(--line);border-radius:4px;
              display:inline-flex;align-items:center;justify-content:center;
              font-weight:700;font-size:12px;color:var(--muted);background:white;}
  .tag-name{font-size:13px;font-weight:600;flex:1;}
  .tag-desc{font-size:11px;color:var(--muted);margin-top:2px;line-height:1.3;}
  .nav{display:flex;gap:8px;justify-content:flex-end;flex:0 0 auto;}
  .btn{padding:8px 16px;font:inherit;font-weight:600;border-radius:5px;cursor:pointer;
       border:1px solid var(--line);background:white;}
  .btn.prev{color:var(--muted);}
  .btn.next{background:var(--accent);color:white;border-color:var(--accent);font-size:14px;padding:8px 22px;}
  .btn.next:disabled{background:#bbb;border-color:#bbb;cursor:not-allowed;}
  .hint{font-size:11px;color:var(--muted);margin-top:4px;}
  .kbd{display:inline-block;background:#eee;padding:1px 5px;border-radius:3px;
       font:11px ui-monospace,monospace;}
</style>
</head>
<body>

<header>
  <h1 id="title">Manual Tag Validation</h1>
  <div class="progress-track"><div class="progress-fill" id="bar" style="width:0%"></div></div>
  <span class="counter" id="counter">0/0</span>
  <span class="save-status" id="save">idle</span>
</header>

<div class="main">
  <div class="col">
    <div class="card meta-card">
      <div class="head" id="evt-head">—</div>
      <div class="sub" id="evt-sub"></div>
      <div class="sub" id="evt-macro"></div>
    </div>
    <div class="card summary-card">
      <div class="label">Narrative summary</div>
      <div class="text" id="evt-summary">—</div>
    </div>
    <div class="card text-card">
      <div class="label">Full text (scroll)</div>
      <div class="body" id="evt-text"></div>
    </div>
  </div>
  <div class="col">
    <div class="card tags-card" id="tags-block"></div>
    <div class="nav">
      <button class="btn prev" id="prev-btn">← Prev</button>
      <button class="btn next" id="next-btn">NEXT →</button>
    </div>
    <div class="hint">
      Click a tag to toggle. Default = 0 (no).
      <span class="kbd">←</span>/<span class="kbd">→</span> nav,
      <span class="kbd">Enter</span> next.
      Autosave on every click.
    </div>
  </div>
</div>

<script>
let DATA = null;
let ANNOT = {};         // event_id -> {tag_key: 0/1}
let cursor = 0;
let _inflight = 0;

async function fetchJSON(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return await r.json();
}
function setSave(state, msg) {
  const el = document.getElementById('save');
  const colors = {idle:'var(--muted)', saving:'var(--accent)', saved:'var(--ok)', error:'var(--warn)'};
  el.style.color = colors[state] || 'var(--muted)';
  el.textContent = msg || state;
}

async function init() {
  DATA = await fetchJSON('/api/data');
  const saved = await fetchJSON('/api/annotations');
  for (const eid in (saved.annotations || {})) {
    const v = saved.annotations[eid];
    ANNOT[eid] = {};
    for (const k of DATA.tag_keys) ANNOT[eid][k] = v[k] || 0;
  }
  cursor = DATA.events.findIndex(e => !ANNOT[e.id]);
  if (cursor < 0) cursor = DATA.events.length - 1;
  buildTagsUI();
  document.getElementById('prev-btn').addEventListener('click', () => { cursor=Math.max(0,cursor-1); render(); });
  document.getElementById('next-btn').addEventListener('click', () => { cursor=Math.min(DATA.events.length-1,cursor+1); render(); });
  document.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft' && !e.target.matches('input,textarea')) { cursor=Math.max(0,cursor-1); render(); }
    if ((e.key === 'ArrowRight' || e.key === 'Enter') && !e.target.matches('input,textarea')) { cursor=Math.min(DATA.events.length-1,cursor+1); render(); }
  });
  render();
}

function buildTagsUI() {
  const blk = document.getElementById('tags-block');
  blk.innerHTML = '';
  const catLabels = {A_outcome:'A. Outcome', B_drivers:'B. Drivers', C_capital:'C. Capital', D_thematic:'D. Thematic'};
  const catClass = {A_outcome:'cat-A', B_drivers:'cat-B', C_capital:'cat-C', D_thematic:'cat-D'};
  for (const [cat, tags] of Object.entries(DATA.categories)) {
    const div = document.createElement('div');
    div.className = 'cat';
    div.innerHTML = `<div class="cat-label ${catClass[cat]}">${catLabels[cat]}</div>`;
    for (const tag of tags) {
      const row = document.createElement('div');
      row.className = 'tag-row';
      row.dataset.tag = tag;
      row.innerHTML = `
        <span class="tag-toggle" data-tag="${tag}">0</span>
        <div style="flex:1">
          <div class="tag-name">${tag}</div>
          <div class="tag-desc">${escapeHtml(DATA.tags[tag] || '')}</div>
        </div>`;
      row.addEventListener('click', () => toggle(tag));
      div.appendChild(row);
    }
    blk.appendChild(div);
  }
}

function ensureBucket(eid) {
  if (!ANNOT[eid]) {
    ANNOT[eid] = {};
    for (const k of DATA.tag_keys) ANNOT[eid][k] = 0;
  }
  return ANNOT[eid];
}

function toggle(tag) {
  const ev = DATA.events[cursor];
  const b = ensureBucket(ev.id);
  b[tag] = b[tag] ? 0 : 1;
  updateTagUI();
  save(ev);
}

function updateTagUI() {
  const ev = DATA.events[cursor];
  const b = ANNOT[ev.id] || {};
  document.querySelectorAll('.tag-row').forEach(r => {
    const tag = r.dataset.tag;
    const on = b[tag] === 1;
    r.classList.toggle('active', on);
    r.querySelector('.tag-toggle').textContent = on ? '1' : '0';
  });
}

async function save(ev) {
  _inflight++;
  setSave('saving', `saving (${_inflight})`);
  try {
    const res = await fetchJSON('/api/annotations', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        event_id: ev.id, ticker: ev.ticker, date: ev.date, sector: ev.sector,
        tags: ANNOT[ev.id],
      }),
    });
    _inflight--;
    if (_inflight === 0) setSave('saved', `saved ${new Date().toLocaleTimeString()} (n=${res.n_annotated})`);
  } catch (e) {
    _inflight--;
    setSave('error', `SAVE FAILED — ${e.message}`);
  }
  updateProgress();
}

function updateProgress() {
  const total = DATA.events.length;
  const done = Object.keys(ANNOT).length;
  document.getElementById('bar').style.width = (100*done/total)+'%';
  document.getElementById('counter').textContent = `${done}/${total} annotated`;
}

function render() {
  const ev = DATA.events[cursor];
  document.getElementById('title').textContent =
    `Manual Tag Validation — Event ${cursor+1}/${DATA.events.length}`;
  document.getElementById('evt-head').textContent = `${ev.ticker}  ·  ${ev.date}  ·  ${ev.sector}`;
  document.getElementById('evt-sub').textContent = `id: ${ev.id}`;
  const m = ev.macro || {};
  document.getElementById('evt-macro').textContent =
    `VIX=${m.vix?.toFixed(1) ?? '?'}  ·  yield_10y=${m.yield_10y?.toFixed(2) ?? '?'}  ·  credit=${m.credit?.toFixed(2) ?? '?'}`;
  document.getElementById('evt-summary').textContent = ev.summary || '—';
  document.getElementById('evt-text').textContent = ev.text || '(no text)';
  document.getElementById('evt-text').scrollTop = 0;
  document.getElementById('prev-btn').disabled = cursor === 0;
  document.getElementById('next-btn').disabled = cursor >= DATA.events.length - 1;
  ensureBucket(ev.id);
  updateTagUI();
  updateProgress();
}

function escapeHtml(s) { const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

init();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5060)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    with open(EVENTS_PATH) as f:
        events = json.load(f)
    _state["picks"] = stratified_pick(events, n=25)
    if os.path.exists(SUMMARIES_PATH):
        with open(SUMMARIES_PATH) as f:
            _state["summaries"] = json.load(f)
    write_static_html()

    url = f"http://127.0.0.1:{args.port}/"
    print(f"picks: {len(_state['picks'])}  out: {OUT_PATH}")
    print(f"serving on {url}")
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
