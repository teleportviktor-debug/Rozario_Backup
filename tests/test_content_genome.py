"""
Tests for Phase 3: Content Genome and Native Video Processing.
Architecture "Genome" - Razum Google AI PRO.
"""

import os
import shutil
import pytest
import numpy as np
from PIL import Image

from services.content_genome.video_dna_extractor import (
    VideoDNAExtractor, VideoDNAMetrics, ColorPaletteProfile, HookStructure
)
from services.content_genome.multimodal_processor import (
    MultimodalProcessor, BoundingBox, SanitizationReport, StoryboardJSON
)
from services.content_genome.dna_registry import DNARegistry


@pytest.fixture
def temp_vault_dir(tmp_path):
    vault = tmp_path / "genome_vault"
    vault.mkdir()
    playbook = tmp_path / "playbook"
    playbook.mkdir()
    return str(vault), str(playbook)


@pytest.fixture
def synthetic_video_frames():
    """Generates synthetic video frames matching Ver Sacrum palette (Obsidian, Cyan, Gold)."""
    frames = []
    # 30 frames = 1 second at 30fps
    for i in range(45):
        # Base obsidian dark background #0a0a0c
        img = Image.new("RGB", (128, 128), color=(10, 10, 12))
        pixels = np.array(img)

        # In first scene: add neon cyan accent (#00f0ff)
        if i < 20:
            pixels[40:70, 40:70] = [0, 240, 255]
        # In second scene (cut at frame 20): add gold accent (#d4af37)
        else:
            pixels[20:80, 20:80] = [212, 175, 55]

        frames.append(Image.fromarray(pixels))
    return frames


def test_video_dna_extractor_metrics(synthetic_video_frames):
    extractor = VideoDNAExtractor(cut_threshold=20.0, fps=30.0)
    dna = extractor.extract_dna_from_frames(
        frames=synthetic_video_frames,
        video_id="test_vid_001"
    )

    assert isinstance(dna, VideoDNAMetrics)
    assert dna.video_id == "test_vid_001"
    assert dna.total_frames == 45
    assert dna.fps == 30.0
    assert dna.duration_sec == 1.5
    # Should detect the cut between frame 19 and 20
    assert dna.cut_count >= 1
    assert dna.cut_frequency_cpm > 0

    # Color palette validation
    assert dna.color_palette.obsidian_ratio > 0.4
    assert dna.color_palette.brand_fidelity_score > 50.0

    # Hook metrics validation
    assert isinstance(dna.hook_structure, HookStructure)
    assert dna.hook_structure.motion_intensity_score > 0
    assert dna.hook_structure.retention_potential in ["HIGH", "MEDIUM", "LOW"]

    # Ver Sacrum aesthetic score
    assert 0 <= dna.ver_sacrum_aesthetic_score <= 100


def test_multimodal_processor_pii_sanitization():
    processor = MultimodalProcessor()

    # 1. Text PII sanitization
    raw_text = "Contact lead john.doe@enterprise.com with API token Bearer ntn_super_secret_token_12345 at (555) 234-5678"
    clean_text, report = processor.sanitize_text(raw_text)

    assert "john.doe@enterprise.com" not in clean_text
    assert "[REDACTED_EMAIL]" in clean_text
    assert "Bearer ntn_super_secret_token_12345" not in clean_text
    assert report.pii_detected is True
    assert report.masked_entities_count >= 2
    assert "EMAIL" in report.detected_categories
    assert "BEARER_TOKEN" in report.detected_categories

    # 2. Visual frame PII masking
    test_img = Image.new("RGB", (100, 100), color=(200, 200, 200))
    boxes = [BoundingBox(ymin=10, xmin=10, ymax=40, xmax=40, label="FACE_PII")]

    masked_img, frame_report = processor.sanitize_frame(test_img, known_boxes=boxes)
    assert frame_report.pii_detected is True
    assert frame_report.masked_entities_count == 1
    assert "FACE_PII" in frame_report.detected_categories

    # Verify masked region has obsidian dark color (10, 10, 12)
    masked_pixels = np.array(masked_img)
    # Inside the bounding box (e.g. at 25, 25)
    center_color = masked_pixels[25, 25]
    assert np.allclose(center_color, [10, 10, 12], atol=5)


def test_multimodal_processor_storyboard_generation():
    processor = MultimodalProcessor()
    storyboard = processor.generate_storyboard(
        video_title="Enterprise Scalability Breakthrough",
        topic="Microservices to Autonomous Genomes",
        duration_sec=16.0
    )

    assert isinstance(storyboard, StoryboardJSON)
    assert storyboard.video_title == "Enterprise Scalability Breakthrough"
    assert storyboard.total_duration_sec == 16.0
    assert len(storyboard.scenes) >= 3

    # Check Ver Sacrum styling tokens in prompts
    first_scene = storyboard.scenes[0]
    assert first_scene.scene_number == 1
    assert first_scene.timestamp_start_sec == 0.0
    assert "obsidian" in first_scene.composition_prompt.lower()
    assert "cyan" in first_scene.composition_prompt.lower()
    assert first_scene.voiceover_script is not None


def test_dna_registry_persistence_and_export(temp_vault_dir, synthetic_video_frames):
    vault_dir, playbook_dir = temp_vault_dir
    registry = DNARegistry(vault_dir=vault_dir, playbook_dir=playbook_dir)

    # 1. Extract DNA
    extractor = VideoDNAExtractor()
    dna = extractor.extract_dna_from_frames(synthetic_video_frames, video_id="vid_persisted_001")

    # 2. Save DNA Profile
    sanitization_report = SanitizationReport(
        pii_detected=False,
        masked_entities_count=0,
        detected_categories=[],
        processing_time_ms=12.5,
        zero_trust_status="COMPLIANT"
    )
    saved_record = registry.save_dna_profile(dna, sanitization_report)
    assert saved_record["video_id"] == "vid_persisted_001"
    assert os.path.exists(registry.profiles_path)

    # Check retrieval
    profiles = registry.get_all_profiles()
    assert len(profiles) == 1
    assert profiles[0]["video_id"] == "vid_persisted_001"

    # 3. Generate and Save Storyboard
    processor = MultimodalProcessor()
    storyboard = processor.generate_storyboard(
        video_title="Autonomous Genomes Showcase",
        topic="B2B Lead Intelligence",
        duration_sec=12.0
    )
    registry.save_storyboard(storyboard)
    assert os.path.exists(registry.storyboards_path)

    # 4. Export to NotebookLM Markdown
    export_path = registry.export_to_notebooklm_playbook(storyboard, dna_metrics=dna)
    assert os.path.exists(export_path)

    with open(export_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# Visual Content Genome & Storyboard Blueprint" in content
    assert "Autonomous Genomes Showcase" in content
    assert "Ver Sacrum Aesthetic Score" in content
    assert "Scene-by-Scene Production Breakdown" in content
    assert "Zero Trust Guarantee" in content
