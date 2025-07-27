
import json
import requests

import streamlit as st

NOTION_TOKEN = st.secrets["notion"]["token"]
DATABASE_ID = st.secrets["notion"]["database"]
PAGE_ID = st.secrets["notion"]["page"]
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

def load_json_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def create_notion_page(data):
    data = {
        "parent": { "database_id": DATABASE_ID },
        "properties": {
            "check": {
                "title": [
                    {
                        "text": {
                            "content": data['check']  # 예시: JSON의 "name" 필드 사용
                        }
                    }
                ]
            },
            "departure": {
                "rich_text": [
                    {
                        "text": {
                            "content": data['departure']
                        }
                    }
                ]
            },
            "arrival": {
                "rich_text": [
                    {
                        "text": {
                            "content": data['arrival']
                        }
                    }
                ]
            },
            "airline": {
                "rich_text": [
                    {
                        "text": {
                            "content": data['airline']
                        }
                    }
                ]
            },
            "date": {
                "rich_text": [
                    {
                        "text": {
                            "content": data['date']
                        }
                    }
                ]
            },
            "time": {
                "rich_text": [
                    {
                        "text": {
                            "content": data['time']
                        }
                    }
                ]
            },
            "fare": {
                "number": data['fare']
            },
            # 다른 속성들도 여기에 추가
        }
    }

    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        print(f"✅ 업로드 성공: ")
    else:
        print(f"❌ 업로드 실패: 상태코드: {response.status_code}")
        print(response.text)
        
def add_comment_to_page(comment_text):
    data = {
        "parent": { "page_id": PAGE_ID },
        "properties": {
		"title": {
                "title": [{ "type": "text", "text": { "content": comment_text } }]
                }
	},
    }
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        data=json.dumps(data)
    )

    if response.status_code == 200:
        print("✅ 댓글 추가 성공")
    else:
        print(f"❌ 댓글 추가 실패: 상태코드 {response.status_code}")
        print(response.text)
