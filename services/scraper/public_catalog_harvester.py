"""
Public Catalog Harvester (services/scraper/public_catalog_harvester.py)
Agent 1 (Lead Scraper) & Agent 4 (Integration Lead)
Zero-API-Key Autonomous Harvester for Fresh Tech Startups (Show HN & Public Feeds).

Features:
1. Public Source: Hacker News Show HN API (https://hn.algolia.com/api/v1/search_by_date?tags=show_hn).
2. Filtering: Only launches with direct external URLs (excludes plain text discussions).
3. Enrichment via Gemini Flash (gemini-1.5-flash) with local zero-trust heuristic fallback:
   - Formulates architectural technical bottleneck (latency, memory, tokens, keystore security).
   - Generates Hormozi-aligned Urgency Score and custom CTA URL.
4. Overload Protection: BATCH_LIMIT = 15 companies.
5. Ingestion: Direct integration with services.scraper.sheets_ingest.append_lead_to_sheet.
"""

import os
import sys
import re
import time
import json
import argparse
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.scraper.sheets_ingest import append_lead_to_sheet, DEFAULT_SPREADSHEET_ID

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SHOW_HN_API_URL = "https://hn.algolia.com/api/v1/search_by_date?tags=show_hn&hitsPerPage=100"
BATCH_LIMIT = 15
DEFAULT_LOOP_INTERVAL_SEC = 2700  # 45 minutes


def extract_company_name(title: str, url: str) -> str:
    """
    Extracts clean company or project name from Show HN title and target URL.
    """
    # Remove 'Show HN:' prefix
    clean = re.sub(r"^Show\s+HN\s*[:–—\-]\s*", "", title, flags=re.IGNORECASE).strip()
    
    # Check for separator like '–', '—', ':', '-'
    separators = [" – ", " — ", " - ", ": "]
    for sep in separators:
        if sep in clean:
            candidate = clean.split(sep)[0].strip()
            # If candidate is a good name (1-4 words, <= 30 chars)
            if 2 <= len(candidate) <= 30 and len(candidate.split()) <= 4:
                return candidate

    # Fallback to domain name if clean title is too descriptive
    try:
        parsed_url = urllib.parse.urlparse(url)
        netloc = parsed_url.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        domain_parts = netloc.split(".")
        if len(domain_parts) >= 2:
            main_domain = domain_parts[0].capitalize()
            if len(main_domain) >= 3 and main_domain not in ["Github", "Huggingface"]:
                return main_domain
    except Exception:
        pass

    words = clean.split()
    return " ".join(words[:3]) if words else "Tech Startup"


