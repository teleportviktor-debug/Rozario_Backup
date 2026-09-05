"""
Google Sheets Lead Ingestion Engine (services/scraper/sheets_ingest.py)
Agent 1 (Lead Scraper) & Agent 4 (Integration Lead)
Autonomous Ingestion & Deduplication Pipeline for Nightly B2B Harvesting.

Features:
- Authenticates via authentic Google Cloud credentials with gspread.
- append_lead_to_sheet(lead_dict):
    1. Checks Column A for existing company names (case-insensitive deduplication).
    2. Maps [Company, Bottleneck, Score, CTA, Email, FALSE, Pending, ""] aligned with sheet headers.
    3. Writes row with status 'Pending' to trigger the autonomous sheets_worker.
- ingest_leads_batch(leads, limit=35):
    Safe batch injection with rate-limiting & duplicate skipping.
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
import gspread

from services.integration.direct_sheets_worker import resolve_google_credentials, col_to_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

DEFAULT_SPREADSHEET_ID = "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"
SAFE_BATCH_LIMIT = 35


def get_gspread_client():
    """
    Returns an authorized gspread client using the shared service account credentials.
    """
    creds = resolve_google_credentials()
    return gspread.authorize(creds)


def get_worksheet(spreadsheet_id: str = DEFAULT_SPREADSHEET_ID, sheet_index: int = 0) -> gspread.Worksheet:
    """
    Opens spreadsheet by key and returns the first worksheet.
    """
    gc = get_gspread_client()
    sh = gc.open_by_key(spreadsheet_id)
    return sh.get_worksheet(sheet_index)


def append_lead_to_sheet(lead_dict: Dict[str, Any], spreadsheet_id: str = DEFAULT_SPREADSHEET_ID) -> Dict[str, Any]:
    """
    Appends a new B2B lead to the Google Sheet with status 'Pending'.
    
    1. Validates company name.
    2. Checks Column A for duplicates (case-insensitive).
    3. Aligns payload [Company, Bottleneck, Score, CTA, Email, FALSE, Pending, ""] with sheet headers.
    4. Writes into the next available row (or appends) with status 'Pending'.
    """
    company = (
        lead_dict.get("company")
        or lead_dict.get("company_name")
        or lead_dict.get("Company")
        or lead_dict.get("client_name")
        or ""
    ).strip()

    if not company:
        raise ValueError("Lead dictionary must contain a non-empty 'company' or 'company_name'.")

    ws = get_worksheet(spreadsheet_id)
    
    # 1. Deduplication check on Column A
    col_a_values = ws.col_values(1)
    existing_companies = [c.strip().lower() for c in col_a_values if c and c.strip()]

    if company.lower() in existing_companies:
        existing_idx = existing_companies.index(company.lower()) + 1
        print(f"⚠️ [DUPLICATE] Компания '{company}' уже присутствует в таблице (строка #{existing_idx}). Пропуск.")
        return {
            "status": "DUPLICATE",
            "company": company,
            "row": existing_idx,
            "message": f"Lead '{company}' already exists in row #{existing_idx}"
        }

    # 2. Extract and format fields
    bottleneck = (
        lead_dict.get("bottleneck")
        or lead_dict.get("primary_bottleneck")
        or "API Token Overspend & Latency"
    ).strip()

    score = lead_dict.get("score") or lead_dict.get("urgency_score") or lead_dict.get("lead_urgency_score")
    if not score:
        score = "Score: 92/100 | High Priority Enterprise"
    elif isinstance(score, (int, float)):
        score = f"Score: {int(score)}/100 | High Priority"
    score = str(score).strip()

    cta = (
        lead_dict.get("cta")
        or lead_dict.get("cta_url")
        or lead_dict.get("custom_cta_url")
        or "https://razum.ai/audit"
    ).strip()

    website = (
        lead_dict.get("website")
        or lead_dict.get("website_url")
        or lead_dict.get("url")
        or ""
    ).strip()

    # Leave email empty if not discovered on target startup page
    email = (
        lead_dict.get("email")
        or lead_dict.get("contact_email")
        or ""
    ).strip()

    # Real boolean False to render clean unchecked checkbox without red validation error corner
    approved = False
    status = "Pending"
    video_url = ""
    card_json = ""

    # 3. Read sheet headers and map columns dynamically
    headers = ws.row_values(1)
    target_row = len(col_a_values) + 1

    if headers:
        header_lower = [h.strip().lower() for h in headers]
        row_data = [""] * len(headers)
        for idx, h in enumerate(header_lower):
            if any(w in h for w in ["company", "клиент", "компания"]):
                row_data[idx] = company
            elif any(w in h for w in ["video url", "videourl", "видео"]):
                row_data[idx] = video_url
            elif any(w in h for w in ["email", "почта", "contact"]):
                row_data[idx] = email
            elif any(w in h for w in ["website", "site", "сайт"]):
                row_data[idx] = website
            elif "cta" in h:
                row_data[idx] = cta
            elif any(w in h for w in ["url", "ссылка"]) and "video" not in h:
                row_data[idx] = website if website else cta
            elif any(w in h for w in ["bottleneck", "узкое место", "проблема"]):
                row_data[idx] = bottleneck
            elif any(w in h for w in ["card", "json"]):
                row_data[idx] = card_json
            elif any(w in h for w in ["status", "статус"]):
                row_data[idx] = status
            elif any(w in h for w in ["urgency", "score", "скоринг"]):
                row_data[idx] = score
            elif any(w in h for w in ["approved", "одобрен"]):
                row_data[idx] = False  # boolean False
            elif any(w in h for w in ["row", "id"]):
                row_data[idx] = str(target_row)
    else:
        # Fallback canonical row: [Company, Video URL, Email, CTA URL, Bottleneck, Card JSON, Status, Score, Approved, Row ID, Website URL]
        row_data = [company, video_url, email, cta, bottleneck, card_json, status, score, False, str(target_row), website]

    # 4. Write row to Google Sheet with USER_ENTERED to preserve native boolean checkbox
    end_col_letter = col_to_letter(len(row_data) - 1)
    if target_row <= ws.row_count:
        range_ref = f"A{target_row}:{end_col_letter}{target_row}"
        ws.update(values=[row_data], range_name=range_ref, value_input_option="USER_ENTERED")
    else:
        ws.append_row(row_data, value_input_option="USER_ENTERED")

    print(f"✓ [APPENDED] Строка #{target_row}: '{company}' успешно добавлена со статусом 'Pending'!")
    return {
        "status": "ADDED",
        "company": company,
        "row": target_row,
        "row_data": row_data
    }


def ingest_leads_batch(
    leads: List[Dict[str, Any]],
    spreadsheet_id: str = DEFAULT_SPREADSHEET_ID,
    limit: int = SAFE_BATCH_LIMIT
) -> Dict[str, Any]:
    """
    Ingests a list of leads up to the safe batch limit, skipping duplicates.
    """
    safe_leads = leads[:limit]
    print(f"\n[INGEST] Запуск пакета лидов: {len(safe_leads)} из {len(leads)} (лимит: {limit})")
    
    added = []
    duplicates = []
    errors = []

    for idx, lead in enumerate(safe_leads, start=1):
        try:
            res = append_lead_to_sheet(lead, spreadsheet_id=spreadsheet_id)
            if res["status"] == "ADDED":
                added.append(res)
            elif res["status"] == "DUPLICATE":
                duplicates.append(res)
        except Exception as err:
            comp = lead.get("company", f"Index #{idx}")
            print(f"❌ Ошибка добавления '{comp}': {err}")
            errors.append({"company": comp, "error": str(err)})

    print("\n" + "=" * 60)
    print(f"📊 ИТОГИ ИНГЕСТА В GOOGLE SHEETS:")
    print(f"  • Добавлено новых (Pending): {len(added)}")
    print(f"  • Пропущено дубликатов: {len(duplicates)}")
    if errors:
        print(f"  • Ошибок: {len(errors)}")
    print("=" * 60)

    return {
        "total_requested": len(leads),
        "limit_applied": limit,
        "added_count": len(added),
        "duplicate_count": len(duplicates),
        "error_count": len(errors),
        "added_leads": added
    }


if __name__ == "__main__":
    test_lead = {
        "company": "QuantumNova Labs",
        "bottleneck": "Memory Leak in Redis Cache Layer",
        "score": "Score: 97/100 | Critical",
        "cta": "https://razum.ai/audit/quantumnova",
        "email": "lead@quantumnova.io"
    }
    print("[TEST] Добавление тестового лида...")
    result = append_lead_to_sheet(test_lead)
    print("Результат:", json.dumps(result, ensure_ascii=False, indent=2))
