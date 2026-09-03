"""
Одноразовый скрипт инициализации Git-репозитория.
Запускать только один раз после установки Git.
"""
import subprocess
import sys
import os
from pathlib import Path

PROJECT = Path(r"c:\Users\user\ГУГЛ ИМПЕРИЯ")
GITHUB_URL = "https://github.com/teleportviktor-debug/Rozario_Backup.git"

# Ищем git в стандартных местах
GIT_PATHS = [
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Users\user\AppData\Local\Programs\Git\bin\git.exe",
]

git = None
for p in GIT_PATHS:
    if os.path.exists(p):
        git = p
        break

if not git:
    # Попробуем из PATH
    try:
        result = subprocess.run(["git", "--version"], capture_output=True)
        if result.returncode == 0:
            git = "git"
    except FileNotFoundError:
        pass

if not git:
    print("[ERROR] Git не найден. Установите Git и запустите снова.")
    sys.exit(1)

print(f"[OK] Git найден: {git}")

def run(cmd, **kwargs):
    if isinstance(cmd, list) and cmd[0] == "git":
        cmd[0] = git
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", 
                           cwd=str(PROJECT), **kwargs)
    out = (result.stdout + result.stderr).strip()
    if out:
        print(f"  > {out}")
    return result.returncode

print("\n[1/7] Версия Git:")
run([git, "--version"])

print("\n[2/7] Инициализация репозитория...")
run([git, "init"])
run([git, "branch", "-M", "main"])

print("\n[3/7] Настройка user...")
run([git, "config", "user.name", "Razum AI — Antigravity Bot"])
run([git, "config", "user.email", "teleportviktor-debug@users.noreply.github.com"])

print("\n[4/7] Подключение remote...")
run([git, "remote", "remove", "origin"])
run([git, "remote", "add", "origin", GITHUB_URL])
print(f"  Remote: {GITHUB_URL}")

print("\n[5/7] Добавление файлов (секреты исключены через .gitignore)...")
# Добавляем всё — .gitignore защищает секреты
run([git, "add", "."])

# Явно убеждаемся что секреты не добавлены
secrets = [
    "service_account.json",
    "drive_markdown_converter/service_account.json",
    "drive_markdown_converter/gen-lang-client-0207478259-8dcd87214378.json",
    "drive_markdown_converter/base64_key.txt",
    "base64_key.txt",
]
for s in secrets:
    run([git, "reset", "HEAD", "--", s])
    print(f"  Исключён из stage: {s}")

# Показываем что будет в коммите
print("\n[6/7] Файлы в коммите:")
run([git, "diff", "--staged", "--name-only"])

print("\n[7/7] Первый коммит и push...")
rc = run([git, "commit", "-m", 
          "init: Zero API Workspace Engine v2.4.0\n\n"
          "- _MEMORY/ shared memory system for all agents\n"
          "- memory_manager.py with read/write/idempotency guards\n"
          "- drive_markdown_converter/ with 24/7 daemon\n"
          "- 5 Antigravity agents + Spark orchestrator\n"
          "- tools/memory_sync.py (Drive + Git sync)\n"
          "- 10_PRODUCTION/ client delivery templates\n"
          "- GitHub Actions: swarm_cron + daily_memory_sync"])

if rc == 0:
    print("\n  Push на GitHub (может открыться браузер для авторизации)...")
    rc2 = run([git, "push", "-u", "origin", "main"])
    if rc2 == 0:
        print("\n[SUCCESS] Репозиторий настроен!")
        print(f"  URL: https://github.com/teleportviktor-debug/Rozario_Backup")
    else:
        print("\n[WARN] Push не удался. Попробуй:")
        print(f"  1. Открой: {GITHUB_URL.replace('.git', '')}")
        print("  2. Убедись что репозиторий существует и у тебя есть доступ")
        print("  3. Войди в GitHub в браузере")
        print(f"  4. Запусти вручную: git push -u origin main")
else:
    print("[WARN] Нечего коммитить или ошибка.")

print("\nГотово.")
