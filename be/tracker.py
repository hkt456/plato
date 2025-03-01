# tracker.py 
# tracker.py
import time
import json
import threading

class ActiveTabTracker:
    """
    Tracks usage by partial increments:
      - 'visibility_states': {tab_id: bool}
      - 'total_times': {tab_id: {"time": float, "title": str}}
    Each second, we add elapsed time to any tab marked visible.
    """

    def __init__(self):
        self.total_times = {}
        self.visibility_states = {}
        self.titles = {}

    def on_tab_visible(self, tab_id, title):
        """
        Mark this tab as visible. If it's new, initialize it in total_times.
        """
        print(f"[Extension] Tab {tab_id} is now VISIBLE with title: {title}")
        self.visibility_states[tab_id] = True
        self.titles[tab_id] = title
        if tab_id not in self.total_times:
            self.total_times[tab_id] = {"time": 0.0, "title": title}

    def on_tab_hidden(self, tab_id):
        """
        Mark this tab as hidden.
        """
        print(f"[Extension] Tab {tab_id} is now HIDDEN.")
        self.visibility_states[tab_id] = False

    def finalize_all_visible(self):
        """
        Called when we stop tracking. Marks all tabs as hidden so they stop accumulating.
        """
        for tab_id in self.visibility_states:
            self.visibility_states[tab_id] = False

    def write_usage_json(self, filename="tab_usage.json"):
        """
        Write usage data to a JSON file.
        """
        data = {
            tab_id: {"time": info["time"], "title": info["title"]}
            for tab_id, info in self.total_times.items()
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[INFO] Saved usage data to {filename}")

def tracking_loop(tracker: ActiveTabTracker, stop_event: threading.Event):
    """
    Continuously:
      - Wait ~1 second
      - Add elapsed time to any tab that is marked visible
    """
    last_time = time.time()
    while not stop_event.is_set():
        now = time.time()
        elapsed = now - last_time
        last_time = now

        # Increment usage for visible tabs
        for tab_id, is_visible in tracker.visibility_states.items():
            if is_visible:
                tracker.total_times[tab_id]["time"] += elapsed

        time.sleep(1)  # Wait 1 second before next increment

    # When stopping, finalize and save data
    tracker.finalize_all_visible()
    tracker.write_usage_json()
    print("[INFO] Tracking loop ended.")

