import os
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
PAGE_ID = os.getenv("PAGE_ID")
NOTION_VERSION = "2022-06-28"
DATA_PATH = "/home/kbae/naver_airplane/data.json"
AIRPORT = ["CJU", "GMP", "PUS", "ICN", "CJJ"]