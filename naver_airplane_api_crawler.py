import requests
import json

url = "https://flight-api.naver.com/flight/domestic/searchFlights"

headers = {
    "Accept": "text/event-stream",
    "Content-Type": "application/json",
    "Origin": "https://flight.naver.com",
    "Referer": "https://flight.naver.com/flights/domestic/CJU-GMP-20250719?adult=1&fareType=YC",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
}

payload = {
    "type": "domestic",
    "device": "PC",
    "fareType": "YC",
    "itineraries": [
        {
            "departureAirport": "CJU",
            "arrivalAirport": "GMP",
            "departureDate": "20250719"  # YYYYMMDD 형식
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

# "data:" 접두어 제거 + 양쪽 공백 제거
json_str = raw_text.lstrip("data:").strip()

try:
    # JSON 문자열 파싱
    data = json.loads(json_str)

    # 파일로 저장
    with open("flight_sse_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ flight_sse_data.json 저장 완료")

except json.JSONDecodeError as e:
    print("❌ JSON 파싱 실패:", e)
    print("원본:", json_str[:500])  # 앞부분 일부만 출력
