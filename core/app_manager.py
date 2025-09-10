# app_manager.py
import os
import time
import streamlit as st

from utils.common import pretty_json
from core.flight_monitor import FlightMonitor


class AppManager:
    def __init__(self, base_dir, kst_today, st):
        self.base_dir = base_dir
        self.kst_today = kst_today
        self.st = st
        self.data_path = os.path.join(self.base_dir, "data.json")

        # 기본 공항 초기화
        self.departure_airport_name = "제주국제공항"
        self.arrival_airport_name = "청주국제공항"
        self.departure_airport = "CJU"
        self.arrival_airport = "CJJ"
        self.departure_date = self.kst_today.strftime("%Y%m%d")

        # 공항 사전
        self.airport_dict = {
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
        self.airport_names = sorted(self.airport_dict.keys())

    def get_payload(self):
        """현재 선택값 기준으로 payload 생성"""
        return {
            "type": "domestic",
            "device": "PC",
            "fareType": "YC",
            "itineraries": [
                {
                    "departureAirport": self.departure_airport,
                    "arrivalAirport": self.arrival_airport,
                    "departureDate": self.departure_date
                }
            ],
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
    
    def init_session_state(self):
        """Streamlit 세션 상태 초기화"""
        if "monitoring" not in self.st.session_state:
            self.st.session_state.monitoring = False
        if "departure" not in self.st.session_state:
            self.st.session_state.departure = "제주국제공항"
        if "arrival" not in self.st.session_state:
            self.st.session_state.arrival = "청주국제공항"
            
    def run_monitoring(self):
        """Streamlit에서 모니터링 실행"""
        payload = self.get_payload
        monitor = FlightMonitor()
        start_time = self.start_time
        end_time = self.end_time
        data_path = self.data_path
        to_email = self.to_email
        with st.spinner("🔄 항공편을 조회 중입니다..."):
            try:
                data = FlightMonitor(monitor)
                filtered_result = self.processor.filter(data, start_time, end_time)

                if not filtered_result:
                    self.processor.save(filtered_result, data_path)
                    st.info("❗조건에 맞는 항공편이 없습니다.")
                else:
                    new_fare = filtered_result.get("fare", float("inf"))
                    existing_data = self.processor.load(data_path)
                    existing_fare = existing_data.get("fare", float("inf")) if existing_data else None

                    if not existing_fare or new_fare != existing_fare:
                        self.processor.save(filtered_result, data_path)
                        st.success(f"✅ 새로운 최저가 발견! {new_fare:,}원으로 업데이트")

                        # 이메일 발송
                        if to_email:
                            subject = "[알림] 새로운 항공권 발견"
                            body = pretty_json(filtered_result)
                            result = self.notifier.send(to_email, subject, body)
                            if result is True:
                                st.success("📧 메일 발송 성공!")
                            else:
                                st.error(f"메일 전송 실패: {result}")
                    else:
                        st.info(f"ℹ️ 기존 운임 {existing_fare:,}원이 더 저렴하거나 동일하므로 변경하지 않음.")

            except Exception as e:
                st.error(f"❌ 모니터링 오류 발생: {e}")

    def render_airport_selection(self):
        """출발/도착 공항 선택 UI 렌더링"""
        col1, col2, col3 = self.st.columns([4, 1, 4])
        
        with col1:
            selected_departure = self.st.selectbox(
                "출발 공항",
                self.airport_names,
                index=self.airport_names.index(self.st.session_state.departure),
                key="departure_select"
            )
            self.st.session_state.departure = selected_departure

        with col2:
            self.st.write("")
            if self.st.button("↔"):
                self.st.session_state.departure, self.st.session_state.arrival = (
                    self.st.session_state.arrival,
                    self.st.session_state.departure,
                )
                self.st.rerun()

        with col3:
            selected_arrival = self.st.selectbox(
                "도착 공항",
                self.airport_names,
                index=self.airport_names.index(self.st.session_state.arrival),
                key="arrival_select"
            )
            self.st.session_state.arrival = selected_arrival

    def render_date_time_selection(self):
        """탑승 날짜와 출발 시간 범위 선택 UI"""
        self.departure_date_obj = self.st.date_input(
            "탑승 날짜",
            value=self.kst_today
        )
        self.departure_date = self.departure_date_obj.strftime("%Y%m%d")

        time_options = [f"{h:02d}00" for h in range(0, 24)]
        self.start_time = self.st.selectbox(
            "출발 시간 범위 시작",
            time_options,
            index=6
        )
        self.end_time = self.st.selectbox(
            "출발 시간 범위 끝",
            time_options,
            index=12
        )

    def render_email_input(self):
        """이메일 입력 UI"""
        self.to_email = self.st.text_input(
            "받는 사람 이메일",
            value=getattr(self, "to_email", "")
        )
        
        
    def render_monitoring_buttons(self):
        """모니터링 시작/중지 버튼 UI"""
        self.placeholder = self.st.empty()

        if getattr(self.st.session_state, "monitoring", False):
            with self.placeholder.container():
                stop = self.st.button("🛑 모니터링 중지", type="primary", use_container_width=True)
                if stop:
                    self.st.session_state.monitoring = False
                    self.st.rerun()
        else:
            with self.placeholder.container():
                start = self.st.button("▶️ 항공편 모니터링 시작", type="secondary", use_container_width=True)
                if start:
                    if not (self.departure_date and self.start_time and self.end_time):
                        self.st.warning("⚠️ 모든 필드를 입력해주세요.")
                    else:
                        self.st.session_state.monitoring = True
                        self.st.rerun()
                        
    def auto_loop(self, payload, start_time, end_time, data_path, to_email, notion_page):
        """주기적 실행"""
        if st.session_state.monitoring:
            self.run_monitoring(payload, start_time, end_time, data_path, to_email)
            st.markdown(f"🔗 [항공권 추적차트 보기]({notion_page})")
            time.sleep(60)
            st.rerun()
