"""
============================================================================
MEMORY SYNC — Этап 1 синхронизации Zero API Workspace Engine
Зеркалирует _MEMORY/ ↔ Google Drive ↔ GitHub

Запуск:
  python tools/memory_sync.py              # однократный sync на Drive
  python tools/memory_sync.py --git        # sync + git commit + push
  python tools/memory_sync.py --status     # показать что будет синхронизировано
============================================================================
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Добавляем корень проекта в sys.path
_PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from python_engine.memory_manager import read_memory, daily_log, _now_iso

# ── Конфигурация ───────────────────────────────────────────────────────────
MEMORY_DIR  = _PROJECT_ROOT / "_MEMORY"
DRIVE_ROOT  = Path(r"g:\Мой диск\AI_WORK_SYSTEM")

# Папки для синхронизации локально → Drive
SYNC_MAP = {
    "_MEMORY":                  "_MEMORY",
    "10_PRODUCTION":            "10_PRODUCTION",
    "03_CRM_LEADS":             "03_CRM",
    "04_SALES_PLAYBOOK":        "04_Playbook",
    "05_CONTENT_PRODUCTION":    "05_Content",
    "08_A2UI_SCHEMAS":          "08_A2UI_SCHEMAS",
}

# Файлы, которые НИКОГДА не синхронизируются (секреты)
EXCLUDE_PATTERNS = {
    "service_account.json",
    "*.json.bak",
    ".env",
    "__pycache__",
    "*.pyc",
    "base64_key.txt",
}

def _now_str() -> str:
    tz = timezone(timedelta(hours=3))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def _is_excluded(filename: str) -> bool:
    """Проверяет, нужно ли исключить файл из синхронизации."""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.startswith("*"):
            if filename.endswith(pattern[1:]):
                return True
        elif filename == pattern:
            return True
    return False

def sync_folder_to_drive(src: Path, dst: Path, dry_run: bool = False) -> dict:
    """
    Синхронизирует папку src → dst (Drive).
    Возвращает статистику: {copied, skipped, errors}
    """
    stats = {"copied": 0, "skipped": 0, "errors": 0}
    if not src.exists():
        return stats

    dst.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        if _is_excluded(item.name):
            stats["skipped"] += 1
            continue
        if item.name.startswith("."):
            continue

        rel = item.relative_to(src)
        dst_item = dst / rel

        if item.is_dir():
            if not dry_run:
                dst_item.mkdir(parents=True, exist_ok=True)
            continue

        # Копируем только если файл изменился (по размеру или mtime)
        if dst_item.exists():
            src_mtime = item.stat().st_mtime
            dst_mtime = dst_item.stat().st_mtime
            if abs(src_mtime - dst_mtime) < 2:  # 2 сек допуск
                stats["skipped"] += 1
                continue

        try:
            if not dry_run:
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst_item)
            stats["copied"] += 1
        except Exception as e:
            print(f"  [WARN] Ошибка копирования {item.name}: {e}")
            stats["errors"] += 1

    return stats

def sync_all_to_drive(dry_run: bool = False) -> bool:
    """
    Зеркалирует все папки проекта на Google Drive.
    Возвращает True при успехе.
    """
    if not DRIVE_ROOT.exists():
        print(f"[WARN] Google Drive не подключён: {DRIVE_ROOT}")
        print("       Убедитесь что Google Drive для рабочего стола запущен.")
        return False

    print(f"[Drive Sync] {'(DRY RUN) ' if dry_run else ''}Начинаю синхронизацию -> {DRIVE_ROOT}")
    total_copied = 0
    total_skipped = 0

    for local_folder, drive_folder in SYNC_MAP.items():
        src = _PROJECT_ROOT / local_folder
        dst = DRIVE_ROOT / drive_folder
        stats = sync_folder_to_drive(src, dst, dry_run=dry_run)
        if stats["copied"] > 0 or dry_run:
            print(f"  {'[DRY]' if dry_run else '[OK] '} {local_folder:30} -> {drive_folder}  "
                  f"(+{stats['copied']} файлов, пропущено: {stats['skipped']})")
        total_copied += stats["copied"]
        total_skipped += stats["skipped"]

    print(f"\n[Drive Sync] Итого: {total_copied} файлов скопировано, {total_skipped} без изменений")
    if not dry_run:
        daily_log("memory_sync", "Drive sync complete", f"Copied: {total_copied}, Skipped: {total_skipped}")
    return True

# ── Git синхронизация ──────────────────────────────────────────────────────

def check_git_available() -> bool:
    """Проверяет что git установлен."""
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def git_status() -> str:
    """Возвращает список изменённых файлов."""
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(_PROJECT_ROOT)
    )
    return result.stdout.strip()

def git_sync(commit_message: str = None) -> bool:
    """
    Выполняет: git add . → git commit → git push
    Безопасно: не коммитит service_account.json и .env
    """
    if not check_git_available():
        print("[ERROR] git не установлен. Скачайте: https://git-scm.com/download/win")
        return False

    # Проверяем наличие remote
    result = subprocess.run(
        ["git", "remote", "-v"],
        capture_output=True, text=True, cwd=str(_PROJECT_ROOT)
    )
    if not result.stdout.strip():
        print("[WARN] git remote не настроен.")
        print("       Выполните: git remote add origin https://github.com/YOUR/repo.git")
        print("       Затем: git branch -M main && git push -u origin main")
        return False

    # git add (без секретов — защита в .gitignore)
    subprocess.run(["git", "add", "_MEMORY/", "10_PRODUCTION/", "python_engine/",
                    "*.json", "*.md", "*.yml"],
                   cwd=str(_PROJECT_ROOT), capture_output=True)

    # git commit
    if not commit_message:
        commit_message = f"memory: daily sync {_now_str()}"
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        capture_output=True, text=True, encoding="utf-8", cwd=str(_PROJECT_ROOT)
    )
    if "nothing to commit" in result.stdout:
        print("[Git] Нет изменений для коммита.")
        return True
    if result.returncode != 0:
        print(f"[Git ERROR] commit: {result.stderr}")
        return False
    print(f"[Git] Commit: {commit_message}")

    # git push
    result = subprocess.run(
        ["git", "push"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(_PROJECT_ROOT)
    )
    if result.returncode != 0:
        print(f"[Git ERROR] push: {result.stderr}")
        return False
    print("[Git] Push: OK")
    daily_log("memory_sync", "Git push", f"Commit: {commit_message}")
    return True

def setup_git_repo(github_url: str) -> bool:
    """
    Инициализирует git репозиторий и настраивает remote.
    Вызывать один раз при первоначальной настройке.
    """
    if not check_git_available():
        print("[ERROR] Установите Git: https://git-scm.com/download/win")
        return False

    cmds = [
        ["git", "init"],
        ["git", "branch", "-M", "main"],
        ["git", "remote", "add", "origin", github_url],
    ]

    # Создаём .gitignore если нет
    gitignore = _PROJECT_ROOT / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text(
            "service_account.json\n"
            "gen-lang-client-*.json\n"
            "base64_key.txt\n"
            ".env\n"
            "__pycache__/\n"
            "*.pyc\n"
            "*.tmp\n"
            ".DS_Store\n",
            encoding="utf-8"
        )
        print("[Git] .gitignore создан")

    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(_PROJECT_ROOT))
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"[Git WARN] {' '.join(cmd)}: {result.stderr.strip()}")

    print(f"[Git] Репозиторий инициализирован: {github_url}")
    print("[Git] Теперь запустите: python tools/memory_sync.py --git")
    return True

# ── Статус ──────────────────────────────────────────────────────────────────

def show_status():
    """Показывает что будет синхронизировано без фактического копирования."""
    print("\n=== СТАТУС СИНХРОНИЗАЦИИ ===\n")
    mem = read_memory()
    print(f"  Проект: {mem.get('project', {}).get('name', '?')}")
    print(f"  Последнее обновление: {mem.get('project', {}).get('last_updated', '?')}")
    print(f"  Выполнено задач: {len(mem.get('completed_tasks', []))}")
    print(f"  Ожидают выполнения: {len(mem.get('pending_tasks', []))}")

    print(f"\n  Google Drive: {'ДОСТУПЕН' if DRIVE_ROOT.exists() else 'НЕДОСТУПЕН'} ({DRIVE_ROOT})")
    print(f"  Git:          {'УСТАНОВЛЕН' if check_git_available() else 'НЕ УСТАНОВЛЕН'}")

    print("\n  Папки для синхронизации:")
    for local, drive in SYNC_MAP.items():
        src = _PROJECT_ROOT / local
        exists = "[OK]" if src.exists() else "[--]"
        count = sum(1 for _ in src.rglob("*") if _.is_file()) if src.exists() else 0
        print(f"    {exists} {local:30} ({count} файлов) -> Drive/{drive}")

    print()
    sync_all_to_drive(dry_run=True)

# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Memory Sync — Zero API Workspace Engine")
    parser.add_argument("--git",    action="store_true", help="Sync + git commit + push")
    parser.add_argument("--status", action="store_true", help="Показать статус без копирования")
    parser.add_argument("--setup-git", metavar="URL",    help="Инициализировать git с указанным GitHub URL")
    parser.add_argument("--message", "-m", default=None, help="Кастомное сообщение для git commit")
    args = parser.parse_args()

    if args.setup_git:
        setup_git_repo(args.setup_git)
    elif args.status:
        show_status()
    elif args.git:
        print("=== ПОЛНАЯ СИНХРОНИЗАЦИЯ: Drive + Git ===\n")
        sync_all_to_drive()
        git_sync(commit_message=args.message)
    else:
        print("=== СИНХРОНИЗАЦИЯ НА GOOGLE DRIVE ===\n")
        sync_all_to_drive()
