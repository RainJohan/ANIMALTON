"""
ANIMALTON — dog breed classifier
-----------------------------------
Uses OpenCV's own inference engine (cv2.dnn) to run a pretrained
MobileNetV2 image classifier (ImageNet), then restricts results to ONLY
dog breeds — everything else (cats, other animals, objects) is rejected
as "not recognized."

In the standard ImageNet class ordering, indices 151–268 (inclusive) are
all dog breeds — from Chihuahua through Mexican hairless dog, 118 breeds
total (things like Pomeranian, Golden Retriever, Shih-Tzu, Husky, etc.
are all in this range). Everything outside it is ignored.

Commit models/mobilenetv2-7.onnx and models/imagenet_classes.txt directly
into the repo. Until those files exist, classify_animal() runs in "DEMO
MODE" and always returns None so the rest of the app still works.
"""

import os

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "mobilenetv2-7.onnx")
LABELS_PATH = os.path.join(BASE_DIR, "models", "imagenet_classes.txt")

# Standard ImageNet ordering: indices 151-268 (inclusive) are dog breeds.
DOG_BREED_START = 151
DOG_BREED_END = 268  # inclusive

_net = None
_labels = None


def _load_model():
    global _net, _labels
    if _net is not None:
        return

    if not (os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH)):
        print("[classifier] WARNING: model files not found — running in DEMO MODE.")
        print(f"[classifier]   expected model at:  {MODEL_PATH}")
        print(f"[classifier]   expected labels at: {LABELS_PATH}")
        _net = False
        return

    try:
        _net = cv2.dnn.readNetFromONNX(MODEL_PATH)
        with open(LABELS_PATH, "r") as f:
            _labels = [line.strip() for line in f.readlines()]
        print(f"[classifier] Model loaded OK. {len(_labels)} labels.")
    except Exception as e:
        print(f"[classifier] ERROR loading model: {e}")
        _net = False


def _is_dog_breed(idx):
    return DOG_BREED_START <= idx <= DOG_BREED_END


def classify_animal(pil_image):
    """
    pil_image: a PIL.Image in RGB mode.
    Returns {"label": str, "confidence": float, "top5": list} only when
    the TOP guess is a dog breed. Returns None otherwise (including for
    cats, other animals, objects, or if the model isn't loaded) — but
    still prints the top 5 to your terminal so you can see what it saw.
    """
    _load_model()
    if _net is False:
        return None

    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    img = cv2.resize(frame, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = (img - mean) / std
    blob = cv2.dnn.blobFromImage(img)

    _net.setInput(blob)
    output = _net.forward()
    scores = output.flatten()

    exp_scores = np.exp(scores - np.max(scores))
    probs = exp_scores / exp_scores.sum()

    top5_idx = np.argsort(probs)[::-1][:5]
    top5 = [
        {"label": (_labels[i].split(",")[0].strip() if _labels else str(i)),
         "confidence": float(probs[i]),
         "is_dog_breed": _is_dog_breed(i)}
        for i in top5_idx
    ]
    print("[classifier] Top 5 guesses:")
    for t in top5:
        tag = "DOG BREED" if t["is_dog_breed"] else "ignored"
        print(f"    {t['label']:<30} {t['confidence']*100:5.1f}%  ({tag})")

    # Instead of only checking the #1 guess, find the highest-confidence
    # guess that IS a dog breed, even if something else briefly outranked
    # it (helps with mixed breeds / awkward angles).
    best_dog = None
    for i in top5_idx:
        if _is_dog_breed(int(i)):
            best_dog = int(i)
            break

    if best_dog is None:
        return None

    confidence = float(probs[best_dog])
    label = _labels[best_dog] if _labels else f"class_{best_dog}"
    label = label.split(",")[0].strip()

    return {"label": label, "confidence": confidence, "top5": top5}