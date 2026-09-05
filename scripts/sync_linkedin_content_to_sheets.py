import os
import sys
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.linkedin.content_generator import generate_linkedin_post, generate_card_html
from services.linkedin.card_renderer import render_card_to_png

SPREADSHEET_ID = "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"
SERVICE_ACCOUNT_PATH = "service_account.json"
TAB_NAME = "LinkedIn_Content"

COLUMNS = [
    "Post ID",
    "Topic",
    "Post Text",
    "Card Image Path",
    "Lead Magnet Keyword",
    "Status"
]

def get_sheets_service():
    if not os.path.exists(SERVICE_ACCOUNT_PATH):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_PATH}")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return build("sheets", "v4", credentials=creds)

def ensure_linkedin_tab(service) -> int:
    """Checks if LinkedIn_Content sheet exists, creates it with formatted headers if not."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = meta.get("sheets", [])

    for s in sheets:
        if s.get("properties", {}).get("title") == TAB_NAME:
            sheet_id = s.get("properties", {}).get("sheetId")
            print(f"📋 Вкладка '{TAB_NAME}' уже существует (Sheet ID: {sheet_id}).")
            return sheet_id

    print(f"🚀 Создаем новую вкладку '{TAB_NAME}' в Google Таблице...")
    add_req = {
        "addSheet": {
            "properties": {
                "title": TAB_NAME,
                "gridProperties": {
                    "rowCount": 100,
                    "columnCount": len(COLUMNS),
                    "frozenRowCount": 1
                }
            }
        }
    }
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [add_req]}
    ).execute()
    
    new_sheet = resp["replies"][0]["addSheet"]["properties"]
    sheet_id = new_sheet["sheetId"]
    print(f"✅ Вкладка '{TAB_NAME}' успешно создана (Sheet ID: {sheet_id})!")

    # Format header row: dark background (#090d16), neon cyan bold text
    format_reqs = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(COLUMNS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.04, "green": 0.05, "blue": 0.09},
                        "textFormat": {
                            "foregroundColor": {"red": 0.0, "green": 0.94, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        }
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": format_reqs}
    ).execute()

    # Write column headers
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A1:F1",
        valueInputOption="USER_ENTERED",
        body={"values": [COLUMNS]}
    ).execute()
    print(f"📝 Заголовки колонок записаны в '{TAB_NAME}'!A1:F1")

    return sheet_id

def create_and_publish_post(topic: str, keyword: str = "ROUTER", post_id: str = None) -> dict:
    if not post_id:
        post_id = "POST-2026-09-01-TTFT-ROUTING"

    print("=" * 76)
    print(f"🚀 [LINKEDIN ENGINE] Подготовка контент-комплекта: '{topic}'")
    print("=" * 76)

    # 1. Generate text
    post_bundle = generate_linkedin_post(topic=topic, keyword=keyword)
    post_text = post_bundle["post_text"]

    # 2. Generate HTML & Render Card PNG
    card_html = generate_card_html(topic=topic, keyword=keyword)
    filename = "linkedin_card_ttft_routing.png"
    rendered_image_path = render_card_to_png(card_html, filename)
    rel_path = os.path.relpath(rendered_image_path, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # 3. Sync to Google Sheets
    service = get_sheets_service()
    ensure_linkedin_tab(service)

    row_data = [
        post_id,
        topic,
        post_text,
        rel_path.replace("\\", "/"),
        keyword,
        "Ready to Post"
    ]

    print(f"\n📊 Запись комплекта в Google Таблицу на лист '{TAB_NAME}'...")
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A2:F2",
        valueInputOption="USER_ENTERED",
        body={"values": [row_data]}
    ).execute()

    print(f"🎉 [SUCCESS] Комплект успешно сохранен в Google Таблицу на лист '{TAB_NAME}'!")
    print(f"   • Post ID: {post_id}")
    print(f"   • Topic: {topic}")
    print(f"   • Image: {rendered_image_path}")
    print(f"   • Status: Ready to Post")

    return {
        "post_id": post_id,
        "topic": topic,
        "post_text": post_text,
        "image_path": rendered_image_path,
        "keyword": keyword,
        "status": "Ready to Post"
    }

OMNI_TAB_NAME = "Omnichannel_Content"
OMNI_COLUMNS = [
    "Topic",
    "LinkedIn_Post",
    "X_Thread",
    "Facebook_Post",
    "Card_Image_Path",
    "Video_Teaser_Prompt",
    "Status"
]

def ensure_omnichannel_tab(service) -> int:
    """Checks if Omnichannel_Content sheet exists, creates it with formatted headers if not."""
    meta = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    sheets = meta.get("sheets", [])

    for s in sheets:
        if s.get("properties", {}).get("title") == OMNI_TAB_NAME:
            sheet_id = s.get("properties", {}).get("sheetId")
            print(f"📋 Вкладка '{OMNI_TAB_NAME}' уже существует (Sheet ID: {sheet_id}).")
            return sheet_id

    print(f"🚀 Создаем новую вкладку '{OMNI_TAB_NAME}' в Google Таблице...")
    add_req = {
        "addSheet": {
            "properties": {
                "title": OMNI_TAB_NAME,
                "gridProperties": {
                    "rowCount": 100,
                    "columnCount": len(OMNI_COLUMNS),
                    "frozenRowCount": 1
                }
            }
        }
    }
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": [add_req]}
    ).execute()

    new_sheet = resp["replies"][0]["addSheet"]["properties"]
    sheet_id = new_sheet["sheetId"]

    # Header styling
    format_reqs = [
        {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": len(OMNI_COLUMNS)
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.04, "green": 0.05, "blue": 0.09},
                        "textFormat": {
                            "foregroundColor": {"red": 0.0, "green": 0.94, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        }
    ]
    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={"requests": format_reqs}
    ).execute()

    # Write column headers
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{OMNI_TAB_NAME}'!A1:G1",
        valueInputOption="USER_ENTERED",
        body={"values": [OMNI_COLUMNS]}
    ).execute()
    print(f"📝 Заголовки колонок записаны в '{OMNI_TAB_NAME}'!A1:G1")

    return sheet_id

def sync_omnichannel_to_sheets(omni_pack: dict, card_image_path: str) -> dict:
    service = get_sheets_service()
    ensure_omnichannel_tab(service)

    rel_path = os.path.relpath(card_image_path, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))).replace("\\", "/")

    row_data = [
        omni_pack["topic"],
        omni_pack["linkedin_post"],
        omni_pack["x_thread"],
        omni_pack["facebook_post"],
        rel_path,
        omni_pack["video_teaser_prompt"],
        "Ready to Post"
    ]

    # Append to Omnichannel_Content
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{OMNI_TAB_NAME}'!A2",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row_data]}
    ).execute()

    print(f"🎉 [SUCCESS] Омниканальный контент успешно записан в '{OMNI_TAB_NAME}'!")
    return {
        "topic": omni_pack["topic"],
        "card_image_path": rel_path,
        "status": "Ready to Post"
    }

if __name__ == "__main__":
    from services.linkedin.content_generator import generate_omnichannel_pack
    pack = generate_omnichannel_pack("Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)", "ROUTER")
    card_path = os.path.abspath("output/linkedin_cards/linkedin_card_ttft_routing.png")
    sync_omnichannel_to_sheets(pack, card_path)

