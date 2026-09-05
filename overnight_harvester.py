"""
Ночной циклический генератор задач «overnight_harvester.py»
Architecture "Genome" (Phase 1 / Data-First Harvest) - Razum Google AI PRO.

Автономный конвейер для непрерывного сбора и накопления пар
«быстрый черновик / глубокий ответ» в /registry/genome_vault/harvest.jsonl.

Использование:
    python overnight_harvester.py
    python overnight_harvester.py --delay 2.0 --max-iter 100
    python overnight_harvester.py --url http://localhost:8000/api/v1/a2ui/render --token ntn_local_harvest_key
"""

import os
import sys
import time
import json
import random
import signal
import asyncio
import argparse
import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Prompts & Context Matrix for Realistic Enterprise Generation
PROMPT_CATALOG = [
    {
        "category": "LEAD_DOSSIER",
        "templates": [
            "Сгенерируй карточку квалификации Enterprise-лида: {company}, бюджет ${budget}k ARR, приоритет {priority}",
            "Подготовь досье ключевого ЛПР: {role} в компании {company}, интерес: миграция в Google Workspace AI",
            "Карточка входящего лида с скорингом намерений {score}/100 для сектора {industry}"
        ],
        "widget_type": "a2ui_card"
    },
    {
        "category": "KPI_TELEMETRY",
        "templates": [
            "Дашборд метрик суверенного кластера: P99 латентность {latency}ms, пропускная способность {tps} req/sec",
            "KPI дашборд расхода токенов и оптимизации затрат: экономия {savings}% при точности 99.8%",
            "Операционный мониторинг узлов роутинга черновиков в регионе {region}"
        ],
        "widget_type": "a2ui_card"
    },
    {
        "category": "CALL_STATUS",
        "templates": [
            "Статус завершенной AI-сессии голосового звонка #{call_id}: сентимент {sentiment}, длительность {duration}",
            "Бриф телефонного интервью с клиентом {company}: подтверждена демонстрация архитектуры Геном",
            "Сводка звонка службы онбординга: квалифицирован тир VIP Sovereign"
        ],
        "widget_type": "a2ui_card"
    },
    {
        "category": "SECURITY_ZERO_TRUST",
        "templates": [
            "Критический алерт безопасности Zero Trust: перехвачен неавторизованный запрос с IP {ip}",
            "Инцидент безопасности: блокировка попытки подбора Internal Integration Token шлюза n8n",
            "Отчет карантина: изолирован подозрительный сеанс доступа к API Google Workspace"
        ],
        "widget_type": "a2ui_card"
    },
    {
        "category": "FINANCE_INVOICE",
        "templates": [
            "Счет-фактура #INV-{invoice_id} за лицензии A2UI CardService: сумма ${amount}, статус PAID",
            "Финансовая квитанция ежемесячной подписки Sovereign AI Engine для клиента {company}",
            "Отчет биллинга: распределение затрат между Fast Worker и Deep Reasoning Worker"
        ],
        "widget_type": "a2ui_card"
    },
    {
        "category": "GENOME_MUTATION",
        "templates": [
            "Реестр мутаций промпта #{mutation_id}: ускорение валидации схемы A2UI на {speedup}%",
            "Одобрена мутация системного промпта «Хирурга» с добавлением золотого акцента #d4af37",
            "Результаты эволюционного теста промпта на 10 эталонных бенчмарках v0"
        ],
        "widget_type": "a2ui_card"
    }
]

COMPANIES = ["FinTech Global", "Nordic Energy", "CyberCorp Ltd", "OmniHealth", "Sovereign Bank", "Quantum Logistics"]
ROLES = ["CTO", "VP of Infrastructure", "Chief AI Architect", "Head of Security", "DevOps Director"]
PRIORITIES = ["CRITICAL_P1", "HIGH_ARR", "STRATEGIC_TIER_1", "ENTERPRISE_VIP"]
REGIONS = ["europe-west1", "europe-north1", "us-central1", "asia-east1"]
SENTIMENTS = ["HIGHLY_POSITIVE (0.96)", "POSITIVE (0.88)", "CONSTRUCTIVE (0.82)"]


