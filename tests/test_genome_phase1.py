"""
Pytest Suite for Genome Architecture Phase 1 (QA & Genome Agent 5)
Verifies:
1. Pydantic CardService v2 schemas integrity.
2. Absence of hallucinations in generated JSON.
3. Absence of unescaped or illegal characters.
4. Correct transpilation of JSX and AST by SurgeonTranspiler.
"""

import pytest
import json
from services.schemas.card_service import (
    GoogleWorkspaceCardMessage,
    CardItemV2,
    Card,
    CardHeader,
    Section,
    Widget,
    TextParagraph,
    DecoratedText,
    ButtonList,
    Button,
    Image,
    Color,
    COLOR_OBSIDIAN,
    COLOR_NEON_CYAN,
    COLOR_KLIMT_GOLD,
)
from services.surgeon.surgeon_transpiler import SurgeonTranspiler


def test_pydantic_color_hex_conversion():
    cyan = Color.from_hex(COLOR_NEON_CYAN)
    assert cyan.red == 0.0
    assert cyan.green > 0.9
    assert cyan.blue == 1.0

    gold = Color.from_hex(COLOR_KLIMT_GOLD)
    assert gold.red > 0.8
    assert gold.green > 0.6
    assert gold.blue > 0.2


def test_widget_validator_rejects_empty():
    with pytest.raises(ValueError):
        Widget()


def test_surgeon_transpile_jsx():
    transpiler = SurgeonTranspiler()
    jsx_sample = """
    <div className="bg-[#0a0a0c] text-white p-6">
      <div className="flex items-center gap-3">
        <img src="https://razum.ai/icon.png" alt="Genome Core" />
        <div>
          <h2 className="text-xl font-bold text-[#00f0ff]">Razum Quantum Node</h2>
          <p className="text-xs text-[#d4af37]">Autonomous Execution Cluster</p>
        </div>
      </div>
      <div className="flex justify-between items-center py-2">
        <span className="text-gray-400">Node Status</span>
        <span className="text-cyan-400">ONLINE_ACTIVE</span>
      </div>
      <p className="mt-4 text-gray-300">
        System synchronized with <b>Zero Trust</b> gateway. All channels operational.
      </p>
      <div className="mt-6 flex gap-2">
        <a href="https://razum.ai/telemetry" className="text-[#00f0ff]">Telemetry</a>
        <button className="text-[#d4af37]">Deploy Mutation</button>
      </div>
    </div>
    """

    card_msg = transpiler.transpile(jsx_sample)
    assert isinstance(card_msg, GoogleWorkspaceCardMessage)
    assert len(card_msg.cardsV2) == 1

    card = card_msg.cardsV2[0].card
    assert "Razum Quantum Node" in card.header.title
    assert "Autonomous Execution Cluster" in card.header.subtitle
    assert card.header.imageUrl == "https://razum.ai/icon.png"

    json_dict = card_msg.to_json_dict()
    # Check no React/Tailwind hallucinations leaked into JSON keys
    raw_json_str = json.dumps(json_dict)
    assert "className" not in raw_json_str
    assert "style=" not in raw_json_str
    assert "flex" not in json_dict


def test_surgeon_transpile_ast():
    transpiler = SurgeonTranspiler()
    ast_sample = {
        "title": "Agentic Genome Lead",
        "subtitle": "High-Value Enterprise AI Lead",
        "iconUrl": "https://razum.ai/lead.png",
        "elements": [
            {
                "type": "decoratedText",
                "topLabel": "Lead Score",
                "text": "98.5 / 100",
                "bottomLabel": "VIP Tier"
            },
            {
                "type": "textParagraph",
                "text": "Enterprise client requested immediate A2UI integration."
            },
            {
                "type": "button",
                "text": "Open Client Dossier",
                "url": "https://workspace.google.com",
                "isGold": True
            }
        ]
    }

    card_msg = transpiler.transpile(ast_sample)
    assert isinstance(card_msg, GoogleWorkspaceCardMessage)
    
    sections = card_msg.cardsV2[0].card.sections
    assert len(sections) >= 1
    widgets = sections[0].widgets
    assert len(widgets) == 3
    assert widgets[0].decoratedText.topLabel == "Lead Score"
    assert "98.5" in widgets[0].decoratedText.text
    assert widgets[1].textParagraph.text == "Enterprise client requested immediate A2UI integration."
    assert widgets[2].buttonList.buttons[0].text == "Open Client Dossier"


