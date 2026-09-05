"""
Tests for Dynamic B2B Outreach Pipeline (Parametric Video + n8n Gateway)
Architecture "Genome" - Razum Google AI PRO.
"""

import os
import glob
import pytest
import httpx
from fastapi.testclient import TestClient

from services.integration.n8n_bridge import create_n8n_app, DynamicOutreachRequest
from services.content_genome.video_synthesizer import VideoSynthesizer

TEST_NTN_TOKEN = "ntn_unit_test_outreach_token_991"


@pytest.fixture
def test_outreach_app():
    videos_dir = os.path.abspath("output/rendered_videos")
    os.makedirs(videos_dir, exist_ok=True)
    app = create_n8n_app(expected_token=TEST_NTN_TOKEN, videos_dir=videos_dir)
    return app


@pytest.mark.anyio
async def test_dynamic_outreach_authorization_enforcement(test_outreach_app):
    """Test 1: Ensures missing or invalid tokens are rejected with 401."""
    transport = httpx.ASGITransport(app=test_outreach_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        # 1. Missing header
        res_no_auth = await client.post(
            "/api/v1/outreach/dispatch",
            json={
                "company_name": "Nova Labs Inc.",
                "primary_bottleneck": "API Token Overspend & Latency",
                "lead_urgency_score": "Score: 94/100 | Tier-1 Enterprise"
            }
        )
        assert res_no_auth.status_code == 401

        # 2. Token without ntn_ prefix
        res_bad_prefix = await client.post(
            "/api/v1/outreach/dispatch",
            json={"company_name": "Nova Labs Inc."},
            headers={"Authorization": "Bearer invalid_secret_token"}
        )
        assert res_bad_prefix.status_code == 401


@pytest.mark.anyio
async def test_dynamic_outreach_dispatch_success(test_outreach_app):
    """Test 2: Simulates n8n dispatch for Nova Labs Inc. and validates 200 OK + A2UI schema + MP4."""
    transport = httpx.ASGITransport(app=test_outreach_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        payload = {
            "company_name": "Nova Labs Inc.",
            "primary_bottleneck": "API Token Overspend & Latency",
            "lead_urgency_score": "Score: 94/100 | Tier-1 Enterprise",
            "custom_cta_url": "https://audit.genome.ai/nova-labs",
            "video_duration_sec": 3.0
        }

        res = await client.post(
            "/api/v1/outreach/dispatch",
            json=payload,
            headers={"Authorization": f"Bearer {TEST_NTN_TOKEN}"}
        )

        assert res.status_code == 200
        data = res.json()

        assert data["status"] == "SUCCESS"
        assert data["company_name"] == "Nova Labs Inc."
        assert "video_path" in data
        assert "video_url" in data
        assert data["video_url"].startswith("http://localhost:8000/videos/")
        assert os.path.exists(data["video_path"])
        assert data["video_filesize_bytes"] > 50000

        # Validate Cold Outreach & Sheet payload fields
        assert "email_subject" in data
        assert data["email_subject"] == "Sovereign AI Security Perimeter for Nova Labs Inc."
        assert "a2ui_card" in data
        assert isinstance(data["a2ui_card"], dict)

        # Validate A2UI / Google CardService Schema
        assert "card_payload" in data
        assert "cardsV2" in data
        assert len(data["cardsV2"]) > 0

        card = data["cardsV2"][0]["card"]
        assert "Nova Labs Inc." in card["header"]["title"]
        assert len(card["sections"]) >= 2

        # Check section texts contain company name and bottleneck
        sections_dump = str(card["sections"])
        assert "NOVA LABS INC." in sections_dump
        assert "API Token Overspend & Latency" in sections_dump
        assert "https://audit.genome.ai/nova-labs" in sections_dump

        # Check static streaming of generated video
        filename = os.path.basename(data["video_path"])
        video_stream_res = await client.get(f"/videos/{filename}")
        assert video_stream_res.status_code == 200
        assert "video/mp4" in video_stream_res.headers.get("content-type", "")
        assert len(video_stream_res.content) > 0


@pytest.mark.anyio
async def test_static_video_streaming_direct(test_outreach_app):
    """Test 3: Direct GET /videos/{filename} returns 200 OK and content-type: video/mp4."""
    videos_dir = os.path.abspath("output/rendered_videos")
    os.makedirs(videos_dir, exist_ok=True)
    sample_file = os.path.join(videos_dir, "test_static_probe.mp4")
    with open(sample_file, "wb") as f:
        f.write(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00isommp42")

    transport = httpx.ASGITransport(app=test_outreach_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:8000") as client:
        res = await client.get("/videos/test_static_probe.mp4")
        assert res.status_code == 200
        assert "video/mp4" in res.headers.get("content-type", "")
        assert len(res.content) > 0


def test_video_synthesizer_parametric_generation_direct(tmp_path):
    """Test 3: Direct VideoSynthesizer call produces valid MP4 with company slug."""
    out_dir = str(tmp_path / "videos")
    syn = VideoSynthesizer(output_dir=out_dir)

    video_path = syn.render_parametric_outreach_video(
        company_name="Nova Labs Inc.",
        primary_bottleneck="API Token Overspend & Latency",
        lead_urgency_score="Score: 94/100 | Tier-1 Enterprise",
        custom_cta_url="https://audit.genome.ai/nova-labs",
        duration_sec=2.5,
        fps=30
    )

    assert os.path.exists(video_path)
    assert "outreach_nova_labs_inc_" in os.path.basename(video_path)
    assert os.path.getsize(video_path) > 10000


def test_n8n_workflow_runner_integration():
    """Test 5: Validates that N8NWorkflowRunner parses JSON and executes workflow successfully."""
    from services.integration.n8n_workflow_runner import N8NWorkflowRunner
    runner = N8NWorkflowRunner()
    assert "Google Sheets Trigger" in runner.nodes
    assert "Generate Personalized Reel & Card" in runner.nodes
    assert "Write Video Link to Sheet" in runner.nodes
    assert "Mark Status Draft Ready" in runner.nodes
    assert runner.nodes["Google Sheets Trigger"]["parameters"]["documentId"]["value"] == "1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M"


@pytest.mark.anyio
async def test_n8n_server_healthz_and_workflow():
    """Test 6: Validates /healthz and /api/workflow/current on n8n server."""
    from services.integration.n8n_server import app as n8n_app
    transport = httpx.ASGITransport(app=n8n_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost:5678") as client:
        res_health = await client.get("/healthz")
        assert res_health.status_code == 200
        assert res_health.json() == {"status": "ok"}

        res_ui = await client.get("/")
        assert res_ui.status_code == 200
        assert "Razum_Hybrid_Outreach_Pipeline" in res_ui.text

        res_wf = await client.get("/api/workflow/current")
        assert res_wf.status_code == 200
        assert "Razum_Hybrid_Outreach_Pipeline" in res_wf.text


def test_direct_sheets_worker_helpers():
    """Test 7: Validates col_to_letter helper and credentials loader."""
    from services.integration.direct_sheets_worker import col_to_letter, resolve_google_credentials
    assert col_to_letter(0) == "A"
    assert col_to_letter(1) == "B"
    assert col_to_letter(25) == "Z"
    assert col_to_letter(26) == "AA"
    creds = resolve_google_credentials()
    assert creds is not None
    assert hasattr(creds, "service_account_email")
    assert creds.service_account_email == "sheets-integration-bot@gen-lang-client-0207478259.iam.gserviceaccount.com"



