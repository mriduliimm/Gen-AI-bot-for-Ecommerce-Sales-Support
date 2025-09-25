import os, json, time
OUT_DIR = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT_DIR, exist_ok=True)

def save_session(data: dict) -> str:
    ts = int(time.time())
    path = os.path.join(OUT_DIR, f"session_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
