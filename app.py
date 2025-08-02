import os
import requests
import json
import time
from datetime import datetime, timedelta, timezone

import streamlit as st

from notion_api import load_json_data, create_notion_page
from processing import filter_flights, load_existing_data, save_data


kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
kst_today = kst_now.date()
    
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.json")
AIRPORT = sorted(["CJU", "GMP", "PUS", "ICN", "CJJ"])

st.set_page_config(page_title="최저가 항공권 추적기", layout="centered")
st.title("✈️ 항공편 추적기")

# 세션 상태 초기화
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
    
# 입력 UI
departure_airport = st.selectbox("출발 공항", AIRPORT)
arrival_airport = st.selectbox("도착 공항", AIRPORT)
departure_date_obj = st.date_input("탑승 날짜", value=kst_today)
departure_date = departure_date_obj.strftime("%Y%m%d")
time_options = [f"{h:02d}00" for h in range(0, 24)]
start_time = st.selectbox("출발 시간 범위 시작", time_options, index=8)
end_time = st.selectbox("출발 시간 범위 끝", time_options, index=12)

# 버튼 영역
placeholder = st.empty()

if st.session_state.monitoring:
    with placeholder.container():
        stop = st.button("🛑 모니터링 중지", type="primary", use_container_width=True)
        if stop:
            st.session_state.monitoring = False
            # st.info("🛑 모니터링이 중지되었습니다.")
            st.rerun()
else:
    with placeholder.container():
        start = st.button("▶️ 항공편 모니터링 시작", type="secondary", use_container_width=True)
        if start:
            if not (departure_date and start_time and end_time):
                st.warning("⚠️ 모든 필드를 입력해주세요.")
            else:
                st.session_state.monitoring = True
                # st.success("✅ 항공편 모니터링을 시작합니다.")
                st.rerun()

# 모니터링 로직
def run_monitoring():
    url = "https://flight-api.naver.com/flight/domestic/searchFlights"
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Origin": "https://flight.naver.com",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {
        "type": "domestic",
        "device": "PC",
        "fareType": "YC",
        "itineraries": [
            {
                "departureAirport": departure_airport,
                "arrivalAirport": arrival_airport,
                "departureDate": departure_date
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

    with st.spinner("🔄 항공편을 조회 중입니다..."):
        try:
            response = requests.post(url, headers=headers, json=payload)
            raw_text = response.content.decode("utf-8")
            json_lines = [line for line in raw_text.splitlines() if line.startswith("data:")]

            json_str = json_lines[-1].lstrip("data:").strip()
            data = json.loads(json_str)
            filtered_result = filter_flights(data, start_time, end_time)

            if not filtered_result:
                st.info("❗조건에 맞는 항공편이 없습니다.")
            else:
                new_fare = filtered_result.get("fare", float("inf"))
                existing_data = load_existing_data(DATA_PATH)
                existing_fare = existing_data.get("fare", float("inf")) if existing_data else None

                if not existing_fare or new_fare != existing_fare:
                    save_data(filtered_result, DATA_PATH)
                    notion_data = load_json_data(DATA_PATH)
                    create_notion_page(notion_data)
                    st.success(f"✅ 새로운 최저가 발견! {new_fare:,}원으로 업데이트")
                else:
                    st.info(f"ℹ️ 기존 운임 {existing_fare:,}원이 더 저렴하거나 동일하므로 변경하지 않음.")

        except json.JSONDecodeError as e:
            st.error(f"❌ JSON 파싱 실패: {e}")
            # st.text_area("응답 원본", raw_text[:500])

# 모니터링 상태면 주기 실행
if st.session_state.monitoring:
    run_monitoring()
    # st.info("⏱️ 60초 후 다음 조회가 자동 실행됩니다.")
    st.markdown("🔗 [항공권 추적차트 보기](https://kbae.notion.site/23d9c513049880398cdaf5a2e4697e40?source=copy_link)")
    time.sleep(60)
    st.rerun()
