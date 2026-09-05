import os
import sys
import json
import re
import html
import urllib.request
import urllib.parse
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.enrichment.intent_analyzer import analyze_intent

DEFAULT_KEYWORDS = ["LLM", "AI Engineer", "Latency", "Inference", "Context Caching", "Agentic", "Streaming"]

def get_latest_hiring_threads(limit=3) -> list[dict]:
    """Retrieves official Hacker News 'Who is hiring?' monthly threads."""
    url = "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who+is+hiring"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        stories = []
        for h in data.get("hits", []):
            title = h.get("title", "")
            if "Who is hiring?" in title and "wants to be hired" not in title.lower():
                stories.append({
                    "id": int(h["objectID"]),
                    "title": title,
                    "date": h.get("created_at", "")[:10]
                })
        return stories[:limit]
    except Exception as e:
        print(f"⚠️ [HN API Error]: {e}")
        # Fallback to known September 2026 thread ID
        return [{"id": 49522897, "title": "Ask HN: Who is hiring? (September 2026)", "date": "2026-09-01"}]

def clean_html(raw_html: str) -> str:
    """Converts HTML breaks/paragraphs to clean text and unescapes entities."""
    text = re.sub(r'<p>|</p>|<br\s*/?>', '\n', raw_html)
    text = re.sub(r'<[^>]+>', ' ', text)
    return html.unescape(text).strip()

def extract_website(raw_html: str, text: str, company: str, email: str = "") -> str:
    """Extracts company website URL from posting markup or email domain."""
    ignored = {
        "ycombinator.com", "news.ycombinator.com", "github.com", "linkedin.com",
        "twitter.com", "x.com", "google.com", "apple.com", "medium.com", "youtube.com",
        "careerjumpship.com", "ashbyhq.com", "greenhouse.io", "lever.co",
        "forms.gle", "oraclecloud.com", "join.com", "notion.site", "notion.so",
        "airtable.com", "workable.com", "applytojob.com", "bamboohr.com"
    }

    # 1. Derive from custom domain in email first if email is company-specific
    if email and "@" in email:
        email_domain = email.split("@")[1].lower()
        if not any(ign in email_domain for ign in ignored) and "." in email_domain and email_domain not in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]:
            return f"https://{email_domain}"

    # 2. Look for href attributes in html
    hrefs = re.findall(r'href=[\'"](https?://[^\'">\s]+)[\'"]', raw_html)
    for h in hrefs:
        domain = urllib.parse.urlparse(h).netloc.lower().replace("www.", "")
        if domain and not any(ign in domain for ign in ignored):
            # Return root or clean URL
            return f"https://{domain}"

    # 3. Look for plain URLs in text
    urls = re.findall(r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<]*)?)', text)
    for u in urls:
        domain = u.split("/")[0].lower().replace("www.", "")
        if domain and not any(ign in domain for ign in ignored):
            return f"https://{domain}"

    # 4. Infer clean domain from company name
    clean_comp = re.sub(r'[^a-zA-Z0-9]', '', company).lower()
    if clean_comp and len(clean_comp) > 2:
        return f"https://{clean_comp}.ai"

    return ""

def extract_email(text: str, website: str = "") -> str:
    """Extracts contact email from text or constructs standard address from domain."""
    # Match standard email addresses
    emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    ignored_emails = {"example.com", "ycombinator.com", "sentry.io"}
    for e in emails:
        clean_e = e.rstrip('.,;:)')
        domain = clean_e.split("@")[-1].lower()
        if domain not in ignored_emails and "." in domain:
            return clean_e

    # Check for obfuscated [at] [dot] patterns
    obfuscated = re.findall(
        r'([a-zA-Z0-9_.+-]+)\s*(?:\[at\]|\(at\)|@)\s*([a-zA-Z0-9-]+)\s*(?:\[dot\]|\(dot\)|\.)\s*([a-zA-Z]{2,})',
        text,
        re.IGNORECASE
    )
    if obfuscated:
        u, d, t = obfuscated[0]
        return f"{u}@{d}.{t}"

    # Fallback to website domain
    if website:
        domain = urllib.parse.urlparse(website).netloc.lower().replace("www.", "")
        if domain:
            return f"jobs@{domain}"

    return ""

def is_job_seeker(text: str) -> bool:
    """Detects if posting is a candidate looking for a job rather than a hiring company."""
    first_lines = text[:300].lower()
    seeker_markers = [
        "seeking", "looking for role", "looking for work", "available for",
        "experienced python engineer", "resume:", "cv:", "years in software engineering",
        "wants to be hired", "hire me", "my github:"
    ]
    return any(m in first_lines for m in seeker_markers)

