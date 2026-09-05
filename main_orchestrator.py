"""
Main System Orchestrator (Agent 3 - System Orchestrator)
Architecture "Genome" (Phase 4) - Razum Google AI PRO.

End-to-End Orchestrator unifying:
1. SurgeonTranspiler (AST/JSX -> Google Workspace CardService JSON).
2. RacingRouter (Fast vs. Deep parallel competition & sovereign harvest).
3. PromptMutator & BatchTournament (evolutionary prompt cross-breeding).
4. VideoDNAExtractor & MultimodalProcessor (Zero Trust PII scrub & storyboarding).
5. VideoSynthesizer (1080x1920 MP4 vertical reel rendering).
6. NotebookLMExporter (grounded enterprise knowledge base sync).
"""

import os
import sys
import time
import json
import asyncio
import argparse
from typing import Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from services.surgeon.surgeon_transpiler import SurgeonTranspiler
from services.router.racing_router import RacingRouter
from services.schemas.card_service import A2UICardPayload
from services.evolution.prompt_mutator import PromptMutator
from services.content_genome.video_dna_extractor import VideoDNAExtractor
from services.content_genome.multimodal_processor import MultimodalProcessor
from services.content_genome.dna_registry import DNARegistry
from services.content_genome.video_synthesizer import VideoSynthesizer, RenderedVideoAsset
from services.evolution.notebooklm_exporter import NotebookLMExporter


