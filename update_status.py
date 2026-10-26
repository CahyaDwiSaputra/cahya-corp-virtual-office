import sys
import json
import time
from pathlib import Path

status_file = Path.home() / "virtual-office" / "status.json"

def update(profile, status, task=None, output=None):
    if not status_file.exists():
        return
    try:
        data = json.loads(status_file.read_text(encoding="utf-8"))
    except Exception:
        data = {}

    if profile in data:
        data[profile]["status"] = status
        if task:
            data[profile]["task"] = task
        if output:
            data[profile]["last_output"] = output
        data[profile]["last_updated"] = time.time()
        status_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Updated {profile}: status={status}")

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        p = sys.argv[1]
        s = sys.argv[2]
        t = sys.argv[3] if len(sys.argv) > 3 else None
        o = sys.argv[4] if len(sys.argv) > 4 else None
        update(p, s, t, o)
