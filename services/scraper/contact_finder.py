"""
Autonomous Contact Crawler (services/scraper/contact_finder.py)
Agent 1 (Lead Scraper) & Agent 4 (Integration Lead)
Autonomous B2B Contact Enrichment Engine for Google Sheets & Local CRM.

Capabilities:
1. Scans Google Spreadsheet 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M for rows with missing emails.
2. For each startup domain, concurrently requests:
   - Root page (/)
   - Dedicated outreach endpoints (/contact, /contacts, /about, /team, /privacy, /terms)
   - GitHub profiles & repo readmes when target is a GitHub launch
3. Robust Email Sanitization & Filtering:
   - Strips image assets, fake examples, wix/sentry/bugsnag/cloud trackers
4. Smart Hierarchical Ranking:
   - Highest score for executive (founder, ceo, cto) & communication (hello, team, contact, hi)
5. Quota-Safe Batch Update:
   - Updates Google Sheet in bulk using batchUpdate
   - Mirrors enriched data into 03_CRM_LEADS/leads_registry.json
"""

import os
import sys
import re
import time
import json
import ssl
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.scraper.sheets_ingest import get_worksheet, DEFAULT_SPREADSHEET_ID
from services.integration.direct_sheets_worker import resolve_google_credentials, col_to_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Noise filter for invalid / tracker / fake emails
BLOCKED_DOMAINS = {
    "example.com", "example.org", "example.net", "yourdomain.com", "domain.com", "email.com", "company.com",
    "wixpress.com", "sentry.io", "sentry-cdn.com", "bugsnag.com", "google.com",
    "googleapis.com", "schema.org", "w3.org", "cloudflare.com", "gravatar.com",
    "fastly.net", "akamaized.net", "vimeo.com", "youtube.com", "facebook.com",
    "twitter.com", "apple.com", "medium.com", "mysite.com", "sample.com",
    "test.com", "localhost"
}

BLOCKED_PREFIXES = {
    "noreply", "no-reply", "donotreply", "user", "username", "someone", "placeholder",
    "test", "admin@admin", "abuse", "mailer-daemon", "postmaster", "support@github.com",
    "privacy@github.com"
}

IMAGE_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".css", ".js",
    ".woff", ".woff2", ".mp4", ".mp3", ".pdf", ".zip", ".tar", ".gz"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8"
}

# SSL Context for resilient scraping
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def is_valid_email(email: str) -> bool:
    """
    Validates if string is a legitimate, non-tracker contact email.
    """
    email = email.strip().lower()
    if not email or len(email) < 6 or len(email) > 65:
        return False

    # Standard syntax check
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False

    # Block image or file extension false matches
    if any(email.endswith(ext) for ext in IMAGE_EXTENSIONS):
        return False

    parts = email.split("@")
    if len(parts) != 2:
        return False
    local_part, domain_part = parts[0], parts[1]

    if domain_part in BLOCKED_DOMAINS:
        return False

    if any(local_part.startswith(prefix) for prefix in BLOCKED_PREFIXES):
        return False

    # Must contain at least one dot in domain part and valid TLD length >= 2
    if "." not in domain_part or len(domain_part.split(".")[-1]) < 2:
        return False

    return True


def rank_email(email: str, base_domain: str) -> int:
    """
    Assigns quality score to an email address to pick the best contact.
    Founder/CEO > Hello/Team/Contact > Info > Support.
    """
    email_lower = email.lower()
    local_part = email_lower.split("@")[0]
    score = 10

    # Executive tier (+100)
    if any(k in local_part for k in ["founder", "ceo", "cto", "co-founder", "cofounder", "owner", "partner"]):
        score += 100
    # Core communication tier (+70)
    elif any(k in local_part for k in ["hello", "contact", "team", "hi", "hey", "reach"]):
        score += 70
    # Business tier (+50)
    elif any(k in local_part for k in ["info", "sales", "press", "media", "biz"]):
        score += 50
    # Support tier (+30)
    elif any(k in local_part for k in ["support", "help", "office"]):
        score += 30

    # Domain match bonus (+40)
    if base_domain and base_domain.lower() in email_lower:
        score += 40

    return score


def fetch_url_html(url: str, timeout: float = 6.0) -> Optional[str]:
    """
    Fetches raw HTML string from a URL with timeout and SSL error tolerance.
    """
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" in content_type or "text/plain" in content_type or not content_type:
                return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        pass
    return None


