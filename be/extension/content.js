// content.js
// This script runs on every webpage due to "matches": ["<all_urls>"].

// Adjust to match your FastAPI server endpoint:
const SERVER_ENDPOINT = "http://127.0.0.1:8000/visibility";

function sendVisibilityChange(state) {
  fetch(SERVER_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      tabUrl: window.location.href,
      state: state,
      timestamp: Date.now()
    })
  }).catch(err => console.error("Failed to send visibility data:", err));
}

// Listen for visibility changes:
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    sendVisibilityChange("hidden");
  } else {
    sendVisibilityChange("visible");
  }
});

// Optionally send an initial state on load:
if (document.hidden) {
  sendVisibilityChange("hidden");
} else {
  sendVisibilityChange("visible");
}

