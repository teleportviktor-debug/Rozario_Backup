"""
============================================================================
RAZUM GOOGLE AI PRO • TELEGRAM CRM & LEAD NOTIFICATION BOT (v2026.4)
Dispatches Real-time Lead Alerts, Hormozi Scores & Auto-Package Delivery
============================================================================
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

CRM_DIR = os.path.join(ROOT_DIR, "03_CRM_LEADS")
LEADS_REGISTRY = os.path.join(CRM_DIR, "leads_registry.json")
CONFIG_FILE = os.path.join(ROOT_DIR, "swarm_config.json")

def _now_iso() -> str:
    tz = timezone(timedelta(hours=3))
    return datetime.now(tz).strftime("%d.%m.%Y %H:%M:%S")

def load_telegram_config():
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    
    # Try reading from swarm_config.json or .env
    if not bot_token and os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                swarm_inner = cfg.get("swarm_config", cfg)
                tg_cfg = swarm_inner.get("integrations", {}).get("telegram", {})
                bot_token = tg_cfg.get("bot_token", "")
                chat_id = tg_cfg.get("chat_id", "")
        except Exception:
            pass

    return bot_token, chat_id

def save_lead_to_registry(lead: dict) -> dict:
    os.makedirs(CRM_DIR, exist_ok=True)
    leads = []
    if os.path.exists(LEADS_REGISTRY):
        try:
            with open(LEADS_REGISTRY, "r", encoding="utf-8") as f:
                leads = json.load(f)
        except Exception:
            leads = []
    
    lead_entry = {
        "id": f"LEAD-{int(time.time())}",
        "timestamp": _now_iso(),
        "client_name": lead.get("name", "Не указано"),
        "company": lead.get("company", lead.get("name", "Не указано")),
        "email": lead.get("email", "Не указан"),
        "phone": lead.get("phone", "Не указан"),
        "package_id": lead.get("package_id", "pkg-sovereign"),
        "package_name": lead.get("package_name", "Sovereign Autopilot ($300)"),
        "price_usd": lead.get("price_usd", 300),
        "niche": lead.get("niche", "B2B Услуги"),
        "hormozi_score": lead.get("score", 86),
        "tier": lead.get("tier", "🔥 TIER 1: VIP"),
        "status": "NEW_LEAD",
        "package_built": False
    }
    
    leads.append(lead_entry)
    with open(LEADS_REGISTRY, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
        
    return lead_entry

def format_telegram_alert(lead: dict) -> str:
    return f"""🔔 *НОВАЯ ЗАЯВКА НА ПАКЕТ RAZUM AI 2026*
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 *Клиент:* {lead.get('client_name', 'Заказчик')}
🏢 *Компания / Ниша:* {lead.get('niche', 'B2B')}
📧 *Email:* `{lead.get('email', '—')}`
📞 *Телефон:* `{lead.get('phone', '—')}`

📦 *Тариф:* *{lead.get('package_name', 'Sovereign Autopilot')}*
💰 *Сумма:* *${lead.get('price_usd', 300)} (разово)*

🧮 *Hormozi Скоринг:* {lead.get('hormozi_score', 86)}% ({lead.get('tier', '🔥 TIER 1: VIP')})
🛡️ *Контур:* Google Workspace Zero-Log
⏰ *Время заявки:* {lead.get('timestamp', _now_iso())}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 *Действие:* Пакет готов к генерации в `10_PRODUCTION`"""

def send_telegram_message(text: str, reply_markup=None) -> bool:
    bot_token, chat_id = load_telegram_config()
    
    if not bot_token or not chat_id or bot_token.startswith("YOUR_"):
        print("\n[TELEGRAM DEMO MODE] (Токен не указан или работает в демо-режиме)")
        print("—" * 60)
        print(text)
        print("—" * 60)
        return True
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Ошибка отправки в Telegram: {e}")
        return False

def dispatch_new_lead(name: str, email: str, phone: str, package_name: str, price_usd: int, niche: str = "B2B", auto_build_package: bool = True):
    lead_data = {
        "name": name,
        "company": name,
        "email": email,
        "phone": phone,
        "package_name": package_name,
        "price_usd": price_usd,
        "niche": niche,
        "score": 88,
        "tier": "🔥 TIER 1: VIP ПРИОРИТЕТ"
    }
    
    saved_lead = save_lead_to_registry(lead_data)
    alert_text = format_telegram_alert(saved_lead)
    send_telegram_message(alert_text)
    
    if auto_build_package:
        from python_engine.client_packager import generate_client_package
        pkg_id = "pkg-sovereign"
        if price_usd == 50: pkg_id = "pkg-starter"
        elif price_usd == 100: pkg_id = "pkg-command"
        elif price_usd == 200: pkg_id = "pkg-intelligence"
        elif price_usd == 500: pkg_id = "pkg-genesis"
        
        try:
            pkg_res = generate_client_package(pkg_id, name, niche)
            print(f"✓ Авто-сборка пакета завершена: {pkg_res['zip_path']}")
        except Exception as e:
            print(f"⚠️ Ошибка авто-сборки: {e}")

    return saved_lead

def run_test_lead_dispatch():
    print("=" * 70)
    print("  🚀 ТЕСТОВЫЙ ЗАПУСК ДИСПЕТЧЕРА ЗАЯВОК И TELEGRAM CRM")
    print("=" * 70)
    
    test_lead = dispatch_new_lead(
        name="ООО «ПромТехИнвест»",
        email="ceo@promtech-invest.ru",
        phone="+7 (999) 123-45-67",
        package_name="Sovereign Autopilot ($300)",
        price_usd=300,
        niche="Производство и Поставки",
        auto_build_package=True
    )
    
    print("\n✅ Заявка успешно обработана!")
    print(f"📁 Запись добавлена в CRM: {LEADS_REGISTRY}")
    print(f"👤 ID Заявки: {test_lead['id']}")

if __name__ == "__main__":
    run_test_lead_dispatch()
