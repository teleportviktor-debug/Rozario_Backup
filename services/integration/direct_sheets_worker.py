"""
Direct Google Sheets Worker (services/integration/direct_sheets_worker.py)
Agent 4 (Integration Lead) & Agent 3 (System Orchestrator)
Zero-Tolerance-To-Mocking Direct Synchronizer for Google Sheets API v4.

Performs authentic, real network calls to Google Sheets API:
1. Authenticates using Google Cloud Service Account / ADC.
2. Connects to spreadsheet: 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M.
3. Finds row with 'Apex Global Logistics'.
4. Updates 'Status' -> 'Generated' and 'Video URL' -> MP4 link.
5. Returns real API response (updatedRange, updatedRows, updatedCells) or real HttpError.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# Force UTF-8 encoding in Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

SPREADSHEET_ID = "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TARGET_COMPANY = "Apex Global Logistics"
TARGET_STATUS = "Generated"
TARGET_VIDEO_URL = "http://localhost:8000/videos/outreach_apex_global_logistics_1788558746.mp4"


def resolve_google_credentials():
    """
    Locates authentic Google Cloud credentials without mocking.
    Priority:
    1. GOOGLE_APPLICATION_CREDENTIALS path
    2. GCP_SERVICE_ACCOUNT_JSON raw JSON string in env
    3. service_account.json in project root or subdirectories
    4. Google ADC (Application Default Credentials)
    """
    from google.oauth2 import service_account
    import google.auth

    # 1. Path in env
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and os.path.exists(env_path):
        print(f"[AUTH] Загрузка учетных данных из GOOGLE_APPLICATION_CREDENTIALS: {env_path}")
        return service_account.Credentials.from_service_account_file(env_path, scopes=SCOPES)

    # 2. Raw JSON in env
    raw_json = os.getenv("GCP_SERVICE_ACCOUNT_JSON")
    if raw_json and raw_json.strip():
        print("[AUTH] Загрузка учетных данных из переменной GCP_SERVICE_ACCOUNT_JSON")
        info = json.loads(raw_json.strip())
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    # 3. Local service_account.json candidates
    candidates = [
        os.path.abspath("service_account.json"),
        os.path.abspath("drive_markdown_converter/service_account.json"),
        os.path.abspath("drive_markdown_converter/gen-lang-client-0207478259-8dcd87214378.json"),
    ]
    for c in candidates:
        if os.path.exists(c):
            print(f"[AUTH] Загрузка локального Service Account ключа: {c}")
            return service_account.Credentials.from_service_account_file(c, scopes=SCOPES)

    # 4. Standard ADC
    try:
        creds, _ = google.auth.default(scopes=SCOPES)
        print("[AUTH] Использование стандартных Google ADC (Application Default Credentials)")
        return creds
    except Exception as e:
        raise PermissionError(
            f"ОШИБКА АВТОРИЗАЦИИ: Учетные данные Google Cloud не обнаружены.\n"
            f"Не найден GOOGLE_APPLICATION_CREDENTIALS, service_account.json или ADC.\n"
            f"Подробности: {e}"
        )


def col_to_letter(col_idx_zero_based: int) -> str:
    """Converts 0-based column index to A1 notation letter (0 -> A, 27 -> AB)."""
    result = ""
    col = col_idx_zero_based
    while col >= 0:
        result = chr(col % 26 + ord('A')) + result
        col = col // 26 - 1
    return result


def sync_apex_lead_to_sheets(spreadsheet_id: str = SPREADSHEET_ID) -> Dict[str, Any]:
    """
    Executes real live API calls to Google Sheets.
    No mocking. If permission is denied or credentials invalid, raises authentic error.
    """
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    print("=" * 76)
    print("🌐 [DIRECT SHEETS WORKER] ПРЯМАЯ ИНТЕГРАЦИЯ С GOOGLE SHEETS API v4")
    print(f"   Spreadsheet ID: {spreadsheet_id}")
    print("=" * 76)

    creds = resolve_google_credentials()
    if hasattr(creds, "service_account_email"):
        print(f"[AUTH] Service Account Email: {creds.service_account_email}")

    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    # -------------------------------------------------------------------------
    # REAL NETWORK CALL 1: Получение структуры таблицы и первого листа
    # -------------------------------------------------------------------------
    print(f"\n📡 [NETWORK CALL 1] GET https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}")
    try:
        meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    except HttpError as http_err:
        print(f"\n❌ [HTTP ERROR ОТ GOOGLE SHEETS API]:")
        print(f"   Status Code: {http_err.resp.status}")
        print(f"   Reason: {http_err.resp.reason}")
        print(f"   Details: {http_err.content.decode('utf-8', errors='ignore')}")
        if http_err.resp.status == 403:
            sa_email = getattr(creds, "service_account_email", "service-account")
            print(f"\n⚠️ ПРИЧИНА 403 (PERMISSION DENIED):")
            print(f"   Таблица {spreadsheet_id} не расшарена для сервисного аккаунта:")
            print(f"   👉 {sa_email}")
            print(f"   РЕШЕНИЕ: Откройте таблицу в браузере и добавьте {sa_email} с правами 'Редактор' (Editor).")
        raise http_err

    sheet_title = meta.get("properties", {}).get("title", "Unknown")
    sheets_list = meta.get("sheets", [])
    if not sheets_list:
        raise ValueError("Таблица не содержит листов!")

    first_sheet_name = sheets_list[0]["properties"]["title"]
    print(f"✓ Успешное подключение к таблице: '{sheet_title}'")
    print(f"✓ Первый доступный лист: '{first_sheet_name}' (всего листов: {len(sheets_list)})")

    # -------------------------------------------------------------------------
    # REAL NETWORK CALL 2: Чтение содержимого листа
    # -------------------------------------------------------------------------
    read_range = f"'{first_sheet_name}'!A1:Z100"
    print(f"\n📡 [NETWORK CALL 2] GET /values/{read_range}")
    data_res = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=read_range
    ).execute()

    rows: List[List[Any]] = data_res.get("values", [])
    print(f"✓ Получено строк из листа: {len(rows)}")

    if not rows:
        # Sheet is completely empty: write headers and row
        headers = ["Company", "Primary Bottleneck", "Lead Urgency Score", "Custom CTA URL", "Status", "Video URL"]
        status_col = 4
        video_col = 5
        rows = [headers]
        row_index_to_update = 2  # Row 2 (1-based)
        print("Лист пуст. Формирование базовой структуры колонок...")
        update_range = f"'{first_sheet_name}'!A1:F2"
        body = {
            "values": [
                headers,
                [TARGET_COMPANY, "API Token Overspend & Latency", "Score: 94/100 | Tier-1 Enterprise", "https://razum.ai/audit/apex", TARGET_STATUS, TARGET_VIDEO_URL]
            ]
        }
        res_update = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=update_range,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        print("\n🎉 [РЕАЛЬНЫЙ ОТВЕТ ОТ GOOGLE SHEETS API]:")
        print(json.dumps(res_update, indent=2, ensure_ascii=False))
        return res_update

    # Parse headers
    headers = [str(cell).strip().lower() for cell in rows[0]]
    print(f"   Заголовки таблицы: {rows[0]}")

    # Identify column indices
    company_col = -1
    status_col = -1
    video_col = -1

    for idx, h in enumerate(headers):
        if any(w in h for w in ["company", "клиент", "компания", "client"]):
            company_col = idx
        elif any(w in h for w in ["status", "статус"]):
            status_col = idx
        elif any(w in h for w in ["video url", "videourl", "video", "видео", "ролик"]):
            video_col = idx

    # If company column not found, assume column A (0)
    if company_col == -1:
        company_col = 0
    # If status column not found, append to header
    if status_col == -1:
        status_col = len(rows[0])
        rows[0].append("Status")
    # If video column not found, append to header
    if video_col == -1:
        video_col = len(rows[0])
        rows[0].append("Video URL")

    # Find row with Target Company
    target_row_idx = -1
    for r_idx in range(1, len(rows)):
        row = rows[r_idx]
        row_str = " ".join([str(c) for c in row]).lower()
        if "apex global logistics" in row_str or TARGET_COMPANY.lower() in row_str:
            target_row_idx = r_idx + 1  # 1-based index in sheets
            break

    # If row not found, append row at the end
    if target_row_idx == -1:
        target_row_idx = len(rows) + 1
        print(f"⚠️ Строка '{TARGET_COMPANY}' не найдена. Создание новой строки #{target_row_idx}...")
    else:
        print(f"✓ Найдена целевая строка #{target_row_idx} с '{TARGET_COMPANY}'")

    # -------------------------------------------------------------------------
    # REAL NETWORK CALL 3: Физическая запись Status и Video URL
    # -------------------------------------------------------------------------
    status_cell_ref = f"'{first_sheet_name}'!{col_to_letter(status_col)}{target_row_idx}"
    video_cell_ref = f"'{first_sheet_name}'!{col_to_letter(video_col)}{target_row_idx}"

    data_updates = [
        {
            "range": status_cell_ref,
            "values": [[TARGET_STATUS]]
        },
        {
            "range": video_cell_ref,
            "values": [[TARGET_VIDEO_URL]]
        }
    ]

    # Also make sure header has column names if we added them
    if len(rows[0]) > len(headers):
        data_updates.append({
            "range": f"'{first_sheet_name}'!A1:{col_to_letter(len(rows[0])-1)}1",
            "values": [rows[0]]
        })

    batch_body = {
        "valueInputOption": "USER_ENTERED",
        "data": data_updates
    }

    print(f"\n📡 [NETWORK CALL 3] BATCH UPDATE ячеек:")
    print(f"   ├─ {status_cell_ref} -> '{TARGET_STATUS}'")
    print(f"   └─ {video_cell_ref} -> '{TARGET_VIDEO_URL}'")

    update_response = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=batch_body
    ).execute()

    print("\n" + "=" * 76)
    print("🎉 [РЕАЛЬНЫЙ ОТВЕТ ОТ GOOGLE SHEETS API v4]:")
    print(json.dumps(update_response, indent=2, ensure_ascii=False))
    print("=" * 76)

    return update_response


if __name__ == "__main__":
    try:
        sync_apex_lead_to_sheets()
    except Exception as e:
        print(f"\n❌ [ОШИБКА ВЫПОЛНЕНИЯ]: {e}")
        sys.exit(1)
