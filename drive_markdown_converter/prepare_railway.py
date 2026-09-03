"""
============================================================================
1-CLICK RAILWAY DEPLOY PREPARER (prepare_railway.py)
Reads service_account.json, minifies it, and automatically copies to clipboard!
============================================================================
"""

import os
import sys
import json
import subprocess

def main():
    print("="*65)
    print("  🚀 RAZUM AI • 1-CLICK RAILWAY DEPLOY HELPER FOR WINDOWS")
    print("="*65)

    sa_file = "service_account.json"
    if not os.path.exists(sa_file):
        # Look in parent or prompt
        parent_sa = os.path.join("..", sa_file)
        if os.path.exists(parent_sa):
            sa_file = parent_sa
        else:
            print(f"\n⚠️ Файл '{sa_file}' не найден в текущей папке.")
            print("Положите ваш файл 'service_account.json' рядом с этим скриптом и запустите снова.")
            input("\nНажмите Enter для выхода...")
            return

    try:
        with open(sa_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Minify JSON to a clean single line
        minified_json = json.dumps(data, separators=(',', ':'))

        # Copy directly to Windows Clipboard via clip.exe or PowerShell
        copied = False
        try:
            process = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
            process.communicate(input=minified_json.encode('utf-8'))
            copied = True
        except Exception:
            try:
                cmd = f"Set-Clipboard -Value @'\n{minified_json}\n'@"
                subprocess.run(["powershell", "-Command", cmd], check=True)
                copied = True
            except Exception:
                pass

        print("\n" + "═"*65)
        if copied:
            print("  ✅ ВСЁ ГОТОВО! ЗНАЧЕНИЕ УСПЕШНО СКОПИРОВАНО В БУФЕР ОБМЕНА!")
        else:
            print("  ✅ ЗНАЧЕНИЕ СФОРМИРОВАНО:")
        print("═"*65)

        print("\n👉 ЧТО СДЕЛАТЬ В RAILWAY:")
        print(" 1. Откройте ваш сервис в Railway -> вкладка 'Variables'")
        print(" 2. Добавьте переменную:")
        print("    Имя переменной:   GCP_SERVICE_ACCOUNT_JSON")
        print("    Значение:         ПРОСТО НАЖМИТЕ Ctrl + V")
        print(" 3. Нажмите 'Add' (Добавить). Деплой начнется автоматически!\n")

        print("─"*65)
        print("Если буфер не сработал, вот готовая строка для копирования:")
        print(minified_json[:120] + "... [полная строка в буфере]")
        print("─"*65)

    except Exception as e:
        print(f"\n❌ Ошибка при чтении файла: {e}")

    input("\nНажмите Enter, чтобы закрыть окно...")

if __name__ == "__main__":
    main()
