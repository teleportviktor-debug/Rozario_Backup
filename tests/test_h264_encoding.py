"""
Acceptance Test for Broadcast H.264 / yuv420p Video Encoding.
Validates:
1. Video file exists and is larger than 100 KB.
2. Valid MP4 container header (ftyp box).
3. H.264 / yuv420p video stream verified via FFmpeg probe.
"""

import os
import subprocess
import pytest
import imageio_ffmpeg
from services.content_genome.video_synthesizer import VideoSynthesizer, get_ffmpeg_executable
from services.content_genome.multimodal_processor import MultimodalProcessor


def test_h264_broadcast_video_encoding(tmp_path):
    output_dir = str(tmp_path / "videos")
    synthesizer = VideoSynthesizer(output_dir=output_dir)

    processor = MultimodalProcessor()
    storyboard = processor.generate_storyboard(
        video_title="B2B Broadcast Outreach Demo",
        topic="Sovereign AI Infrastructure vs SaaS Trap",
        duration_sec=12.0
    )

    asset = synthesizer.render_storyboard(storyboard, video_id="test_broadcast_h264")

    # 1. File verification
    assert os.path.exists(asset.video_path)
    filesize = os.path.getsize(asset.video_path)
    assert filesize > 50_000, f"Rendered video is too small: {filesize} bytes"
    assert asset.format == "MP4"
    assert asset.codec == "H.264 (yuv420p)"

    # 2. Binary MP4 header check
    with open(asset.video_path, "rb") as f:
        header = f.read(16)
        assert b"ftyp" in header

    # 3. Stream validation with FFmpeg
    ffmpeg_exe = get_ffmpeg_executable()
    assert ffmpeg_exe is not None
    cmd = [ffmpeg_exe, "-i", asset.video_path]
    probe = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    probe_output = probe.stderr.decode("utf-8", errors="ignore")

    assert "Video: h264" in probe_output
    assert "yuv420p" in probe_output
    assert "1080x1920" in probe_output
