import requests
import json

class FlightMonitor:
    def __init__(self, base_url="https://flight-api.naver.com/flight/domestic/searchFlights"):
        self.base_url = base_url
        self.headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json",
            "Origin": "https://flight.naver.com",
            "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/128.0.0.0 Safari/537.36"
                )
        }

    def build_payload(self, dep_airport, arr_airport, dep_date):
        """API 요청에 필요한 payload 구성"""
        return {
            "domesticRoundTrip": False,
            "specialTicket": False,
            "adult": 1,
            "child": 0,
            "infant": 0,
            "fareType": [],
            "depAirport": dep_airport,
            "arrAirport": arr_airport,
            "depDate": dep_date
        }

    def search_flights(self, dep_airport, arr_airport, dep_date):
        """항공권 API 호출"""
        payload = self.build_payload(dep_airport, arr_airport, dep_date)
        try:
            response = requests.post(self.base_url, headers=self.headers, data=json.dumps(payload), timeout=30)
            if response.status_code == 200:
                return response.text  # 아직 stream 데이터라서 JSON 파싱은 다른 함수에서 처리
            else:
                return None
        except requests.exceptions.RequestException as e:
            return str(e)

    def parse_flight_data(self, raw_text):
        """event-stream 형태 응답에서 마지막 JSON만 파싱"""
        try:
            json_lines = [line for line in raw_text.splitlines() if line.startswith("data:")]
            if not json_lines:
                return None
            json_str = json_lines[-1].lstrip("data:").strip()
            return json.loads(json_str)
        except Exception as e:
            return {"error": str(e)}
