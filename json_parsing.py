
import datetime

def time_in_range(time_str, start="0800", end="1200"):
    return start <= time_str <= end

def get_min_fare_for_flight(fares):
    return min(fare.get("adultTotalFare", float('inf')) for fare in fares if fare.get("adultTotalFare") is not None)

def filter_flights(data):
    filtered = []
    for flight in data.get("flights", []):
        segment = flight.get("segment", {})
        dep_time = segment.get("departure", {}).get("time", "")
        arr_time = segment.get("arrival", {}).get("time", "")
        if time_in_range(dep_time) and time_in_range(arr_time):
            min_fare = get_min_fare_for_flight(flight.get("fares", []))
            filtered.append((flight, min_fare))

    if not filtered:
        return None

    # 같은 편명 중 최소가만 남기기
    flight_dict = {}
    for flight, fare in filtered:
        flight_num = flight.get("segment", {}).get("flightNumber", "")
        if flight_num not in flight_dict or fare < flight_dict[flight_num][1]:
            flight_dict[flight_num] = (flight, fare)

    # 전체 중 가장 싼 항공편 하나 추출
    lowest_flight, lowest_fare = min(flight_dict.values(), key=lambda x: x[1])

    # 필요한 정보 추출
    segment = lowest_flight.get("segment", {})
    dep = segment.get("departure", {})
    arr = segment.get("arrival", {})
    airline_code = segment.get("airlineCode", "")
    airline_name = data.get("status", {}).get("airlinesCodeMap", {}).get(airline_code, airline_code)
    check_time = datetime.datetime.now().isoformat(timespec='seconds')

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

