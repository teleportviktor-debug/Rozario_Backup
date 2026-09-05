"""
End-to-End Pipeline Acceptance Tests (Phase 4).
Architecture "Genome" - Razum Google AI PRO.
"""

import os
import pytest
import asyncio
from main_orchestrator import GenomeSystemOrchestrator
from services.content_genome.video_synthesizer import VideoSynthesizer, RenderedVideoAsset
from services.content_genome.multimodal_processor import MultimodalProcessor
from services.evolution.notebooklm_exporter import NotebookLMExporter


def test_end_to_end_full_cycle(tmp_path):
    orchestrator = GenomeSystemOrchestrator()
    custom_output = str(tmp_path / "rendered_output")
    orchestrator.video_synthesizer.output_dir = custom_output
    os.makedirs(custom_output, exist_ok=True)

    result = asyncio.run(orchestrator.run_full_cycle(
        topic="Sovereign Enterprise AI Pipeline Architecture",
        context={"budget": "$150k+", "urgency": "High", "role": "CTO"},
        duration_sec=8.0
    ))

    # 1. Result Structure
    assert result["status"] == "SUCCESS"
    assert result["execution_time_sec"] > 0
    assert "card_payload" in result
    assert "cardsV2" in result

    # 2. A2UI Card & Google Workspace CardService JSON
    assert len(result["cardsV2"]) > 0
    card_obj = result["cardsV2"][0]["card"]
    assert "header" in card_obj
    assert "sections" in card_obj

    # 3. Storyboard
    sb = result["storyboard"]
    assert sb["total_duration_sec"] == 8.0
    assert len(sb["scenes"]) >= 2

    # 4. Synthesized Video File
    video_asset = result["video_asset"]
    assert video_asset["format"] == "MP4"
    assert video_asset["resolution"] == "1080x1920"
    assert os.path.exists(video_asset["video_path"])
    assert os.path.getsize(video_asset["video_path"]) > 500

    # 5. Zero Trust Compliance
    assert result["zero_trust"]["zero_trust_status"] == "COMPLIANT"

    # 6. NotebookLM Grounding Docs
    for doc_path in result["notebooklm_exports"]:
        assert os.path.exists(doc_path)
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "CANONICAL_TRUTH" in content or "NOTEBOOKLM_GROUNDING_METADATA" in content or "Visual Content Genome" in content


def test_video_synthesizer_direct_rendering(tmp_path):
    output_dir = str(tmp_path / "videos")
    synthesizer = VideoSynthesizer(output_dir=output_dir)

    processor = MultimodalProcessor()
    storyboard = processor.generate_storyboard(
        video_title="Direct Synthesis Test",
        topic="Low Latency Transpilation",
        duration_sec=10.0
    )

    asset = synthesizer.render_storyboard(storyboard, video_id="test_direct_synth")

    assert isinstance(asset, RenderedVideoAsset)
    assert os.path.exists(asset.video_path)
    assert asset.video_path.endswith(".mp4")
    assert asset.scenes_count == len(storyboard.scenes)
    assert asset.filesize_bytes > 0
    assert os.path.exists(asset.preview_frames_dir)


def test_notebooklm_exporter_metadata(tmp_path):
    exporter = NotebookLMExporter(workspace_root=str(tmp_path))
    state_file = exporter.export_system_genome_state()
    templates_file = exporter.export_generative_templates()

    assert os.path.exists(state_file)
    assert os.path.exists(templates_file)

    with open(state_file, "r", encoding="utf-8") as f:
        data = f.read()
        assert "CANONICAL_TRUTH" in data or "<!-- NOTEBOOKLM_GROUNDING_METADATA" in data
        assert "Razum Google AI PRO: Sovereign Genome System State" in data
        assert "#0a0a0c" in data
        assert "#00f0ff" in data
        assert "#d4af37" in data
