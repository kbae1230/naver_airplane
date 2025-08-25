

## ✈️ 소개

**naver_airplane**은 [Notion API](https://www.notion.so/)와 Naver 항공권 API를 통합하여 항공편 정보를 추적하고 시각화 및 알림을 받는 애플리케이션입니다.

<img width="786" height="575" alt="image" src="https://github.com/user-attachments/assets/8ddc6e99-20ee-4bdf-be1d-e1b0162683e5" />

## 🚀 기능

- 항공권 최저가 또는 취소표 메일 알림
- 항공권 정보 결과를 노션에 시각화하여 사용자에게 제공

## 🛠️ 기술 스택

- Python 3.x
- Notion API
- Streamlit (for web interface)
- 기타 Python 라이브러리

## 📁 파일 구조

```text
naver_airplane/
├── app.py              # 메인 애플리케이션 코드
├── notion_api.py       # Notion API와의 통신 코드
├── processing.py       # 데이터 처리 및 필터링 코드
├── data.json           # 애플리케이션 데이터 파일
├── .devcontainer/      # 개발 환경 설정 파일
├── .github/workflows/  # GitHub Actions 워크플로우 설정 파일

└── .vscode/            # VS Code 설정 파일
```

## ⚠️ Secret 설정
Step 1. Make a toml file named with secrets.toml under .streamlit

```text
[notion]
token = ""
database = ""
page = ""

[email]
id = ""
pw = "" # This is an APP PASSWORD not Real password. How to generate it (https://support.google.com/mail/thread/205453566/how-to-generate-an-app-password?hl=en")
```
Step 2. Set Secrets in App settings (https://share.streamlit.io/)
