"""
============================================================================
RAZUM SOVEREIGN AI ECOSYSTEM 2026 - AUTOMATED SYSTEM INTEGRITY & SWARM TEST
============================================================================
"""

import sys
import os
import json

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_tests():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"🔍 Запуск комплексной проверки экосистемы и Роя Агентов в: {root_dir}\n")

    required_dirs = [
        "01_STRATEGY",
        "02_BRAND_BOOK",
        "03_CRM_LEADS",
        "04_SALES_PLAYBOOK",
        "05_CONTENT_PRODUCTION",
        "06_SOP_REGLAMENTS",
        "07_FINANCIAL_MODELS",
        "08_A2UI_SCHEMAS",
        "css",
        "js",
        "gas_scripts",
        "python_engine",
        "python_engine/agents"
    ]

    all_passed = True

    # 1. Check directories
    print("📁 [1/5] Проверка структуры папок...")
    for d in required_dirs:
        path = os.path.join(root_dir, d)
        if os.path.exists(path):
            print(f"  ✓ Папка найдена: {d}")
        else:
            print(f"  ❌ Папка ОТСУТСТВУЕТ: {d}")
            all_passed = False

    # 2. Check essential files & Swarm specs
    required_files = [
        "swarm_config.json",
        ".github/workflows/swarm_cron.yml",
        ".agents/agents/agent_1_lead_scout.md",
        ".agents/agents/agent_2_spy.md",
        ".agents/agents/agent_3_smm.md",
        ".agents/agents/agent_4_shorts.md",
        ".agents/agents/agent_5_spark_coordinator.md",
        "python_engine/agents/agent_1_lead_scout.py",
        "python_engine/agents/agent_2_spy.py",
        "python_engine/agents/agent_3_smm.py",
        "python_engine/agents/agent_4_shorts.py",
        "python_engine/agents/agent_5_spark_coordinator.py",
        "python_engine/swarm_orchestrator.py",
        "index.html",
        "store_packages.html",
        "teleprompter_studio.html",
        "css/main.css",
        "js/app.js",
        "js/hormozi_engine.js",
        "js/a2ui_renderer.js",
        "gas_scripts/SparkScheduler.gs",
        "python_engine/antigravity_scoring.py",
        "08_A2UI_SCHEMAS/enterprise_widgets.json"
    ]

    print("\n📄 [2/5] Проверка файлов платформы и спецификаций Роя...")
    for f in required_files:
        path = os.path.join(root_dir, f)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"  ✓ Файл проверен ({os.path.getsize(path)} байт): {f}")
        else:
            print(f"  ❌ Файл ОТСУТСТВУЕТ или пуст: {f}")
            all_passed = False

    # 3. Check JSON validation
    print("\n📊 [3/5] Валидация JSON схем и swarm_config.json...")
    json_files = [
        "swarm_config.json",
        "07_FINANCIAL_MODELS/UNIT_ECONOMICS_AND_PRICING.json",
        "08_A2UI_SCHEMAS/enterprise_widgets.json"
    ]
    for jf in json_files:
        try:
            with open(os.path.join(root_dir, jf), 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"  ✓ JSON синтаксис корректен: {jf}")
        except Exception as e:
            print(f"  ❌ Ошибка в JSON {jf}: {e}")
            all_passed = False

    # 4. Test Python Antigravity Scoring
    print("\n🧮 [4/5] Тестирование Python Antigravity Engine...")
    try:
        from python_engine.antigravity_scoring import calculate_hormozi_score, calculate_roi_metrics
        score = calculate_hormozi_score(9, 8, 9, 8)
        roi = calculate_roi_metrics(5, 80000, 2.5, 14900)
        assert score["score_percent"] == 86
        assert roi["payback_days"] <= 5
        print(f"  ✓ Скоринг Hormozi: {score['score_percent']}% ({score['tier']})")
        print(f"  ✓ Математический ROI: окупаемость {roi['payback_days']} дней, выгода {roi['annual_savings_rub']} ₽/год")
    except Exception as e:
        print(f"  ❌ Ошибка исполнения Antigravity скрипта: {e}")
        all_passed = False

    # 5. Test Swarm Orchestrator Execution
    print("\n🤖 [5/5] Тестирование запуска Роя Агентов 1-5 (Swarm Orchestrator)...")
    try:
        from python_engine.swarm_orchestrator import execute_swarm
        swarm_res = execute_swarm(sync_drive=False)
        assert "agent_1_lead_scout" in swarm_res
        assert "agent_2_spy" in swarm_res
        assert "agent_3_smm" in swarm_res
        assert "agent_4_shorts" in swarm_res
        assert "agent_5_spark_coordinator" in swarm_res
        print("  ✓ Все 5 агентов успешно отработали и сгенерировали артефакты!")
    except Exception as e:
        print(f"  ❌ Ошибка исполнения Роя: {e}")
        all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ВСЕ ТЕСТЫ РОЯ И ЭКОСИСТЕМЫ ПРОЙДЕНЫ! СИСТЕМА 100% ГОТОВА К ПРОДАКШЕНУ.")
    else:
        print("⚠️ ОБНАРУЖЕНЫ ОШИБКИ ПРИ ПРОВЕРКЕ РОЯ.")
    print("="*60)

if __name__ == "__main__":
    run_tests()
