import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.linkedin.content_generator import generate_linkedin_post, generate_card_html
from services.linkedin.card_renderer import render_card_to_png, OUTPUT_DIR

def test_content_generator():
    topic = "Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)"
    keyword = "ROUTER"
    
    bundle = generate_linkedin_post(topic=topic, keyword=keyword)
    assert bundle["topic"] == topic
    assert bundle["keyword"] == keyword
    assert "Streaming latency" in bundle["post_text"]
    assert keyword in bundle["post_text"]
    assert len(bundle["post_text"]) > 200

    html = generate_card_html(topic=topic, keyword=keyword)
    assert "<!DOCTYPE html>" in html
    assert "1080px" in html
    assert "1350px" in html
    assert "SLASHING STREAMING TTFT" in html
    assert keyword in html

def test_card_renderer():
    topic = "Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)"
    html = generate_card_html(topic=topic, keyword="ROUTER")
    png_path = render_card_to_png(html, "test_verify_card.png")
    
    assert os.path.exists(png_path)
    assert os.path.getsize(png_path) > 10000

    # Clean up test artifact
    if os.path.exists(png_path):
        os.remove(png_path)
