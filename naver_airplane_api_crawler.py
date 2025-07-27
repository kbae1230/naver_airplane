import os
import requests
import json


import json2notion
from config import DATA_PATH

url = "https://flight-api.naver.com/flight/domestic/searchFlights"

headers = {
    "Accept": "text/event-stream",
    "Content-Type": "application/json",
    "Origin": "https://flight.naver.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

payload = {
    "type": "domestic",
    "device": "PC",
    "fareType": "YC",
    "itineraries": [
        {
            "departureAirport": "CJU",
            "arrivalAirport": "CJJ",
            "departureDate": "20250811"  # YYYYMMDD 형식
        }
    ],
    "person": {
        "adult": 1,
        "child": 0,
        "infant": 0
    },
    "tripType": "OW",
    "initialRequest": True,
    "flightFilter": {
        "filter": {
            "type": "departure"
        },
        "limit": 50,
        "skip": 0,
        "sort": {
            "segment.departure.time": 1,
            "minFare": 1
        }
    }
}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)

raw_text = response.content.decode('utf-8')
json_str = raw_text.lstrip("data:").strip()




def load_existing_data(path=DATA_PATH):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
            except json.JSONDecodeError:
                print("❌ 기존 data.json 파싱 실패")
                return None
    return None

        
def save_data(existing_data, path=DATA_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)


def main():
    try:
        data = json.loads(json_str)

        from json_parsing import filter_flights
        filtered_result = filter_flights(data)  # {'departure': ..., 'fare': ...}

        if not filtered_result:
            print("❗조건에 맞는 항공편이 없습니다.")
        else:
            new_fare = filtered_result.get("fare", float("inf"))

            existing_data = load_existing_data()
            # 오류 방지를 위한 dict 확인
            existing_fares = existing_data.get("fare", float("inf"))

            # 새 운임이 기존 값들보다 낮으면 추가
            if not existing_fares or new_fare != existing_fares:
                existing_data = filtered_result
                save_data(existing_data)
                # print("✅ 운임 변경!")
                data = json2notion.load_json_data(DATA_PATH)
                json2notion.create_notion_page(data)
                
            else:
                print("ℹ️ 기존 운임이 더 저렴하거나 동일하므로 변경하지 않음.")
                
    except json.JSONDecodeError as e:
        print("JSON 파싱 실패:", e)
        print("원본:", json_str[:500])  # 앞부분 일부만 출력

if __name__ == "__main__":
    main()