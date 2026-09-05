import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.hiring_intent_scraper import scrape_hiring_intent
from services.enrichment.intent_analyzer import analyze_intent

def test_intent_analyzer():
    mock_posting = {
        "company": "LiveKit",
        "website": "https://livekit.io",
        "role": "Real-time AI Streaming Engineer",
        "keywords": ["Streaming", "Latency", "AI Engineer"],
        "email": "jobs@livekit.io",
        "tech_stack": "Real-time voice and streaming inference infrastructure.",
        "full_text": "LiveKit is looking for an AI Engineer to optimize real-time streaming audio latency. Founded by Suhail Doshi."
    }
    result = analyze_intent(mock_posting)
    assert result["company"] == "LiveKit"
    assert result["website"] == "https://livekit.io"
    assert "latency" in result["tech_stack_core_pain"].lower() or "streaming" in result["tech_stack_core_pain"].lower()
    assert "Saw you are hiring" in result["intent_angle"]
    assert "linkedin.com/search" in result["linkedin_search_url"]
    assert result["contact_email"] == "jobs@livekit.io"
    assert result["status"] == "Qualified Intent"

def test_hiring_intent_scraper_run():
    leads = scrape_hiring_intent(limit=3)
    assert len(leads) >= 1
    lead = leads[0]
    required_keys = [
        "company", "website", "hiring_role", "tech_stack_core_pain",
        "founder_name", "linkedin_search_url", "contact_email", "intent_angle", "status"
    ]
    for key in required_keys:
        assert key in lead, f"Missing key '{key}' in scraped lead"
        assert lead[key] != "", f"Key '{key}' should not be empty"
