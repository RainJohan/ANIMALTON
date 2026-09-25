// ANIMALTON — camera + upload logic
//
// Anti-cheat note: the live-capture path (video → canvas → /api/capture)
// never involves a file picker — it's a snapshot of an active
// getUserMedia stream. Upload (/api/upload) is a separate, clearly
// distinct path that intentionally bypasses that protection.

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const frozenFrame = document.getElementById("frozenFrame");
const captureBtn = document.getElementById("captureBtn");
const statusEl = document.getElementById("status");
const flash = document.getElementById("flash");
const analyzingOverlay = document.getElementById("analyzingOverlay");

const captureUI = document.getElementById("captureUI");
const catchScreen = document.getElementById("catchScreen");
const catchBadge = document.getElementById("catchBadge");
const catchPhoto = document.getElementById("catchPhoto");
const catchName = document.getElementById("catchName");
const catchMeta = document.getElementById("catchMeta");
const catchContinueBtn = document.getElementById("catchContinueBtn");
const catchViewLink = document.getElementById("catchViewLink");

const dropzone = document.getElementById("dropzone");
const dropzoneContent = document.getElementById("dropzoneContent");
const uploadInput = document.getElementById("uploadInput");
const uploadPreview = document.getElementById("uploadPreview");

const desktopTip = document.getElementById("desktopTip");
const tipCloseBtn = document.getElementById("tipCloseBtn");
const tipReopenBtn = document.getElementById("tipReopenBtn");

// ---------- Camera ----------

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } },
      audio: false,
    });
    video.srcObject = stream;
  } catch (err) {
    statusEl.textContent =
      "Camera access is required to play. Please allow camera permission and reload.";
    console.error(err);
  }
}

function captureFrame() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.9);
}

function playShutterEffect() {
  flash.classList.add("flash-active");
  setTimeout(() => flash.classList.remove("flash-active"), 180);
}

function showAnalyzing(previewSrc) {
  frozenFrame.src = previewSrc;
  frozenFrame.classList.remove("hidden");
  video.classList.add("hidden");
  analyzingOverlay.classList.remove("hidden");
  statusEl.textContent = "";
}

function hideAnalyzing() {
  analyzingOverlay.classList.add("hidden");
  frozenFrame.classList.add("hidden");
  video.classList.remove("hidden");
  if (!statusEl.textContent) {
    statusEl.textContent = "Point your camera at an animal and tap the shutter";
  }
}

function handleResponse(data) {
  if (!data.ok) {
    statusEl.textContent = data.error || "Something went wrong.";
  } else if (!data.caught) {
    statusEl.textContent = data.message;
  } else {
    showCatchScreen(data);
  }
}

async function handleCapture() {
  if (!video.videoWidth) {
    statusEl.textContent = "Camera isn't ready yet — one second...";
    return;
  }
  captureBtn.disabled = true;
  playShutterEffect();
  const imageData = captureFrame();
  showAnalyzing(imageData);

  try {
    const res = await fetch("/api/capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData }),
    });
    handleResponse(await res.json());
  } catch (err) {
    statusEl.textContent = "Network error — is the server running?";
    console.error(err);
  } finally {
    hideAnalyzing();
    captureBtn.disabled = false;
  }
}

captureBtn.addEventListener("click", handleCapture);

// ---------- Catch screen: fully replaces the camera UI ----------

function showCatchScreen(data) {
  captureUI.classList.add("hidden");

  catchBadge.textContent = data.new_species ? "✨ New species discovered!" : "Caught again!";
  catchPhoto.src = data.photo_url;
  catchName.textContent = capitalize(data.label);
  catchMeta.textContent = `${data.category} · ${(data.confidence * 100).toFixed(1)}% match`;
  catchViewLink.href = `/species/${encodeURIComponent(data.label)}`;

  catchScreen.classList.remove("hidden");
  catchScreen.classList.remove("catch-screen-animate");
  void catchScreen.offsetWidth; // force reflow so the pop-in animation replays
  catchScreen.classList.add("catch-screen-animate");
}

function closeCatchScreen() {
  catchScreen.classList.add("hidden");
  captureUI.classList.remove("hidden");
  statusEl.textContent = "Point your camera at an animal and tap the shutter";
}

catchContinueBtn.addEventListener("click", closeCatchScreen);

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// ---------- Upload: drag & drop + click-to-browse, with preview ----------

function showUploadPreview(file) {
  const url = URL.createObjectURL(file);
  uploadPreview.src = url;
  uploadPreview.classList.remove("hidden");
  dropzoneContent.classList.add("hidden");
  return url;
}

function resetDropzone() {
  uploadPreview.classList.add("hidden");
  dropzoneContent.classList.remove("hidden");
  uploadInput.value = "";
}

async function submitUpload(file) {
  const previewUrl = showUploadPreview(file);
  showAnalyzing(previewUrl);

  const formData = new FormData();
  formData.append("photo", file);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    handleResponse(await res.json());
  } catch (err) {
    statusEl.textContent = "Network error — is the server running?";
    console.error(err);
  } finally {
    hideAnalyzing();
    resetDropzone();
  }
}

dropzone.addEventListener("click", () => uploadInput.click());
uploadInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) submitUpload(file);
});
["dragenter", "dragover"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone-active");
  });
});
["dragleave", "drop"].forEach((evt) => {
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone-active");
  });
});
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) submitUpload(file);
});

// ---------- "How it works" panel — hideable, remembers choice ----------

const TIP_HIDDEN_KEY = "animalton_tip_hidden";

function applyTipVisibility() {
  const hidden = localStorage.getItem(TIP_HIDDEN_KEY) === "true";
  desktopTip.classList.toggle("hidden", hidden);
  tipReopenBtn.classList.toggle("hidden", !hidden);
}

tipCloseBtn.addEventListener("click", () => {
  localStorage.setItem(TIP_HIDDEN_KEY, "true");
  applyTipVisibility();
});
tipReopenBtn.addEventListener("click", () => {
  localStorage.setItem(TIP_HIDDEN_KEY, "false");
  applyTipVisibility();
});

applyTipVisibility();
startCamera();