"""
============================================================================
RAZUM GOOGLE AI PRO • ANTIGRAVITY SWARM ORCHESTRATOR (v2026.4.1)
Coordinates & Dispatches Execution of 5 Decentralized Autonomous Agents
Deployment: cloud_github_actions_cron | Auto-Heal: True

Shared Memory: _MEMORY/MEMORY.json (SSoT)
  - Каждый агент читает состояние перед запуском
  - Агенты 1-4 пишут в _MEMORY/agentN_output.json
  - Agent 5 (Spark) консолидирует всё в MEMORY.json
============================================================================
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Memory Manager — общая память всех агентов
from python_engine.memory_manager import (
    read_memory, get_project_snapshot, is_task_done,
    write_agent_output, update_memory, mark_task_done, daily_log
)

# Agent Engine Imports
from python_engine.agents.agent_1_lead import run_lead_scraper
from python_engine.agents.agent_2_spy import run_spy_agent
from python_engine.agents.agent_google_radar import analyze_google_ecosystem
from python_engine.agents.agent_3_smm import run_smm_agent
from python_engine.agents.agent_4_video import run_video_agent
from python_engine.agents.agent_5_spark import run_spark_watchdog

def _now_iso() -> str:
    tz = timezone(timedelta(hours=3))
    return datetime.now(tz).isoformat()

def execute_antigravity_swarm(agent_filter=None, sync_drive=True):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ── 1. Читаем текущее состояние проекта ───────────────────────────────
    print(get_project_snapshot())
    print("=" * 75)
    print("  ANTIGRAVITY SWARM INIT - RAZUM GOOGLE AI PRO")
    print(f"  Deployment: Cloud GitHub Actions Cron | Auto-Heal: Active")
    print(f"  Timestamp: {_now_iso()}")
    print("=" * 75)

    results = {}
    daily_log("swarm_orchestrator", "Swarm cycle started", f"agent_filter={agent_filter or 'all'}")

    # ── 2. Agent 1: Lead Scraper & Hormozi Valuator [cron(0 */4 * * *)] ──
    if not agent_filter or agent_filter in ["1", "agent_1_lead", "agent_1_lead_scout"]:
        task_id = f"agent_1_lead_{_now_iso()[:10]}"
        if not is_task_done(task_id):
            print("\n[1/5] [agent_1_lead] Scraping B2B contacts & applying Hormozi scoring...")
            try:
                res1 = run_lead_scraper()
                write_agent_output("agent_1_lead", res1)
                update_memory({"agent_last_run": {"agent_1_lead": _now_iso()}})
                daily_log("agent_1_lead", "Scraping & Hormozi scoring", f"Leads: {res1.get('leads_count', 0)}")
                print(f"  [OK] Leads: {res1.get('leads_count', 0)} -> 03_CRM/Sheets")
                results["agent_1_lead"] = res1
            except Exception as e:
                print(f"  [ERROR] agent_1_lead: {e}")
                daily_log("agent_1_lead", "Scraping failed", str(e), level="ERROR")
        else:
            print(f"  [SKIP] agent_1_lead: задача {task_id} уже выполнена сегодня")

    # ── 3. Agent 2: Competitor Spy & Google AI Radar [cron(0 10 * * *)] ──
    if not agent_filter or agent_filter in ["2", "agent_2_spy", "agent_google_radar"]:
        print("\n[2/5] [agent_2_spy] Competitor Spy & Google AI Radar (Julian Goldie)...")
        try:
            res2 = run_spy_agent()
            radar_res = analyze_google_ecosystem()
            res2["google_radar"] = radar_res
            write_agent_output("agent_2_spy", res2)
            update_memory({"agent_last_run": {"agent_2_spy": _now_iso()}})
            daily_log("agent_2_spy", "Competitor & Google Radar analysis", f"Competitors: {res2.get('competitors_analyzed', 0)}, Google Tools: {radar_res.get('tools_analyzed', 0)}")
            print(f"  [OK] Competitors: {res2.get('competitors_analyzed', 0)} -> 04_Playbook/")
            print(f"  [OK] Google AI Radar: {radar_res.get('tools_analyzed', 0)} tools analyzed -> 04_Playbook/GOOGLE_AI_ECOSYSTEM_RADAR.md")
            results["agent_2_spy"] = res2
        except Exception as e:
            print(f"  [ERROR] agent_2_spy: {e}")
            daily_log("agent_2_spy", "Spy analysis failed", str(e), level="ERROR")

    # ── 4. Agent 3: Neuro-SMM Post Generator [cron(0 9,15,19 * * *)] ────
    if not agent_filter or agent_filter in ["3", "agent_3_smm"]:
        print("\n[3/5] [agent_3_smm] Generating daily posts (Obsidian/Cyan aesthetic)...")
        try:
            res3 = run_smm_agent()
            write_agent_output("agent_3_smm", res3)
            update_memory({"agent_last_run": {"agent_3_smm": _now_iso()}})
            daily_log("agent_3_smm", "SMM post generation", f"Posts: {res3.get('posts_generated', 0)}")
            print(f"  [OK] Posts: {res3.get('posts_generated', 0)} -> 05_Content/Posts/")
            results["agent_3_smm"] = res3
        except Exception as e:
            print(f"  [ERROR] agent_3_smm: {e}")
            daily_log("agent_3_smm", "SMM generation failed", str(e), level="ERROR")

    # ── 5. Agent 4: 15s Shorts & MoviePy [cron(0 12 * * *)] ─────────────
    if not agent_filter or agent_filter in ["4", "agent_4_video", "agent_4_shorts"]:
        print("\n[4/5] [agent_4_video] Scripting 15s Shorts & MoviePy render commands...")
        try:
            res4 = run_video_agent()
            write_agent_output("agent_4_video", res4)
            update_memory({"agent_last_run": {"agent_4_shorts": _now_iso()}})
            daily_log("agent_4_video", "Shorts scripting", f"Videos ready: {res4.get('videos_ready', 0)}")
            print(f"  [OK] Videos: {res4.get('videos_ready', 0)} -> 05_Content/Video/")
            results["agent_4_video"] = res4
        except Exception as e:
            print(f"  [ERROR] agent_4_video: {e}")
            daily_log("agent_4_video", "Video scripting failed", str(e), level="ERROR")

    # ── 6. Agent 5: Spark Watchdog — консолидирует MEMORY.json ───────────
    print("\n[5/5] [agent_5_spark] Watchdog + MEMORY.json consolidation...")
    try:
        res5 = run_spark_watchdog()
        # Spark — единственный агент с правом обновления MEMORY.json
        update_memory({
            "agent_last_run": {"agent_5_spark": _now_iso()},
            "current_phase": {"next_step": res5.get("recommended_next_step", "Проверь DAILY_LOG")}
        }, updated_by="agent_5_spark")
        daily_log("agent_5_spark", "Watchdog cycle complete", f"A2UI: {res5.get('email_widget', 'none')}")
        print(f"  [OK] Watchdog OK | Email Widget: {res5.get('email_widget', 'none')}")
        results["agent_5_spark"] = res5
    except Exception as e:
        print(f"  [ERROR] agent_5_spark: {e}")
        daily_log("agent_5_spark", "Watchdog failed", str(e), level="ERROR")

    # ── 7. Sync _MEMORY/ to Drive ─────────────────────────────────────────
    if sync_drive:
        g_drive_dir = r"g:\Мой диск\AI_WORK_SYSTEM"
        if os.path.exists(g_drive_dir):
            try:
                sync_swarm_to_drive(root_dir, g_drive_dir)
                daily_log("swarm_orchestrator", "Drive sync", "OK: _MEMORY/ + outputs synced")
                print(f"\n[Drive Sync] _MEMORY/ mirrored to: {g_drive_dir}")
            except Exception as e:
                print(f"\n[Drive Sync] Warning: {e}")

    print("\n" + "="*75)
    print("🎉 ALL 5 ANTIGRAVITY SWARM AGENTS SYNCHRONIZED & READY FOR CLOUD CRON")
    print("="*75)
    # Provide compatibility aliases in return dictionary
    if "agent_1_lead" in results:
        results["agent_1_lead_scout"] = results["agent_1_lead"]
    if "agent_4_video" in results:
        results["agent_4_shorts"] = results["agent_4_video"]
    if "agent_5_spark" in results:
        results["agent_5_spark_coordinator"] = results["agent_5_spark"]

    return results

# Aliases for backward compatibility
execute_swarm = execute_antigravity_swarm

def sync_swarm_to_drive(src_root, dst_root):
    """
    Зеркалирует ключевые папки проекта на Google Drive.
    Включает _MEMORY/ (общая память) и 10_PRODUCTION/ (клиентские пакеты).
    """
    import shutil

    # Sync config files
    for cfg in ["antigravity_swarm_init.json", "swarm_config.json"]:
        sp = os.path.join(src_root, cfg)
        dp = os.path.join(dst_root, cfg)
        if os.path.exists(sp):
            shutil.copy2(sp, dp)

    # Output mappings (локальная папка → папка на Drive)
    folders_to_sync = [
        ("_MEMORY", "_MEMORY"),                         # Общая память агентов
        ("10_PRODUCTION", "10_PRODUCTION"),             # Клиентские пакеты
        ("03_CRM_LEADS", "03_CRM"),                     # CRM лиды
        ("04_SALES_PLAYBOOK", "04_Playbook"),           # Конкурентная разведка
        ("05_CONTENT_PRODUCTION", "05_Content"),        # Контент
        ("08_A2UI_SCHEMAS", "08_A2UI_SCHEMAS"),         # A2UI схемы
    ]

    for src_f, dst_f in folders_to_sync:
        s = os.path.join(src_root, src_f)
        d = os.path.join(dst_root, dst_f)
        if os.path.exists(s):
            os.makedirs(d, exist_ok=True)
            for item in os.listdir(s):
                s_item = os.path.join(s, item)
                d_item = os.path.join(d, item)
                if os.path.isfile(s_item):
                    shutil.copy2(s_item, d_item)
                elif os.path.isdir(s_item):
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Swarm Orchestrator")
    parser.add_argument("--agent", type=str, help="Specific agent ID (1-5, agent_1_lead, etc.)")
    parser.add_argument("--no-drive-sync", action="store_true", help="Skip Drive sync")
    parser.add_argument("--memory", action="store_true", help="Show project memory snapshot and exit")
    args = parser.parse_args()

    if args.memory:
        print(get_project_snapshot())
    else:
        execute_antigravity_swarm(
            agent_filter=args.agent,
            sync_drive=not args.no_drive_sync
        )

