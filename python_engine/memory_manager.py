"""
============================================================================
MEMORY MANAGER — Zero API Workspace Engine
Общая память для всех агентов Antigravity Swarm.

Правила:
  - read_memory()       → доступно всем агентам
  - is_task_done()      → доступно всем агентам (идемпотентная проверка)
  - update_memory()     → ТОЛЬКО Agent 5 (Spark)
  - write_agent_output()→ агенты 1-4 пишут только в свой output-файл
  - daily_log()         → доступно всем агентам (append-only)
============================================================================
"""

import json
import os
import sys
import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Пути ──────────────────────────────────────────────────────────────────
_ROOT = Path(__file__).parent.parent          # c:\Users\user\ГУГЛ ИМПЕРИЯ\
_MEMORY_DIR = _ROOT / "_MEMORY"
_MEMORY_FILE = _MEMORY_DIR / "MEMORY.json"
_TASK_REGISTRY = _MEMORY_DIR / "TASK_REGISTRY.json"
_ERRORS_FILE = _MEMORY_DIR / "ERRORS.md"
_DAILY_LOG_DIR = _MEMORY_DIR / "DAILY_LOG"

# ── Утилиты ───────────────────────────────────────────────────────────────
_lock = threading.Lock()

def _now_iso() -> str:
    tz = timezone(timedelta(hours=3))  # UTC+3 Одесса
    return datetime.now(tz).isoformat()

def _today_str() -> str:
    tz = timezone(timedelta(hours=3))
    return datetime.now(tz).strftime("%Y-%m-%d")

