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
from scrapers.hiring_intent_scraper import scrape_hiring_intent

SPREADSHEET_ID = "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"
SERVICE_ACCOUNT_PATH = "service_account.json"
TAB_NAME = "Hot_Hiring_Leads"

COLUMNS = [
    "Company",
    "Website",
    "Hiring Role",
    "Tech Stack / Core Pain",
    "Founder / CTO Name",
    "LinkedIn Search URL",
    "Contact Email",
    "Intent Angle",
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

def ensure_hot_hiring_tab(service) -> int:
    """Checks if Hot_Hiring_Leads sheet exists, creates it with formatted headers if not."""
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
                    "rowCount": 200,
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

    # Format header row: dark background (#0f172a), white bold text
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
                        "backgroundColor": {"red": 0.06, "green": 0.09, "blue": 0.16},
                        "textFormat": {
                            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                            "bold": True,
                            "fontSize": 11
                        },
                        "horizontalAlignment": "CENTER"
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": len(COLUMNS)
                }
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
        range=f"'{TAB_NAME}'!A1:I1",
        valueInputOption="USER_ENTERED",
        body={"values": [COLUMNS]}
    ).execute()
    print(f"📝 Заголовки колонок записаны в '{TAB_NAME}'!A1:I1")

    return sheet_id

def sync_leads_to_sheet(leads: list[dict]):
    service = get_sheets_service()
    sheet_id = ensure_hot_hiring_tab(service)

    # Ensure header exists
    header_check = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A1:I1"
    ).execute()
    if not header_check.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"'{TAB_NAME}'!A1:I1",
            valueInputOption="USER_ENTERED",
            body={"values": [COLUMNS]}
        ).execute()

    rows_data = []
    for lead in leads:
        row = [
            lead.get("company", ""),
            lead.get("website", ""),
            lead.get("hiring_role", ""),
            lead.get("tech_stack_core_pain", ""),
            lead.get("founder_name", ""),
            lead.get("linkedin_search_url", ""),
            lead.get("contact_email", ""),
            lead.get("intent_angle", ""),
            lead.get("status", "Qualified Intent")
        ]
        rows_data.append(row)

    print(f"\n📊 Запись {len(rows_data)} строк в '{TAB_NAME}'...")
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{TAB_NAME}'!A2:I{len(rows_data) + 1}",
        valueInputOption="USER_ENTERED",
        body={"values": rows_data}
    ).execute()
    print(f"🎉 [SUCCESS] Успешно записано {len(rows_data)} лидов в Google Таблицу на лист '{TAB_NAME}'!")

def main():
    print("=" * 76)
    print("🚀 [PIPELINE: INTENT SCRAPER -> GOOGLE SHEETS]")
    print("=" * 76)
    
    # 1. Scrape 10 leads with confirmed AI hiring signals
    leads = scrape_hiring_intent(limit=10)
    if not leads:
        print("❌ Не удалось найти лиды!")
        sys.exit(1)

    # 2. Sync to Hot_Hiring_Leads tab
    sync_leads_to_sheet(leads)

if __name__ == "__main__":
    main()
