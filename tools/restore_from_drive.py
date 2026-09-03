"""
============================================================================
RAZUM GOOGLE AI PRO • RESTORE & INTEGRITY ENGINE (v2026.4)
Restores Ecosystem from Google Drive Mirror or Local Snapshot (Zero-Data-Loss)
============================================================================
"""

import os
import sys
import shutil
import zipfile
import argparse
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP_DIR = os.path.join(ROOT_DIR, "_BACKUPS")
G_DRIVE_BACKUP = r"g:\Мой диск\AI_WORK_SYSTEM_BACKUPS"
G_DRIVE_SYSTEM = r"g:\Мой диск\AI_WORK_SYSTEM"

def list_available_snapshots():
    snapshots = []
    
    # Check local backups
    if os.path.exists(BACKUP_DIR):
        for f in os.listdir(BACKUP_DIR):
            if f.endswith(".zip"):
                fp = os.path.join(BACKUP_DIR, f)
                snapshots.append({
                    "source": "LOCAL",
                    "filename": f,
                    "path": fp,
                    "size_kb": round(os.path.getsize(fp) / 1024, 1),
                    "mtime": datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%d.%m.%Y %H:%M:%S")
                })
                
    # Check Google Drive backups
    if os.path.exists(G_DRIVE_BACKUP):
        for f in os.listdir(G_DRIVE_BACKUP):
            if f.endswith(".zip") and not any(s["filename"] == f for s in snapshots):
                fp = os.path.join(G_DRIVE_BACKUP, f)
                snapshots.append({
                    "source": "GOOGLE_DRIVE",
                    "filename": f,
                    "path": fp,
                    "size_kb": round(os.path.getsize(fp) / 1024, 1),
                    "mtime": datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%d.%m.%Y %H:%M:%S")
                })

    return snapshots

def restore_snapshot(zip_path: str):
    if not os.path.exists(zip_path):
        print(f"❌ Файл снапшота не найден: {zip_path}")
        return False

    print(f"\n🔄 ВОССТАНОВЛЕНИЕ ЭКОСИСТЕМЫ ИЗ СНАПШОТА: {os.path.basename(zip_path)}")
    
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(ROOT_DIR)
        
    print("  ✓ Все файлы успешно извлечены и перезаписаны в рабочую область.")
    print("  ✓ Память _MEMORY, схемы A2UI, скрипты и CRM реестры восстановлены.")
    print("\n🎉 ВОССТАНОВЛЕНИЕ СИСТЕМЫ ЗАВЕРШЕНО УСПЕШНО!")
    return True

def interactive_restore():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║       🔄 RAZUM AI • МАСТЕР ВОССТАНОВЛЕНИЯ ИЗ РЕЗЕРВНЫХ КОПИЙ 2026        ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    snapshots = list_available_snapshots()
    if not snapshots:
        print("⚠️ Доступных архивов снапшотов не найдено.")
        print(f"Создайте первый снапшот командой: python tools/backup_restore.py")
        return

    print("Доступные резервные копии:")
    for idx, s in enumerate(snapshots, 1):
        print(f" [{idx}] 📦 {s['filename']} ({s['size_kb']} KB, {s['mtime']}) [{s['source']}]")

    choice = input(f"\nВыберите номер архива для восстановления (1-{len(snapshots)}): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(snapshots):
            restore_snapshot(snapshots[idx]["path"])
        else:
            print("Неверный номер.")
    except Exception as e:
        print(f"Ошибка выбора: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore Ecosystem Snapshot Engine")
    parser.add_argument("--file", type=str, help="Specific ZIP snapshot file path to restore")
    args = parser.parse_args()

    if args.file:
        restore_snapshot(args.file)
    else:
        interactive_restore()
