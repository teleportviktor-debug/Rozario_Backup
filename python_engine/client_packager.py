"""
============================================================================
RAZUM GOOGLE AI PRO • CLIENT PACKAGE DELIVERY ENGINE (v2026.4)
Automated Assembler for Sovereign AI Turnkey Client Packages ($50 - $500)
============================================================================
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
import argparse
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTION_DIR = os.path.join(ROOT_DIR, "10_PRODUCTION")
TEMPLATES_DIR = os.path.join(PRODUCTION_DIR, "_TEMPLATES")
PRICING_FILE = os.path.join(ROOT_DIR, "07_FINANCIAL_MODELS", "UNIT_ECONOMICS_AND_PRICING.json")

def load_pricing_packages():
    if os.path.exists(PRICING_FILE):
        with open(PRICING_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {pkg["id"]: pkg for pkg in data.get("packages", [])}
    return {}

PACKAGES = {
    "pkg-starter": {
        "id": "pkg-starter",
        "name": "Spark Starter",
        "price": "$50",
        "price_val": 50,
        "desc": "Автономный парсер почты и первичных документов в Google Таблицу за 15 минут.",
        "gas_scripts": ["Code.gs"],
        "include_python_engine": False,
        "include_video_studio": False
    },
    "pkg-command": {
        "id": "pkg-command",
        "name": "Command Center",
        "price": "$100",
        "price_val": 100,
        "desc": "Командный центр для малого бизнеса: авто-парсер счетов + CRM реестр + Telegram бот.",
        "gas_scripts": ["Code.gs", "InvoicingParser.gs"],
        "include_python_engine": False,
        "include_video_studio": False
    },
    "pkg-intelligence": {
        "id": "pkg-intelligence",
        "name": "Intelligence Module",
        "price": "$200",
        "price_val": 200,
        "desc": "B2B Sales Intelligence: Hormozi скоринг лидов, скрипты продаж и аудит звонков.",
        "gas_scripts": ["Code.gs", "MCP_Server.gs"],
        "include_python_engine": True,
        "include_video_studio": True
    },
    "pkg-sovereign": {
        "id": "pkg-sovereign",
        "name": "Sovereign Autopilot",
        "price": "$300",
        "price_val": 300,
        "desc": "Полный суверенный автопилот: 24/7 Spark Watchdog, Zero-Leakage контур и Google Workspace MCP.",
        "gas_scripts": ["Code.gs", "MCP_Server.gs", "InvoicingParser.gs", "SparkScheduler.gs"],
        "include_python_engine": True,
        "include_video_studio": True
    },
    "pkg-genesis": {
        "id": "pkg-genesis",
        "name": "Genesis Enterprise",
        "price": "$500",
        "price_val": 500,
        "desc": "Enterprise White-Label AI-Геном: индивидуальный суверенный рой агентов с правом перепродажи.",
        "gas_scripts": ["Code.gs", "MCP_Server.gs", "InvoicingParser.gs", "SparkScheduler.gs"],
        "include_python_engine": True,
        "include_video_studio": True
    }
}

def generate_client_package(package_id: str, client_name: str, niche: str = "Бизнес и Услуги", email: str = ""):
    pkg = PACKAGES.get(package_id, PACKAGES["pkg-sovereign"])
    
    clean_client = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in client_name).strip()
    clean_client = clean_client.replace(" ", "_")
    folder_name = f"{pkg['name'].replace(' ', '_')}_{clean_client}_v2026"
    package_dir = os.path.join(PRODUCTION_DIR, folder_name)
    
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir, exist_ok=True)
    
    now_str = datetime.now().strftime("%d.%m.%Y")
    sha_payload = f"{client_name}:{pkg['id']}:{datetime.now().isoformat()}:RAZUM_SOVEREIGN_CORE_2026"
    sha256_hash = f"sha256:{hashlib.sha256(sha_payload.encode('utf-8')).hexdigest()}"
    
    print(f"\n📦 СБОРКА КЛИЕНТСКОГО ПАКЕТА: {pkg['name']} ({pkg['price']})")
    print(f"👤 Клиент: {client_name} ({niche})")
    print(f"📁 Папка: {package_dir}")
    
    # 1. Generate Passport Certificate HTML
    passport_template_path = os.path.join(TEMPLATES_DIR, "PASSPORT_TEMPLATE.html")
    passport_html = ""
    if os.path.exists(passport_template_path):
        with open(passport_template_path, "r", encoding="utf-8") as f:
            passport_html = f.read()
    
    passport_html = passport_html.replace("{{CLIENT_NAME}}", client_name)
    passport_html = passport_html.replace("{{PACKAGE_NAME}}", pkg["name"])
    passport_html = passport_html.replace("{{PACKAGE_PRICE}}", pkg["price"])
    passport_html = passport_html.replace("{{CLIENT_NICHE}}", niche)
    passport_html = passport_html.replace("{{ISSUE_DATE}}", now_str)
    passport_html = passport_html.replace("{{SHA256_HASH}}", sha256_hash)
    
    with open(os.path.join(package_dir, "PASSPORT_SECURITY_CERTIFICATE.html"), "w", encoding="utf-8") as f:
        f.write(passport_html)
    print("  ✓ Паспорт безопасности: PASSPORT_SECURITY_CERTIFICATE.html")

    # 1.5 Generate Customized CLIENT_ONBOARDING_PORTAL.html
    portal_template_path = os.path.join(ROOT_DIR, "client_portal.html")
    if os.path.exists(portal_template_path):
        with open(portal_template_path, "r", encoding="utf-8") as f:
            portal_html = f.read()
        portal_html = portal_html.replace("Личный Кабинет Развертывания", f"Личный Кабинет: {client_name}")
        portal_html = portal_html.replace("Sovereign Autopilot ($300)", f"{pkg['name']} ({pkg['price']})")
        portal_html = portal_html.replace("A8F9C02E4B178D3290FEBC11", sha256_hash)
        with open(os.path.join(package_dir, "CLIENT_ONBOARDING_PORTAL.html"), "w", encoding="utf-8") as f:
            f.write(portal_html)
        print("  ✓ Интерактивный портал: CLIENT_ONBOARDING_PORTAL.html")

    # Copy CSS and Assets for standalone execution
    os.makedirs(os.path.join(package_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(package_dir, "assets"), exist_ok=True)
    if os.path.exists(os.path.join(ROOT_DIR, "css", "main.css")):
        shutil.copy2(os.path.join(ROOT_DIR, "css", "main.css"), os.path.join(package_dir, "css", "main.css"))
    if os.path.exists(os.path.join(ROOT_DIR, "assets", "razum_logo.jpg")):
        shutil.copy2(os.path.join(ROOT_DIR, "assets", "razum_logo.jpg"), os.path.join(package_dir, "assets", "razum_logo.jpg"))

    # 2. Generate Customized README & INSTALL
    readme_content = f"""# 🚀 ПАКЕТ ВНЕДРЕНИЯ: {pkg['name'].upper()} ({pkg['price']})
