"""
============================================================================
RAZUM INTELLIGENT AI 2026 • MASTER CONTROL CLI & SWARM DISPATCHER
Unified command center for Swarm Agents, Teleprompter, CRM & CI/CD
============================================================================
"""

import os
import sys
import subprocess
import webbrowser

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║              ⚡ RAZUM GOOGLE AI PRO • MASTER SWARM HUB 2026             ║
║            Autonomous Multi-Agent System & Production Orchestrator       ║
╚══════════════════════════════════════════════════════════════════════════╝
""")

def main_menu():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        print_banner()
        print(" [1] 🤖 Запустить Рой Агентов (Full Swarm Batch: Agents 1-5)")
        print(" [2] 🎯 Запустить Agent 1: Lead Scout & Hormozi PPDU Scoring")
        print(" [3] 🕵️ Запустить Agent 2: Market Spy & Source Mixing Battlecards")
        print(" [4] 📱 Запустить Agent 3: Neuro-SMM Daily Publisher (09:00, 15:00, 19:00)")
        print(" [5] 🎬 Запустить Agent 4: 15s Shorts Video Scripting & FFmpeg Manifest")
        print(" [6] ⚡ Запустить Agent 5: Spark Coordinator & A2UI Health Check")
        print(" [7] 🎙️ Открыть Веб-Студию Телесуфлера (Teleprompter Studio)")
        print(" [8] 🌐 Открыть Главный Сайт (Live GitHub Pages / Local Index)")
        print(" [9] 🔍 Запустить Полный Системный Тест (run_full_system_check.py)")
        print(" [10] 📦 Собрать Клиентский Пакет Внедрения (10_PRODUCTION ZIP)")
        print(" [11] 📱 Telegram CRM & Тест Обработки Лида (telegram_crm_bot.py)")
        print(" [12] 💾 Создать Полный Резервный Снапшот Системы (ZIP Backup)")
        print(" [13] 📊 Синхронизировать Лиды в Google Sheets (03_CRM CSV)")
        print(" [14] 📄 Сгенерировать Коммерческое Предложение (КП HTML)")
        print(" [15] 🌐 Собрать Пакет для GitHub Pages (GITHUB_PAGES_DEPLOY.zip)")
        print(" [16] 🎬 Открыть Видео-Студию Shorts & Reels (video_studio.html)")
        print(" [0] ❌ Выход")
        print("═"*74)

        choice = input("Выберите действие (0-16): ").strip()

        if choice == "1":
            from python_engine.swarm_orchestrator import execute_swarm
            execute_swarm()
            input("\nНажмите Enter для продолжения...")

        elif choice == "2":
            from python_engine.agents.agent_1_lead_scout import run_lead_scout
            res = run_lead_scout()
            print(f"\n✓ Agent 1 завершил работу: {res['leads_processed']} лидов обработано.")
            input("\nНажмите Enter для продолжения...")

        elif choice == "3":
            from python_engine.agents.agent_2_spy import run_spy_agent
            res = run_spy_agent()
            print(f"\n✓ Agent 2 завершил работу: {res['competitors_analyzed']} конкурентов проанализировано.")
            input("\nНажмите Enter для продолжения...")

        elif choice == "4":
            from python_engine.agents.agent_3_smm import run_smm_agent
            res = run_smm_agent()
            print(f"\n✓ Agent 3 завершил работу: {res['posts_generated']} постов сгенерировано.")
            input("\nНажмите Enter для продолжения...")

        elif choice == "5":
            from python_engine.agents.agent_4_shorts import run_shorts_agent
            res = run_shorts_agent()
            print(f"\n✓ Agent 4 завершил работу: {res['shorts_created']} сценариев 15s Shorts создано.")
            input("\nНажмите Enter для продолжения...")

        elif choice == "6":
            from python_engine.agents.agent_5_spark_coordinator import run_coordinator_agent
            res = run_coordinator_agent()
            print(f"\n✓ Agent 5 завершил работу: A2UI виджеты обновлены ({res['schema_path']}).")
            input("\nНажмите Enter для продолжения...")

        elif choice == "7":
            tele_path = os.path.join(root_dir, "teleprompter_studio.html")
            print(f"Открытие телесуфлера: {tele_path}")
            webbrowser.open(f"file:///{tele_path.replace(os.sep, '/')}")

        elif choice == "8":
            index_path = os.path.join(root_dir, "index.html")
            print("Открытие сайта...")
            webbrowser.open(f"file:///{index_path.replace(os.sep, '/')}")

        elif choice == "9":
            import run_full_system_check
            run_full_system_check.run_tests()
            input("\nНажмите Enter для продолжения...")

        elif choice == "10":
            from python_engine.client_packager import interactive_cli
            interactive_cli()
            input("\nНажмите Enter для продолжения...")

        elif choice == "11":
            from python_engine.telegram_crm_bot import run_test_lead_dispatch
            run_test_lead_dispatch()
            input("\nНажмите Enter для продолжения...")

        elif choice == "12":
            from tools.backup_restore import create_system_snapshot
            create_system_snapshot()
            input("\nНажмите Enter для продолжения...")

        elif choice == "13":
            from python_engine.sheets_crm_sync import sync_leads_to_sheets
            sync_leads_to_sheets()
            input("\nНажмите Enter для продолжения...")

        elif choice == "14":
            from python_engine.proposal_generator import generate_proposal_html
            c_name = input("Введите имя клиента / компании: ").strip() or "ООО Новый Клиент"
            c_niche = input("Введите нишу бизнеса: ").strip() or "B2B Услуги"
            print("Выберите тариф: 1=Spark($50), 2=Command($100), 3=Intelligence($200), 4=Sovereign($300), 5=Genesis($500)")
            p_opt = input("Номер тарифа (1-5): ").strip()
            p_map = {"1": "pkg-starter", "2": "pkg-command", "3": "pkg-intelligence", "4": "pkg-sovereign", "5": "pkg-genesis"}
            p_id = p_map.get(p_opt, "pkg-sovereign")
            res_path = generate_proposal_html(c_name, c_niche, p_id)
            webbrowser.open(f"file:///{res_path.replace(os.sep, '/')}")
            input("\nНажмите Enter для продолжения...")

        elif choice == "15":
            from tools.prepare_github_deploy import bundle_github_pages
            bundle_github_pages()
            input("\nНажмите Enter для продолжения...")

        elif choice == "16":
            video_path = os.path.join(root_dir, "video_studio.html")
            print(f"Открытие видео-студии Shorts: {video_path}")
            webbrowser.open(f"file:///{video_path.replace(os.sep, '/')}")
            input("\nНажмите Enter для продолжения...")

        elif choice == "0":
            print("Выход из системы Razum AI.")
            break
        else:
            print("Неверный выбор. Повторите ввод.")

if __name__ == "__main__":
    main_menu()
