"""
Telegram Notification Bridge for Mobile Pipeline Control (Razum AI)
Zero-dependency alerting engine sending real-time lead and audit push notifications
directly to Telegram on iOS / Android smartphones.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

TELEGRAM_API_BASE = "https://api.telegram.org"


class TelegramBridge:
    """Dispatches push notifications and PDF teardown files to Telegram."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = (bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
        self.chat_id = (chat_id or os.getenv("TELEGRAM_CHAT_ID", "")).strip()

    @property
    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Sends an HTML formatted text push notification."""
        if not self.is_configured:
            print(f"ℹ️ [TG Bridge (Dry Run / Token Unset)]: \n{text}\n")
            return True

        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("ok"):
                    print("📲 [TG Bridge]: Push-уведомление успешно доставлено в Telegram!")
                    return True
                else:
                    print(f"⚠️ [TG Bridge Error]: {res.get('description')}")
                    return False
        except Exception as err:
            print(f"❌ [TG Bridge Request Failed]: {err}")
            return False

    def send_lead_alert(self, lead_data: Dict[str, Any]) -> bool:
        """Sends an instant alert when a high-intent hiring lead is captured."""
        company = lead_data.get("company", "Unknown")
        role = lead_data.get("hiring_role", lead_data.get("role", "AI Engineer"))
        pain = lead_data.get("tech_stack_core_pain", lead_data.get("pain", "LLM Latency & Token Bloat"))
        email = lead_data.get("contact_email", lead_data.get("email", "N/A"))
        website = lead_data.get("website", "")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = (
            f"🎯 <b>NEW HIGH-INTENT B2B LEAD CAPTURED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 <b>Company:</b> {company}\n"
            f"🌐 <b>Website:</b> {website}\n"
            f"💼 <b>Hiring Role:</b> <code>{role}</code>\n"
            f"⚡ <b>Core Pain:</b> <i>{pain}</i>\n"
            f"✉️ <b>Contact:</b> {email}\n"
            f"🕒 <b>Timestamp:</b> {now_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🚀 <i>Status: Ready for 3-Page Audit Generation</i>"
        )
        return self.send_message(msg)

    def send_audit_ready_alert(self, company: str, pdf_path: str, public_url: str = "") -> bool:
        """Sends an alert when a 3-page confidential audit PDF has been rendered."""
        filename = os.path.basename(pdf_path)
        filesize_kb = round(os.path.getsize(pdf_path) / 1024, 1) if os.path.exists(pdf_path) else 0
        now_str = datetime.now().strftime("%H:%M:%S")

        landing_link = public_url or "http://localhost:8000/landing"

        msg = (
            f"📑 <b>3-PAGE PDF AUDIT READY FOR DISPATCH</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🏢 <b>Target:</b> {company}\n"
            f"📄 <b>File:</b> <code>{filename}</code> ({filesize_kb} KB)\n"
            f"🎯 <b>SLA Offer:</b> $490 Fixed 48h Sprint\n"
            f"🔗 <b>Microlanding:</b> <a href=\"{landing_link}\">Open Portal</a>\n"
            f"🕒 <b>Rendered:</b> {now_str}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✨ <i>Open email draft or approve dispatch in Sheets</i>"
        )
        return self.send_message(msg)

    def send_document(self, file_path: str, caption: str = "") -> bool:
        """Sends the raw PDF file directly to Telegram chat via multipart form-data."""
        if not self.is_configured:
            print(f"ℹ️ [TG Bridge (Dry Run Document)]: Would send {file_path} with caption '{caption}'")
            return True

        if not os.path.exists(file_path):
            print(f"⚠️ [TG Bridge]: File not found: {file_path}")
            return False

        url = f"{TELEGRAM_API_BASE}/bot{self.bot_token}/sendDocument"
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

        filename = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        body = bytearray()
        # Chat ID part
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{self.chat_id}\r\n'.encode("utf-8"))

        # Caption part
        if caption:
            body.extend(f"--{boundary}\r\n".encode("utf-8"))
            body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode("utf-8"))

        # Document file part
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="document"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: application/pdf\r\n\r\n")
        body.extend(file_bytes)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                if res.get("ok"):
                    print(f"📎 [TG Bridge]: PDF файл '{filename}' успешно отправлен в Telegram!")
                    return True
                else:
                    print(f"⚠️ [TG Bridge Error]: {res.get('description')}")
                    return False
        except Exception as err:
            print(f"❌ [TG Bridge File Upload Failed]: {err}")
            return False


# Singleton instance helper
tg_notifier = TelegramBridge()


if __name__ == "__main__":
    print("=" * 76)
    print("📲 [TEST] Telegram Bridge Push Notifier")
    print("=" * 76)

    test_lead = {
        "company": "PermitFlow",
        "website": "https://permitflow.com",
        "hiring_role": "Staff, Fullstack & Frontend Software Engineers",
        "tech_stack_core_pain": "Production LLM Token Budget Overrun & Unbounded API Gateway Latency",
        "contact_email": "jobs@permitflow.com"
    }

    print("\n1. Testing Lead Alert:")
    tg_notifier.send_lead_alert(test_lead)

    print("\n2. Testing Audit Ready Alert:")
    sample_pdf = os.path.abspath("output/audit_briefs/audit_permitflow.pdf")
    tg_notifier.send_audit_ready_alert(
        company="PermitFlow",
        pdf_path=sample_pdf,
        public_url="https://enticing-handstand-trouble.ngrok-free.dev/landing"
    )
