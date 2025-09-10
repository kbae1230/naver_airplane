import requests
import json

class FlightAPI:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        
    def fetch(self, payload):
        response = requests.post(self.url, headers=self.headers, json=payload)
        return response.json()

    def search_flights(self, payload):
        response = requests.post(self.url, headers=self.headers, json=payload)
        raw_text = response.content.decode("utf-8")
        json_lines = [line for line in raw_text.splitlines() if line.startswith("data:")]
        if not json_lines:
            raise ValueError("응답에 data: 라인이 없음")
        json_str = json_lines[-1].lstrip("data:").strip()
        return json.loads(json_str)