def parse_comment_lead(item: dict, story_id: int, keywords: list) -> dict | None:
    """Parses a single HN comment into a structured job posting lead."""
    raw_html = item.get("comment_text", "")
    if not raw_html:
        return None

    text = clean_html(raw_html)
    if is_job_seeker(text):
        return None

    # Check for target keywords
    text_lower = text.lower()
    matched_kws = [kw for kw in keywords if kw.lower() in text_lower]
    if not matched_kws:
        return None

    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines:
        return None
    first_line = lines[0]

    # Standard format: Company | Role | Location | ...
    parts = [p.strip() for p in first_line.split('|')]
    if len(parts) >= 2:
        raw_company = parts[0]
        raw_role = parts[1]
    else:
        dash_parts = [p.strip() for p in re.split(r'[-–—]', first_line)]
        if len(dash_parts) >= 2:
            raw_company = dash_parts[0]
            raw_role = dash_parts[1]
        else:
            raw_company = first_line[:35]
            raw_role = f"Senior {matched_kws[0]} Engineer"

    # Clean company name
    company = re.sub(r'\(YC.*?\)', '', raw_company, flags=re.IGNORECASE).strip()
    company = re.sub(r'https?://\S+', '', company).strip()
    company = re.sub(r'[:;,].*', '', company).strip()
    company = company.rstrip('.').strip()

    if not company or len(company) < 2 or "careerjumpship" in company.lower() or "who is hiring" in company.lower():
        return None

    bad_company_prefixes = ["hi hn", "hiring:", "looking for", "i run", "we are", "seeking", "python /", "backend /", "full stack /"]
    if any(company.lower().startswith(p) for p in bad_company_prefixes):
        return None

    # Clean role title
    role = re.sub(r'https?://\S+', '', raw_role).strip()
    role = re.sub(r'\(.*?\)', '', role).strip()

    # Disambiguate location strings vs actual engineering role
    location_words = ["stockholm", "london", "onsite", "remote", "new york", "san francisco", "austin", "hybrid", "usa", "worldwide", "full-time", "part-time"]
    if any(role.lower().strip() == loc or (len(role.split()) <= 2 and loc in role.lower()) for loc in location_words) or len(role) < 3 or len(role) > 80:
        found_role = None
        for p in parts[2:]:
            if any(eng in p.lower() for eng in ["engineer", "developer", "lead", "architect", "researcher", "scientist"]):
                found_role = re.sub(r'\(.*?\)', '', p).strip()
                break
        if not found_role:
            for l in lines[1:4]:
                if any(eng in l.lower() for eng in ["engineer", "developer", "architect"]):
                    found_role = l[:50].strip()
                    break
        role = found_role if found_role else f"Senior {matched_kws[0]} Engineer"

    if "building an" in role.lower() or "is building" in role.lower():
        role = f"Agentic AI Engineer"

    # Extract email and website
    email = extract_email(text)
    website = extract_website(raw_html, text, company, email=email)
    if not email and website:
        email = extract_email(text, website=website)

    # Extract tech stack snippet
    desc_lines = lines[1:4] if len(lines) > 1 else lines[:2]
    tech_stack = " ".join(desc_lines)[:350].strip()

    date_posted = item.get("created_at", "")[:10]
    if not date_posted:
        date_posted = datetime.utcnow().strftime("%Y-%m-%d")

    return {
        "company": company,
        "website": website,
        "role": role,
        "keywords": matched_kws,
        "email": email,
        "tech_stack": tech_stack,
        "date_posted": date_posted,
        "full_text": text
    }

def scrape_hiring_intent(limit: int = 10, keywords: list = None) -> list[dict]:
    """
    Scrapes live open AI startup vacancies with hiring intent,
    and enriches them with pain analysis, LinkedIn URL, and intent angle.
    """
    if not keywords:
        keywords = DEFAULT_KEYWORDS

    print("=" * 76)
    print("🕵️ [HIRING INTENT SCRAPER] Поиск горячих AI-стартапов по сигналу найма")
    print(f"   Фильтры ключевых слов: {', '.join(keywords)}")
    print(f"   Целевой лимит: {limit} лидов")
    print("=" * 76)

    stories = get_latest_hiring_threads(limit=3)
    print(f"📋 Обнаружено активных тредов найма: {len(stories)}")
    for s in stories:
        print(f"   • {s['title']} (ID: {s['id']}, Date: {s['date']})")

    collected_leads = []
    seen_companies = set()

    for story in stories:
        if len(collected_leads) >= limit:
            break

        story_id = story["id"]
        print(f"\n🔍 Парсинг комментариев верхнего уровня из треда {story_id}...")
        url = f"https://hn.algolia.com/api/v1/search?tags=comment,story_{story_id}&hitsPerPage=200"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"⚠️ Ошибка запроса к треду {story_id}: {e}")
            continue

        hits = data.get("hits", [])
        for h in hits:
            if h.get("parent_id") != story_id:
                continue

            raw_lead = parse_comment_lead(h, story_id, keywords)
            if not raw_lead:
                continue

            comp_key = raw_lead["company"].lower().strip()
            if comp_key in seen_companies or len(comp_key) < 2:
                continue
            seen_companies.add(comp_key)

            # Analyze and enrich with intent_analyzer
            enriched = analyze_intent(raw_lead)
            enriched["date_posted"] = raw_lead["date_posted"]
            enriched["matched_signals"] = ", ".join(raw_lead["keywords"])

            collected_leads.append(enriched)
            print(f"  ✨ [LEAD #{len(collected_leads)}] {enriched['company']} | {enriched['hiring_role']}")
            print(f"     🌐 {enriched['website']} | ✉️ {enriched['contact_email']}")
            print(f"     ⚡ Pain: {enriched['tech_stack_core_pain']}")
            print(f"     🎯 Angle: {enriched['intent_angle']}")

            if len(collected_leads) >= limit:
                break

    print("\n" + "=" * 76)
    print(f"🏆 [СБОР ЗАВЕРШЕН]: Собрано {len(collected_leads)} горячих AI-стартапов!")
    print("=" * 76)
    return collected_leads

if __name__ == "__main__":
    leads = scrape_hiring_intent(limit=10)
    print(f"\nИтоговый результат: {len(leads)} записей.")
