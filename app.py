import os
import requests
import json
import time
import random
from datetime import datetime, timedelta, timezone

import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from processing import filter_flights, load_existing_data, save_data

# =========================
# 기본 설정
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.json")

EMAIL = st.secrets["email"]["id"]
PASSWORD = st.secrets["email"]["pw"]

kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
kst_today = kst_now.date()

airport_dict = {
    "김포국제공항": "GMP",
    "인천국제공항": "ICN",
    "김해국제공항": "PUS",
    "제주국제공항": "CJU",
    "청주국제공항": "CJJ",
    "대구국제공항": "TAE",
    "양양국제공항": "YNY",
    "무안국제공항": "MWX",
    "여수공항": "RSU",
    "사천공항": "HIN",
    "포항공항": "KPO",
    "군산공항": "KUV",
    "원주공항": "WJU",
    "울산공항": "USN"
}
airport_names = sorted(airport_dict.keys())

# =========================
# API 설정
# =========================
URL = "https://flight-api.naver.com/flight/domestic/searchFlights"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
]

def make_headers():
    return {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
        "Origin": "https://flight.naver.com",
        "User-Agent": random.choice(USER_AGENTS),
    }

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="최저가 항공권 추적기", layout="centered")
st.title("✈️ 항공편 추적기")

if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
if "dep_idx" not in st.session_state:
    st.session_state.dep_idx = airport_names.index("제주국제공항")
if "arr_idx" not in st.session_state:
    st.session_state.arr_idx = airport_names.index("청주국제공항")

col1, col2, col3 = st.columns([4, 1, 4])
with col1:
    dep_idx = st.selectbox(
        "출발 공항",
        range(len(airport_names)),
        index=st.session_state.dep_idx,
        format_func=lambda x: airport_names[x],
    )

with col2:
    st.write("")
    if st.button("↔"):
        st.session_state.dep_idx, st.session_state.arr_idx = (
            st.session_state.arr_idx,
            st.session_state.dep_idx,
        )
        st.rerun()

with col3:
    arr_idx = st.selectbox(
        "도착 공항",
        range(len(airport_names)),
        index=st.session_state.arr_idx,
        format_func=lambda x: airport_names[x],
    )

st.session_state.dep_idx = dep_idx
st.session_state.arr_idx = arr_idx

departure_airport = airport_dict[airport_names[dep_idx]]
arrival_airport = airport_dict[airport_names[arr_idx]]

departure_date_obj = st.date_input("탑승 날짜", value=kst_today)
departure_date = departure_date_obj.strftime("%Y%m%d")

time_options = [f"{h:02d}00" for h in range(24)]
start_time = st.selectbox("출발 시간 시작", time_options, index=6)
end_time = st.selectbox("출발 시간 끝", time_options, index=12)

to_email = st.text_input("받는 사람 이메일")

payload = {
    "type": "domestic",
    "device": "PC",
    "fareType": "YC",
    "itineraries": [{
        "departureAirport": departure_airport,
        "arrivalAirport": arrival_airport,
        "departureDate": departure_date
    }],
    "person": {"adult": 1, "child": 0, "infant": 0},
    "tripType": "OW",
    "initialRequest": True,
    "flightFilter": {
        "filter": {"type": "departure"},
        "limit": 50,
        "skip": 0,
        "sort": {"segment.departure.time": 1, "minFare": 1}
    }
}

# =========================
# 이메일
# =========================
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return str(e)

# =========================
# 모니터링 로직 (핵심)
# =========================
def run_monitoring():
    with st.spinner("🔄 항공편 조회 중..."):
        headers = make_headers()
        response = requests.post(URL, headers=headers, json=payload)

        st.write("📡 HTTP 상태코드:", response.status_code)
        st.write("📦 Content-Type:", response.headers.get("Content-Type"))

        # 🚫 서버 차단 / 오류
        if response.status_code != 200:
            st.error("🚫 서버 오류 또는 차단 감지")
            st.code(response.text[:1000], language="html")
            st.session_state.monitoring = False
            return

        raw_text = response.text

        # HTML 응답 방어
        if raw_text.strip().startswith("<html"):
            st.error("🚫 HTML 응답 수신 (차단/서버 오류)")
            st.code(raw_text[:1500], language="html")
            st.session_state.monitoring = False
            return

        json_lines = [l for l in raw_text.splitlines() if l.startswith("data:")]
        if not json_lines:
            st.error("❌ data: SSE 라인이 없음")
            st.code(raw_text[:1500])
            st.session_state.monitoring = False
            return

        json_str = json_lines[-1].replace("data:", "").strip()
        data = json.loads(json_str)

        filtered = filter_flights(data, start_time, end_time)

        if not filtered:
            st.info("조건에 맞는 항공편 없음")
            save_data(filtered, DATA_PATH)
            return

        existing = load_existing_data(DATA_PATH)
        if not existing or filtered["fare"] != existing.get("fare"):
            save_data(filtered, DATA_PATH)
            st.success(f"✅ 최저가 갱신: {filtered['fare']:,}원")

            if to_email:
                send_email(
                    to_email,
                    "[알림] 항공권 최저가",
                    json.dumps(filtered, ensure_ascii=False, indent=2)
                )
        else:
            st.info("기존 최저가 유지")

# =========================
# 실행 루프
# =========================
placeholder = st.empty()

if st.session_state.monitoring:
    run_monitoring()
    time.sleep(random.randint(90, 180))
    st.rerun()
else:
    if st.button("▶️ 항공편 모니터링 시작", use_container_width=True):
        st.session_state.monitoring = True
        st.rerun()
