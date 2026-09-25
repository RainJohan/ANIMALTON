"""
ANIMALTON — animal classifier
-------------------------------
Uses OpenCV's own inference engine (cv2.dnn) to run a pretrained
MobileNetV2 image classifier (ImageNet), recognizing any of the ~398
animal classes in the dataset (indices 0-397 in the standard ordering).

Returns BOTH a clean display label (e.g. "hammerhead") and the full raw
ImageNet label with all its synonyms (e.g. "hammerhead, hammerhead
shark") — categories.py uses the raw version for keyword matching, so
a species doesn't get miscategorized just because its short display
name happens to drop the word that would have identified its group.

ACCURACY NOTE: ImageNet-1k has real gaps in animal coverage — an animal
outside its 398 known classes will always get misclassified as its
nearest known class. This can't be fully fixed without a broader
wildlife-specific model (e.g. one trained on iNaturalist's 5,000+
species).
"""

import os

import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "mobilenetv2-7.onnx")
LABELS_PATH = os.path.join(BASE_DIR, "models", "imagenet_classes.txt")

ANIMAL_INDEX_CUTOFF = 398

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


def _preprocess(frame_bgr):
    h, w = frame_bgr.shape[:2]
    side = min(h, w)
    top = (h - side) // 2
    left = (w - side) // 2
    cropped = frame_bgr[top:top + side, left:left + side]

    img = cv2.resize(cropped, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = (img - mean) / std
    return cv2.dnn.blobFromImage(img)


def _run_inference(blob):
    _net.setInput(blob)
    output = _net.forward()
    scores = output.flatten()
    exp_scores = np.exp(scores - np.max(scores))
    return exp_scores / exp_scores.sum()


def classify_animal(pil_image):
    """
    pil_image: a PIL.Image in RGB mode.
    Returns {"label", "raw_label", "confidence", "index", "top5"} if the
    top guess is an animal class, otherwise None.
    """
    _load_model()
    if _net is False:
        return None

    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    probs_normal = _run_inference(_preprocess(frame))
    probs_flipped = _run_inference(_preprocess(cv2.flip(frame, 1)))
    probs = (probs_normal + probs_flipped) / 2.0

    top5_idx = np.argsort(probs)[::-1][:5]
    top5 = [
        {"label": (_labels[i].split(",")[0].strip() if _labels else str(i)),
         "confidence": float(probs[i]),
         "is_animal": i < ANIMAL_INDEX_CUTOFF}
        for i in top5_idx
    ]
    print("[classifier] Top 5 guesses:")
    for t in top5:
        tag = "animal" if t["is_animal"] else "not-animal"
        print(f"    {t['label']:<30} {t['confidence']*100:5.1f}%  ({tag})")

    top_idx = int(top5_idx[0])
    confidence = float(probs[top_idx])

    if top_idx >= ANIMAL_INDEX_CUTOFF:
        return None

    raw_label = _labels[top_idx] if _labels else f"class_{top_idx}"
    label = raw_label.split(",")[0].strip()

    return {
        "label": label,
        "raw_label": raw_label,
        "confidence": confidence,
        "index": top_idx,
        "top5": top5,
    }