def generate_random_task() -> Dict[str, Any]:
    """Generates synthetic enterprise prompt with dynamic metadata."""
    category_data = random.choice(PROMPT_CATALOG)
    template = random.choice(category_data["templates"])

    prompt = template.format(
        company=random.choice(COMPANIES),
        role=random.choice(ROLES),
        budget=random.randint(75, 450),
        priority=random.choice(PRIORITIES),
        score=round(random.uniform(88.0, 99.8), 1),
        industry=random.choice(["Fintech", "Telecom", "HealthTech", "Retail AI"]),
        latency=random.randint(18, 48),
        tps=random.randint(850, 4200),
        savings=round(random.uniform(32.0, 68.0), 1),
        region=random.choice(REGIONS),
        call_id=random.randint(1000, 9999),
        sentiment=random.choice(SENTIMENTS),
        duration=f"0{random.randint(2, 8)}:{random.randint(10, 59)}",
        ip=f"198.51.100.{random.randint(10, 240)}",
        invoice_id=f"2026-{random.randint(100, 999)}",
        amount=f"{random.randint(8, 65)},000.00",
        mutation_id=random.randint(200, 999),
        speedup=round(random.uniform(14.0, 38.0), 1)
    )

    user_context = {
        "category": category_data["category"],
        "client_timestamp": datetime.now(timezone.utc).isoformat(),
        "trace_id": f"trace_harvester_{random.randint(100000, 999999)}",
        "autonomous_worker": "overnight_harvester_v1"
    }

    return {
        "prompt": prompt,
        "user_context": user_context,
        "widget_type": category_data["widget_type"],
        "style_theme": random.choice(["OBSIDIAN_CYAN", "VER_SACRUM_GOLD"])
    }


