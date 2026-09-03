"""
============================================================================
RAZUM AI 2026 • GOOGLE SHEETS LIVE CRM SYNC & PIPELINE METRICS ENGINE
Exports Leads, Hormozi Heatmaps & Calculates Total Revenue Pipeline (USD)
============================================================================
"""

import os
import sys
import json
import csv
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CRM_DIR = os.path.join(ROOT_DIR, "03_CRM_LEADS")
LEADS_REGISTRY = os.path.join(CRM_DIR, "leads_registry.json")
SHEETS_EXPORT_CSV = os.path.join(CRM_DIR, "WORKSPACE_STUDIO_SHEETS_EXPORT.csv")
G_DRIVE_CRM = r"g:\Мой диск\03_CRM"

def sync_leads_to_sheets():
    if not os.path.exists(LEADS_REGISTRY):
        print(f"⚠️ Реестр лидов не найден: {LEADS_REGISTRY}")
        return

    with open(LEADS_REGISTRY, "r", encoding="utf-8") as f:
        try:
            leads = json.load(f)
        except Exception:
            leads = []

    if not leads:
        print("Реестр лидов пуст.")
        return

    print("=" * 70)
    print("  📊 СИНХРОНИЗАЦИЯ РЕЕСТРА ЛИДОВ И GOOGLE SHEETS CRM 2026")
    print("=" * 70)

    total_pipeline_usd = 0
    tier1_count = 0
    tier2_count = 0

    csv_rows = [
        [
            "ID Лида", "Дата и Время", "Клиент / Компания", "Ниша",
            "Email", "Телефон / TG", "Выбранный Тариф", "Сумма ($)",
            "Hormozi Скоринг", "Категория", "Статус Сделки", "Пакет Собран"
        ]
    ]

    for lead in leads:
        price = lead.get("price_usd", 300)
        score = lead.get("hormozi_score", 86)
        tier = lead.get("tier", "🔥 TIER 1: VIP")
        total_pipeline_usd += price

        if "TIER 1" in tier: tier1_count += 1
        else: tier2_count += 1

        csv_rows.append([
            lead.get("id", "LEAD-001"),
            lead.get("timestamp", datetime.now().strftime("%d.%m.%Y %H:%M")),
            lead.get("client_name", "—"),
            lead.get("niche", "B2B"),
            lead.get("email", "—"),
            lead.get("phone", "—"),
            lead.get("package_name", "Sovereign Autopilot"),
            f"${price}",
            f"{score}%",
            tier,
            lead.get("status", "NEW_LEAD"),
            "ДА (10_PRODUCTION)" if lead.get("package_built", True) else "В очереди"
        ])

    # Write CSV
    with open(SHEETS_EXPORT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)

    print(f"  ✓ Локальный экспорт для Google Таблиц: {SHEETS_EXPORT_CSV}")
    print(f"  📈 Всего лидов в пайплайне: {len(leads)}")
    print(f"  🔥 VIP Лидов (Tier 1): {tier1_count}")
    print(f"  💰 Общий объем потенциальной выручки: ${total_pipeline_usd:,} USD")

    # Mirror to Google Drive 03_CRM
    if os.path.exists(r"g:\Мой диск"):
        try:
            os.makedirs(G_DRIVE_CRM, exist_ok=True)
            drive_csv = os.path.join(G_DRIVE_CRM, "WORKSPACE_STUDIO_SHEETS_EXPORT.csv")
            with open(drive_csv, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f)
                writer.writerows(csv_rows)
            print(f"  ☁️ Зеркало на Google Drive: {drive_csv}")
        except Exception as e:
            print(f"  ⚠️ Drive note: {e}")

    print("=" * 70)

if __name__ == "__main__":
    sync_leads_to_sheets()
