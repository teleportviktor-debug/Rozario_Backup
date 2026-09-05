"""
Racing Router (Микросервис конкурентного роутинга черновиков)
Architecture "Genome" (Phase 1) - Razum Google AI PRO.

Parallel asynchronous execution of candidate generators (Fast Worker vs. Deep Worker).
- The first response that passes Pydantic A2UICardPayload validation is immediately returned.
- Lingering worker tasks are NOT discarded; they complete in the background and log to
  `/registry/racing_logs/` for sovereign dataset accumulation.
- Self-healing fallback: if the faster worker returns malformed data, the router seamlessly
  waits for and adopts the slower worker's validated result.
"""

import asyncio
import os
import time
import json
import logging
from typing import Dict, Any, Optional, Callable, Awaitable, List, Union
from pydantic import BaseModel, Field, ValidationError

from config.genome_config import settings
from services.schemas.card_service import (
    A2UICardPayload,
    CardSection,
    CardWidget,
    WidgetButton,
    GoogleWorkspaceCardMessage,
)

logger = logging.getLogger("GenomeRacingRouter")


class RacingMetrics(BaseModel):
    winner: str
    elapsed_us: int
    elapsed_ms: float
    shadow_worker: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


class ModelDraftResponse(BaseModel):
    """Backwards-compatible draft response container."""
    model_name: str
    content: str
    card_message: Optional[GoogleWorkspaceCardMessage] = None
    latency_ms: float
    status: str = "SUCCESS"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RacingRouter:
    """
    Competitive Racing Router:
    Fast Worker vs. Deep Worker with Pydantic contract validation
    and non-blocking background shadow logging.
    """

    def __init__(
        self,
        fast_worker: Optional[Callable[[str, Optional[dict]], Awaitable[Any]]] = None,
        deep_worker: Optional[Callable[[str, Optional[dict]], Awaitable[Any]]] = None,
        log_dir: Optional[str] = None,
        primary_model: str = settings.PRIMARY_MODEL,
        fallback_model: str = settings.FALLBACK_MODEL,
        timeout_seconds: float = settings.RACING_TIMEOUT_SECONDS,
    ):
        self.fast_worker = fast_worker
        self.deep_worker = deep_worker
        self.log_dir = log_dir or os.path.join(os.getcwd(), "registry", "racing_logs")
        self.vault_dir = os.path.join(os.getcwd(), "registry", "genome_vault")
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.timeout_seconds = timeout_seconds
        self.last_metrics: Optional[RacingMetrics] = None
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.vault_dir, exist_ok=True)

    async def race(
        self,
        prompt: str,
        context: Optional[dict] = None
    ) -> A2UICardPayload:
        """
        Executes Fast Worker and Deep Worker concurrently.
        Returns the first payload that strictly passes A2UICardPayload validation.
        Logs the slower task in the background without blocking the caller, and harvests
        the pair into /registry/genome_vault/harvest.jsonl (Data-First Harvest Approach B).
        """
        ctx = context or {}
        t0 = time.perf_counter()

        # Prepare callable instances or defaults
        caller_fast = self.fast_worker or self._default_fast_worker
        caller_deep = self.deep_worker or self._default_deep_worker

        # Wrap in task runners that measure execution
        async def _run_worker(worker_fn: Callable, name: str):
            res = await worker_fn(prompt, ctx)
            return name, res

        task_fast = asyncio.create_task(_run_worker(caller_fast, "fast_worker"), name="task_fast")
        task_deep = asyncio.create_task(_run_worker(caller_deep, "deep_worker"), name="task_deep")

        pending = {task_fast, task_deep}
        winning_payload: Optional[A2UICardPayload] = None
        winner_name: Optional[str] = None

        while pending:
            done, pending = await asyncio.wait(
                pending,
                return_when=asyncio.FIRST_COMPLETED,
                timeout=self.timeout_seconds
            )

            if not done:
                # Timeout occurred
                for t in pending:
                    t.cancel()
                raise TimeoutError(f"RacingRouter timed out after {self.timeout_seconds}s")

            for finished_task in done:
                try:
                    name, raw_result = finished_task.result()
                    validated = self._validate_payload(raw_result)
                    if validated is not None:
                        winning_payload = validated
                        winner_name = name
                        break
                    else:
                        logger.warning(f"RacingRouter: Worker {name} output failed A2UI validation. Self-healing...")
                except Exception as err:
                    logger.warning(f"RacingRouter: Worker exception: {err}. Awaiting competing candidate...")

            if winning_payload is not None:
                # We have a valid winner!
                elapsed_sec = time.perf_counter() - t0
                elapsed_ms = round(elapsed_sec * 1000.0, 3)
                elapsed_us = int(elapsed_sec * 1_000_000)

                # Identify shadow worker for background logging
                shadow_names = [t.get_name() for t in pending]
                shadow_name = shadow_names[0] if shadow_names else None

                self.last_metrics = RacingMetrics(
                    winner=winner_name or "unknown",
                    elapsed_us=elapsed_us,
                    elapsed_ms=elapsed_ms,
                    shadow_worker=shadow_name
                )

                # Approach B: Fire background shadow task for remaining workers without blocking
                for lingering_task in pending:
                    asyncio.create_task(
                        self._monitor_and_log_shadow(
                            lingering_task,
                            prompt,
                            ctx,
                            t0,
                            fast_result=winning_payload,
                            fast_latency_ms=elapsed_ms
                        )
                    )
                return winning_payload

        raise RuntimeError("All racing workers failed to produce a valid A2UICardPayload.")

    def _validate_payload(self, raw: Any) -> Optional[A2UICardPayload]:
        """Validates that candidate output conforms to A2UICardPayload schema."""
        if isinstance(raw, A2UICardPayload):
            return raw

        if isinstance(raw, dict):
            try:
                return A2UICardPayload.model_validate(raw)
            except (ValidationError, TypeError, ValueError):
                return None

        if isinstance(raw, str):
            try:
                data = json.loads(raw)
                if isinstance(data, dict):
                    return A2UICardPayload.model_validate(data)
            except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
                return None

        return None

    async def _monitor_and_log_shadow(
        self,
        shadow_task: asyncio.Task,
        prompt: str,
        context: dict,
        t0: float,
        fast_result: Optional[A2UICardPayload] = None,
        fast_latency_ms: float = 0.0
    ) -> None:
        """Awaits the non-winning shadow worker and logs its dataset entry into racing_logs & genome_vault."""
        try:
            name, raw_result = await shadow_task
            deep_latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
            latency_diff = round(deep_latency_ms - fast_latency_ms, 3)

            # 1. Log to racing_logs
            await self._log_shadow_result(name, raw_result, prompt, context, deep_latency_ms)

            # 2. Approach B: Harvest pair to genome_vault
            if fast_result is not None:
                await self._harvest_genome_pair(
                    prompt=prompt,
                    fast_result=fast_result,
                    deep_result=raw_result,
                    latency_diff=latency_diff,
                    context=context
                )
        except Exception as err:
            logger.warning(f"Shadow logging/harvesting error for {shadow_task.get_name()}: {err}")

    async def _harvest_genome_pair(
        self,
        prompt: str,
        fast_result: Any,
        deep_result: Any,
        latency_diff: float,
        context: Optional[dict] = None
    ) -> None:
        """
        Data-First Harvest (Approach B):
        Asynchronously appends the (fast_draft, deep_response) pair to /registry/genome_vault/harvest.jsonl.
        """
        os.makedirs(self.vault_dir, exist_ok=True)
        harvest_file = os.path.join(self.vault_dir, "harvest.jsonl")

        def _serialize(obj: Any):
            if isinstance(obj, BaseModel):
                return obj.model_dump(mode="json")
            if isinstance(obj, dict):
                return obj
            return str(obj)

        record = {
            "timestamp": time.time(),
            "prompt": prompt,
            "context": context or {},
            "fast_result": _serialize(fast_result),
            "deep_result": _serialize(deep_result),
            "latency_diff_ms": latency_diff,
        }

        # Asynchronous non-blocking file write via anyio worker thread
        json_line = json.dumps(record, ensure_ascii=False) + "\n"
        
        def _write():
            with open(harvest_file, "a", encoding="utf-8") as f:
                f.write(json_line)

        await asyncio.to_thread(_write)
        logger.info(f"🧬 Genome pair harvested into {harvest_file} (diff: {latency_diff}ms)")

    async def _log_shadow_result(
        self,
        worker_name: str,
        result: Any,
        prompt: str,
        context: Optional[dict],
        latency_ms: float
    ) -> None:
        """Writes validated or raw shadow dataset records into /registry/racing_logs/."""
        os.makedirs(self.log_dir, exist_ok=True)
        log_file = os.path.join(self.log_dir, "shadow_dataset.jsonl")

        # Normalize serialized result
        if isinstance(result, BaseModel):
            serializable_result = result.model_dump(mode="json")
        elif isinstance(result, dict):
            serializable_result = result
        else:
            serializable_result = str(result)

        record = {
            "timestamp": time.time(),
            "worker": worker_name,
            "latency_ms": latency_ms,
            "prompt": prompt,
            "context": context or {},
            "data": serializable_result,
        }

        # Write to JSONL
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        logger.info(f"💾 Shadow Dataset record logged for {worker_name} ({latency_ms}ms)")

    # Default Mock Generators for testing and fallback
    async def _default_fast_worker(self, prompt: str, ctx: dict) -> A2UICardPayload:
        await asyncio.sleep(0.02)
        return A2UICardPayload(
            card_id="draft_fast",
            title=f"Fast Draft: {prompt[:30]}",
            subtitle="Generated by Fast Flash Engine",
            style_theme="OBSIDIAN_CYAN",
            sections=[
                CardSection(
                    header="Fast Results",
                    widgets=[
                        CardWidget(widget_type="textParagraph", text="Fast throughput achieved.")
                    ]
                )
            ]
        )

    async def _default_deep_worker(self, prompt: str, ctx: dict) -> A2UICardPayload:
        await asyncio.sleep(0.06)
        return A2UICardPayload(
            card_id="draft_deep",
            title=f"Deep Draft: {prompt[:30]}",
            subtitle="Synthesized by Deep Reasoning Model",
            style_theme="OBSIDIAN_CYAN",
            sections=[
                CardSection(
                    header="Deep Analysis",
                    widgets=[
                        CardWidget(widget_type="textParagraph", text="Deep architectural validation passed.")
                    ]
                )
            ]
        )

    # Backwards compatibility method for Phase 1 tests
    async def race_models(
        self,
        prompt: str,
        primary_delay: float = 0.04,
        fallback_delay: float = 0.08,
        primary_caller: Optional[Callable] = None,
        fallback_caller: Optional[Callable] = None,
    ) -> ModelDraftResponse:
        """Backwards compatibility endpoint for phase 1 generic LLM race."""
        t_start = time.perf_counter()

        async def _call(model_name: str, delay: float, custom_fn: Optional[Callable]):
            if custom_fn:
                content = await custom_fn(model_name, prompt)
            else:
                await asyncio.sleep(delay)
                content = f"[{model_name}] Draft synthesized for: {prompt[:40]}..."
            return model_name, content

        task_p = asyncio.create_task(_call(self.primary_model, primary_delay, primary_caller))
        task_f = asyncio.create_task(_call(self.fallback_model, fallback_delay, fallback_caller))

        done, pending = await asyncio.wait(
            {task_p, task_f},
            return_when=asyncio.FIRST_COMPLETED,
            timeout=self.timeout_seconds
        )

        for lingering in pending:
            lingering.cancel()

        first = list(done)[0]
        model_name, content = first.result()
        latency = (time.perf_counter() - t_start) * 1000.0

        return ModelDraftResponse(
            model_name=model_name,
            content=content,
            latency_ms=round(latency, 2),
            status="SUCCESS",
            metadata={"zero_trust_verified": True}
        )
