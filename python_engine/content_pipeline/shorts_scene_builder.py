"""
============================================================================
RAZUM AI 2026 • SHORTS SCENE BUILDER
Transforms PROMO_REELS JSON into per-scene HTML render instructions
for Playwright capture. Injects AI-generated backgrounds.
============================================================================
"""

import os
import sys
import json
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
FRAMES_DIR = ROOT_DIR / "assets" / "shorts_frames"
OUTPUT_DIR = ROOT_DIR / "05_Content" / "Video" / "rendered_shorts"

# Import scene data from existing pipeline
sys.path.insert(0, str(ROOT_DIR / "python_engine"))
from video_render_pipeline import PROMO_REELS


def build_scene_manifest(reel_index: int = 0) -> dict:
    """
    Takes a single reel from PROMO_REELS and builds a complete
    render manifest with file paths, timings, and scene data
    ready for Playwright capture.
    """
    reel = PROMO_REELS[reel_index]
    manifest = {
        "reel_id": reel["id"],
        "title": reel["title"],
        "total_duration_sec": reel["duration_sec"],
        "aspect_ratio": reel["aspect_ratio"],
        "soundtrack_bpm": reel["soundtrack_bpm"],
        "scenes": []
    }

    for i, scene in enumerate(reel["scenes"]):
        # Parse timing "0:00 - 0:03" -> start_sec, end_sec
        parts = scene["time"].split(" - ")
        start_sec = _parse_time(parts[0])
        end_sec = _parse_time(parts[1])

        scene_entry = {
            "index": i,
            "scene_type": scene["scene_type"],
            "start_sec": start_sec,
            "end_sec": end_sec,
            "duration_sec": end_sec - start_sec,
            "sound_cue": scene["sound_cue"],
            "visual_description": scene["visual"],
            "text_overlay": scene["text_overlay"],
            "voiceover": scene["voiceover"],
            "bg_image": _find_bg_image(reel["id"], i),
            "template_html": str(TEMPLATES_DIR / "short_9x16_base.html"),
            "output_frame_path": str(OUTPUT_DIR / f"{reel['id']}_scene_{i:02d}.webm"),
        }

        # Add optional metrics for SOLUTION/DEMO scenes
        if scene["scene_type"] in ("SOLUTION", "DEMO"):
            scene_entry["metrics"] = _extract_metrics(scene["visual"])

        manifest["scenes"].append(scene_entry)

    return manifest


def build_all_manifests() -> list:
    """Build render manifests for all reels."""
    manifests = []
    for i in range(len(PROMO_REELS)):
        m = build_scene_manifest(i)
        manifests.append(m)

        # Save manifest JSON for debugging / manual inspection
        manifest_path = OUTPUT_DIR / f"{m['reel_id']}_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
        print(f"  ✓ Манифест сцен: {manifest_path}")

    return manifests


def _parse_time(t: str) -> float:
    """Parse '0:03' or '0:18' to seconds as float."""
    parts = t.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0.0


def _find_bg_image(reel_id: str, scene_index: int) -> str:
    """
    Look for a pre-generated background image for this scene.
    Falls back to empty string if not found (template uses gradient).
    """
    candidates = [
        FRAMES_DIR / f"{reel_id}_scene_{scene_index:02d}.jpg",
        FRAMES_DIR / f"{reel_id}_scene_{scene_index:02d}.png",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return ""


def _extract_metrics(visual_text: str) -> list:
    """
    Attempt to extract numeric metrics from scene visual description.
    Returns a list of {value, label} dicts for metric cards.
    """
    metrics = []
    # Simple pattern matching for common B2B metric patterns
    import re
    patterns = [
        (r"(\d+(?:\.\d+)?)\s*секунд", "секунд"),
        (r"\$(\d+(?:,\d+)?)", "стоимость"),
        (r"(\d+)\s*колонок", "колонок"),
        (r"(\d+)\s*час", "часов"),
        (r"(\d+)%", "точность"),
    ]
    for pattern, label in patterns:
        match = re.search(pattern, visual_text)
        if match:
            metrics.append({"value": match.group(0), "label": label})

    return metrics[:3]  # Max 3 metric cards


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 65)
    print("🎬 SHORTS SCENE BUILDER: Сборка манифестов рендеринга")
    print("=" * 65)
    manifests = build_all_manifests()
    print(f"\n✅ Собрано {len(manifests)} манифестов для {sum(len(m['scenes']) for m in manifests)} сцен.")
