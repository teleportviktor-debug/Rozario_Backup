"""
Real Google Gmail API OAuth Service (services/integration/gmail_oauth_service.py)
Agent 4 (Integration Lead) & Agent 3 (System Orchestrator)
Zero-Tolerance-To-Mocking Direct Gmail Dispatcher via OAuth 2.0.

Workflow:
1. Loads or initiates OAuth 2.0 flow using 'credentials.json' / 'client_secret.json'.
2. Persists user authorization in 'token_gmail.json'.
3. Authorizes official Gmail API v1 client with scope:
   https://www.googleapis.com/auth/gmail.compose
4. Real creation of drafts in personal mailbox:
   service.users().drafts().create(userId='me', body={'message': {'raw': raw_b64}})
"""

import os
import sys
import json
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Required Gmail scope for composing drafts and messages
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

TOKEN_FILE = os.path.abspath("token_gmail.json")
CREDENTIALS_CANDIDATES = [
    os.path.abspath("credentials.json"),
    os.path.abspath("client_secret.json"),
    os.path.abspath(r"C:\Users\user\Downloads\client_secret_309834348335-0evg1ddbhp6kviurpk6unbgsf6s03l44.apps.googleusercontent.com.json"),
]


def resolve_client_secret_file() -> str:
    """Finds existing OAuth 2.0 client secret JSON file."""
    for path in CREDENTIALS_CANDIDATES:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        "OAuth 2.0 Client Secret (credentials.json) не найден. "
        "Поместите client_secret.json в корень проекта."
    )


def get_gmail_credentials() -> Credentials:
    """
    Authenticates user via OAuth 2.0 to access personal Gmail inbox.
    Loads valid token from token_gmail.json, refreshes if expired,
    or launches local server auth flow.
    """
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            print(f"✓ [GMAIL OAUTH] Загружен сохраненный токен: {TOKEN_FILE}")
        except Exception as e:
            print(f"⚠️ [GMAIL OAUTH] Ошибка чтения токена {TOKEN_FILE}: {e}")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 [GMAIL OAUTH] Обновление истекшего access токена через refresh token...")
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, "w", encoding="utf-8") as token_out:
                    token_out.write(creds.to_json())
                print("✓ [GMAIL OAUTH] Токен успешно обновлен.")
                return creds
            except Exception as e:
                print(f"⚠️ [GMAIL OAUTH] Ошибка обновления токена: {e}. Запуск новой авторизации...")

        # Initiates fresh browser OAuth flow
        client_secrets_path = resolve_client_secret_file()
        print(f"🔑 [GMAIL OAUTH] Инициализация OAuth flow через: {client_secrets_path}")
        print("🌐 [GMAIL OAUTH] Открываем локальный сервер для однократной авторизации пользователя...")
        flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
        creds = flow.run_local_server(port=8088, open_browser=True, prompt="consent", access_type="offline")

        with open(TOKEN_FILE, "w", encoding="utf-8") as token_out:
            token_out.write(creds.to_json())
        print(f"✓ [GMAIL OAUTH] Новый токен сохранен в {TOKEN_FILE}")

    return creds


def get_real_gmail_service():
    """Returns official Google Gmail API v1 service instance."""
    creds = get_gmail_credentials()
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def create_real_gmail_draft(
    to_email: str,
    subject: str,
    html_body: str,
    plain_body: str,
    company: str
) -> Dict[str, Any]:
    """
    Creates a REAL draft in personal Gmail inbox (mail.google.com).
    Returns real API response dictionary containing 'id' and 'message'.
    """
    service = get_real_gmail_service()

    message = MIMEMultipart("alternative")
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(plain_body, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    raw_b64 = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    body = {
        "message": {
            "raw": raw_b64
        }
    }

    print(f"🚀 [GMAIL API CALL] Отправка запроса drafts().create(userId='me') для {to_email}...")
    response = service.users().drafts().create(userId="me", body=body).execute()

    draft_id = response.get("id")
    msg_id = response.get("message", {}).get("id")
    print(f"💎 [REAL GMAIL DRAFT CREATED] Настоящий ID черновика: {draft_id} (Message ID: {msg_id})")

    # Persist copy in local CRM draft logs
    drafts_dir = os.path.join("03_CRM_LEADS", "drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    draft_record = {
        "draft_id": draft_id,
        "message_id": msg_id,
        "created_at": datetime.now().isoformat(),
        "to": to_email,
        "company": company,
        "subject": subject,
        "plain_text": plain_body,
        "html_body": html_body,
        "raw_response": response
    }
    with open(os.path.join(drafts_dir, f"{draft_id}.json"), "w", encoding="utf-8") as f:
        json.dump(draft_record, f, ensure_ascii=False, indent=2)

    return response


if __name__ == "__main__":
    print("Testing Gmail OAuth connection...")
    service = get_real_gmail_service()
    profile = service.users().getProfile(userId="me").execute()
    print("✓ Successfully connected to Gmail user account:", profile.get("emailAddress"))
