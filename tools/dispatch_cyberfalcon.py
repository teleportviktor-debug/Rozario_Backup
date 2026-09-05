"""
CyberFalcon 77 Outreach Dispatcher & Google Sheets Live Sync
Agent 4 (Integration Lead) & Agent 3 (System Orchestrator)

Executes:
1. HTTP POST to http://localhost:8000/api/v1/outreach/dispatch (CyberFalcon 77).
2. Obtains parametric H.264 video URL and cardsV2.
3. Authenticates with Google Sheets API v4 via service_account.json.
4. Locates 'CyberFalcon 77' row in spreadsheet 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M.
5. Updates 'Status' -> 'Generated' and 'Video URL' -> video_url.
6. Outputs full Google Sheets API response.
"""

import os
import sys
import json
import time
import requests
from googleapiclient.discovery import build
from services.integration.direct_sheets_worker import resolve_google_credentials, col_to_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DISPATCH_URL = "http://localhost:8000/api/v1/outreach/dispatch"
TOKEN = "Bearer ntn_master_dev_key_2026"
SPREADSHEET_ID = "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"

PAYLOAD = {
    "company_name": "CyberFalcon 77",
    "primary_bottleneck": "Database Latency Spike at 4 AM",
    "lead_urgency_score": "Score: 98/100 | Critical Enterprise",
    "custom_cta_url": "https://razum.ai/audit/falcon"
}


def dispatch_cyberfalcon():
    print("=" * 76)
    print("🚀 [ЭТАП 1/2] ГЕНЕРАЦИЯ ВИДЕО И КАРТОЧКИ: CyberFalcon 77")
    print(f"   URL: {DISPATCH_URL}")
    print(f"   Header: Authorization: {TOKEN}")
    print("=" * 76)

    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    start_t = time.time()
    resp = requests.post(DISPATCH_URL, headers=headers, json=PAYLOAD, timeout=60)
    elapsed = time.time() - start_t

    if resp.status_code != 200:
        print(f"❌ Ошибка вызова FastAPI: {resp.status_code}\n{resp.text}")
        sys.exit(1)

    data = resp.json()
    video_url = data.get("video_url")
    video_path = data.get("video_path")
    email_subject = data.get("email_subject")
    filesize = data.get("video_filesize_bytes")

    print(f"\n✓ Успешно сгенерировано за {elapsed:.2f} сек (HTTP 200 OK):")
    print(f"   • Компания: {data.get('company_name')}")
    print(f"   • Video URL: {video_url}")
    print(f"   • Локальный путь: {video_path}")
    print(f"   • Размер файла: {filesize:,} байт")
    print(f"   • Тема письма: {email_subject}")

    # -------------------------------------------------------------
    # STAGE 2: Direct Google Sheets API update
    # -------------------------------------------------------------
    print("\n" + "=" * 76)
    print("📊 [ЭТАП 2/2] СИНХРОНИЗАЦИЯ С GOOGLE ТАБЛИЦЕЙ")
    print(f"   Spreadsheet ID: {SPREADSHEET_ID}")
    print("=" * 76)

    creds = resolve_google_credentials()
    service = build("sheets", "v4", credentials=creds, cache_discovery=False)

    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    first_sheet_name = meta["sheets"][0]["properties"]["title"]
    print(f"✓ Подключено к листу: '{first_sheet_name}'")

    read_range = f"'{first_sheet_name}'!A1:Z100"
    data_res = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=read_range
    ).execute()

    rows = data_res.get("values", [])
    if not rows:
        print("❌ Таблица пуста!")
        sys.exit(1)

    headers_row = [str(c).strip().lower() for c in rows[0]]
    raw_headers = rows[0]
    print(f"   Заголовки таблицы: {raw_headers}")

    company_col = -1
    status_col = -1
    video_col = -1

    for idx, h in enumerate(headers_row):
        if any(w in h for w in ["company", "клиент", "компания", "client"]):
            company_col = idx
        elif any(w in h for w in ["status", "статус"]):
            status_col = idx
        elif any(w in h for w in ["video url", "videourl", "video", "видео", "ролик"]):
            video_col = idx

    if company_col == -1: company_col = 0
    if status_col == -1:
        status_col = len(raw_headers)
        raw_headers.append("Status")
    if video_col == -1:
        video_col = len(raw_headers)
        raw_headers.append("Video URL")

    # Find row with CyberFalcon 77
    target_row_idx = -1
    for r_idx in range(1, len(rows)):
        row_str = " ".join([str(c) for c in rows[r_idx]]).lower()
        if "cyberfalcon" in row_str or "cyberfalcon 77" in row_str:
            target_row_idx = r_idx + 1
            print(f"✓ Найдена строка #{target_row_idx} с 'CyberFalcon 77': {rows[r_idx]}")
            break

    if target_row_idx == -1:
        # Append if not found
        target_row_idx = len(rows) + 1
        print(f"⚠️ Строка 'CyberFalcon 77' не найдена. Создание строки #{target_row_idx}...")
        new_row = ["CyberFalcon 77", video_url, "ops@cyberfalcon77.io", "https://razum.ai/audit/falcon", "Database Latency Spike at 4 AM", "{}", "Generated", "Score: 98/100", "TRUE", f"ROW-{target_row_idx}"]
        append_res = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{first_sheet_name}'!A{target_row_idx}",
            valueInputOption="USER_ENTERED",
            body={"values": [new_row]}
        ).execute()
        print("\n🎉 [РЕАЛЬНЫЙ ОТВЕТ GOOGLE SHEETS API (APPEND)]:")
        print(json.dumps(append_res, indent=2, ensure_ascii=False))
        return {
            "video_url": video_url,
            "video_path": video_path,
            "row": target_row_idx,
            "status": "Generated",
            "api_response": append_res
        }

    status_cell_ref = f"'{first_sheet_name}'!{col_to_letter(status_col)}{target_row_idx}"
    video_cell_ref = f"'{first_sheet_name}'!{col_to_letter(video_col)}{target_row_idx}"

    batch_body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": status_cell_ref, "values": [["Generated"]]},
            {"range": video_cell_ref, "values": [[video_url]]}
        ]
    }

    print(f"\n📡 Обновление ячеек:")
    print(f"   ├─ {status_cell_ref} -> 'Generated'")
    print(f"   └─ {video_cell_ref} -> '{video_url}'")

    update_res = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=batch_body
    ).execute()

    print("\n" + "=" * 76)
    print("🎉 [РЕАЛЬНЫЙ ОТВЕТ GOOGLE SHEETS API v4]:")
    print(json.dumps(update_res, indent=2, ensure_ascii=False))
    print("=" * 76)

    return {
        "video_url": video_url,
        "video_path": video_path,
        "row": target_row_idx,
        "status": "Generated",
        "api_response": update_res
    }


if __name__ == "__main__":
    dispatch_cyberfalcon()
