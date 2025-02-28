# tracker.py
import time
import json
import PyChromeDevTools

class ActiveTabTracker:
    """
    Tracks how long each tab stays in the 'visible' state along with its title.
    """
    def __init__(self):
        self.start_times = {}       # {target_id: float(timestamp)}
        self.total_times = {}       # {target_id: {'time': seconds, 'title': str}}
        self.visibility_states = {} # {target_id: bool}
        self.titles = {}            # {target_id: str}

    def on_tab_visible(self, target_id, title):
        """Record the time when the tab becomes visible and update its title."""
        print(f"Target {target_id} is now visible with title: {title}")
        self.start_times[target_id] = time.time()
        self.titles[target_id] = title

    def on_tab_hidden(self, target_id):
        """When the tab is hidden, accumulate the time it was visible."""
        print(f"Target {target_id} is now hidden.")
        if target_id in self.start_times:
            delta = time.time() - self.start_times[target_id]
            current_title = self.titles.get(target_id, '')
            if target_id in self.total_times:
                self.total_times[target_id]['time'] += delta
                self.total_times[target_id]['title'] = current_title
            else:
                self.total_times[target_id] = {'time': delta, 'title': current_title}
            del self.start_times[target_id]

    def finalize_all_visible(self):
        """Finalize timing for all tabs that are still visible."""
        for tid in list(self.start_times.keys()):
            self.on_tab_hidden(tid)

    def print_usage(self):
        """Print the usage report to the console."""
        print("\n=== Tab Usage Report ===")
        for tid, data in self.total_times.items():
            print(f"  Target {tid} ('{data['title']}') was visible for {data['time']:.2f} seconds.")

    def write_usage_json(self, filename="tab_usage.json"):
        """Write usage data to a JSON file."""
        data = {tid: {"time": info["time"], "title": info["title"]}
                for tid, info in self.total_times.items()}
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved usage data to {filename}")

def attach_target(chrome, target_id):
    """Attach to a target with error handling."""
    try:
        chrome.Target.attachToTarget(targetId=target_id, flatten=True)
    except Exception as e:
        if "already attached" not in str(e).lower():
            raise

def tracking_loop(tracker: ActiveTabTracker):
    """
    Main loop that listens for Chrome events and updates the tracker.
    Make sure Chrome is running with remote debugging enabled.
    """
    chrome = PyChromeDevTools.ChromeInterface(host="127.0.0.1", port=9222)
    
    # Process existing targets
    existing_targets = chrome.Target.getTargets()[0]
    for tinfo in existing_targets.get("targetInfos", []):
        if tinfo.get("type") == "page":
            tid = tinfo["targetId"]
            attach_target(chrome, tid)
            is_visible = tinfo.get("isVisible", False)
            title = tinfo.get("title", "")
            tracker.visibility_states[tid] = is_visible
            tracker.titles[tid] = title
            if is_visible:
                tracker.on_tab_visible(tid, title)
    
    # Enable target discovery for new tabs
    chrome.Target.setDiscoverTargets(discover=True)

    def handle_event(msg):
        method = msg.get("method")
        params = msg.get("params", {})

        # Handle new tabs
        if method == "Target.targetCreated":
            target_info = params.get("targetInfo", {})
            if target_info.get("type") == "page":
                target_id = target_info["targetId"]
                is_visible = target_info.get("isVisible", True)
                title = target_info.get("title", "")
                print(f"New tab detected: {title} (ID: {target_id})")
                tracker.visibility_states[target_id] = is_visible
                tracker.titles[target_id] = title
                attach_target(chrome, target_id)

                # Simulate switching by hiding other visible tabs
                for tid in tracker.visibility_states:
                    if tid != target_id and tracker.visibility_states[tid]:
                        tracker.on_tab_hidden(tid)
                        tracker.visibility_states[tid] = False
                if is_visible:
                    tracker.on_tab_visible(target_id, title)

        # Handle tab updates (visibility or title changes)
        elif method == "Target.targetInfoChanged":
            target_info = params.get("targetInfo", {})
            target_id = target_info.get("targetId")
            if target_info.get("type") == "page":
                new_visible = target_info.get("isVisible", True)
                prev_visible = tracker.visibility_states.get(target_id, False)
                new_title = target_info.get("title", "")
                if new_title and tracker.titles.get(target_id) != new_title:
                    tracker.titles[target_id] = new_title
                if new_visible != prev_visible:
                    if new_visible:
                        current_title = tracker.titles.get(target_id, new_title)
                        print(f"User switched to tab {target_id} ({current_title})")
                        tracker.on_tab_visible(target_id, current_title)
                    else:
                        print(f"User switched away from tab {target_id}")
                        tracker.on_tab_hidden(target_id)
                    tracker.visibility_states[target_id] = new_visible

    print("Tracking time spent on active tabs. Running background tracker...")
    try:
        while True:
            messages = chrome.wait_event(event="event", timeout=1)[1]
            if messages:
                for msg in messages:
                    handle_event(msg)
    except Exception as e:
        print("Error in tracking loop:", e)
    finally:
        tracker.finalize_all_visible()
        tracker.print_usage()
        tracker.write_usage_json()

