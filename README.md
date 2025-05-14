# DDGolf Reservation Bot

⛳ A desktop application that automates golf course reservations for [ddgolf.co.kr](http://www.ddgolf.co.kr), with a built-in PyQt6 GUI. Supports both immediate and scheduled weekly reservation attempts.

> ⚠️ **Disclaimer**: This tool is intended for personal and authorized use only. Do not attempt to automate or exploit systems without permission.

> ✅ **.py source code included**  
> ✅ **.exe executable included** (for Windows users who don’t have Python installed)

---

## 🚀 Features

- Secure login with stored credentials
- Add and manage desired reservation dates and time ranges
- Manual reservation trigger
- Automatic weekly reservation at **Monday 13:00**
- Logs all actions to `log.txt`
- Visual countdown to next reservation attempt

---

## 💻 How to Run

### Option 1: Run the Executable (Recommended for Windows users)

Download and run:

```
DDGolf_Reservation_Bot.exe
```

> ⚠️ Make sure to **run on Monday before 13:00**, and **keep your PC on and the app running** until at least 13:02 for auto-reservation to work properly.

---

### Option 2: Run the Python Source

#### Requirements

- Python 3.9+
- Required packages:

```bash
pip install PyQt6 requests
```

#### Run the app

```bash
python ddgolf_reservation_bot.py
```

---

## 📁 File Structure

```
ddgolf_reservation_bot.py   # Main source code (GUI application)
DDGolf_Reservation_Bot.exe  # Windows executable
README.md                   # Project documentation
LICENSE                     # License (MIT)
log.txt                     # Log file (generated after running)
```

---

## 🧪 Example UI & Output

- 로그인 정보 저장
- 예약 날짜와 시간 입력
- 예약 성공/실패 로그 표시
- 자동 예약 타이머 표시

```
✅ 로그인이 가능한 계정 정보입니다.
✅ 예약 페이지 접속 성공 (20250520)
🔍 전체 예약 가능 항목 : 4
✅ 1. 예약 시도 성공 - 20250520 | 0930
🛑 빠른 요청 종료 (13:02)
```

---

## 🧑‍💻 Author

- Email: gump71036969@gmail.com

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.