def extract_emails_from_text(html: str) -> Set[str]:
    """
    Extracts mailto links and regex emails from HTML text.
    """
    if not html:
        return set()

    found = set()
    # 1. mailto: links
    mailtos = re.findall(r'mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', html, flags=re.IGNORECASE)
    for m in mailtos:
        cleaned = m.split("?")[0].strip().lower()
        if is_valid_email(cleaned):
            found.add(cleaned)

    # 2. General regex patterns
    raw_emails = re.findall(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b', html)
    for e in raw_emails:
        cleaned = e.strip().lower().rstrip(".")
        if is_valid_email(cleaned):
            found.add(cleaned)

    # 3. XML / Atom <email> tags (common in GitHub commit feeds)
    atom_emails = re.findall(r'<email>([^<]+)</email>', html, flags=re.IGNORECASE)
    for e in atom_emails:
        cleaned = e.strip().lower()
        if is_valid_email(cleaned) and "noreply" not in cleaned:
            found.add(cleaned)

    return found


def crawl_domain_for_contact(website_url: str) -> Optional[str]:
    """
    Performs multi-page crawl on target website or GitHub repo to find best contact email.
    """
    if not website_url or not website_url.startswith("http"):
        return None

    try:
        parsed = urllib.parse.urlparse(website_url)
        netloc = parsed.netloc.lower()
        root_base = f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        return None

    # Handle GitHub repository targets specifically
    if "github.com" in netloc:
        path_parts = [p for p in parsed.path.strip("/").split("/") if p]
        candidate_urls = [website_url]
        if len(path_parts) >= 1:
            owner = path_parts[0]
            # Check owner profile
            candidate_urls.append(f"https://github.com/{owner}")
        if len(path_parts) >= 2:
            owner, repo = path_parts[0], path_parts[1]
            # Check commit feeds for real author email
            candidate_urls.append(f"https://github.com/{owner}/{repo}/commits/main.atom")
            candidate_urls.append(f"https://github.com/{owner}/{repo}/commits/master.atom")
            # Check raw README
            for branch in ["main", "master"]:
                candidate_urls.append(f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md")
    else:
        # Standard web domain targets
        subpages = [
            "/",
            "/contact",
            "/contacts",
            "/contact-us",
            "/about",
            "/about-us",
            "/team",
            "/privacy",
            "/terms",
            "/help"
        ]
        candidate_urls = [urllib.parse.urljoin(root_base, path) for path in subpages]

    discovered_emails: Set[str] = set()

    # Query candidate pages with worker threads
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_url_html, u): u for u in candidate_urls}
        for fut in as_completed(futures):
            html = fut.result()
            if html:
                extracted = extract_emails_from_text(html)
                discovered_emails.update(extracted)
                # Early exit if we already found a top-tier executive email
                if any(any(k in e for k in ["founder", "ceo", "cto"]) for e in extracted):
                    break

    if not discovered_emails:
        return None

    # Rank discovered emails and select the top candidate
    clean_domain = netloc.replace("www.", "").split(".")[0]
    scored = [(rank_email(e, clean_domain), e) for e in discovered_emails]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def enrich_sheet_contacts(
    limit: Optional[int] = None,
    start_row: int = 2,
    spreadsheet_id: str = DEFAULT_SPREADSHEET_ID
) -> Dict[str, Any]:
    """
    Extracts missing contact emails from startup websites and saves them to Google Sheet & CRM.
    """
    ws = get_worksheet(spreadsheet_id)
    rows = ws.get_all_values()
    if not rows:
        print("❌ Таблица пуста.")
        return {"processed": 0, "found": 0, "updates": []}

    headers = [h.strip().lower() for h in rows[0]]
    company_col = 0
    email_col = 2
    website_col = 10 if len(rows[0]) > 10 else -1
    cta_col = 3

    # Parse headers dynamically if available
    for idx, h in enumerate(headers):
        if any(w in h for w in ["company", "клиент", "компания"]):
            company_col = idx
        elif any(w in h for w in ["email", "почта"]):
            email_col = idx
        elif any(w in h for w in ["website", "site", "сайт"]):
            website_col = idx
        elif "cta" in h:
            cta_col = idx

    # Collect rows needing email enrichment
    tasks = []
    for r_idx in range(start_row - 1, len(rows)):
        row = rows[r_idx]
        if not row or not any(row):
            continue

        company = row[company_col].strip() if len(row) > company_col else ""
        if not company:
            continue

        current_email = row[email_col].strip() if len(row) > email_col else ""
        if current_email:
            # Email already exists
            continue

        # Extract target website URL
        url = ""
        if website_col != -1 and len(row) > website_col and row[website_col].strip():
            url = row[website_col].strip()
        elif cta_col != -1 and len(row) > cta_col and row[cta_col].strip():
            # If cta is external url
            cta_val = row[cta_col].strip()
            if not cta_val.startswith("https://razum.ai"):
                url = cta_val

        if url:
            tasks.append({
                "row_num": r_idx + 1,
                "company": company,
                "url": url
            })

    if limit is not None:
        tasks = tasks[:limit]

    print("=" * 76)
    print("🕵️ [AUTONOMOUS CONTACT CRAWLER ACTIVATED]")
    print(f"   Таблица: {spreadsheet_id}")
    print(f"   Строк на обработку: {len(tasks)}" + (f" (Лимит: {limit})" if limit else ""))
    print("=" * 76)

    if not tasks:
        print("✓ Все строки уже содержат контактные email либо не имеют URL для краулинга.")
        return {"processed": 0, "found": 0, "updates": []}

    # Concurrently crawl target domains
    found_updates = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        future_to_task = {
            executor.submit(crawl_domain_for_contact, t["url"]): t
            for t in tasks
        }
        for fut in as_completed(future_to_task):
            t = future_to_task[fut]
            email = fut.result()
            if email:
                print(f"  🎯 [НАЙДЕН EMAIL] Строка #{t['row_num']}: {t['company']:<20} ➔ {email}")
                found_updates.append({
                    "row": t["row_num"],
                    "company": t["company"],
                    "email": email,
                    "url": t["url"]
                })
            else:
                print(f"  ⚪ [НЕ НАЙДЕН]     Строка #{t['row_num']}: {t['company']:<20} ({t['url'][:35]})")

    print("\n" + "-" * 76)
    print(f"📊 ИТОГИ СБОРА КОНТАКТОВ: Найдено {len(found_updates)} email из {len(tasks)} проверенных сайтов.")
    print("-" * 76)

    # 1. Update Google Sheet via quota-safe batch update
    if found_updates:
        print("\n📝 Сохранение найденных email в Google Таблицу (Batch Update)...")
        creds = resolve_google_credentials()
        from googleapiclient.discovery import build
        service = build("sheets", "v4", credentials=creds, cache_discovery=False)
        sheet_title = ws.title

        col_letter = col_to_letter(email_col)
        data_payload = [
            {
                "range": f"'{sheet_title}'!{col_letter}{u['row']}",
                "values": [[u["email"]]]
            }
            for u in found_updates
        ]

        service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"valueInputOption": "USER_ENTERED", "data": data_payload}
        ).execute()
        print("✓ Google Таблица успешно обновлена.")

        # 2. Mirror into local CRM registry
        crm_path = os.path.join("03_CRM_LEADS", "leads_registry.json")
        if os.path.exists(crm_path):
            try:
                with open(crm_path, "r", encoding="utf-8") as f:
                    leads_data = json.load(f)
            except Exception:
                leads_data = []

            update_map = {u["company"].lower(): u["email"] for u in found_updates}
            crm_updated = 0
            for lead in leads_data:
                comp = (lead.get("company") or lead.get("client_name") or "").strip().lower()
                if comp in update_map:
                    lead["email"] = update_map[comp]
                    crm_updated += 1

            with open(crm_path, "w", encoding="utf-8") as f:
                json.dump(leads_data, f, ensure_ascii=False, indent=2)
            print(f"✓ Локальный CRM-реестр синхронизирован ({crm_updated} записей обновлено).")

    return {
        "processed": len(tasks),
        "found": len(found_updates),
        "updates": found_updates
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Contact Crawler")
    parser.add_argument("--limit", type=int, default=None, help="Process max N rows (e.g. 10 for test)")
    parser.add_argument("--start-row", type=int, default=2, help="Row number to start from (default 2)")
    args = parser.parse_args()

    enrich_sheet_contacts(limit=args.limit, start_row=args.start_row)


if __name__ == "__main__":
    main()