**Заказчик:** {client_name}  
**Отрасль:** {niche}  
**Дата выдачи:** {now_str}  
**Хеш контура:** `{sha256_hash}`  

---

## 🏛️ Что входит в ваш комплект поставки:
1. 👑 **`CLIENT_ONBOARDING_PORTAL.html`** — ваш персональный интерактивный портал развертывания.
2. 🛡️ **`PASSPORT_SECURITY_CERTIFICATE.html`** — ваш суверенный паспорт безопасности.
3. ⚙️ **`gas_scripts/`** — готовые скрипты Google Apps Script для вставки в Google Sheets.
4. 📖 **`INSTALL_GUIDE.md`** — пошаговая инструкция установки за 15 минут без программирования.
5. 🚀 **`QUICK_START.bat`** — запуск портала в 1 клик.
"""
    with open(os.path.join(package_dir, "README_START_HERE.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("  ✓ Инструкция: README_START_HERE.md")

    # 3. Copy Install and Checklist Templates
    install_tpl = os.path.join(TEMPLATES_DIR, "INSTALL_TEMPLATE.md")
    if os.path.exists(install_tpl):
        with open(install_tpl, "r", encoding="utf-8") as f:
            content = f.read().replace("{{PRODUCT_NAME}}", pkg["name"]).replace("{{VERSION}}", "2026.4")
        with open(os.path.join(package_dir, "INSTALL_GUIDE.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓ Руководство: INSTALL_GUIDE.md")

    checklist_tpl = os.path.join(TEMPLATES_DIR, "FINAL_CHECKLIST_TEMPLATE.md")
    if os.path.exists(checklist_tpl):
        with open(checklist_tpl, "r", encoding="utf-8") as f:
            content = f.read().replace("{{PRODUCT_NAME}}", pkg["name"]).replace("{{CLIENT_NAME}}", client_name)
        with open(os.path.join(package_dir, "DEPLOYMENT_CHECKLIST.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print("  ✓ Чек-лист: DEPLOYMENT_CHECKLIST.md")

    # 4. Copy Customized Google Apps Scripts
    pkg_gas_dir = os.path.join(package_dir, "gas_scripts")
    os.makedirs(pkg_gas_dir, exist_ok=True)
    
    gas_source_dir = os.path.join(ROOT_DIR, "gas_scripts")
    if os.path.exists(gas_source_dir):
        for script_file in os.listdir(gas_source_dir):
            if script_file.endswith(".gs"):
                src_path = os.path.join(gas_source_dir, script_file)
                dest_path = os.path.join(pkg_gas_dir, script_file)
                with open(src_path, "r", encoding="utf-8") as f:
                    script_content = f.read()
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(script_content)
        print(f"  ✓ Скрипты GAS скопированы в: gas_scripts/")

    # 5. Include Teleprompter Studio for Intelligence / Sovereign / Genesis
    if pkg["id"] in ["pkg-intelligence", "pkg-sovereign", "pkg-genesis"]:
        tele_src = os.path.join(ROOT_DIR, "teleprompter_studio.html")
        if os.path.exists(tele_src):
            shutil.copy2(tele_src, os.path.join(package_dir, "Teleprompter_Studio.html"))
            print("  ✓ AI-Телесуфлер: Teleprompter_Studio.html")

    # 6. Generate Environment and Launcher
    env_example = f"""# RAZUM SOVEREIGN AI • CONFIGURATION ({pkg['name']})
