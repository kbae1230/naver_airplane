import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")
NOTION_VERSION = "2022-06-28"
DATA_PATH = os.path.join(BASE_DIR, "data.json")
AIRPORT = ["CJU", "GMP", "PUS", "ICN", "CJJ"]