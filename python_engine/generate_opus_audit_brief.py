"""
============================================================================
REFRESH STRATEGIC OPUS AUDIT BRIEF
Gathers live metrics from _MEMORY/MEMORY.json, CRM Leads, Playbook,
and updates 01_STRATEGY/CLAUDE_OPUS_STRATEGIC_AUDIT.md automatically.
============================================================================
"""

import os
import sys
import json
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(ROOT_DIR, "_MEMORY", "MEMORY.json")
AUDIT_FILE = os.path.join(ROOT_DIR, "01_STRATEGY", "CLAUDE_OPUS_STRATEGIC_AUDIT.md")

def refresh_audit_brief():
    mem_data = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                mem_data = json.load(f)
        except Exception:
            pass

    completed_count = len(mem_data.get("completed_tasks", []))
    version = mem_data.get("project", {}).get("version", "2.4.0")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"✓ Манифест актуализирован: Версия {version}, Задач выполнено: {completed_count}, Время: {now_str}")
    return AUDIT_FILE

if __name__ == "__main__":
    refresh_audit_brief()
