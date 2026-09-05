"""
End-to-End Tests for n8n Bridge Gateway (Agent 5 - QA & Security)
Verifies:
1. Security: Rejection of requests lacking token or with non-ntn tokens (401).
2. Successful Authorization: Bearer ntn_test_secret_key returns 200 OK with valid A2UI JSON.
3. Background Harvest: Verifies asynchronous recording of (fast_draft, deep_response)
   pair in /registry/genome_vault/harvest.jsonl.
"""

import os
import json
import asyncio
import pytest
import httpx
from services.integration.n8n_bridge import create_n8n_app
from services.router.racing_router import RacingRouter
from services.schemas.card_service import (
    A2UICardPayload,
    CardSection,
    CardWidget,
)

TEST_SECRET_TOKEN = "ntn_test_secret_key_888"


@pytest.fixture
def mock_router(tmp_path):
    vault_dir = str(tmp_path / "genome_vault")
    racing_dir = str(tmp_path / "racing_logs")

    async def fast_gen(prompt: str, ctx: dict):
        await asyncio.sleep(0.02)
        return A2UICardPayload(
            card_id="fast_harvest_card",
            title=f"Fast: {prompt}",
            subtitle="Rapid Engine",
            style_theme="OBSIDIAN_CYAN",
            sections=[
                CardSection(
                    header="Fast",
                    widgets=[CardWidget(widget_type="textParagraph", text="Fast draft")]
                )
            ]
        )

    async def deep_gen(prompt: str, ctx: dict):
        await asyncio.sleep(0.08)
        return A2UICardPayload(
            card_id="deep_harvest_card",
            title=f"Deep: {prompt}",
            subtitle="Deep Reasoning",
            style_theme="OBSIDIAN_CYAN",
            sections=[
                CardSection(
                    header="Deep",
                    widgets=[CardWidget(widget_type="textParagraph", text="Deep validated")]
                )
            ]
        )

    router = RacingRouter(
        fast_worker=fast_gen,
        deep_worker=deep_gen,
        log_dir=racing_dir
    )
    router.vault_dir = vault_dir
    return router


@pytest.fixture
def test_app(mock_router):
    return create_n8n_app(router=mock_router, expected_token=TEST_SECRET_TOKEN)


@pytest.mark.anyio
async def test_zero_trust_security_rejections(test_app):
    """Test 1: Requests without token or with invalid formats are rejected with 401."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Missing header
        res1 = await client.post("/api/v1/a2ui/render", json={"prompt": "Test Prompt"})
        assert res1.status_code == 401
        assert "Missing" in res1.json()["detail"]

        # 2. Token without ntn_ prefix
        res2 = await client.post(
            "/api/v1/a2ui/render",
            json={"prompt": "Test Prompt"},
            headers={"Authorization": "Bearer invalid_secret_token"}
        )
        assert res2.status_code == 401
        assert "ntn_" in res2.json()["detail"]

        # 3. Wrong ntn_ secret key
        res3 = await client.post(
            "/api/v1/a2ui/render",
            json={"prompt": "Test Prompt"},
            headers={"Authorization": "Bearer ntn_wrong_secret_key"}
        )
        assert res3.status_code == 401
        assert "credentials" in res3.json()["detail"] or "mismatch" in res3.json()["detail"]


@pytest.mark.anyio
async def test_successful_authorized_render(test_app):
    """Test 2: Valid Authorization header returns 200 OK and valid A2UI / Google CardService JSON."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/a2ui/render",
            json={
                "prompt": "Autonomous AI Banking Lead",
                "user_context": {"lead_score": 99.2, "region": "EU"},
                "widget_type": "a2ui_card",
                "style_theme": "OBSIDIAN_CYAN"
            },
            headers={"Authorization": f"Bearer {TEST_SECRET_TOKEN}"}
        )

        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "card_payload" in data
        assert "cardsV2" in data
        assert len(data["cardsV2"]) >= 1

        payload = data["card_payload"]
        assert "Fast: Autonomous AI Banking Lead" in payload["title"]
        assert payload["card_id"] == "fast_harvest_card"


@pytest.mark.anyio
async def test_data_first_harvest_persistence(test_app, mock_router):
    """Test 3: Checks that the genome pair is harvested into harvest.jsonl with timestamp and both results."""
    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/v1/a2ui/render",
            json={
                "prompt": "Harvest Verification Cluster",
                "user_context": {"cluster_id": "CLS-994"}
            },
            headers={"Authorization": f"Bearer {TEST_SECRET_TOKEN}"}
        )
        assert res.status_code == 200

    # Allow non-blocking background shadow worker & harvest write to complete
    await asyncio.sleep(0.2)

    harvest_file = os.path.join(mock_router.vault_dir, "harvest.jsonl")
    assert os.path.exists(harvest_file), f"Harvest file {harvest_file} was not created!"

    with open(harvest_file, "r", encoding="utf-8") as f:
        records = [json.loads(line.strip()) for line in f if line.strip()]

    assert len(records) >= 1
    rec = records[-1]

    # Verify genome record structure
    assert "timestamp" in rec
    assert rec["prompt"] == "Harvest Verification Cluster"
    assert "fast_result" in rec
    assert "deep_result" in rec
    assert rec["fast_result"]["card_id"] == "fast_harvest_card"
    assert rec["deep_result"]["card_id"] == "deep_harvest_card"
    assert "latency_diff_ms" in rec
    assert rec["latency_diff_ms"] >= 0
