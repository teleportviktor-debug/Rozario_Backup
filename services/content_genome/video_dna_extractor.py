"""
Visual DNA Extractor (Agent 2 - Vision & Video Engineer)
Architecture "Genome" (Phase 3) - Razum Google AI PRO.

Extracts visual DNA from video frames:
- Shot duration & Cut frequency (editing pace).
- Color histogram analysis & Brand palette alignment:
    Obsidian (#0a0a0c), Neon Cyan (#00f0ff), Klimt Gold (#d4af37).
- Hook structure detection (first 2.5s: motion dynamics & visual intensity).
"""

import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import numpy as np
from PIL import Image

# Corporate Brand Palette Hex & RGB Normalized
COLOR_OBSIDIAN_RGB = np.array([10, 10, 12], dtype=np.float32)
COLOR_NEON_CYAN_RGB = np.array([0, 240, 255], dtype=np.float32)
COLOR_KLIMT_GOLD_RGB = np.array([212, 175, 55], dtype=np.float32)


class ColorPaletteProfile(BaseModel):
    obsidian_ratio: float = Field(..., description="Proportion of Obsidian dark tones (#0a0a0c)")
    cyan_ratio: float = Field(..., description="Proportion of Neon Cyan accents (#00f0ff)")
    gold_ratio: float = Field(..., description="Proportion of Klimt Gold accents (#d4af37)")
    other_ratio: float = Field(..., description="Proportion of non-brand colors")
    brand_fidelity_score: float = Field(..., description="Brand alignment index (0.0 to 100.0)")


class HookStructure(BaseModel):
    hook_duration_sec: float = 2.5
    motion_intensity_score: float = Field(..., description="0-100 motion dynamics in first 2.5s")
    visual_contrast_score: float = Field(..., description="0-100 visual contrast & text density index")
    retention_potential: str = Field(..., description="HIGH, MEDIUM, LOW")


class VideoDNAMetrics(BaseModel):
    video_id: str
    total_frames: int
    fps: float
    duration_sec: float
    cut_count: int
    cut_frequency_cpm: float = Field(..., description="Cuts per minute")
    avg_shot_duration_sec: float
    color_palette: ColorPaletteProfile
    hook_structure: HookStructure
    ver_sacrum_aesthetic_score: float = Field(..., description="Aesthetic compliance score 0-100")


