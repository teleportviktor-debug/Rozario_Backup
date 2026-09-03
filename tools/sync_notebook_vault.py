"""
Скрипт прямого копирования структурированных документов проекта в папку 02_FOR_NOTEBOOK на Google Диск (G:).
Позволяет пользователю в 1 клик добавить 3 ноутбука в NotebookLM.
"""
import os
import sys
import shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"c:\Users\user\ГУГЛ ИМПЕРИЯ"
G_NOTEBOOK = r"g:\Мой диск\02_FOR_NOTEBOOK"

COLLECTIONS = {
    "01_CORE": [
        os.path.join(ROOT, "MASTER_ARCHITECTURAL_REPORT_GEMINI_2026.md"),
        os.path.join(ROOT, "PROJECT_SNAPSHOT_v2.4.md"),
        os.path.join(ROOT, "01_STRATEGY", "2026_MASTER_ROADMAP_90_DAYS.md"),
        os.path.join(ROOT, "02_BRAND_BOOK", "SOVEREIGN_BRAND_IDENTITY_2026.md"),
        os.path.join(ROOT, "_MEMORY", "DECISIONS.md"),
        os.path.join(ROOT, "_MEMORY", "ERRORS.md"),
        os.path.join(ROOT, "packages_proposal.md" if os.path.exists(os.path.join(ROOT, "packages_proposal.md")) else os.path.join(ROOT, "MASTER_ARCHITECTURAL_REPORT_GEMINI_2026.md")),
    ],
    "02_SALES": [
        os.path.join(ROOT, "04_SALES_PLAYBOOK", "GRAND_SLAM_SCRIPTS_AND_OBJECTIONS.md"),
        os.path.join(ROOT, "05_CONTENT_PRODUCTION", "VIRAL_RETENTION_MAX_CALENDAR.md"),
        os.path.join(ROOT, "06_SOP_REGLAMENTS", "ZERO_LOG_SECURITY_SOP.md"),
        os.path.join(ROOT, "07_FINANCIAL_MODELS", "UNIT_ECONOMICS_AND_PRICING.json"),
        os.path.join(ROOT, "03_CRM_LEADS", "SAMPLE_LEAD_BRIEFS.json"),
    ],
    "03_TECHNICAL": [
        os.path.join(ROOT, "drive_markdown_converter", "README.md"),
        os.path.join(ROOT, "python_engine", "swarm_orchestrator.py"),
        os.path.join(ROOT, "python_engine", "memory_manager.py"),
        os.path.join(ROOT, "gas_scripts", "SparkScheduler.gs"),
        os.path.join(ROOT, "gas_scripts", "MCP_Server.gs"),
        os.path.join(ROOT, "gas_scripts", "InvoicingParser.gs"),
        os.path.join(ROOT, "gas_scripts", "LiveSheetsWebhook.gs"),
        os.path.join(ROOT, "gas_scripts", "Code.gs"),
        os.path.join(ROOT, "swarm_config.json"),
        os.path.join(ROOT, "antigravity_swarm_init.json")
    ]
}

def sync_to_gdrive_notebook():
    total_copied = 0
    print(f"Syncing curated documents to Google Drive: {G_NOTEBOOK} ...\n")
    
    for folder, files in COLLECTIONS.items():
        target_dir = os.path.join(G_NOTEBOOK, folder)
        os.makedirs(target_dir, exist_ok=True)
        print(f"📁 [{folder}] -> {target_dir}")
        for src in files:
            if os.path.exists(src):
                dest = os.path.join(target_dir, os.path.basename(src))
                shutil.copy2(src, dest)
                print(f"  [OK] {os.path.basename(src)}")
                total_copied += 1
            else:
                print(f"  [SKIP] {src} not found")
        print()

    print(f"🎉 Total files synchronized to 02_FOR_NOTEBOOK: {total_copied}")

if __name__ == "__main__":
    sync_to_gdrive_notebook()
