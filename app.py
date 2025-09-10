# app.py
import os
from datetime import datetime, timedelta, timezone
import streamlit as st

from core.app_manager import AppManager

# --- 기본 설정 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
kst_now = datetime.now(timezone.utc) + timedelta(hours=9)
kst_today = kst_now.date()

# --- Streamlit 페이지 설정 ---
st.set_page_config(page_title="최저가 항공권 추적기", layout="centered")
st.title("✈️ 항공편 추적기")

# --- AppManager 인스턴스 생성 ---
manager = AppManager(base_dir=BASE_DIR, kst_today=kst_today, st=st)

# --- UI 구성 및 상태 초기화 ---
manager.init_session_state()
manager.render_airport_selection()
manager.render_date_time_selection()
manager.render_email_input()
manager.render_monitoring_buttons()

# --- 모니터링 실행 ---
if st.session_state.monitoring:
    manager.run_monitoring()
