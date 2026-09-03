"""
============================================================================
GOOGLE DRIVE MARKDOWN CONVERTER • ZERO-FRICTION CONFIGURATION
Supports: Direct Raw JSON paste, Individual Env Tokens, Base64 & Local Files
============================================================================
"""

import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Google Drive Folder Names / IDs
INBOX_FOLDER_NAME = os.getenv("DRIVE_INBOX_FOLDER", "01_INBOX")
NOTEBOOK_FOLDER_NAME = os.getenv("DRIVE_NOTEBOOK_FOLDER", "02_FOR_NOTEBOOK")
ARCHIVE_FOLDER_NAME = os.getenv("DRIVE_ARCHIVE_FOLDER", "_ARCHIVE")

INBOX_FOLDER_ID = os.getenv("DRIVE_INBOX_FOLDER_ID", None)
NOTEBOOK_FOLDER_ID = os.getenv("DRIVE_NOTEBOOK_FOLDER_ID", None)
ARCHIVE_FOLDER_ID = os.getenv("DRIVE_ARCHIVE_FOLDER_ID", None)

# --- 1. DIRECT RAW JSON ---
SERVICE_ACCOUNT_RAW_JSON = os.getenv("GCP_SERVICE_ACCOUNT_JSON", None)

# --- 2. INDIVIDUAL ENV TOKENS ---
GCP_CLIENT_EMAIL = os.getenv("GCP_CLIENT_EMAIL", None)
GCP_PRIVATE_KEY = os.getenv("GCP_PRIVATE_KEY", None)
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", None)

# --- 3. BACKWARDS COMPATIBILITY ---
SERVICE_ACCOUNT_JSON_BASE64 = os.getenv("GCP_SERVICE_ACCOUNT_BASE64", None)
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

# Polling and batch settings
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
BATCH_SIZE_LIMIT = int(os.getenv("BATCH_SIZE_LIMIT", "20"))
TEMP_DIR = os.getenv("LOCAL_TEMP_DIR", "/tmp/drive_converter" if os.name != 'nt' else str(Path.home() / ".cache" / "drive_converter"))

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".html", ".htm", ".txt", ".csv", ".json", ".xml", ".rtf", ".md"
}

def get_service_account_credentials_dict():
    """
    Auto-detects credentials in 4 zero-friction ways:
    1. Direct Raw JSON string in GCP_SERVICE_ACCOUNT_JSON
    2. Individual plain text tokens (GCP_CLIENT_EMAIL + GCP_PRIVATE_KEY)
    3. Base64 encoded string in GCP_SERVICE_ACCOUNT_BASE64
    4. Local service_account.json file
    """
    # 1. Direct Raw JSON string
    if SERVICE_ACCOUNT_RAW_JSON and SERVICE_ACCOUNT_RAW_JSON.strip():
        try:
            return json.loads(SERVICE_ACCOUNT_RAW_JSON.strip())
        except Exception as e:
            raise ValueError(f"Ошибка чтения GCP_SERVICE_ACCOUNT_JSON: {e}")

    # 2. Individual plain text tokens
    if GCP_CLIENT_EMAIL and GCP_PRIVATE_KEY:
        private_key = GCP_PRIVATE_KEY.replace("\\n", "\n")
        return {
            "type": "service_account",
            "project_id": GCP_PROJECT_ID or "razum-google-ai-pro",
            "private_key": private_key,
            "client_email": GCP_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token"
        }

    # 3. Base64 encoded JSON
    if SERVICE_ACCOUNT_JSON_BASE64 and SERVICE_ACCOUNT_JSON_BASE64.strip():
        try:
            decoded = base64.b64decode(SERVICE_ACCOUNT_JSON_BASE64.strip()).decode("utf-8")
            return json.loads(decoded)
        except Exception as e:
            raise ValueError(f"Ошибка декодирования GCP_SERVICE_ACCOUNT_BASE64: {e}")

    # 4. Local service_account.json file
    local_paths = [
        SERVICE_ACCOUNT_FILE,
        "service_account.json",
        os.path.join(os.path.dirname(__file__), "service_account.json"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "service_account.json")
    ]
    for p in local_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

    return None
