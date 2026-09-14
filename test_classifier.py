"""
Quick diagnostic — checks whether the model is loaded and what it guesses
on a test photo.

Usage:
    python test_classifier.py path/to/a/dog/photo.jpg
"""
import sys
import os
from PIL import Image
import classifier

MODEL_EXISTS = os.path.exists(classifier.MODEL_PATH)
LABELS_EXIST = os.path.exists(classifier.LABELS_PATH)

print("=" * 50)
print(f"Model file present?  {MODEL_EXISTS}  ({classifier.MODEL_PATH})")
print(f"Labels file present? {LABELS_EXIST}  ({classifier.LABELS_PATH})")
print("=" * 50)

if not (MODEL_EXISTS and LABELS_EXIST):
    print("\n>>> THIS IS YOUR PROBLEM <<<")
    print("Model files are missing, so classify_animal() always runs in DEMO")
    print("MODE and returns None for every photo, regardless of what's in it.")
    print("\nDownload them with:")
    print("  curl -L -o models/mobilenetv2-7.onnx https://github.com/onnx/models/raw/main/validated/vision/classification/mobilenet/model/mobilenetv2-7.onnx")
    print("  curl -L -o models/imagenet_classes.txt https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt")
    sys.exit(1)

if len(sys.argv) < 2:
    print("\nUsage: python test_classifier.py path/to/photo.jpg")
    sys.exit(1)

img = Image.open(sys.argv[1]).convert("RGB")
result = classifier.classify_animal(img)
print(f"\nResult: {result}")