def count_vault_records(vault_file: str) -> int:
    """Counts total harvested records in genome vault file."""
    if not os.path.exists(vault_file):
        return 0
    try:
        with open(vault_file, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


class OvernightHarvester:
    """Continuous background runner executing cyclic generation requests to n8n bridge."""

    def __init__(
        self,
        endpoint_url: str = "http://localhost:8000/api/v1/a2ui/render",
        auth_token: str = "ntn_local_harvest_key",
        delay_seconds: float = 3.0,
        max_iterations: int = 0,
        vault_path: Optional[str] = None
    ):
        self.endpoint_url = endpoint_url
        self.auth_token = auth_token
        self.delay_seconds = delay_seconds
        self.max_iterations = max_iterations
        self.vault_path = vault_path or os.path.join(os.getcwd(), "registry", "genome_vault", "harvest.jsonl")
        self.is_running = True
        self.stats = {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
            "avg_latency_ms": 0.0,
            "start_time": None
        }

    def stop(self):
        self.is_running = False

    async def run(self):
        """Main harvesting loop."""
        self.stats["start_time"] = time.time()
        initial_vault_count = count_vault_records(self.vault_path)

        print("\n" + "=" * 70)
        print(" [*] RAZUM GOOGLE AI PRO -- OVERNIGHT GENOME HARVESTER [*]")
        print("=" * 70)
        print(f"Target Gateway: {self.endpoint_url}")
        print(f"Auth Token:     {self.auth_token[:8]}***")
        print(f"Cycle Delay:    {self.delay_seconds}s")
        print(f"Max Cycles:     {'Unlimited (Overnight)' if self.max_iterations == 0 else self.max_iterations}")
        print(f"Genome Vault:   {self.vault_path}")
        print(f"Current Pairs:  {initial_vault_count} in vault")
        print("=" * 70 + "\n")

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "X-Client-Role": "OvernightHarvester"
        }

        total_latencies = []

        async with httpx.AsyncClient(timeout=25.0) as client:
            # Pre-flight health check
            try:
                health_url = self.endpoint_url.replace("/api/v1/a2ui/render", "/health")
                h_res = await client.get(health_url)
                if h_res.status_code == 200:
                    print(f"[OK] Gateway status: ONLINE ({h_res.json().get('status', 'OK')})")
                else:
                    print(f"[!] Gateway health check warning: HTTP {h_res.status_code}")
            except Exception as e:
                print(f"[!] Notice: Gateway not responding at {health_url} ({e})")
                print("  Make sure uvicorn is running: uvicorn services.integration.n8n_bridge:app --port 8000\n")

            iteration = 0
            while self.is_running:
                iteration += 1
                if self.max_iterations > 0 and iteration > self.max_iterations:
                    print(f"\n✓ Reached target iterations ({self.max_iterations}). Stopping.")
                    break

                task_payload = generate_random_task()
                t0 = time.perf_counter()

                try:
                    response = await client.post(
                        self.endpoint_url,
                        json=task_payload,
                        headers=headers
                    )
                    latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)
                    total_latencies.append(latency_ms)

                    self.stats["total_sent"] += 1

                    if response.status_code == 200:
                        self.stats["successful"] += 1
                        res_data = response.json()
                        winner = res_data.get("winner_worker", "fast_worker")
                        card_id = res_data.get("card_payload", {}).get("card_id", "genome_card")
                        
                        # Check vault count
                        curr_vault = count_vault_records(self.vault_path)

                        print(
                            f"[{datetime.now().strftime('%H:%M:%S')}] "
                            f"#{iteration:04d} | HTTP 200 OK | "
                            f"Winner: {winner:12s} | "
                            f"Latency: {latency_ms:6.1f}ms | "
                            f"Card: {card_id:15s} | "
                            f"Vault: {curr_vault:4d} pairs"
                        )
                    else:
                        self.stats["failed"] += 1
                        print(
                            f"[{datetime.now().strftime('%H:%M:%S')}] "
                            f"#{iteration:04d} | HTTP {response.status_code} ERROR: {response.text[:80]}"
                        )

                except httpx.ConnectError:
                    self.stats["failed"] += 1
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"#{iteration:04d} | CONNECTION REFUSED to {self.endpoint_url}. Retrying..."
                    )
                except Exception as err:
                    self.stats["failed"] += 1
                    print(
                        f"[{datetime.now().strftime('%H:%M:%S')}] "
                        f"#{iteration:04d} | EXCEPTION: {err}"
                    )

                # Delay between cycles
                try:
                    await asyncio.sleep(self.delay_seconds)
                except asyncio.CancelledError:
                    break

        self._print_summary(initial_vault_count, total_latencies)

    def _print_summary(self, initial_vault_count: int, latencies: List[float]):
        final_vault = count_vault_records(self.vault_path)
        gained = max(0, final_vault - initial_vault_count)
        elapsed_min = round((time.time() - (self.stats["start_time"] or time.time())) / 60.0, 2)
        avg_lat = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

        print("\n" + "=" * 70)
        print(" [*] OVERNIGHT HARVEST RUN SUMMARY [*]")
        print("=" * 70)
        print(f"Total Cycles Run:   {self.stats['total_sent']}")
        print(f"Successful 200 OK:  {self.stats['successful']}")
        print(f"Failed Requests:    {self.stats['failed']}")
        print(f"Average Latency:    {avg_lat} ms")
        print(f"Elapsed Time:       {elapsed_min} minutes")
        print(f"Genome Pairs Added: +{gained} (Total in Vault: {final_vault})")
        print(f"Vault File:         {self.vault_path}")
        print("=" * 70 + "\n")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Razum Genome Overnight Task Harvester")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/a2ui/render", help="Endpoint URL")
    parser.add_argument("--token", default="ntn_local_harvest_key", help="Zero Trust Authorization Token")
    parser.add_argument("--delay", type=float, default=2.5, help="Delay between generation cycles in seconds")
    parser.add_argument("--max-iter", type=int, default=0, help="Max iterations (0 = infinite overnight)")
    parser.add_argument("--vault", default=None, help="Custom path to harvest.jsonl")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    harvester = OvernightHarvester(
        endpoint_url=args.url,
        auth_token=args.token,
        delay_seconds=args.delay,
        max_iterations=args.max_iter,
        vault_path=args.vault
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def sig_handler(sig, frame):
        print("\n[!] Received stop signal. Finalizing current cycle...")
        harvester.stop()

    try:
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)
    except (ValueError, AttributeError):
        pass

    try:
        loop.run_until_complete(harvester.run())
    except KeyboardInterrupt:
        harvester.stop()
    finally:
        loop.close()
