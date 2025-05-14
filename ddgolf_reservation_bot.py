import sys
import requests
import re
from datetime import datetime, timedelta
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


def login(user_id, password):
    session = requests.Session()
    session.get("http://www.ddgolf.co.kr/08member/member01.asp")
    login_url = "http://www.ddgolf.co.kr/08member/login_ok.asp"
    login_payload = {
        "page": "",
        "UserID": user_id,
        "Password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "http://www.ddgolf.co.kr/08member/member01.asp",
        "Origin": "http://www.ddgolf.co.kr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    login_response = session.post(login_url, data=login_payload, headers=headers, allow_redirects=False)
    return session, login_response


def reserve_page_crawling(session, submit_date):
    reserve_url = "http://www.ddgolf.co.kr/03reservation/reservation01_1.asp"
    reserve_payload = {"submitDate": submit_date}
    reserve_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"http://www.ddgolf.co.kr/03reservation/reservation01_240826.asp",
        "Origin": "http://www.ddgolf.co.kr",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = session.post(reserve_url, data=reserve_payload, headers=reserve_headers)
    html = res.text
    matches = re.findall(
        r"""bookProsecc\(\s*'([^']*)','([^']*)','([^']*)','([^']*)','([^']*)','([^']*)','([^']*)'\s*\)""",
        html)
    cart_values = dict(re.findall(
        r"""<input[^>]+id=["']a_cart(\d+)["'][^>]+value=["']([^"']*)["']""",
        html
    ))
    return res, matches, cart_values

class GolfReservationChecker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⛳ DD Golf 예약 매크로")
        self.setGeometry(100, 100, 600, 500)

        # 저장된 로그인 정보
        self.stored_id = None
        self.stored_pw = None

        self.user_info_label = QLabel("👤 사용자 정보\nID: 없음\n상태: 미저장")
        self.user_info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.user_info_label.setStyleSheet("font-size: 14px; padding: 10px;")

        self.warning_message = QLabel("🚨 컴퓨터가 꺼지면 예약을 수행할 수 없습니다.\n🚨 때문에 월요일 아침에 해당 프로그램을 실행하시는 걸 추천드립니다.")
        self.warning_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.warning_message.setStyleSheet("color: red; font-size: 14px; padding: 5px;")

        self.next_run_label = QLabel("⏳ 자동 예약 실행까지 남은 시간\n⏰ --:--:--")
        self.next_run_label.setStyleSheet("font-size: 12px; color: gray; padding: 5px;")

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("아이디 입력")
        self.pw_input = QLineEdit()
        self.pw_input.setPlaceholderText("비밀번호 입력")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("💾 로그인 정보 저장")
        self.login_button.clicked.connect(self.login_button_clicked)

        self.date_label = QLabel("예약 날짜 (YYYYMMDD) 및 시간 범위:")
        self.date_input_list = QListWidget()
        self.date_input_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.add_button = QPushButton("➕ 날짜/시간 항목 추가")
        self.remove_button = QPushButton("➖ 선택된 날짜/시간 항목 삭제")
        self.check_button = QPushButton("📅 즉시 예약 진행")
        self.reserve_button = QPushButton("⏰ 자동 예약 진행")
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        self.add_button.clicked.connect(self.add_date_time_entry)
        self.remove_button.clicked.connect(self.remove_selected_entries)
        self.check_button.clicked.connect(self.main_core)
        # self.reserve_button.clicked.connect(self.setup_weekly_timer)
        self.reserve_button.clicked.connect(self.setup_fast_request_timer)

        self.auto_trigger_timer = QTimer()
        self.auto_trigger_timer.timeout.connect(self.update_countdown)
        self.auto_trigger_timer.start(1000)

        login_layout = QVBoxLayout()
        login_layout.addWidget(QLabel("🔐 로그인 정보"))
        login_layout.addWidget(self.id_input)
        login_layout.addWidget(self.pw_input)
        login_layout.addWidget(self.login_button)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.date_label)
        input_layout.addWidget(self.date_input_list)
        input_layout.addWidget(self.add_button)
        input_layout.addWidget(self.remove_button)

        right_layout = QVBoxLayout()
        right_layout.addLayout(login_layout)
        right_layout.addLayout(input_layout)
        right_layout.addWidget(self.check_button)
        right_layout.addWidget(self.reserve_button)
        right_layout.addWidget(self.result_display)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.user_info_label)
        left_layout.addWidget(self.next_run_label)
        left_layout.addStretch()

        center_layout = QHBoxLayout()
        center_layout.addLayout(left_layout, 1)
        center_layout.addLayout(right_layout, 3)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.warning_message)
        main_layout.addLayout(center_layout)

        self.setLayout(main_layout)

    def log(self, message: str):
        self.result_display.append(message)
        with open("log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} : " + message + "\n")

    def update_countdown(self):
        now = datetime.now()
        if now.weekday() == 0:
            days_ahead = 0 if now.hour < 13 else 7
        else:
            days_ahead = (7 - now.weekday()) % 7
        next_monday_13 = datetime.combine(now.date() + timedelta(days=days_ahead), datetime.min.time()) + timedelta(
            hours=13)
        remaining = next_monday_13 - now

        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        self.next_run_label.setText(f"⏳ 자동 예약 실행까지 남은 시간\n⏰ {time_str}")

    def setup_fast_request_timer(self):
        now = datetime.now()

        # 다음 월요일 12:59:00 계산
        days_ahead = (7 - now.weekday()) % 7
        if days_ahead == 0 and now.hour >= 13:
            days_ahead = 7
        next_monday = now + timedelta(days=days_ahead)
        start_time = next_monday.replace(hour=12, minute=59, second=0, microsecond=0)

        delay_ms = int((start_time - now).total_seconds() * 1000)

        self.fast_start_timer = QTimer(self)
        self.fast_start_timer.setSingleShot(True)
        self.fast_start_timer.timeout.connect(self.start_spamming_main_core)
        self.fast_start_timer.start(delay_ms)

        self.log(f"⏰ 빠른 요청 시작 예약됨: {start_time}")

    def start_spamming_main_core(self):
        self.log("🚀 빠른 요청 시작!")

        # 빠른 호출용 타이머 (0.1초 간격)
        self.spam_timer = QTimer(self)
        self.spam_timer.timeout.connect(self.main_core)
        self.spam_timer.start(100)  # 100ms = 0.1초

        # 종료용 타이머 설정 (3분 후 정지)
        self.stop_timer = QTimer(self)
        self.stop_timer.setSingleShot(True)
        self.stop_timer.timeout.connect(self.stop_spamming_main_core)
        self.stop_timer.start(3 * 60 * 1000)  # 3분 = 180,000ms

    def stop_spamming_main_core(self):
        self.spam_timer.stop()
        self.log("🛑 빠른 요청 종료 (13:02)")
        # 다음 주를 위해 다시 예약
        self.setup_fast_request_timer()

    def login_button_clicked(self):
        user_id = self.id_input.text().strip()
        password = self.pw_input.text().strip()

        if not user_id or not password:
            self.log("❌ 아이디 또는 비밀번호를 입력해주세요.")
            return

        session, login_response = login(user_id, password)
        if login_response.status_code != 302 or login_response.headers.get("Location") != "/":
            self.log("❌ 로그인이 불가능한 계정 정보입니다.")
            return
        else:
            self.log("✅ 로그인이 가능한 계정 정보입니다.")

        self.stored_id = user_id
        self.stored_pw = password
        self.user_info_label.setText(f"👤 사용자 정보\nID: {user_id}\n상태: 저장됨")
        self.log("✅ 로그인 정보가 저장되었습니다.")

    def main_core(self):
        if not self.stored_id or not self.stored_pw:
            self.log("⚠️ 먼저 로그인 정보를 저장해주세요.")
            return

        try:
            # 매 예약 시도마다 새 로그인
            session, login_response = login(self.stored_id, self.stored_pw)
            if login_response.status_code != 302 or login_response.headers.get("Location") != "/":
                self.log("❌ 예약 전에 로그인 실패. 정보 확인 필요.")
                return

            date_time_entries = self.get_date_time_entries()
            if date_time_entries:
                for entry in date_time_entries:
                    print(entry)
                    date, start_time, end_time = entry
                    res, matches, cart_values = reserve_page_crawling(session=session, submit_date=date)
                    if res.status_code == 200:
                        self.log(f"✅ 예약 페이지 접속 성공 ({date})")
                        if matches:
                            self.log(f"🔍 전체 예약 가능 항목 : {len(matches)}")
                            success_count = 0
                            for i, match in enumerate(matches, 1):
                                (
                                    paraBookDate, paraBookTime, paraBookCrs, paraBookCname,
                                    j, paraRoundf, paraCartDiv
                                ) = match

                                if start_time <= int(paraBookTime) <= end_time:
                                    a_cart = cart_values.get(j, "0")  # 기본값은 "0"

                                    reservation_data = {
                                        "book_date": paraBookDate,
                                        "book_time": paraBookTime,
                                        "book_crs": paraBookCrs,
                                        "person": "4",
                                        "a_cart": a_cart,
                                        "roundf": paraRoundf
                                    }

                                    reservation_headers = {
                                        "Content-Type": "application/x-www-form-urlencoded",
                                        "Referer": f"http://www.ddgolf.co.kr/03reservation/reservation01_240826.asp",
                                        "Origin": "http://www.ddgolf.co.kr",
                                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                                    }

                                    # 디버깅.
                                    self.log(f"⏰ 현재 시각 : {datetime.now()}")
                                    self.log(f"📦 [예약 시도 {i}번]")
                                    self.log(f"➡ URL: http://www.ddgolf.co.kr/03reservation/reservation_submit4.asp")
                                    self.log(f"➡ DATA: {reservation_data}")
                                    self.log(f"➡ HEADERS: {reservation_headers}")

                                    res_submit = session.post(
                                        "http://www.ddgolf.co.kr/03reservation/reservation_submit4.asp",
                                        data=reservation_data,
                                        headers=reservation_headers
                                    )

                                    if res_submit.status_code == 200 and "alert" not in res_submit.text.lower():
                                        self.log(f"✅ {i}. 예약 시도 성공 - {paraBookDate} | {paraBookTime}")
                                        success_count += 1
                                    else:
                                        self.log(f"❌ {i}. 예약 시도 실패 - {paraBookDate} | {paraBookTime}")
                                else:
                                    self.log(f"⏭️ {i}. 예약 시간 {paraBookDate} | {paraBookTime}은 지정한 시간 범위 밖입니다. 건너뜁니다.")
                            self.log(f"🎯 총 예약 성공: {success_count}건")
                        else:
                            self.log("⚠️ 예약 가능 항목이 없습니다.")
                    else:
                        self.log(f"❌ 예약 페이지 접속 실패 ({date})")
            else:
                self.log("❌ 날짜/시간 범위가 올바르지 않습니다.")
        except Exception as e:
            self.log(f"🚨 오류 발생: {str(e)}")

    def add_date_time_entry(self):
        dialog = DateTimeInputDialog(self)
        if dialog.exec():
            date, start_time, end_time = dialog.get_values()
            if date and start_time and end_time:
                item = f"{date} | {start_time} ~ {end_time}"
                self.date_input_list.addItem(item)

    def remove_selected_entries(self):
        selected_items = self.date_input_list.selectedItems()
        for item in selected_items:
            row = self.date_input_list.row(item)
            self.date_input_list.takeItem(row)

    def get_date_time_entries(self):
        entries = []
        for i in range(self.date_input_list.count()):
            item = self.date_input_list.item(i).text()
            date, time_range = item.split(" | ")
            start_time, end_time = time_range.split(" ~ ")
            entries.append((date.strip(), int(start_time.strip()), int(end_time.strip())))
        return entries


class DateTimeInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("날짜 및 시간 입력")
        self.setGeometry(200, 200, 300, 300)

        # 날짜 입력 (달력)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyyMMdd")

        # 시(hour)와 분(minute) 선택 콤보박스
        self.start_hour_combo = QComboBox()
        self.start_minute_combo = QComboBox()
        self.end_hour_combo = QComboBox()
        self.end_minute_combo = QComboBox()

        # 시, 분 선택 항목 설정
        self.start_hour_combo.addItems([f"{h:02}" for h in range(1, 25)])
        self.end_hour_combo.addItems([f"{h:02}" for h in range(1, 25)])
        self.start_minute_combo.addItems(["00", "30"])
        self.end_minute_combo.addItems(["00", "30"])

        # 확인 및 취소 버튼
        self.ok_button = QPushButton("확인")
        self.cancel_button = QPushButton("취소")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # 레이아웃 구성
        layout = QVBoxLayout()

        layout.addWidget(QLabel("📅 날짜"))
        layout.addWidget(self.date_edit)

        layout.addWidget(QLabel("⏰ 시작 시간"))
        start_time_layout = QHBoxLayout()
        start_time_layout.addWidget(self.start_hour_combo)
        start_time_layout.addWidget(QLabel(":"))
        start_time_layout.addWidget(self.start_minute_combo)
        layout.addLayout(start_time_layout)

        layout.addWidget(QLabel("⏰ 끝 시간"))
        end_time_layout = QHBoxLayout()
        end_time_layout.addWidget(self.end_hour_combo)
        end_time_layout.addWidget(QLabel(":"))
        end_time_layout.addWidget(self.end_minute_combo)
        layout.addLayout(end_time_layout)

        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def get_values(self):
        date_str = self.date_edit.date().toString("yyyyMMdd")
        start_time_str = f"{self.start_hour_combo.currentText()}{self.start_minute_combo.currentText()}"
        end_time_str = f"{self.end_hour_combo.currentText()}{self.end_minute_combo.currentText()}"
        return (date_str, start_time_str, end_time_str)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GolfReservationChecker()
    window.show()
    sys.exit(app.exec())
