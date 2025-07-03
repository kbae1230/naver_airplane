import requests
import requests
import json

NOTION_TOKEN = "your-secret-token"
DATABASE_ID = "your-database-id"

# Notion에 알림 전송
def send_to_notion(flight, airlines_code_map, notion_token, database_id):
    segment = flight.get("segment", {})
    airline_code = segment.get("airlineCode", "")
    airline_name = airlines_code_map.get(airline_code, airline_code)
    flight_number = segment.get("flightNumber", "")
    dep_time = segment.get("departure", {}).get("time", "")
    arr_time = segment.get("arrival", {}).get("time", "")
    min_fare = flight.get("minFare", 0)
    seat_count = flight.get("seatCount", 0)

    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": { "database_id": database_id },
        "properties": {
            "항공사명": {
                "title": [{ "text": { "content": airline_name } }]
            },
            "편명": {
                "rich_text": [{ "text": { "content": flight_number } }]
            },
            "출발시간": {
                "rich_text": [{ "text": { "content": f"{dep_time[:2]}시 {dep_time[2:]}분" } }]
            },
            "도착시간": {
                "rich_text": [{ "text": { "content": f"{arr_time[:2]}시 {arr_time[2:]}분" } }]
            },
            "최저가": {
                "number": min_fare
            },
            "남은좌석수": {
                "number": seat_count
            }
        }
    }

    notion_url = "https://api.notion.com/v1/pages"
    res = requests.post(notion_url, headers=headers, json=data)

    if res.status_code == 200:
        print(f"✅ Notion 알림 전송 성공: {airline_name} {flight_number}")
    else:
        print("❌ Notion 전송 실패:", res.status_code, res.text)
        
        
def time_in_range(time_str, start="0800", end="1200"):
    return start <= time_str <= end

def get_min_fare_for_flight(fares):
    return min(fare.get("adultFare", float('inf')) for fare in fares)

def filter_flights(data):
    filtered = []
    for flight in data.get("flights", []):
        dep_time = flight.get("segment", {}).get("departure", {}).get("time", "")
        arr_time = flight.get("segment", {}).get("arrival", {}).get("time", "")
        if time_in_range(dep_time) and time_in_range(arr_time):
            min_fare = get_min_fare_for_flight(flight.get("fares", []))
            filtered.append((flight, min_fare))
    if not filtered:
        return []

    # 같은 편명 중 최소가만 남기기
    flight_dict = {}
    for flight, fare in filtered:
        flight_num = flight.get("segment", {}).get("flightNumber", "")
        if flight_num not in flight_dict or fare < flight_dict[flight_num][1]:
            flight_dict[flight_num] = (flight, fare)

    # 최소가 기준으로 정렬 후 상위 3개
    unique_flights = list(flight_dict.values())
    unique_flights.sort(key=lambda x: x[1])
    return [item[0] for item in unique_flights[:3]]

def print_flight_info(flight, airlines_code_map):
    segment = flight.get("segment", {})
    airline_code = segment.get("airlineCode", "정보없음")
    airline_name = airlines_code_map.get(airline_code, airline_code)
    flight_number = segment.get("flightNumber", "정보없음")
    departure = segment.get("departure", {})
    arrival = segment.get("arrival", {})
    dep_time = departure.get("time", "정보없음")
    arr_time = arrival.get("time", "정보없음")
    print(f"항공사명: {airline_name}")
    print(f"편명: {flight_number}")
    print(f"출발 시간: {dep_time[:2]}시 {dep_time[2:]}분")
    print(f"도착 시간: {arr_time[:2]}시 {arr_time[2:]}분")
    print(f"최저가: {flight.get('minFare', '정보없음')}원")
    print(f"남은 좌석 수: {flight.get('seatCount', '정보없음')}석")
    print("-" * 30)

# 요청 설정
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
            "departureDate": "20250720"
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

# 요청 실행
response = requests.post(url, headers=headers, json=payload)
print("Status Code:", response.status_code)

raw_text = response.content.decode('utf-8')
json_str = raw_text.lstrip("data:").strip()

try:
    data = json.loads(json_str)
    airlines_code_map = data.get("status", {}).get("airlinesCodeMap", {})
    best_flights = filter_flights(data)

    if best_flights:


        for flight in best_flights:
            print_flight_info(flight, airlines_code_map)
            send_to_notion(flight, airlines_code_map, NOTION_TOKEN, DATABASE_ID)
        print(f"조건에 맞는 최저가 하위 {len(best_flights)}개 항공편:")
    else:
        print("조건에 맞는 비행편이 없습니다.")
except json.JSONDecodeError as e:
    print("❌ JSON 파싱 실패:", e)
    print("응답 일부:", json_str[:500])
