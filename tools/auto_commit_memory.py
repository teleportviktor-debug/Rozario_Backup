import os
import subprocess
import time
import sys
from datetime import datetime

# Обеспечиваем корректный вывод UTF-8 в консоль Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_DIR = os.path.join(ROOT_DIR, "_MEMORY")

def run_git_command(command, cwd=ROOT_DIR):
    git_exe = r"C:\Program Files\Git\bin\git.exe"
    # Replace the generic "git" with the absolute path
    if command[0] == "git":
        command[0] = git_exe
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка Git: {e.stderr.strip()}")
        return None

def auto_commit_memory():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Запуск синхронизации _MEMORY/ с GitHub...")
    
    # Добавляем только папку _MEMORY
    run_git_command(["git", "add", "_MEMORY/"])
    
    # Проверяем есть ли изменения
    status = run_git_command(["git", "status", "--porcelain", "_MEMORY/"])
    if not status:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Нет новых изменений в _MEMORY/. Пропуск.")
        return

    # Коммитим
    commit_msg = f"Auto-sync memory state: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    run_git_command(["git", "commit", "-m", commit_msg])
    
    # Пушим в origin (предполагается, что ветка main или master)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Выполняется push в удаленный репозиторий...")
    push_result = run_git_command(["git", "push"])
    
    if push_result is not None:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Успешно синхронизировано!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--daemon", action="store_true", help="Запустить как фоновый процесс (каждые 30 мин)")
    args = parser.parse_args()

    if args.daemon:
        print("Запущен режим демона: авто-коммит каждые 30 минут.")
        while True:
            auto_commit_memory()
            time.sleep(30 * 60) # 30 минут
    else:
        auto_commit_memory()
