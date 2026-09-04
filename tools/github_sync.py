"""
============================================================================
RAZUM AI 2026 • DIRECT GITHUB CLOUD REPO SYNC ENGINE (REST API)
Uploads & Synchronizes All Files to GitHub without needing Git CLI or Admin
============================================================================
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = "teleportviktor-debug"
REPO = "Rozario_Backup"
BRANCH = "main"

SYNC_FILES = [
    "index.html",
    "store_packages.html",
    "teleprompter_studio.html",
    "Teleprompter_Studio.html",
    "video_studio.html",
    "client_portal.html",
    "sovereign_transformation.html",
    "client_presentation.html",
    "css/main.css",
    "js/app.js",
    "js/hormozi_engine.js",
    "js/a2ui_renderer.js",
    "js/sound_lab.js",
    "js/doc_parser.js",
    "js/self_healing_engine.js",
    "js/geo_optimizer.js",
    "js/speech_auditor.js",
    "js/passport_generator.js",
    "assets/razum_logo.jpg",
    "assets/launch_visuals/sovereign_architecture.jpg",
    "assets/launch_visuals/saas_vs_sovereign.jpg",
    "assets/launch_visuals/ai_swarm_agents.jpg",
    "gas_scripts/LiveSheetsWebhook.gs",
    "gas_scripts/Code.gs",
    "swarm_config.json"
]

def get_file_sha(file_path: str, token: str):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{file_path}?ref={BRANCH}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Razum-Sync-Agent"
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise e

def upload_file_to_github(rel_path: str, token: str):
    local_path = os.path.join(ROOT_DIR, rel_path)
    if not os.path.exists(local_path):
        print(f"  ⚠️ Пропущен (не найден): {rel_path}")
        return False

    with open(local_path, "rb") as f:
        content_bytes = f.read()

    b64_content = base64.b64encode(content_bytes).decode("utf-8")
    sha = get_file_sha(rel_path, token)

    payload = {
        "message": f"Auto-Sync: update {rel_path} [Razum AI 2026]",
        "content": b64_content,
        "branch": BRANCH
    }
    if sha:
        payload["sha"] = sha

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{rel_path}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "Razum-Sync-Agent"
        },
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print(f"  ✓ Синхронизирован: {rel_path}")
                return True
    except Exception as e:
        print(f"  ❌ Ошибка загрузки {rel_path}: {e}")
        return False

def sync_all(token: str = None):
    print("=" * 70)
    print(f"  🌐 ПРЯМАЯ СИНХРОНИЗАЦИЯ С GITHUB: {OWNER}/{REPO} (ветка {BRANCH})")
    print("=" * 70)

    if not token:
        token = os.environ.get("GITHUB_TOKEN")

    if not token:
        token = input("Введите ваш GitHub Personal Access Token (PAT): ").strip()

    if not token:
        print("❌ Токен не указан. Синхронизация отменена.")
        return

    success_count = 0
    for rel_path in SYNC_FILES:
        if upload_file_to_github(rel_path, token):
            success_count += 1

    print("=" * 70)
    print(f"🎉 СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА! Успешно обновлено: {success_count}/{len(SYNC_FILES)} файлов.")
    print(f"Сайт доступен: https://{OWNER}.github.io/{REPO}/")
    print("=" * 70)

if __name__ == "__main__":
    t = sys.argv[1] if len(sys.argv) > 1 else None
    sync_all(t)
