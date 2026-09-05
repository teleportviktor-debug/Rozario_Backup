"""
Tests for NotebookLM Auto-Sync Engine (Agent 5 - QA & Verification).
Verifies:
1. Exact mapping of 5 directories to their corresponding Notebook IDs.
2. Sanitization of content (binary control character removal while preserving YAML frontmatter).
3. Deduplication logic (skips unchanged content, calls refresh on changes).
4. Exponential backoff retry mechanism on network / quota errors.
5. Persistent sync ledger generation in sync_ledger.json.
"""

import os
import json
import pytest
from services.evolution.notebooklm_exporter import NotebookLMAutoSync, NOTEBOOK_MAPPING


@pytest.fixture
def temp_sync_env(tmp_path):
    root = tmp_path / "workspace"
    root.mkdir()
    ledger = str(tmp_path / "ledger" / "sync_ledger.json")

    # Create dummy canonical dirs
    for folder in NOTEBOOK_MAPPING.keys():
        fdir = root / folder
        fdir.mkdir()
        # Create a sample markdown file
        doc = fdir / "TEST_DOC.md"
        doc.write_text(
            "---\nauthority_level: \"CANONICAL_TRUTH\"\n---\n# Sample Doc\n\n## STRICT_BOUNDARIES\n[NO_GROUNDED_DATA]",
            encoding="utf-8"
        )

    return str(root), ledger


def test_notebook_mapping_contract():
    expected = {
        "01_STRATEGY": "notebooks/f616009b-aee3-4002-aeef-b5fed3975ce7",
        "02_BRAND": "notebooks/6a67491f-3cc2-4ccf-a2af-d67dd25171f8",
        "03_CRM": "notebooks/a8546f6f-d37d-4c51-a394-2f5193a6f9fb",
        "04_PLAYBOOK": "notebooks/fa1411c4-bf25-47d9-bdea-d42b23d95185",
        "05_CONTENT": "notebooks/e2628ca6-8790-470d-863c-8f96c56e08fb",
    }
    assert NOTEBOOK_MAPPING == expected


def test_content_sanitization_removes_binary_noise():
    sync = NotebookLMAutoSync()
    raw = "---\nauthority_level: \"CANONICAL_TRUTH\"\n---\n# Header\x00\x07\x1b\nLine text\twith tabs and\r\nnewlines."
    clean = sync.sanitize_content(raw)

    assert "\x00" not in clean
    assert "\x07" not in clean
    assert "\x1b" not in clean
    assert 'authority_level: "CANONICAL_TRUTH"' in clean
    assert "# Header" in clean
    assert "\t" in clean


def test_sync_deduplication_and_refresh(temp_sync_env):
    root, ledger_file = temp_sync_env
    sync = NotebookLMAutoSync(workspace_root=root, ledger_path=ledger_file)

    test_file = os.path.join(root, "01_STRATEGY", "TEST_DOC.md")
    notebook_id = NOTEBOOK_MAPPING["01_STRATEGY"]

    # 1. First sync -> CREATE_SOURCE
    res1 = sync.sync_source(test_file, notebook_id)
    assert res1["status"] == "SYNCED"
    assert res1["action"] == "CREATE_SOURCE"
    assert "source_id" in res1
    src_id = res1["source_id"]

    # 2. Immediate second sync without edits -> SKIPPED_NO_CHANGE
    res2 = sync.sync_source(test_file, notebook_id)
    assert res2["status"] == "UP_TO_DATE"
    assert res2["action"] == "SKIPPED_NO_CHANGE"
    assert res2["source_id"] == src_id

    # 3. Edit file content -> REFRESH_SOURCE with same source_id
    with open(test_file, "a", encoding="utf-8") as f:
        f.write("\n\nUpdated new content section.")

    res3 = sync.sync_source(test_file, notebook_id)
    assert res3["status"] == "SYNCED"
    assert res3["action"] == "REFRESH_SOURCE"
    assert res3["source_id"] == src_id

    # 4. Verify persistent ledger
    assert os.path.exists(ledger_file)
    with open(ledger_file, "r", encoding="utf-8") as f:
        ledger_data = json.load(f)

    file_key = f"{notebook_id}::TEST_DOC.md"
    assert file_key in ledger_data["sources"]
    assert len(ledger_data["sync_history"]) == 2  # 1 CREATE + 1 REFRESH


def test_exponential_backoff_retry():
    sync = NotebookLMAutoSync(max_retries=2, base_backoff_sec=0.01)

    attempts = 0

    def mock_flaky_send(payload):
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise TimeoutError("Simulated 429 Quota Exceeded")
        return {"source_id": payload["source_id"], "status": "SUCCESS"}

    sync._send_http_request = mock_flaky_send

    res = sync._dispatch_api_with_backoff(
        action="CREATE_SOURCE",
        notebook_id="test_nb",
        source_id="test_src",
        title="Doc",
        content="Hello"
    )
    assert res["status"] == "SUCCESS"
    assert attempts == 2
    assert res["retries"] == 1
