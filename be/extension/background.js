// background.js (Manifest V3 service worker)
chrome.runtime.onInstalled.addListener(() => {
  // On install or update, inject content.js into all existing tabs
  injectContentScripts();
});

chrome.runtime.onStartup.addListener(() => {
  // Also inject scripts when Chrome restarts (optional)
  injectContentScripts();
});

function injectContentScripts() {
  // Query all open tabs
  chrome.tabs.query({}, (tabs) => {
    for (const tab of tabs) {
      // Filter out special URLs like chrome://, about://, etc.
      if (tab.url && /^https?:\/\//.test(tab.url)) {
        // Use the Scripting API to inject content.js
        chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content.js"]
        }, () => {
          if (chrome.runtime.lastError) {
            console.warn("Script injection failed: ", chrome.runtime.lastError.message);
          } else {
            console.log(`Injected content.js into tab ${tab.id} (${tab.url})`);
          }
        });
      }
    }
  });
}

