"""
Скрипт первичной загрузки ключевых документов проекта в папку 02_FOR_NOTEBOOK на Google Drive.
Это подготавливает базу знаний для NotebookLM.
"""
import os
import sys

conv_dir = os.path.join(os.path.dirname(__file__), "..", "drive_markdown_converter")
sys.path.insert(0, os.path.abspath(conv_dir))
os.chdir(conv_dir)
from drive_service import GoogleDriveService

def seed_notebook_documents():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ds = GoogleDriveService()
    notebook_folder_id = ds.folder_ids["notebook"]

    docs_to_upload = [
        # 1. Core architecture & snapshot
        os.path.join(root, "MASTER_ARCHITECTURAL_REPORT_GEMINI_2026.md"),
        os.path.join(root, "PROJECT_SNAPSHOT_v2.4.md"),
        os.path.join(root, "01_STRATEGY", "2026_MASTER_ROADMAP_90_DAYS.md"),
        os.path.join(root, "02_BRAND_BOOK", "SOVEREIGN_BRAND_IDENTITY_2026.md"),
        os.path.join(root, "_MEMORY", "DECISIONS.md"),
        os.path.join(root, "_MEMORY", "ERRORS.md"),
        
        # 2. Sales & Packages & Operations
        os.path.join(root, "04_SALES_PLAYBOOK", "GRAND_SLAM_SCRIPTS_AND_OBJECTIONS.md"),
        os.path.join(root, "05_CONTENT_PRODUCTION", "VIRAL_RETENTION_MAX_CALENDAR.md"),
        os.path.join(root, "06_SOP_REGLAMENTS", "ZERO_LOG_SECURITY_SOP.md"),
        os.path.join(root, "drive_markdown_converter", "README.md")
    ]

    print(f"Uploading core markdown docs to Google Drive 02_FOR_NOTEBOOK (ID: {notebook_folder_id})...")
    uploaded = 0
    for path in docs_to_upload:
        if not os.path.exists(path):
            print(f" [SKIP] File not found: {path}")
            continue
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        file_id = ds.upload_markdown(filename, content)
        print(f" [OK] Uploaded: {filename} -> Drive File ID: {file_id}")
        uploaded += 1

    print(f"\nSuccessfully seeded {uploaded} documents to Google Drive folder 02_FOR_NOTEBOOK!")

if __name__ == "__main__":
    seed_notebook_documents()