class VideoDNAExtractor:
    """
    Extracts high-resolution visual and temporal DNA from video frames.
    Works natively with PIL Images or numpy arrays without heavy external dependencies.
    """

    def __init__(
        self,
        cut_threshold: float = 28.0,
        fps: float = 30.0
    ):
        self.cut_threshold = cut_threshold
        self.fps = fps

    def extract_dna_from_frames(
        self,
        frames: List[Image.Image],
        video_id: str = "vid_synthetic_001",
        custom_fps: Optional[float] = None
    ) -> VideoDNAMetrics:
        """
        Processes an ordered sequence of PIL Image frames and extracts complete Video DNA.
        """
        if not frames:
            raise ValueError("Frame list cannot be empty.")

        fps = custom_fps or self.fps
        total_frames = len(frames)
        duration_sec = max(0.1, round(total_frames / fps, 2))

        # 1. Temporal Editing Pace (Cuts, Shot Durations)
        cuts = self._detect_cuts(frames)
        cut_count = len(cuts)
        cuts_per_min = round((cut_count / duration_sec) * 60.0, 2)
        shot_count = cut_count + 1
        avg_shot_duration = round(duration_sec / shot_count, 2)

        # 2. Color Palette & Brand Alignment
        palette_profile = self._analyze_color_palette(frames)

        # 3. Hook Structure (first 2.5 seconds)
        hook_frames_count = max(1, min(total_frames, int(2.5 * fps)))
        hook_frames = frames[:hook_frames_count]
        hook_metrics = self._analyze_hook_structure(hook_frames)

        # 4. Overall Ver Sacrum / Cyber-Minimalism Aesthetic Score
        # Combination of Brand fidelity + Hook dynamics + Pacing balance
        pacing_score = min(100.0, max(0.0, 100.0 - abs(cuts_per_min - 18.0) * 2.0))
        aesthetic_score = round(
            (palette_profile.brand_fidelity_score * 0.5) +
            (hook_metrics.motion_intensity_score * 0.25) +
            (pacing_score * 0.25),
            2
        )

        return VideoDNAMetrics(
            video_id=video_id,
            total_frames=total_frames,
            fps=fps,
            duration_sec=duration_sec,
            cut_count=cut_count,
            cut_frequency_cpm=cuts_per_min,
            avg_shot_duration_sec=avg_shot_duration,
            color_palette=palette_profile,
            hook_structure=hook_metrics,
            ver_sacrum_aesthetic_score=aesthetic_score
        )

    def _detect_cuts(self, frames: List[Image.Image]) -> List[int]:
        """Detects scene transition cuts using frame-to-frame RGB delta difference."""
        cuts = []
        if len(frames) < 2:
            return cuts

        # Downsample frames for fast and robust histogram difference
        thumbnails = [np.array(f.resize((64, 64)).convert("RGB"), dtype=np.float32) for f in frames]

        for i in range(1, len(thumbnails)):
            delta = np.mean(np.abs(thumbnails[i] - thumbnails[i - 1]))
            if delta > self.cut_threshold:
                cuts.append(i)

        return cuts

    def _analyze_color_palette(self, frames: List[Image.Image]) -> ColorPaletteProfile:
        """
        Calculates color distance to Obsidian (#0a0a0c), Cyan (#00f0ff), and Gold (#d4af37).
        """
        sample_step = max(1, len(frames) // 10)
        sampled = frames[::sample_step]

        total_pixels = 0
        obsidian_count = 0
        cyan_count = 0
        gold_count = 0

        for img in sampled:
            # Resize for fast vector processing
            arr = np.array(img.resize((32, 32)).convert("RGB"), dtype=np.float32)
            pixels = arr.reshape(-1, 3)
            total_pixels += len(pixels)

            # Distances to target centroids in RGB space
            dist_obsidian = np.linalg.norm(pixels - COLOR_OBSIDIAN_RGB, axis=1)
            dist_cyan = np.linalg.norm(pixels - COLOR_NEON_CYAN_RGB, axis=1)
            dist_gold = np.linalg.norm(pixels - COLOR_KLIMT_GOLD_RGB, axis=1)

            # Thresholds for color belonging (Obsidian dark tones include near-black surfaces up to distance 85)
            obsidian_mask = dist_obsidian < 85.0
            cyan_mask = dist_cyan < 120.0
            gold_mask = dist_gold < 110.0

            obsidian_count += int(np.sum(obsidian_mask))
            cyan_count += int(np.sum(cyan_mask))
            gold_count += int(np.sum(gold_mask))

        if total_pixels == 0:
            total_pixels = 1

        obsidian_ratio = round(obsidian_count / total_pixels, 3)
        cyan_ratio = round(cyan_count / total_pixels, 3)
        gold_ratio = round(gold_count / total_pixels, 3)
        other_ratio = max(0.0, round(1.0 - (obsidian_ratio + cyan_ratio + gold_ratio), 3))

        # Brand Fidelity: Ver Sacrum canonical palette match
        # Canonical Ver Sacrum composition: Obsidian (#0a0a0c) canvas with Cyan (#00f0ff) & Gold (#d4af37) accents
        in_brand_ratio = min(1.0, obsidian_ratio + cyan_ratio + gold_ratio)
        accent_bonus = min(15.0, (cyan_ratio + gold_ratio) * 150.0)
        brand_score = (in_brand_ratio * 86.0) + accent_bonus
        normalized_fidelity = min(100.0, round(brand_score, 2))

        return ColorPaletteProfile(
            obsidian_ratio=obsidian_ratio,
            cyan_ratio=cyan_ratio,
            gold_ratio=gold_ratio,
            other_ratio=other_ratio,
            brand_fidelity_score=normalized_fidelity
        )

    def _analyze_hook_structure(self, hook_frames: List[Image.Image]) -> HookStructure:
        """
        Evaluates motion intensity and visual contrast in hook segment (first 2.5s).
        """
        if len(hook_frames) < 2:
            return HookStructure(
                hook_duration_sec=round(len(hook_frames) / self.fps, 2),
                motion_intensity_score=50.0,
                visual_contrast_score=50.0,
                retention_potential="MEDIUM"
            )

        downsampled = [np.array(f.resize((48, 48)).convert("L"), dtype=np.float32) for f in hook_frames]

        deltas = []
        contrasts = []
        for i in range(1, len(downsampled)):
            diff = np.mean(np.abs(downsampled[i] - downsampled[i - 1]))
            deltas.append(diff)
            # High standard deviation represents high contrast text/shapes
            contrasts.append(float(np.std(downsampled[i])))

        avg_motion = float(np.mean(deltas)) if deltas else 10.0
        avg_contrast = float(np.mean(contrasts)) if contrasts else 20.0

        # Normalization to 0-100 (taking into account high dynamic range of cyber obsidian typography)
        motion_score = min(100.0, round(avg_motion * 4.0, 2))
        contrast_score = min(100.0, round(avg_contrast * 3.6, 2))

        retention = "HIGH" if (motion_score > 55.0 or contrast_score > 60.0) else (
            "MEDIUM" if (motion_score > 25.0 or contrast_score > 35.0) else "LOW"
        )

        return HookStructure(
            hook_duration_sec=round(len(hook_frames) / self.fps, 2),
            motion_intensity_score=motion_score,
            visual_contrast_score=contrast_score,
            retention_potential=retention
        )