CLIENT_NAME="{client_name}"
PACKAGE_ID="{pkg['id']}"
PACKAGE_PRICE="{pkg['price']}"
DEPLOYMENT_HASH="{sha256_hash}"
DRIVE_NOTEBOOK_FOLDER=02_FOR_NOTEBOOK
ZERO_LOG_ENCRYPTION=ENABLED
"""
    with open(os.path.join(package_dir, ".env.example"), "w", encoding="utf-8") as f:
        f.write(env_example)

    quick_start_bat = """@echo off
chcp 65001 > nul
title Sovereign AI Quick Start
echo ===================================================
echo   RAZUM SOVEREIGN AI • CLIENT ONBOARDING 2026
echo ===================================================
echo.
start CLIENT_ONBOARDING_PORTAL.html
echo [OK] Интерактивный портал клиента успешно открыт!
pause
"""
    with open(os.path.join(package_dir, "QUICK_START.bat"), "w", encoding="utf-8") as f:
        f.write(quick_start_bat)

    # 7. Create Production ZIP Archive
    zip_filename = f"DELIVERY_{pkg['name'].replace(' ', '_')}_{clean_client}.zip"
    zip_filepath = os.path.join(PRODUCTION_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_filepath, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, package_dir)
                zf.write(file_path, rel_path)
    
    print(f"\n🎉 ZIP-АРХИВ УСПЕШНО СОБРАН: {zip_filepath} ({os.path.getsize(zip_filepath)} байт)")
    
    # 8. Mirror to Google Drive 10_PRODUCTION if exists
    g_prod = r"g:\Мой диск\10_PRODUCTION"
    if os.path.exists(r"g:\Мой диск"):
        try:
            os.makedirs(g_prod, exist_ok=True)
            shutil.copy2(zip_filepath, os.path.join(g_prod, zip_filename))
            print(f"☁️ Зеркало на Google Drive: {os.path.join(g_prod, zip_filename)}")
        except Exception as e:
            print(f"⚠️ Drive mirror note: {e}")

    return {
        "success": True,
        "package_id": pkg["id"],
        "package_name": pkg["name"],
        "client_name": client_name,
        "folder": package_dir,
        "zip_path": zip_filepath,
        "sha256": sha256_hash
    }

def interactive_cli():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║        📦 RAZUM AI • ГЕНЕРАТОР ГОТОВЫХ КЛИЕНТСКИХ ПАКЕТОВ 2026           ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    print("Выберите тариф для сборки:")
    print(" [1] ⚡ Spark Starter ($50) — Парсер почты и первичных документов")
    print(" [2] 🏢 Command Center ($100) — Авто-парсер счетов + CRM реестр")
    print(" [3] 🎯 Intelligence Module ($200) — Hormozi скоринг + скрипты продаж")
    print(" [4] 🛡️ Sovereign Autopilot ($300) — Полный суверенный контур + Spark Watchdog")
    print(" [5] 👑 Genesis Enterprise ($500) — White-Label AI-Геном компании")
    
    choice = input("\nНомер тарифа (1-5, по умолч. 4): ").strip() or "4"
    pkg_map = {
        "1": "pkg-starter",
        "2": "pkg-command",
        "3": "pkg-intelligence",
        "4": "pkg-sovereign",
        "5": "pkg-genesis"
    }
    selected_pkg = pkg_map.get(choice, "pkg-sovereign")
    
    client_name = input("Имя клиента / Название компании (напр., ООО Вектор): ").strip() or "ООО Вектор"
    niche = input("Ниша / Отрасль (напр., Оптовая торговля): ").strip() or "Оптовая торговля"
    
    res = generate_client_package(selected_pkg, client_name, niche)
    print("\n" + "="*75)
    print(f"✅ Пакет готов к передаче заказчику!")
    print(f"📦 Путь к архиву: {res['zip_path']}")
    print("="*75)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client Package Delivery Assembler")
    parser.add_argument("--package", type=str, default="pkg-sovereign", help="Package ID (pkg-starter..pkg-genesis)")
    parser.add_argument("--client", type=str, default="ООО Вектор", help="Client name")
    parser.add_argument("--niche", type=str, default="Оптовая торговля", help="Client niche")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        interactive_cli()
    else:
        generate_client_package(args.package, args.client, args.niche)
