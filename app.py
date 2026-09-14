"""
ANIMALTON — backend server
---------------------------
A Flask app that:
  1. Serves a "Camera" page (live capture only — no file picker/upload).
  2. Receives a captured frame from the browser (base64 PNG/JPEG).
  3. Runs it through OpenCV's DNN-based dog breed classifier (see classifier.py).
  4. If a dog breed is recognized, saves the photo + adds it to that
     breed's Pokedex-style collection (data/collection.json) — every
     capture is kept, not just the most recent.
  5. Serves a "Gallery" page (all species caught) and a "Species" page
     per breed showing every photo you've ever caught of it.

Local run:
    python app.py
Production (used automatically by the Procfile on Render/etc.):
    gunicorn app:app
"""

import base64
import io
import json
import os
import time
import uuid
from datetime import datetime

from flask import Flask, jsonify, render_template, request, abort
from PIL import Image

from classifier import classify_animal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, "static", "captures")
COLLECTION_PATH = os.path.join(BASE_DIR, "data", "collection.json")

os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(COLLECTION_PATH), exist_ok=True)

app = Flask(__name__)

# If your dog keeps saying "no animal recognized", lower this after
# checking test_classifier.py to see its real confidence numbers.
CONFIDENCE_THRESHOLD = 0.20


def load_collection():
    if not os.path.exists(COLLECTION_PATH):
        return {}
    with open(COLLECTION_PATH, "r") as f:
        return json.load(f)


def save_collection(collection):
    with open(COLLECTION_PATH, "w") as f:
        json.dump(collection, f, indent=2)


@app.template_filter("datetime")
def format_datetime(ts):
    return datetime.fromtimestamp(ts).strftime("%b %d, %Y · %I:%M %p")


@app.route("/")
def index():
    """Live-camera capture page (this is the ONLY way images get in)."""
    return render_template("index.html")


@app.route("/gallery")
def gallery():
    """Pokedex-style grid — one card per species caught."""
    collection = load_collection()
    entries = sorted(collection.values(), key=lambda e: e["first_caught"])
    return render_template("gallery.html", entries=entries)


@app.route("/species/<label>")
def species_detail(label):
    """Full photo history for a single species — every catch, not just the latest."""
    collection = load_collection()
    entry = collection.get(label)
    if entry is None:
        abort(404)
    # Most recent photo first
    photos = sorted(entry["photos"], key=lambda p: p["caught_at"], reverse=True)
    return render_template("species.html", entry=entry, photos=photos)


@app.route("/api/capture", methods=["POST"])
def api_capture():
    """
    Receives a single frame captured live from the browser's camera stream
    (see static/js/camera.js — it is NEVER a file upload; it's a canvas
    snapshot of an active getUserMedia video feed).
    """
    payload = request.get_json(silent=True)
    if not payload or "image" not in payload:
        return jsonify({"ok": False, "error": "No image data received."}), 400

    try:
        header, b64data = payload["image"].split(",", 1)
        img_bytes = base64.b64decode(b64data)
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return jsonify({"ok": False, "error": "Could not decode image."}), 400

    result = classify_animal(image)  # -> {"label", "confidence", "top5"} or None

    if result is None or result["confidence"] < CONFIDENCE_THRESHOLD:
        return jsonify({
            "ok": True,
            "caught": False,
            "message": "No animal recognized — try getting closer or improving the lighting.",
        })

    label = result["label"]
    confidence = result["confidence"]

    filename = f"{label.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(CAPTURES_DIR, filename)
    image.save(filepath, "JPEG", quality=88)

    collection = load_collection()
    now = time.time()
    if label not in collection:
        collection[label] = {
            "label": label,
            "first_caught": now,
            "times_caught": 0,
            "best_confidence": 0.0,
            "photos": [],
        }
    entry = collection[label]
    entry["times_caught"] += 1
    entry["best_confidence"] = max(entry["best_confidence"], confidence)
    # Every catch is kept — no more trimming to the last 5.
    entry["photos"].append({
        "file": filename,
        "confidence": confidence,
        "caught_at": now,
    })
    save_collection(collection)

    is_new = entry["times_caught"] == 1

    return jsonify({
        "ok": True,
        "caught": True,
        "new_species": is_new,
        "label": label,
        "confidence": confidence,
        "photo_url": f"/static/captures/{filename}",
    })


@app.route("/api/collection")
def api_collection():
    return jsonify(load_collection())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)