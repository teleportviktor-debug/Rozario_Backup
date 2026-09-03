"""
============================================================================
RAZUM GOOGLE AI PRO • AUTOMATED BACKUP & RESTORE ENGINE (v2026.4)
Creates Versioned Snapshots & Mirrors to Google Drive (Zero-Data-Loss)
============================================================================
"""

import os
import sys
import shutil
import zipfile
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(ROOT_DIR, "_BACKUPS")
G_DRIVE_BACKUP = r"g:\Мой диск\AI_WORK_SYSTEM_BACKUPS"

INCLUDE_DIRS = [
    "_MEMORY",
    "01_STRATEGY",
    "02_BRAND_BOOK",
    "03_CRM_LEADS",
    "04_SALES_PLAYBOOK",
    "05_CONTENT_PRODUCTION",
    "06_SOP_REGLAMENTS",
    "07_FINANCIAL_MODELS",
    "08_A2UI_SCHEMAS",
    "10_PRODUCTION",
    "gas_scripts",
    "python_engine"
]

INCLUDE_FILES = [
    "swarm_config.json",
    "antigravity_swarm_init.json",
    "index.html",
    "store_packages.html",
    "teleprompter_studio.html",
    "run_razum_system.py",
    "run_full_system_check.py",
    "MASTER_ARCHITECTURAL_REPORT_GEMINI_2026.md",
    "PROJECT_SNAPSHOT_v2.4.md"
]

def create_system_snapshot():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_name = f"RAZUM_ECOSYSTEM_SNAPSHOT_{timestamp}.zip"
    archive_path = os.path.join(BACKUP_DIR, archive_name)

    print(f"\n📦 СОЗДАНИЕ ПОЛНОГО СНАПШОТА СИСТЕМЫ: {archive_name}")
    total_files = 0

    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add files
        for f in INCLUDE_FILES:
            fp = os.path.join(ROOT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, f)
                total_files += 1

        # Add directories
        for d in INCLUDE_DIRS:
            dp = os.path.join(ROOT_DIR, d)
            if os.path.exists(dp):
                for root, _, files in os.walk(dp):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, ROOT_DIR)
                        zf.write(full_path, rel_path)
                        total_files += 1

    size_kb = round(os.path.getsize(archive_path) / 1024, 1)
    print(f"  ✓ Локальный архив: {archive_path} ({size_kb} KB, {total_files} файлов)")

    # Mirror to Google Drive
    if os.path.exists(r"g:\Мой диск"):
        try:
            os.makedirs(G_DRIVE_BACKUP, exist_ok=True)
            drive_dest = os.path.join(G_DRIVE_BACKUP, archive_name)
            shutil.copy2(archive_path, drive_dest)
            print(f"  ☁️ Резервная копия на Google Диске: {drive_dest}")
        except Exception as e:
            print(f"  ⚠️ Drive mirror note: {e}")

    print("\n🎉 СНАПШОТ ЭКОСИСТЕМЫ УСПЕШНО СОХРАНЕН!")
    return archive_path

if __name__ == "__main__":
    create_system_snapshot()