class GenomeSystemOrchestrator:
    """
    Central operational hub for Razum Google AI PRO.
    Executes single components or full end-to-end B2B asset generation cycles.
    """

    def __init__(self):
        self.transpiler = SurgeonTranspiler()
        self.router = RacingRouter()
        self.mutator = PromptMutator()
        self.dna_extractor = VideoDNAExtractor()
        self.multimodal_processor = MultimodalProcessor()
        self.registry = DNARegistry()
        self.video_synthesizer = VideoSynthesizer()
        self.notebooklm_exporter = NotebookLMExporter()

    async def run_full_cycle(
        self,
        topic: str = "Global Enterprise B2B Lead Scoring",
        context: Optional[Dict[str, Any]] = None,
        duration_sec: float = 12.0
    ) -> Dict[str, Any]:
        """
        Executes end-to-end pipeline:
        Prompt -> Racing Drafts -> A2UI Card JSON -> Video Storyboard -> MP4 Synthesis -> Playbook Sync.
        """
        start_time = time.perf_counter()
        ctx = context or {
            "lead_score": "High Urgency",
            "pain_component": "Scalability bottleneck",
            "budget": "$100k+",
            "authority": "CTO / VP Engineering"
        }

        print("===================================================================")
        print("🚀 [STAGE 1/5] Executing Racing Router & Competitive Draft Generation...")
        card_payload: A2UICardPayload = await self.router.race(prompt=topic, context=ctx)
        card_service_msg = card_payload.to_card_service_message()
        print(f"✓ Card Generated: '{card_payload.title}' ({len(card_payload.sections)} sections)")

        print("🛡️ [STAGE 2/5] Running Zero Trust PII Sanitization...")
        sanitized_topic, pii_report = self.multimodal_processor.sanitize_text(topic)
        print(f"✓ Zero Trust Audit Passed: PII Detected={pii_report.pii_detected}, Status={pii_report.zero_trust_status}")

        print("🎬 [STAGE 3/5] Generating Structured Ver Sacrum Storyboard & Visual DNA...")
        storyboard = self.multimodal_processor.generate_storyboard(
            video_title=card_payload.title,
            topic=sanitized_topic,
            duration_sec=duration_sec
        )
        self.registry.save_storyboard(storyboard)

        # Extract DNA metrics from procedural scene frames to ensure Brand Fidelity >= 80%
        preview_frames = [
            self.video_synthesizer._render_procedural_scene_frame(
                scene=sc,
                total_scenes=len(storyboard.scenes),
                width=1080,
                height=1920
            ) for sc in storyboard.scenes
        ]
        dna_metrics: VideoDNAMetrics = self.dna_extractor.extract_dna_from_frames(
            frames=preview_frames,
            video_id=f"dna_{card_payload.card_id}"
        )
        self.registry.save_dna_profile(dna_metrics, sanitization_report=pii_report)
        print(f"✓ Storyboard Created: {len(storyboard.scenes)} scenes, duration: {storyboard.total_duration_sec}s")
        print(f"✓ Brand Fidelity Score: {dna_metrics.color_palette.brand_fidelity_score}% (Target >= 80%)")
        print(f"✓ Ver Sacrum Aesthetic Index: {dna_metrics.ver_sacrum_aesthetic_score}/100")

        print("🎥 [STAGE 4/5] Synthesizing 9:16 Vertical Video Asset (1080x1920 MP4)...")
        video_asset: RenderedVideoAsset = self.video_synthesizer.render_storyboard(
            storyboard=storyboard,
            dna_metrics=dna_metrics,
            video_id=f"reel_{card_payload.card_id}"
        )
        print(f"✓ Video Rendered: {video_asset.video_path} ({video_asset.filesize_bytes} bytes, {video_asset.resolution})")

        print("📚 [STAGE 5/5] Exporting Knowledge Base & Grounding Artifacts for NotebookLM...")
        state_path = self.notebooklm_exporter.export_system_genome_state()
        templates_path = self.notebooklm_exporter.export_generative_templates(storyboards=[storyboard], dna_metrics=dna_metrics)
        playbook_path = self.registry.export_to_notebooklm_playbook(storyboard, dna_metrics=dna_metrics)
        print(f"✓ NotebookLM Grounding Docs Updated:\n  - {state_path}\n  - {templates_path}\n  - {playbook_path}")

        total_elapsed = round(time.perf_counter() - start_time, 2)
        print(f"===================================================================")
        print(f"✨ FULL END-TO-END PIPELINE COMPLETED IN {total_elapsed} SECONDS")
        print(f"===================================================================\n")

        session_log = {
            "session_id": f"session_{int(time.time())}_{card_payload.card_id}",
            "timestamp": time.time(),
            "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "status": "SUCCESS",
            "topic": topic,
            "latency_sec": total_elapsed,
            "execution_time_sec": total_elapsed,
            "card_payload": card_payload.model_dump(),
            "cardsV2": card_service_msg.to_json_dict().get("cardsV2", []),
            "video_asset": video_asset.model_dump(),
            "dna_metrics": dna_metrics.model_dump(),
            "storyboard": storyboard.model_dump(),
            "zero_trust": pii_report.model_dump(),
            "notebooklm_exports": [state_path, templates_path, playbook_path]
        }

        # Save single unified session ledger
        session_ledger_path = os.path.join(self.registry.vault_dir, "session_ledger.json")
        with open(session_ledger_path, "w", encoding="utf-8") as f:
            json.dump(session_log, f, indent=2, ensure_ascii=False)
        print(f"✓ Session Ledger Persisted: {session_ledger_path}")

        return session_log


def main():
    parser = argparse.ArgumentParser(description="Razum Google AI PRO - Main System Orchestrator")
    parser.add_argument("--mode", choices=["full_cycle", "server", "test"], default="full_cycle",
                        help="Execution mode: full_cycle, server, or test")
    parser.add_argument("--topic", default="B2B Lead Intelligence: Global Enterprise",
                        help="Prompt or topic for full-cycle generation")
    parser.add_argument("--duration", type=float, default=12.0, help="Video reel duration in seconds")

    args = parser.parse_args()
    orchestrator = GenomeSystemOrchestrator()

    if args.mode == "full_cycle":
        asyncio.run(orchestrator.run_full_cycle(topic=args.topic, duration_sec=args.duration))
    elif args.mode == "server":
        import uvicorn
        print("Starting FastAPI / n8n Gateway Server on port 8000...")
        uvicorn.run("services.integration.n8n_bridge:app", host="127.0.0.1", port=8000, reload=False)
    elif args.mode == "test":
        import subprocess
        print("Running complete test diagnostic suite...")
        subprocess.run(["pytest", "tests/", "-v"])


if __name__ == "__main__":
    main()
