"""
============================================================================
RAZUM AI 2026 • GITHUB PAGES DEPLOYMENT BUNDLER (v2026.4)
Packages Web Assets for 1-Click Upload to GitHub Repository (Rozario_Backup)
============================================================================
"""

import os
import sys
import zipfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY_ZIP = os.path.join(ROOT_DIR, "GITHUB_PAGES_DEPLOY.zip")

INCLUDE_FILES = [
    "index.html",
    "store_packages.html",
    "teleprompter_studio.html",
    "Teleprompter_Studio.html",  # Case-sensitivity compatibility for Linux GitHub Pages
    "video_studio.html",
    "client_portal.html",
    "README.md",
    "swarm_config.json"
]

INCLUDE_DIRS = [
    "css",
    "js",
    "assets",
    "gas_scripts"
]

def bundle_github_pages():
    print("=" * 70)
    print("  🌐 СБОРКА ПАКЕТА ДЛЯ ДЕПЛОЯ НА GITHUB PAGES (Rozario_Backup)")
    print("=" * 70)

    # Ensure Teleprompter_Studio.html alias exists for case-sensitivity
    src_tele = os.path.join(ROOT_DIR, "teleprompter_studio.html")
    dest_tele = os.path.join(ROOT_DIR, "Teleprompter_Studio.html")
    if os.path.exists(src_tele):
        with open(src_tele, "r", encoding="utf-8") as f:
            content = f.read()
        with open(dest_tele, "w", encoding="utf-8") as f:
            f.write(content)

    total_files = 0
    with zipfile.ZipFile(DEPLOY_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in INCLUDE_FILES:
            fp = os.path.join(ROOT_DIR, f)
            if os.path.exists(fp):
                zf.write(fp, f)
                print(f"  ✓ Добавлен файл: {f}")
                total_files += 1

        for d in INCLUDE_DIRS:
            dp = os.path.join(ROOT_DIR, d)
            if os.path.exists(dp):
                for root, _, files in os.walk(dp):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, ROOT_DIR)
                        zf.write(full_path, rel_path)
                        total_files += 1

    size_kb = round(os.path.getsize(DEPLOY_ZIP) / 1024, 1)
    print(f"\n🎉 ПАКЕТ ДЛЯ GITHUB PAGES УСПЕШНО СОБРАН: {DEPLOY_ZIP} ({size_kb} KB, {total_files} файлов)")
    print("=" * 70)
    print("Как загрузить на GitHub за 30 секунд:")
    print(" 1. Откройте в браузере: https://github.com/teleportviktor-debug/Rozario_Backup")
    print(" 2. Нажмите 'Add file' -> 'Upload files'")
    print(" 3. Перетащите файлы или распакованный архив -> Нажмите 'Commit changes'")
    print(" 4. Ваши новые страницы (store_packages.html, teleprompter) сразу появятся онлайн!")
    print("=" * 70)

if __name__ == "__main__":
    bundle_github_pages()
