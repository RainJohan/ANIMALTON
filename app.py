"""
ANIMALTON — backend server
--------------------------------------------
This is a small website (made with Flask). It can:
  - take a camera photo or an uploaded photo,
  - ask the AI what animal it is,
  - save the catch in a collection,
  - show the collection in 3 levels:
        Gallery (categories)  ->  Category (species)  ->  Species (photos)
"""

import base64          # to decode the camera photo sent as text
import io              # to treat bytes like a file
import json            # to save/load the collection file
import os
import time
import uuid            # to make random unique file names
from datetime import datetime

from flask import Flask, jsonify, render_template, request, abort
from PIL import Image  # to open and save pictures

from classifier import classify_animal          # the AI (classifier.py)
from categories import categorize, CATEGORIES   # groups like "Sharks" (categories.py)
from species_info import get_species_info       # description per animal (species_info.py)

# ---------- Settings ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAPTURES_DIR = os.path.join(BASE_DIR, "static", "captures")     # saved photos
COLLECTION_PATH = os.path.join(BASE_DIR, "data", "collection.json")  # saved list

# Make the folders if they don't exist yet
os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(COLLECTION_PATH), exist_ok=True)

app = Flask(__name__)   # create the website

# The AI must be at least 20% sure, or we say "no animal found"
CONFIDENCE_THRESHOLD = 0.20


# ---------- Helpers ----------

def load_collection():
    """Read the collection from the file. Empty {} if there's no file yet."""
    if not os.path.exists(COLLECTION_PATH):
        return {}
    with open(COLLECTION_PATH, "r") as f:
        return json.load(f)


def save_collection(collection):
    """Write the collection to the file."""
    with open(COLLECTION_PATH, "w") as f:
        json.dump(collection, f, indent=2)


def get_category_key(entry):
    """Which category is this animal in? Use the saved one, or work it out."""
    return entry.get("category") or categorize(entry["label"])


@app.template_filter("datetime")
def format_datetime(timestamp):
    """Lets HTML pages show a time nicely, e.g. 'Jan 05, 2025 · 03:20 PM'."""
    return datetime.fromtimestamp(timestamp).strftime("%b %d, %Y · %I:%M %p")


# ---------- Catching an animal ----------

def process_catch(image):
    """Shared by camera AND upload: identify the animal and save it."""

    # 1. Ask the AI
    result = classify_animal(image)

    # 2. Nothing found, or AI not sure enough? Tell the user.
    if result is None or result["confidence"] < CONFIDENCE_THRESHOLD:
        return jsonify({
            "ok": True,
            "caught": False,
            "message": "No animal recognized — try getting closer or improving the lighting.",
        })

    label = result["label"]              # e.g. "hammerhead"
    confidence = result["confidence"]    # e.g. 0.87

    # 3. Find its category (e.g. "shark"), using the dog index + the name
    category_key = categorize(label, result["index"])

    # 4. Save the photo with a unique name, e.g. hammerhead_a1b2c3d4.jpg
    filename = f"{label.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.jpg"
    image.save(os.path.join(CAPTURES_DIR, filename), "JPEG", quality=88)

    # 5. Update the collection
    collection = load_collection()
    now = time.time()

    # First time we see this animal? Create a new entry for it.
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
    entry["times_caught"] += 1                                          # +1 catch
    entry["best_confidence"] = max(entry["best_confidence"], confidence)  # keep best score
    entry["photos"].append({                                            # remember the photo
        "file": filename,
        "confidence": confidence,
        "caught_at": now,
    })
    save_collection(collection)

    # 6. Send the result back to the page
    return jsonify({
        "ok": True,
        "caught": True,
        "new_species": entry["times_caught"] == 1,   # True if first time ever
        "label": label,
        "category": CATEGORIES[category_key]["name"],
        "confidence": confidence,
        "photo_url": f"/static/captures/{filename}",
    })


# ---------- Routes (the website's pages / URLs) ----------

@app.route("/")
def index():
    """Home page with the camera."""
    return render_template("index.html")


@app.route("/api/capture", methods=["POST"])
def api_capture():
    """Receives a live camera snapshot (sent as base64 text)."""
    data = request.get_json(silent=True)
    if not data or "image" not in data:
        return jsonify({"ok": False, "error": "No image data received."}), 400
    try:
        # The text looks like "data:image/jpeg;base64,AAAA..." — keep the part after the comma
        base64_text = data["image"].split(",", 1)[1]
        image = Image.open(io.BytesIO(base64.b64decode(base64_text))).convert("RGB")
    except Exception:
        return jsonify({"ok": False, "error": "Could not decode image."}), 400
    return process_catch(image)


@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Receives an uploaded photo file (any saved photo works here)."""
    if "photo" not in request.files:
        return jsonify({"ok": False, "error": "No file received."}), 400
    try:
        image = Image.open(request.files["photo"].stream).convert("RGB")
    except Exception:
        return jsonify({"ok": False, "error": "Could not read image file."}), 400
    return process_catch(image)


@app.route("/gallery")
def gallery():
    """Level 1: one card for each category you've caught something in."""
    collection = load_collection()

    # Put every animal into a group by its category
    grouped = {}
    for entry in collection.values():
        grouped.setdefault(get_category_key(entry), []).append(entry)

    # Build one card for each category that has animals
    cards = []
    for key, category in CATEGORIES.items():
        animals = grouped.get(key, [])
        if not animals:
            continue                         # skip empty categories
        cards.append({
            "key": key,
            **category,                      # name, emoji, description, etc.
            "species_count": len(animals),
            "total_catches": sum(a["times_caught"] for a in animals),
            "cover_photo": animals[0]["photos"][-1]["file"],   # newest photo of first animal
        })
    return render_template("gallery.html", categories=cards)


@app.route("/category/<key>")
def category_detail(key):
    """Level 2: all the animals you've caught in one category."""
    if key not in CATEGORIES:
        abort(404)                           # unknown category -> "not found"

    collection = load_collection()
    animals = [e for e in collection.values() if get_category_key(e) == key]
    animals.sort(key=lambda e: e["first_caught"])   # oldest first
    return render_template("category.html", category=CATEGORIES[key], key=key, species_list=animals)


@app.route("/species/<label>")
def species_detail(label):
    """Level 3: one animal — description, ratings and all its photos."""
    entry = load_collection().get(label)
    if entry is None:
        abort(404)

    category = CATEGORIES[get_category_key(entry)]
    info = get_species_info(label, category)   # own info, or the category's info
    photos = sorted(entry["photos"], key=lambda p: p["caught_at"], reverse=True)  # newest first
    return render_template("species.html", entry=entry, photos=photos, info=info)


@app.route("/api/collection")
def api_collection():
    """Returns the whole collection as JSON."""
    return jsonify(load_collection())


# ---------- Start the server ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))     # use PORT setting, or 5000
    app.run(host="0.0.0.0", port=port, debug=True)