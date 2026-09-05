import os
import wave
import pytest
import numpy as np
from PIL import Image

from services.content_genome.audio_designer import AudioDesigner
from services.content_genome.video_synthesizer import (
    VideoSynthesizer, draw_framer_glow_card, draw_interactive_input, COLOR_OBSIDIAN_FRAMER
)


def test_audio_designer_sfx_synthesis(tmp_path):
    output_dir = str(tmp_path / "audio")
    designer = AudioDesigner(output_dir=output_dir, sample_rate=22050)

    click_path = designer.generate_click_sfx()
    assert os.path.exists(click_path)
    assert os.path.getsize(click_path) > 100

    type_path = designer.generate_type_sfx()
    assert os.path.exists(type_path)
    assert os.path.getsize(type_path) > 100

    whoosh_path = designer.generate_whoosh_sfx()
    assert os.path.exists(whoosh_path)
    assert os.path.getsize(whoosh_path) > 100

    bgm_path = designer.generate_bgm_track(duration_sec=2.0)
    assert os.path.exists(bgm_path)
    assert os.path.getsize(bgm_path) > 1000

    timeline_path = designer.build_sfx_timeline_track(
        duration_sec=2.0,
        scene_timestamps=[1.0],
        typing_intervals=[(0.1, 0.8)],
        card_reveal_times=[0.5, 1.2]
    )
    assert os.path.exists(timeline_path)
    assert os.path.getsize(timeline_path) > 1000


def test_framer_card_and_input_rendering():
    base = Image.new("RGB", (640, 1136), COLOR_OBSIDIAN_FRAMER)

    # 1. Test glowing card
    card_img = draw_framer_glow_card(
        base_img=base,
        box=(40, 80, 600, 300),
        radius=24,
        glow_radius=12
    )
    assert isinstance(card_img, Image.Image)
    assert card_img.size == (640, 1136)

    # 2. Test interactive input with model selector
    input_img = draw_interactive_input(
        base_img=card_img,
        box=(40, 340, 600, 500),
        model_badge_text="Razum 3.8 / A2UI",
        prompt_text="Audit enterprise zero trust perimeter",
        blink_cursor=True
    )
    assert isinstance(input_img, Image.Image)
    assert input_img.size == (640, 1136)
