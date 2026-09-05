"""
Pytest Suite for Racing Router (Agent 5 - QA & Testing)
Verifies:
1. Speed Race: Router returns in ~200ms without awaiting the 800ms worker.
2. Self-Healing Schema Recovery: Malformed fast output seamlessly triggers fallback to deep worker.
3. Non-blocking Shadow Logging: Slower worker's output is recorded to /registry/racing_logs/ asynchronously.
"""

import os
import json
import asyncio
import time
import pytest
from services.router.racing_router import RacingRouter
from services.schemas.card_service import (
    A2UICardPayload,
    CardSection,
    CardWidget,
    WidgetButton,
)


def make_valid_payload(card_id: str, title: str) -> A2UICardPayload:
    return A2UICardPayload(
        card_id=card_id,
        title=title,
        subtitle="Verified Autonomous Card",
        style_theme="OBSIDIAN_CYAN",
        sections=[
            CardSection(
                header="Metrics",
                widgets=[
                    CardWidget(
                        widget_type="decoratedText",
                        top_label="Status",
                        text="VALIDATED_ONLINE"
                    )
                ]
            )
        ]
    )


@pytest.mark.anyio
async def test_racing_speed_fast_worker_wins(tmp_path):
    """
    Test 1: Worker A (200ms) vs Worker B (800ms).
    Validates that router returns in ~200ms without blocking on Worker B.
    """
    async def worker_a(prompt: str, ctx: dict):
        await asyncio.sleep(0.2)  # 200ms
        return make_valid_payload("card_fast", "Fast Worker Result")

    async def worker_b(prompt: str, ctx: dict):
        await asyncio.sleep(0.8)  # 800ms
        return make_valid_payload("card_deep", "Deep Worker Result")

    router = RacingRouter(
        fast_worker=worker_a,
        deep_worker=worker_b,
        log_dir=str(tmp_path)
    )

    t0 = time.perf_counter()
    winner_payload = await router.race(prompt="Draft Q3 Strategy")
    elapsed = time.perf_counter() - t0

    # Must complete near ~200ms (well under 800ms)
    assert elapsed < 0.5, f"Expected elapsed < 0.5s, got {elapsed:.3f}s"
    assert winner_payload.card_id == "card_fast"
    assert "Fast Worker Result" in winner_payload.title
    assert router.last_metrics is not None
    assert router.last_metrics.winner == "fast_worker"
    assert router.last_metrics.elapsed_us > 0


@pytest.mark.anyio
async def test_racing_self_healing_schema_recovery(tmp_path):
    """
    Test 2: Fast Worker A returns corrupted/invalid JSON schema.
    Router automatically recovers by waiting for and adopting Worker B's validated result.
    """
    async def worker_a_broken(prompt: str, ctx: dict):
        await asyncio.sleep(0.1)  # 100ms
        # Invalid schema: missing required fields 'title' and 'sections'
        return {"broken": "data", "missing_required_fields": True}

    async def worker_b_valid(prompt: str, ctx: dict):
        await asyncio.sleep(0.3)  # 300ms
        return make_valid_payload("card_deep_recovered", "Recovered Deep Analysis")

    router = RacingRouter(
        fast_worker=worker_a_broken,
        deep_worker=worker_b_valid,
        log_dir=str(tmp_path)
    )

    t0 = time.perf_counter()
    recovered_payload = await router.race(prompt="Self-healing test")
    elapsed = time.perf_counter() - t0

    # Adopts Worker B's result
    assert recovered_payload.card_id == "card_deep_recovered"
    assert "Recovered Deep Analysis" in recovered_payload.title
    assert router.last_metrics.winner == "deep_worker"
    assert 0.25 <= elapsed < 0.6


@pytest.mark.anyio
async def test_racing_background_shadow_logging(tmp_path):
    """
    Test 3: Checks that the second worker completes in the background and
    writes its dataset record to the shadow log file without delaying the response.
    """
    log_dir = str(tmp_path / "racing_logs")

    async def fast_worker(prompt: str, ctx: dict):
        await asyncio.sleep(0.05)
        return make_valid_payload("fast_id", "Immediate UI Card")

    async def deep_worker(prompt: str, ctx: dict):
        await asyncio.sleep(0.25)
        return make_valid_payload("deep_shadow_id", "Deep Sovereign Dataset Card")

    router = RacingRouter(
        fast_worker=fast_worker,
        deep_worker=deep_worker,
        log_dir=log_dir
    )

    t0 = time.perf_counter()
    res = await router.race(prompt="Telemetry Archiving")
    elapsed_main = time.perf_counter() - t0

    # Main response returned quickly
    assert elapsed_main < 0.15
    assert res.card_id == "fast_id"

    # Allow background shadow task to finalize (wait 300ms)
    await asyncio.sleep(0.35)

    log_file = os.path.join(log_dir, "shadow_dataset.jsonl")
    assert os.path.exists(log_file), "Shadow dataset file was not created!"

    with open(log_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) >= 1
    record = json.loads(lines[-1])
    assert record["worker"] == "deep_worker"
    assert "Telemetry Archiving" in record["prompt"]
    assert record["data"]["card_id"] == "deep_shadow_id"
    assert record["latency_ms"] >= 200.0
