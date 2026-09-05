"""
Tests for Canonical NotebookLM Knowledge Base Verification.
Validates:
1. YAML frontmatter contains authority_level: "CANONICAL_TRUTH".
2. STRICT_BOUNDARIES block exists and contains [NO_GROUNDED_DATA] instruction.
3. Required parameters and structured tables exist in all 5 canonical directories.
"""

import os
import re
import pytest

REQUIRED_FILES = [
    "01_STRATEGY/SYSTEM_GENOME_STATE.md",
    "02_BRAND/VISUAL_DNA_REGISTRY.md",
    "03_CRM/CRM_PIPELINE_SPECIFICATION.md",
    "04_PLAYBOOK/LEAD_SCORING_HORMOZI.md",
    "05_CONTENT/CONTENT_PRODUCTION_MATRIX.md",
]


@pytest.fixture
def workspace_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_knowledge_base_files_exist(workspace_root):
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(workspace_root, rel_path)
        assert os.path.exists(full_path), f"File {rel_path} does not exist!"
        assert os.path.getsize(full_path) > 300, f"File {rel_path} is too small or empty!"


def test_yaml_frontmatter_canonical_truth(workspace_root):
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(workspace_root, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check frontmatter
        assert content.startswith("---"), f"{rel_path} does not start with YAML frontmatter!"
        frontmatter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
        assert frontmatter_match is not None, f"Could not parse frontmatter in {rel_path}!"
        
        fm = frontmatter_match.group(1)
        assert 'authority_level: "CANONICAL_TRUTH"' in fm or "authority_level: 'CANONICAL_TRUTH'" in fm, \
            f"Missing canonical authority_level in {rel_path}!"


def test_strict_boundaries_and_token(workspace_root):
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(workspace_root, rel_path)
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "## STRICT_BOUNDARIES" in content, f"Missing '## STRICT_BOUNDARIES' section in {rel_path}!"
        assert "[NO_GROUNDED_DATA]" in content, f"Missing '[NO_GROUNDED_DATA]' instruction in {rel_path}!"


def test_hormozi_scoring_table_parameters(workspace_root):
    playbook_file = os.path.join(workspace_root, "04_PLAYBOOK/LEAD_SCORING_HORMOZI.md")
    with open(playbook_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify 4 dimensions of Hormozi scoring
    assert "Pain" in content
    assert "Power" in content
    assert "Decision" in content
    assert "Urgency" in content
    assert "$100,000+" in content
    assert "Tier 1" in content


def test_visual_dna_brand_tokens(workspace_root):
    brand_file = os.path.join(workspace_root, "02_BRAND/VISUAL_DNA_REGISTRY.md")
    with open(brand_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify brand tokens
    assert "#0a0a0c" in content
    assert "#00f0ff" in content
    assert "#d4af37" in content
    assert "Ver Sacrum" in content
    assert "1080x1920" in content