def enrich_with_gemini_or_heuristic(company: str, description: str, url: str) -> Dict[str, str]:
    """
    Enriches startup with architectural bottleneck, urgency score, and CTA URL.
    Attempts Gemini Flash if API key is present; otherwise applies domain-specific heuristics.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", company.lower()).strip("-")
    if not slug:
        slug = "startup"
    default_cta = f"https://razum.ai/audit/{slug}"

    # Try Gemini 1.5 Flash if GEMINI_API_KEY is available
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip():
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"You are a principal systems architect.\n"
                f"Analyze this tech startup launch:\n"
                f"Company Name: {company}\n"
                f"Description: {description}\n"
                f"Product URL: {url}\n\n"
                f"Output a JSON object with:\n"
                f'1. "bottleneck": Precise technical architectural vulnerability (e.g. latency, token overspend, cache drift, microservice timeout) in 5-8 words.\n'
                f'2. "urgency_score": e.g. "Score: 95/100 | Critical Enterprise"\n\n'
                f"Respond ONLY with valid JSON."
            )
            response = model.generate_content(prompt)
            match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(0))
                return {
                    "bottleneck": parsed.get("bottleneck", "API Token Overrun & VPC Boundary Vulnerability"),
                    "score": parsed.get("urgency_score", "Score: 94/100 | Critical Enterprise"),
                    "cta": default_cta
                }
        except Exception as e:
            print(f"  [GEMINI NOTE] Heuristic fallback applied ({e})")

    # High-intent Domain-Specific Heuristic Engine
    text_lower = f"{company} {description} {url}".lower()

    if any(k in text_lower for k in ["local-first", "sqlite", "sync", "offline", "crdt"]):
        bottleneck = "Local-First Multi-Client State Drift & Conflict Resolution Latency"
        score = "Score: 96/100 | Critical Enterprise"
    elif any(k in text_lower for k in ["ai", "llm", "prompt", "model", "gpt", "rag", "agent", "inference"]):
        bottleneck = "LLM Token Budget Overrun & Unbounded Streaming Latency Spikes"
        score = "Score: 97/100 | Critical Enterprise"
    elif any(k in text_lower for k in ["rust", "wasm", "memory", "perf", "launcher", "cli", "compiler"]):
        bottleneck = "Thread Concurrency Contention & Cache Line Invalidation Overhead"
        score = "Score: 93/100 | High Priority"
    elif any(k in text_lower for k in ["security", "auth", "token", "key", "privacy", "zero trust"]):
        bottleneck = "SaaS Webhook Keystore Exposure & Zero Trust Boundary Leak"
        score = "Score: 98/100 | Critical Enterprise"
    elif any(k in text_lower for k in ["market", "b2b", "commerce", "craft", "vendor", "platform"]):
        bottleneck = "Transactional Edge Database Connection Pool Exhaustion"
        score = "Score: 92/100 | High Priority"
    elif any(k in text_lower for k in ["scheduler", "worker", "queue", "cron", "event", "routine"]):
        bottleneck = "Distributed Event Loop Starvation & Memory Leak Under Spike Load"
        score = "Score: 95/100 | Critical Enterprise"
    else:
        bottleneck = "Unmonitored Third-Party API Key Overrun & Cloud Egress Latency"
        score = "Score: 91/100 | High Priority"

    return {
        "bottleneck": bottleneck,
        "score": score,
        "cta": default_cta
    }


def fetch_show_hn_launches(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetches latest Show HN submissions from the open Hacker News Algolia API.
    Filters to only items with direct external URLs.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request(SHOW_HN_API_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            hits = data.get("hits", [])
    except Exception as err:
        print(f"❌ [SHOW HN FETCH ERROR]: {err}")
        return []

    valid_launches = []
    for h in hits:
        url = h.get("url") or ""
        title = h.get("title") or ""
        story_text = h.get("story_text") or ""
        
        # Filter out text-only posts (where URL is missing or points to HN comments)
        if not url or "news.ycombinator.com" in url or not (url.startswith("http://") or url.startswith("https://")):
            continue

        company = extract_company_name(title, url)
        valid_launches.append({
            "raw_title": title,
            "company": company,
            "url": url,
            "description": story_text if story_text else title,
            "created_at": h.get("created_at")
        })

        if len(valid_launches) >= limit:
            break

    return valid_launches


def harvest_and_ingest(
    count: int = 10,
    max_batch_limit: int = BATCH_LIMIT,
    spreadsheet_id: str = DEFAULT_SPREADSHEET_ID
) -> List[Dict[str, Any]]:
    """
    Harvests fresh startups from Show HN and ingests them into Google Sheets.
    """
    target_count = min(count, max_batch_limit)
    print("=" * 76)
    print(f"🌐 [PUBLIC CATALOG HARVESTER ACTIVATED]")
    print(f"   Источник: Hacker News Show HN Open Feed (Zero API Keys)")
    print(f"   Цель сбора: {target_count} стартапов (Лимит пачки: {max_batch_limit})")
    print("=" * 76)

    launches = fetch_show_hn_launches(limit=60)
    print(f"✓ Найдено {len(launches)} запусков с прямыми внешними URL.")

    ingested = []
    for item in launches:
        if len(ingested) >= target_count:
            break

        company = item["company"]
        url = item["url"]
        desc = item["description"]

        print(f"\n🔍 Анализ запуска: '{company}' ({url})")
        enriched = enrich_with_gemini_or_heuristic(company, desc, url)
        print(f"  • Bottleneck: {enriched['bottleneck']}")
        print(f"  • Urgency Score: {enriched['score']}")
        print(f"  • Custom CTA: {enriched['cta']}")

        # Only extract email if explicitly discovered in launch text/description, otherwise leave blank
        email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", desc)
        discovered_email = email_match.group(0) if email_match else ""

        lead_payload = {
            "company": company,
            "website": url,
            "bottleneck": enriched["bottleneck"],
            "score": enriched["score"],
            "cta": enriched["cta"],
            "email": discovered_email
        }

        # Ingest to Google Sheets with status 'Pending'
        try:
            res = append_lead_to_sheet(lead_payload, spreadsheet_id=spreadsheet_id)
            if res.get("status") == "ADDED":
                item_record = {
                    **item,
                    **enriched,
                    "sheet_row": res.get("row")
                }
                ingested.append(item_record)
                print(f"  🚀 [УСПЕХ] Добавлен в строку #{res.get('row')} со статусом 'Pending'!")
            elif res.get("status") == "DUPLICATE":
                print(f"  ⏩ [ПРОПУСК] Уже присутствует в таблице.")
        except Exception as e:
            print(f"  ❌ Ошибка добавления в Google Sheets: {e}")

    print("\n" + "=" * 76)
    print(f"🎉 ИТОГ ХАРВЕСТИНГА: {len(ingested)}/{target_count} стартапов успешно внесены в контур!")
    print("=" * 76)
    return ingested


def run_continuous(
    count: int = 10,
    interval_sec: int = DEFAULT_LOOP_INTERVAL_SEC,
    max_batch_limit: int = BATCH_LIMIT,
    spreadsheet_id: str = DEFAULT_SPREADSHEET_ID
):
    """
    Continuous background loop: harvests a batch, then sleeps for interval_sec (default 45 min / 2700s).
    """
    print("=" * 76)
    print("🌙 [AUTONOMOUS CONTINUOUS CATALOG HARVESTER INITIALIZED]")
    print(f"   Интервал опроса: {interval_sec} сек (~{interval_sec // 60} мин)")
    print(f"   Цель за прогон: {count} стартапов (Лимит: {max_batch_limit})")
    print("=" * 76)

    iteration = 1
    try:
        while True:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[ЦИКЛ #{iteration} • {now_str}] Старт проверки ленты Show HN...")
            try:
                ingested = harvest_and_ingest(
                    count=count,
                    max_batch_limit=max_batch_limit,
                    spreadsheet_id=spreadsheet_id
                )
                print(f"✓ Цикл #{iteration} завершен. Добавлено новых: {len(ingested)}")
            except Exception as e:
                print(f"❌ Ошибка в цикле #{iteration}: {e}")

            print(f"\n⏳ [ОЖИДАНИЕ] Засыпаем на {interval_sec // 60} минут ({interval_sec} сек) до следующего сканирования...")
            sys.stdout.flush()
            time.sleep(interval_sec)
            iteration += 1
    except KeyboardInterrupt:
        print("\n[STOP] Харвестер остановлен пользователем.")


def main():
    parser = argparse.ArgumentParser(description="Public Catalog Harvester (Show HN / Product Hunt)")
    parser.add_argument("--count", type=int, default=10, help="Number of startups to harvest (default 10)")
    parser.add_argument("--limit", type=int, default=BATCH_LIMIT, help="Max batch limit (default 15)")
    parser.add_argument("--loop", action="store_true", help="Run in continuous background loop mode (every 45 min)")
    parser.add_argument("--interval", type=int, default=DEFAULT_LOOP_INTERVAL_SEC, help="Loop interval in seconds (default 2700)")
    args = parser.parse_args()

    if args.loop:
        run_continuous(count=args.count, interval_sec=args.interval, max_batch_limit=args.limit)
    else:
        harvest_and_ingest(count=args.count, max_batch_limit=args.limit)


if __name__ == "__main__":
    main()
