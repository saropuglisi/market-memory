"""Local Flask app for blind A/B review.

Usage:
  python -m evaluation.qualitative.serve_review                       # auto-pick latest *_data.json
  python -m evaluation.qualitative.serve_review --data <path.json>    # specific file

Opens the browser automatically. Responses are saved incrementally to
evaluation/qualitative/reviews/<review_id>_responses.json after each Save.
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import threading
import time
import webbrowser

from flask import Flask, jsonify, request, send_from_directory

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REVIEW_DIR = os.path.join(ROOT, "evaluation", "qualitative", "reviews")
STATIC_DIR = os.path.join(ROOT, "evaluation", "qualitative", "static")
os.makedirs(REVIEW_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder=None)

_state = {"data_path": None, "responses_path": None, "review_id": None}
_save_lock = threading.Lock()


def _load_data():
    with open(_state["data_path"]) as f:
        return json.load(f)


def _load_responses():
    if not os.path.exists(_state["responses_path"]):
        return {"review_id": _state["review_id"], "completed_at": None, "responses": []}
    with open(_state["responses_path"]) as f:
        return json.load(f)


def _save_responses(obj):
    with _save_lock:
        tmp = _state["responses_path"] + ".tmp"
        with open(tmp, "w") as f:
            json.dump(obj, f, indent=2)
        os.replace(tmp, _state["responses_path"])


@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/static/<path:fname>")
def static_file(fname):
    return send_from_directory(STATIC_DIR, fname)


@app.route("/api/data")
def api_data():
    return jsonify(_load_data())


@app.route("/api/responses", methods=["GET"])
def api_responses_get():
    return jsonify(_load_responses())


@app.route("/api/responses", methods=["POST"])
def api_responses_post():
    """Body either:
      legacy v1: {query_id, candidate_label, utility, insight, transferability, notes}
      v2:        {query_id, candidate_label, ratings: {<metric_key>: 1..5,...}, notes, cannot_evaluate?}
      skip:      {query_id, skipped: true}
      candidate-cannot-evaluate: {query_id, candidate_label, cannot_evaluate: true, notes}
    Upserts on (query_id, candidate_label)."""
    body = request.get_json(force=True)
    qid = body.get("query_id")
    if qid is None:
        return jsonify({"error": "query_id required"}), 400

    cur = _load_responses()
    if body.get("skipped"):
        cur["responses"] = [r for r in cur["responses"] if r.get("query_id") != qid]
        cur["responses"].append({"query_id": qid, "skipped": True})
    else:
        lbl = body.get("candidate_label")
        if lbl is None:
            return jsonify({"error": "candidate_label required"}), 400
        cur["responses"] = [r for r in cur["responses"]
                            if not (r.get("query_id") == qid and r.get("candidate_label") == lbl)
                            and not (r.get("query_id") == qid and r.get("skipped"))]
        entry = {
            "query_id": qid,
            "candidate_label": lbl,
            "notes": body.get("notes", "") or "",
        }
        if body.get("cannot_evaluate"):
            entry["cannot_evaluate"] = True
        elif "ratings" in body:
            entry["ratings"] = {k: int(v) for k, v in body["ratings"].items() if v is not None}
        else:
            # legacy v1
            entry["utility"] = int(body["utility"])
            entry["insight"] = int(body["insight"])
            entry["transferability"] = int(body["transferability"])
        cur["responses"].append(entry)
    from datetime import datetime
    cur["completed_at"] = datetime.now().isoformat(timespec="seconds")
    _save_responses(cur)
    return jsonify({"ok": True, "n_responses": len(cur["responses"])})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", help="path to *_data.json (default: latest)")
    ap.add_argument("--port", type=int, default=5000)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args()

    if args.data:
        data_path = args.data
    else:
        cands = sorted(glob.glob(os.path.join(REVIEW_DIR, "*_data.json")))
        if not cands:
            print("No *_data.json found in reviews/. Run prepare_review_data.py first.")
            return
        data_path = cands[-1]

    with open(data_path) as f:
        data = json.load(f)
    review_id = data["review_id"]
    _state["data_path"] = data_path
    _state["review_id"] = review_id
    _state["responses_path"] = os.path.join(REVIEW_DIR, f"{review_id}_responses.json")

    print(f"review_id : {review_id}")
    print(f"data      : {data_path}")
    print(f"responses : {_state['responses_path']}")
    url = f"http://127.0.0.1:{args.port}/"
    print(f"serving on {url}")

    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
