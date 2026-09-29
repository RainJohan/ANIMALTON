"""
ANIMALTON — animal classifier (simple version)
-----------------------------------------------
What this file does:
  1. Loads a ready-made AI model (MobileNetV2) that can recognize 1000 things.
  2. Takes a photo and asks the model: "what is this?"
  3. If the answer is an animal, it returns the animal's name and how sure
     the model is. If it's not an animal, it returns None.

Why "398"? In the ImageNet list, the first 398 items are animals. Everything
after that (guitars, cars, pizza...) is not an animal.

Limit: the model only knows those 398 animals. An animal it doesn't know
will be guessed as the closest one it does know.
"""

import os

import cv2                # OpenCV: reads the AI model and edits images
import numpy as np        # NumPy: does math on lists of numbers

# ---------- Settings ----------

# The folder where this file lives, so we can find the model files next to it
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# The AI model file, and the text file with the 1000 names it can say
MODEL_PATH = os.path.join(BASE_DIR, "models", "mobilenetv2-7.onnx")
LABELS_PATH = os.path.join(BASE_DIR, "models", "imagenet_classes.txt")

# Items number 0-397 are animals. Number 398 and up are NOT animals.
ANIMAL_CUTOFF = 398

# These start empty; load_model() fills them in the first time we need them
net = None      # None = not loaded yet, False = failed to load
labels = []     # the list of names, e.g. ["tench", "goldfish", ...]


# ---------- Loading the model ----------

def load_model():
    """Load the AI model and the name list. Only does the work once."""
    global net, labels

    # Already tried before? Then don't do it again.
    if net is not None:
        return

    # If a file is missing, print a warning and give up (net = False)
    if not (os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH)):
        print("[classifier] WARNING: model files not found.")
        print(f"[classifier]   expected model at:  {MODEL_PATH}")
        print(f"[classifier]   expected labels at: {LABELS_PATH}")
        net = False
        return

    try:
        # Load the model into OpenCV
        net = cv2.dnn.readNetFromONNX(MODEL_PATH)
        # Read the names file: one name per line
        with open(LABELS_PATH, "r") as f:
            labels = [line.strip() for line in f]
        print(f"[classifier] Model loaded OK. {len(labels)} labels.")
    except Exception as e:
        print(f"[classifier] ERROR loading model: {e}")
        net = False


# ---------- Getting the image ready ----------

def prepare_image(frame):
    """Turn a normal photo into the exact shape the model expects."""
    # Cut a square out of the middle of the photo
    height, width = frame.shape[:2]
    side = min(height, width)                 # the shorter side = square size
    top = (height - side) // 2                # how much to cut from the top
    left = (width - side) // 2                # how much to cut from the left
    square = frame[top:top + side, left:left + side]

    # Shrink it to 224 x 224 pixels (the size the model was trained on)
    img = cv2.resize(square, (224, 224))

    # OpenCV uses Blue-Green-Red colors, the model wants Red-Green-Blue.
    # Also change pixel values from 0-255 to 0-1.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # Normalize the colors using the same numbers the model was trained with
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img = (img - mean) / std

    # Wrap the image into the "blob" format OpenCV's model accepts
    return cv2.dnn.blobFromImage(img)


# ---------- Asking the model ----------

def get_probabilities(frame):
    """Run the model on one photo. Returns 1000 percentages (they add up to 1)."""
    net.setInput(prepare_image(frame))        # give the photo to the model
    scores = net.forward().flatten()          # model answers with 1000 raw scores

    # Softmax: turn raw scores into percentages
    # (subtracting the max first just avoids huge numbers)
    exp_scores = np.exp(scores - np.max(scores))
    return exp_scores / exp_scores.sum()


def classify_animal(pil_image):
    """
    Give it a photo (PIL image, RGB).
    Returns {"label", "confidence", "index"} if it's an animal, else None.
    """
    load_model()
    if net is False:                          # model couldn't load
        return None

    # PIL gives RGB; OpenCV likes BGR, so convert
    frame = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Ask the model twice: normal photo AND mirrored photo, then average.
    # This makes the answer a bit more reliable.
    normal = get_probabilities(frame)
    mirrored = get_probabilities(cv2.flip(frame, 1))
    probs = (normal + mirrored) / 2.0

    # Find the 5 best guesses (highest percentage first)
    top5 = np.argsort(probs)[::-1][:5]

    # Print them in the console so you can see what the AI is thinking
    print("[classifier] Top 5 guesses:")
    for i in top5:
        name = labels[i].split(",")[0].strip()
        kind = "animal" if i < ANIMAL_CUTOFF else "not-animal"
        print(f"    {name:<30} {probs[i]*100:5.1f}%  ({kind})")

    best = int(top5[0])                       # number of the best guess

    # Best guess isn't an animal? Then say "nothing found".
    if best >= ANIMAL_CUTOFF:
        return None

    # Names can have synonyms: "hammerhead, hammerhead shark".
    # We only keep the first name.
    label = labels[best].split(",")[0].strip()

    return {
        "label": label,
        "confidence": float(probs[best]),
        "index": best,
    }