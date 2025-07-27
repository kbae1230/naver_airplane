import os

def load_env(path=".env"):
    if not os.path.exists(path):
        print(f"{path} 파일이 존재하지 않습니다.")
        return

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "" or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.strip().split("=", 1)
                os.environ[key] = value.strip().strip("'").strip('"')
                
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")
NOTION_VERSION = "2022-06-28"
DATA_PATH = os.path.join(BASE_DIR, "data.json")
AIRPORT = ["CJU", "GMP", "PUS", "ICN", "CJJ"]