// Note: This script assumes that the extension's popup page
// runs on the same origin as your web app so that sessionStorage is accessible.

const timerDiv = document.getElementById("timer");

// Messages for work session
const workMessages = [
  "You're doing great!",
  "Keep it up!",
  "You're making progress!",
  "Remember to stay hydrate!",
  "Do you best!",
  "Keep up the good work!",
  "Stay focused and productive!",
  "You're crushing it—keep going!"
];

let lastMessageChange = 0;
const MESSAGE_CHANGE_INTERVAL = 10 * 1000; // 10 seconds
let currentWorkMessage = workMessages[0];

// Function to pick a random work message
function pickRandomWorkMessage() {
  const randomIndex = Math.floor(Math.random() * workMessages.length);
  return workMessages[randomIndex];
}

// Poll sessionStorage every 5 seconds to check session status
function checkSessionStatus() {
  try {
    // Retrieve the session status; sessionStorage values are strings
    const running = sessionStorage.getItem("running");

    if (running !== "true") {
      const now = Date.now();
      if (now - lastMessageChange > MESSAGE_CHANGE_INTERVAL) {
        currentWorkMessage = pickRandomWorkMessage();
        lastMessageChange = now;
      }
      timerDiv.innerText = currentWorkMessage;
    } else {
      timerDiv.innerText = "You are idle";
    }
  } catch (err) {
    console.error(err);
    timerDiv.innerText = "Error checking session status.";
  }
}

// Start checking the session status immediately and then every 5 seconds
checkSessionStatus();
setInterval(checkSessionStatus, 5000);

