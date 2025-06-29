import json

def time_in_range(time_str, start="0800", end="1000"):
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

with open("flight_sse_data.json", encoding="utf-8") as f:
    data = json.load(f)

airlines_code_map = data.get("status", {}).get("airlinesCodeMap", {})

best_flights = filter_flights(data)
if best_flights:
    print(f"조건에 맞는 최저가 하위 {len(best_flights)}개 항공편:")
    for flight in best_flights:
        print_flight_info(flight, airlines_code_map)
else:
    print("조건에 맞는 비행편이 없습니다.")
