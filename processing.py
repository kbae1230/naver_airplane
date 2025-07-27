import os
import json
from datetime import datetime, timedelta, timezone


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

def time_in_range(time_str, start, end):
    return start <= time_str <= end

def get_min_fare_for_flight(fares):
    return min(fare.get("adultTotalFare", float('inf')) for fare in fares if fare.get("adultTotalFare") is not None)

def filter_flights(data, start, end):
    filtered = []
    for flight in data.get("flights", []):
        segment = flight.get("segment", {})
        dep_time = segment.get("departure", {}).get("time", "")
        arr_time = segment.get("arrival", {}).get("time", "")
        if time_in_range(dep_time, start, end) and time_in_range(arr_time, start, end):
            min_fare = get_min_fare_for_flight(flight.get("fares", []))
            filtered.append((flight, min_fare))

    if not filtered:
        return None

    flight_dict = {}
    for flight, fare in filtered:
        flight_num = flight.get("segment", {}).get("flightNumber", "")
        if flight_num not in flight_dict or fare < flight_dict[flight_num][1]:
            flight_dict[flight_num] = (flight, fare)

    lowest_flight, lowest_fare = min(flight_dict.values(), key=lambda x: x[1])

    segment = lowest_flight.get("segment", {})
    dep = segment.get("departure", {})
    arr = segment.get("arrival", {})
    airline_code = segment.get("airlineCode", "")
    airline_name = data.get("status", {}).get("airlinesCodeMap", {}).get(airline_code, airline_code)
    kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
    check_time = kst_now.strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "check": check_time,
        "departure": data.get("status", {}).get("departure", {}).get("depAirportName", dep.get("airportCode", "")),
        "arrival": data.get("status", {}).get("departure", {}).get("arrAirportName", arr.get("airportCode", "")),
        "date": dep.get("date", ""),
        "time": dep.get("time", ""),
        "airline": airline_name,
        "fare": lowest_fare
    }

    return result

