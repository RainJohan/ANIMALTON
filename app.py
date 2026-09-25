"""
ANIMALTON — backend server
---------------------------
Flask app: live-camera capture (+ upload), OpenCV/DNN animal detection,
a category-organized Pokedex-style gallery (Lions, Sharks, Snakes...),
and per-species pages with individual descriptions and photo history.
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
from categories import categorize, CATEGORIES
from species_info import get_species_info

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, "static", "captures")
COLLECTION_PATH = os.path.join(BASE_DIR, "data", "collection.json")

os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(COLLECTION_PATH), exist_ok=True)

app = Flask(__name__)

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
    return render_template("index.html")


def _process_catch(image):
    """Shared logic for both camera captures and uploads."""
    result = classify_animal(image)

    if result is None or result["confidence"] < CONFIDENCE_THRESHOLD:
        return jsonify({
            "ok": True,
            "caught": False,
            "message": "No animal recognized — try getting closer or improving the lighting.",
        })

    label = result["label"]
    confidence = result["confidence"]
    # Categorize using the CLEAN label, not the full raw ImageNet label —
    # some species' synonyms accidentally contain another animal's name
    # (cougar's synonyms include "mountain lion", koala's include "koala
    # bear"), which caused real miscategorization when matched against
    # the full label. See categories.py for the targeted overrides that
    # replace that approach for genuine conflicts like "tiger cat".
    category_key = categorize(label, result.get("index"))

    filename = f"{label.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(CAPTURES_DIR, filename)
    image.save(filepath, "JPEG", quality=88)

    collection = load_collection()
    now = time.time()
    if label not in collection:
        collection[label] = {
            "label": label,
            "category": category_key,
            "first_caught": now,
            "times_caught": 0,
            "best_confidence": 0.0,
            "photos": [],
        }
    entry = collection[label]
    entry["times_caught"] += 1
    entry["best_confidence"] = max(entry["best_confidence"], confidence)
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
        "category": CATEGORIES[category_key]["name"],
        "confidence": confidence,
        "photo_url": f"/static/captures/{filename}",
    })


@app.route("/api/capture", methods=["POST"])
def api_capture():
    """Live camera frame — a canvas snapshot of the getUserMedia stream,
    never a file upload. This is what keeps 'catches' honest."""
    payload = request.get_json(silent=True)
    if not payload or "image" not in payload:
        return jsonify({"ok": False, "error": "No image data received."}), 400
    try:
        header, b64data = payload["image"].split(",", 1)
        img_bytes = base64.b64decode(b64data)
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return jsonify({"ok": False, "error": "Could not decode image."}), 400
    return _process_catch(image)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """File upload identification. NOTE: bypasses the live-camera
    anti-cheat — any saved photo can be submitted here."""
    if "photo" not in request.files:
        return jsonify({"ok": False, "error": "No file received."}), 400
    file = request.files["photo"]
    try:
        image = Image.open(file.stream).convert("RGB")
    except Exception:
        return jsonify({"ok": False, "error": "Could not read image file."}), 400
    return _process_catch(image)


@app.route("/gallery")
def gallery():
    """Top-level view: one card per category (Lions, Sharks, Snakes...)."""
    collection = load_collection()
    grouped = {}
    for entry in collection.values():
        key = entry.get("category") or categorize(entry["label"])
        grouped.setdefault(key, []).append(entry)

    category_cards = []
    for key, cat in CATEGORIES.items():
        species_list = grouped.get(key, [])
        if not species_list:
            continue
        category_cards.append({
            "key": key,
            **cat,
            "species_count": len(species_list),
            "total_catches": sum(e["times_caught"] for e in species_list),
            "cover_photo": species_list[0]["photos"][-1]["file"],
        })
    return render_template("gallery.html", categories=category_cards)


@app.route("/category/<key>")
def category_detail(key):
    """Second-level view: every species/breed caught within one category."""
    if key not in CATEGORIES:
        abort(404)
    collection = load_collection()
    species_list = [
        e for e in collection.values()
        if (e.get("category") or categorize(e["label"])) == key
    ]
    species_list.sort(key=lambda e: e["first_caught"])
    return render_template("category.html", category=CATEGORIES[key], key=key, species_list=species_list)


@app.route("/species/<label>")
def species_detail(label):
    """Third-level view: individual description, ratings and full photo
    history for one specific species."""
    collection = load_collection()
    entry = collection.get(label)
    if entry is None:
        abort(404)
    category_key = entry.get("category") or categorize(entry["label"])
    info = get_species_info(label, CATEGORIES[category_key])
    photos = sorted(entry["photos"], key=lambda p: p["caught_at"], reverse=True)
    return render_template("species.html", entry=entry, photos=photos, info=info)


@app.route("/api/collection")
def api_collection():
    return jsonify(load_collection())


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)