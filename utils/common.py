import json
import os

def pretty_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2)

def load_existing_data(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("❌ 기존 data.json 파싱 실패")
                return None
    return None

def save_data(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

