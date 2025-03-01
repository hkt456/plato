// popup.js
const serverUrl = "http://127.0.0.1:8000";  // Your FastAPI base URL

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusDiv = document.getElementById("status");

startBtn.addEventListener("click", async () => {
  try {
    const res = await fetch(`${serverUrl}/start_tracking`, { method: "POST" });
    const data = await res.json();
    statusDiv.innerText = data.status || JSON.stringify(data);
  } catch (err) {
    console.error(err);
    statusDiv.innerText = "Error starting tracking.";
  }
});

stopBtn.addEventListener("click", async () => {
  try {
    const res = await fetch(`${serverUrl}/stop_tracking`, { method: "POST" });
    const data = await res.json();
    statusDiv.innerText = data.status || JSON.stringify(data);
  } catch (err) {
    console.error(err);
    statusDiv.innerText = "Error stopping tracking.";
  }
});

// On popup load, let's check if tracking is running:
checkTrackingStatus();

async function checkTrackingStatus() {
  try {
    // We call /status now, not /usage
    const res = await fetch(`${serverUrl}/status`);
    const data = await res.json();

    if (data.running) {
      statusDiv.innerText = "Currently tracking.";
    } else {
      statusDiv.innerText = "Not tracking.";
    }
  } catch (err) {
    console.error(err);
    statusDiv.innerText = "Could not connect to server.";
  }
}