def test_html_sanitization_no_hallucinations():
    transpiler = SurgeonTranspiler()
    dirty_text = '<div onclick="alert(1)">Hello <script>bad()</script> <b class="bold">Razum</b> <span style="color:red">Cyber</span></div>'
    sanitized = transpiler._sanitize_html(dirty_text)
    
    # Only allowed tags (b, i, u, font, a, br) and no scripts or style attributes
    assert "<script>" not in sanitized
    assert "alert" not in sanitized
    assert "onclick" not in sanitized
    assert "<b>Razum</b>" in sanitized
    assert "Cyber" in sanitized


def test_no_unescaped_characters_and_strict_spec():
    transpiler = SurgeonTranspiler()
    jsx_with_symbols = """
    <div>
      <p>Razum AI & Gemini Flash 2.5: High-speed throughput > 99.9% & latency < 120ms.</p>
    </div>
    """
    card_msg = transpiler.transpile(jsx_with_symbols)
    json_str = card_msg.to_json_str()

    # Verify JSON deserializes cleanly without decoding issues
    parsed = json.loads(json_str)
    assert "cardsV2" in parsed
    card = parsed["cardsV2"][0]["card"]
    assert "header" in card
    assert "sections" in card

    # Ensure no control characters or invalid JSON artifacts
    assert "\\u0000" not in json_str
    assert "\t" not in card["sections"][0]["widgets"][0]["textParagraph"]["text"]


@pytest.mark.anyio
async def test_racing_router_first_completed():
    from services.router.racing_router import RacingRouter

    router = RacingRouter(
        primary_model="gemini-2.5-flash",
        fallback_model="gemini-2.0-flash-lite"
    )

    # Fast primary (10ms) vs slow fallback (100ms)
    winner = await router.race_models(
        prompt="Generate Genome Lead Card",
        primary_delay=0.01,
        fallback_delay=0.1
    )

    assert winner.model_name == "gemini-2.5-flash"
    assert winner.status == "SUCCESS"
    assert winner.latency_ms < 100.0


def test_n8n_bridge_token_validation():
    from services.router.n8n_bridge import N8NBridge

    # Valid token starting with ntn_
    bridge = N8NBridge(token="ntn_production_secure_token_999")
    headers = bridge.get_auth_headers()
    assert headers["X-N8N-Integration-Token"] == "ntn_production_secure_token_999"
    assert "Bearer ntn_production_secure_token_999" in headers["Authorization"]

    # Inbound verification
    assert bridge.verify_inbound_request({"X-N8N-Integration-Token": "ntn_production_secure_token_999"}) is True
    assert bridge.verify_inbound_request({"X-N8N-Integration-Token": "ntn_wrong_token"}) is False
    assert bridge.verify_inbound_request({}) is False

    # Rejection of invalid prefix
    with pytest.raises(ValueError, match="Invalid n8n integration token format"):
        N8NBridge(token="invalid_prefix_token_123")


def test_a2ui_card_payload_transpilation():
    from services.schemas.card_service import (
        A2UICardPayload,
        CardSection,
        CardWidget,
        WidgetButton,
    )
    from services.surgeon.surgeon_transpiler import SurgeonTranspiler

    payload = A2UICardPayload(
        card_id="genome_lead_99",
        title="Enterprise Lead Discovery",
        subtitle="Tier 1 Banking Client",
        style_theme="OBSIDIAN_CYAN",
        sections=[
            CardSection(
                header="Pipeline Metrics",
                widgets=[
                    CardWidget(
                        widget_type="decoratedText",
                        top_label="Pipeline Latency",
                        text="42ms",
                        bottom_label="P99 SLA Verified"
                    ),
                    CardWidget(
                        widget_type="textParagraph",
                        text="High throughput Zero Trust routing node active."
                    ),
                    CardWidget(
                        widget_type="buttonList",
                        buttons=[
                            WidgetButton(
                                text="Open Portal",
                                action_type="OPEN_URL",
                                url="https://razum.ai/portal"
                            )
                        ]
                    )
                ]
            )
        ]
    )

    # Direct model conversion
    msg1 = payload.to_card_service_message()
    assert isinstance(msg1, GoogleWorkspaceCardMessage)
    assert msg1.cardsV2[0].cardId == "genome_lead_99"
    assert "Enterprise Lead Discovery" in msg1.cardsV2[0].card.header.title

    # SurgeonTranspiler ingestion
    transpiler = SurgeonTranspiler()
    msg2 = transpiler.transpile(payload)
    assert isinstance(msg2, GoogleWorkspaceCardMessage)
    assert len(msg2.cardsV2[0].card.sections) == 1
    widgets = msg2.cardsV2[0].card.sections[0].widgets
    assert len(widgets) == 3
    assert widgets[0].decoratedText.topLabel == "Pipeline Latency"
    assert widgets[2].buttonList.buttons[0].text == "Open Portal"



