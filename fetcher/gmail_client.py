"""
Gmail API로 SSD/자동차 SW 데일리 다이제스트 메일을 가져오는 모듈.

사전 준비:
1. Google Cloud Console에서 발급받은 credentials.json을
   이 파일과 같은 폴더(fetcher/)에 둔다.
2. pip install google-auth-oauthlib google-api-python-client --break-system-packages
3. 처음 실행하면 브라우저가 뜨면서 Google 로그인 + 권한 동의를 요구한다.
   동의하면 token.json이 자동 생성되고, 이후로는 재인증 없이 동작한다.
"""

from __future__ import annotations

import base64
import os
import re
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 메일을 "읽기"만 하면 되므로 readonly 범위만 요청한다.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(CURRENT_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CURRENT_DIR, "token.json")

# 다이제스트 메일 제목 패턴: "[2026-09-08] SSD/자동차 SW 펌웨어 데일리 브리핑"
SUBJECT_PATTERN = re.compile(r"\[(\d{4}-\d{2}-\d{2})\]\s*SSD")


def get_gmail_service():
    """OAuth 인증을 처리하고 Gmail API 서비스 객체를 반환한다."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif os.environ.get("CI"):
            # GitHub Actions 등 headless 환경에서는 브라우저 인증 플로우를
            # 띄울 수 없다. token.json에 유효한 refresh_token이 이미 있어야 한다.
            raise RuntimeError(
                "CI 환경에서 Gmail 인증에 실패했습니다. "
                "로컬에서 한 번 인증을 완료한 뒤 생성된 token.json 내용을 "
                "GMAIL_TOKEN_JSON 시크릿에 최신 상태로 넣어주세요."
            )
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _decode_body(payload: dict) -> str:
    """Gmail API 메시지 payload에서 본문 텍스트를 추출한다."""
    if "parts" in payload:
        for part in payload["parts"]:
            # text/plain을 우선적으로 찾는다.
            if part.get("mimeType") == "text/plain":
                data = part["body"].get("data")
                if data:
                    return base64.urlsafe_b64decode(data).decode(
                        "utf-8", errors="ignore"
                    )
        # text/plain이 없으면 재귀적으로 하위 parts 탐색
        for part in payload["parts"]:
            result = _decode_body(part)
            if result:
                return result
        return ""
    else:
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode(
                "utf-8", errors="ignore"
            )
        return ""


def fetch_latest_digest(days_back: int = 2) -> dict | None:
    """
    최근 `days_back`일 내에 도착한 다이제스트 메일 중 가장 최신 것을 가져온다.

    Returns:
        {"date": "2026-09-08", "subject": "...", "body": "..."} 또는
        해당 기간에 다이제스트가 없으면 None
    """
    service = get_gmail_service()

    after_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y/%m/%d")
    query = f'subject:"SSD" after:{after_date}'

    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=10)
        .execute()
    )
    messages = results.get("messages", [])

    for msg_ref in messages:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=msg_ref["id"], format="full")
            .execute()
        )

        headers = msg["payload"]["headers"]
        subject = next(
            (h["value"] for h in headers if h["name"] == "Subject"), ""
        )

        match = SUBJECT_PATTERN.search(subject)
        if not match:
            continue

        body = _decode_body(msg["payload"])

        return {
            "date": match.group(1),
            "subject": subject,
            "body": body,
        }

    return None


if __name__ == "__main__":
    digest = fetch_latest_digest()
    if digest:
        print(f"=== {digest['date']} : {digest['subject']} ===")
        print(digest["body"][:500])
        print("... (생략)")
    else:
        print("최근 다이제스트 메일을 찾지 못했습니다.")