def _load_json(path: Path) -> Dict:
    """Безопасное чтение JSON файла."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_json(path: Path, data: Dict, indent: int = 2) -> None:
    """Атомарная запись JSON (write-to-temp, rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    tmp.replace(path)  # атомарная замена на Windows

# ── Публичный API ──────────────────────────────────────────────────────────

def read_memory() -> Dict[str, Any]:
    """
    Читает полное состояние проекта из MEMORY.json.
    Доступно всем агентам.
    
    Returns:
        dict: Полное состояние проекта
    
    Example:
        mem = read_memory()
        print(mem["current_phase"]["next_step"])
    """
    return _load_json(_MEMORY_FILE)


def get_next_step() -> str:
    """Возвращает текущий следующий шаг проекта."""
    mem = read_memory()
    return mem.get("current_phase", {}).get("next_step", "Проверь MEMORY.json — next_step не задан")


def get_pending_tasks() -> List[str]:
    """Возвращает список незавершённых задач."""
    mem = read_memory()
    return mem.get("pending_tasks", [])


def is_task_done(task_id: str) -> bool:
    """
    Проверяет, выполнена ли задача. Идемпотентная защита.
    Агент ОБЯЗАН вызвать это перед выполнением любой задачи.
    
    Args:
        task_id: ID задачи из TASK_REGISTRY.json
    
    Returns:
        True если задача уже выполнена (не выполнять повторно!)
    
    Example:
        if is_task_done("scrape_leads_2026-09-02"):
            print("Уже выполнено, пропускаем")
            return
    """
    registry = _load_json(_TASK_REGISTRY)
    task = registry.get("tasks", {}).get(task_id, {})
    return task.get("status") == "done"


def write_agent_output(agent_id: str, output: Dict[str, Any]) -> None:
    """
    Агенты 1-4 пишут свои результаты в отдельный файл.
    НЕ обновляет MEMORY.json напрямую — это делает только Agent 5.
    
    Args:
        agent_id: Например "agent_1_lead"
        output:   Результаты работы агента
    
    Example:
        write_agent_output("agent_1_lead", {
            "leads_count": 15,
            "top_lead": {"name": "...", "score": 9}
        })
    """
    output_file = _MEMORY_DIR / f"{agent_id}_output.json"
    payload = {
        "agent_id": agent_id,
        "timestamp": _now_iso(),
        "output": output
    }
    with _lock:
        _save_json(output_file, payload)


def update_memory(updates: Dict[str, Any], updated_by: str = "agent_5_spark") -> None:
    """
    Обновляет MEMORY.json. ТОЛЬКО для Agent 5 (Spark).
    Агенты 1-4 используют write_agent_output() вместо этого.
    
    Args:
        updates:    Словарь с ключами для обновления (deep merge)
        updated_by: ID агента, делающего обновление
    
    Example:
        update_memory({
            "current_phase": {"next_step": "Запустить agent_3_smm"},
            "agent_last_run": {"agent_1_lead": "2026-09-02T10:00:00+03:00"}
        }, updated_by="agent_5_spark")
    """
    with _lock:
        mem = _load_json(_MEMORY_FILE)
        _deep_merge(mem, updates)
        mem["project"]["last_updated"] = _now_iso()
        mem["project"]["last_updated_by"] = updated_by
        _save_json(_MEMORY_FILE, mem)


def mark_task_done(task_id: str, completed_by: str, output: str) -> None:
    """
    Отмечает задачу как выполненную в TASK_REGISTRY.json.
    ТОЛЬКО для Agent 5 (Spark).
    
    Args:
        task_id:      ID задачи
        completed_by: Кто выполнил
        output:       Краткое описание результата
    """
    with _lock:
        registry = _load_json(_TASK_REGISTRY)
        if "tasks" not in registry:
            registry["tasks"] = {}
        registry["tasks"][task_id] = {
            "status": "done",
            "completed_at": _now_iso(),
            "completed_by": completed_by,
            "output": output
        }
        # Также убрать из pending в MEMORY.json
        mem = _load_json(_MEMORY_FILE)
        pending = mem.get("pending_tasks", [])
        if task_id in pending:
            pending.remove(task_id)
        completed = mem.get("completed_tasks", [])
        if task_id not in completed:
            completed.append(task_id)
        mem["pending_tasks"] = pending
        mem["completed_tasks"] = completed
        _save_json(_TASK_REGISTRY, registry)
        _save_json(_MEMORY_FILE, mem)


def daily_log(agent_id: str, action: str, result: str, level: str = "INFO") -> None:
    """
    Добавляет строку в ежедневный журнал. Append-only.
    Доступно всем агентам.
    
    Args:
        agent_id: "agent_1_lead", "agent_2_spy", "drive_converter", etc.
        action:   Что сделал агент
        result:   Результат действия
        level:    "INFO" | "WARNING" | "ERROR"
    
    Example:
        daily_log("agent_1_lead", "Scraping B2B contacts", "15 лидов найдено, score avg 7.2")
    """
    _DAILY_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = _DAILY_LOG_DIR / f"{_today_str()}.md"
    timestamp = datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M:%S")
    icon = {"INFO": "✓", "WARNING": "⚠", "ERROR": "✗"}.get(level, "•")
    line = f"| {timestamp} | {agent_id} | {action} | {icon} {result} |\n"

    if not log_file.exists():
        header = (
            f"# Daily Log — {_today_str()}\n\n"
            f"## Действия агентов\n\n"
            f"| Время | Агент | Действие | Результат |\n"
            f"|---|---|---|---|\n"
        )
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(header)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


def log_error(agent_id: str, error: str, resolution: str = "pending") -> None:
    """
    Фиксирует ошибку в ERRORS.md.
    Доступно всем агентам.
    """
    entry = (
        f"\n## {level_prefix(resolution)}: {error[:60]}...\n"
        f"- **Дата:** {_today_str()}\n"
        f"- **Агент:** {agent_id}\n"
        f"- **Ошибка:** {error}\n"
        f"- **Решение:** {resolution}\n"
        f"- **Статус:** {'resolved' if resolution != 'pending' else 'open'}\n"
        "---\n"
    )
    with open(_ERRORS_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    daily_log(agent_id, f"ERROR: {error[:50]}", resolution, level="ERROR")


def get_project_snapshot() -> str:
    """
    Возвращает краткий текстовый снимок состояния проекта.
    Используй это для быстрого понимания контекста в начале сессии.
    
    Returns:
        Многострочная строка с состоянием проекта
    """
    mem = read_memory()
    project = mem.get("project", {})
    phase = mem.get("current_phase", {})
    pending = mem.get("pending_tasks", [])
    completed = mem.get("completed_tasks", [])
    agent_runs = mem.get("agent_last_run", {})

    lines = [
        "=" * 60,
        f"  ПРОЕКТ: {project.get('name', 'Unknown')} v{project.get('version', '?')}",
        f"  Обновлён: {project.get('last_updated', '?')} ({project.get('last_updated_by', '?')})",
        "=" * 60,
        f"  Текущая фаза: {phase.get('description', '?')}",
        f"  Следующий шаг: {phase.get('next_step', '?')}",
        "-" * 60,
        f"  Выполнено задач: {len(completed)}",
        f"  Ожидают выполнения: {len(pending)}",
    ]
    if pending:
        lines.append("  Pending:")
        for t in pending[:5]:
            lines.append(f"    - {t}")
    lines.append("-" * 60)
    lines.append("  Последний запуск агентов:")
    for agent, ts in agent_runs.items():
        lines.append(f"    {agent}: {ts or 'Никогда'}")
    lines.append("=" * 60)
    return "\n".join(lines)


# ── Утилиты ────────────────────────────────────────────────────────────────

def level_prefix(resolution: str) -> str:
    return "OPEN" if resolution == "pending" else "RESOLVED"

def _deep_merge(base: Dict, updates: Dict) -> Dict:
    """Рекурсивный deep merge словарей."""
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


# ── Quick-start для агентов ────────────────────────────────────────────────

def agent_startup_check(agent_id: str, task_id: str) -> bool:
    """
    Стандартный старт любого агента.
    1. Печатает снимок проекта
    2. Проверяет, нужно ли вообще запускаться (идемпотентность)
    
    Returns:
        True  → задача нужна, продолжай
        False → задача уже выполнена, пропусти
    
    Example:
        if not agent_startup_check("agent_1_lead", "scrape_leads_2026-09-02"):
            return {"status": "skipped", "reason": "already_done"}
    """
    print(get_project_snapshot())
    if is_task_done(task_id):
        print(f"[{agent_id}] Задача '{task_id}' уже выполнена. Пропускаю.")
        daily_log(agent_id, f"Startup check: task {task_id}", "Skipped (already done)", level="INFO")
        return False
    daily_log(agent_id, f"Startup: running task {task_id}", "Starting...", level="INFO")
    return True


if __name__ == "__main__":
    # Быстрая проверка: python memory_manager.py
    print(get_project_snapshot())
    print("\n[TEST] is_task_done('deploy_drive_markdown_converter'):", is_task_done("deploy_drive_markdown_converter"))
    print("[TEST] is_task_done('nonexistent_task'):", is_task_done("nonexistent_task"))
