// ANIMALTON — camera capture logic
//
// Anti-cheat: never show a file picker. Get direct camera access via
// getUserMedia and stream it live into a <video>. Tapping the shutter
// grabs the current frame from that live stream — there's no point in
// the flow where an old photo could be substituted.

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const frozenFrame = document.getElementById("frozenFrame");
const captureBtn = document.getElementById("captureBtn");
const statusEl = document.getElementById("status");
const flash = document.getElementById("flash");
const analyzingOverlay = document.getElementById("analyzingOverlay");
const resultCard = document.getElementById("resultCard");
const resultPhoto = document.getElementById("resultPhoto");
const resultText = document.getElementById("resultText");
const closeResult = document.getElementById("closeResult");

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } }, // rear camera on phones
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

async function handleCapture() {
  if (!video.videoWidth) {
    statusEl.textContent = "Camera isn't ready yet — one second...";
    return;
  }

  captureBtn.disabled = true;
  playShutterEffect();

  const imageData = captureFrame();

  frozenFrame.src = imageData;
  frozenFrame.classList.remove("hidden");
  video.classList.add("hidden");
  analyzingOverlay.classList.remove("hidden");
  statusEl.textContent = "";

  try {
    const res = await fetch("/api/capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData }),
    });
    const data = await res.json();

    if (!data.ok) {
      statusEl.textContent = data.error || "Something went wrong.";
    } else if (!data.caught) {
      statusEl.textContent = data.message;
    } else {
      showResult(data);
    }
  } catch (err) {
    statusEl.textContent = "Network error — is the server running?";
    console.error(err);
  } finally {
    analyzingOverlay.classList.add("hidden");
    frozenFrame.classList.add("hidden");
    video.classList.remove("hidden");
    captureBtn.disabled = false;
    if (!statusEl.textContent) {
      statusEl.textContent = "Point your camera at an animal and tap the shutter";
    }
  }
}

function showResult(data) {
  resultPhoto.src = data.photo_url;
  const title = data.new_species ? "New species discovered!" : "Caught again!";
  resultText.innerHTML = `
    <h2>${title}</h2>
    <p class="species-name">${capitalize(data.label)}</p>
    <p class="conf">Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
  `;
  resultCard.classList.remove("hidden");
  statusEl.textContent = "Point your camera at an animal and tap the shutter";
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

captureBtn.addEventListener("click", handleCapture);
closeResult.addEventListener("click", () => resultCard.classList.add("hidden"));

startCamera();