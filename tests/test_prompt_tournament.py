"""
Pytest Suite for Phase 2: Prompt Tournament, Cross-Breeding, and Batch API (Agent 5 - QA & Testing)
Verifies:
1. Mutation preserves core invariants: Zero Trust and brand palette (#0a0a0c, #00f0ff, #d4af37).
2. Cross-breeding (crossover) combines parent genes from Lead Scoring and Content Factory.
3. Batch tournament executes multi-metric fitness scoring and appends to mutation_ledger.jsonl.
4. PlaybookSync generates visual Mermaid lineage graph and NotebookLM-ready knowledge items.
"""

import os
import json
import pytest
from services.evolution.prompt_mutator import PromptMutator, MutationResult, CrossoverResult
from services.evolution.batch_tournament import BatchTournamentOrchestrator, FitnessEvaluation
from services.evolution.playbook_sync import PlaybookSync


@pytest.fixture
def mutator():
    return PromptMutator(seed=42)


@pytest.fixture
def tournament(tmp_path):
    ledger = str(tmp_path / "mutation_ledger.jsonl")
    return BatchTournamentOrchestrator(ledger_path=ledger)


def test_prompt_mutator_preserves_invariants(mutator):
    """
    Test 1: Mutator applies varied hook/constraint/layout genes while guaranteeing
    that Zero Trust and the brand palette (#00f0ff, #d4af37) are strictly preserved.
    """
    base_prompts = [
        "Сгенерируй карточку лида для финтех компании с оценкой скоринга ARR.",
        "Подготовь KPI дашборд расхода токенов и задержек в Google Cloud.",
        "Создай статус звонка голосового робота с сентиментом клиента."
    ]

    for base in base_prompts:
        mutant = mutator.mutate_prompt(base_prompt=base, mutation_rate=0.9)
        assert isinstance(mutant, MutationResult)
        assert len(mutant.mutation_id) > 0
        assert mutant.generation == 1

        # Check strict invariant preservation
        text = mutant.prompt_text
        assert "Zero Trust" in text
        assert "#00f0ff" in text
        assert "#d4af37" in text
        assert len(mutant.applied_mutations) >= 1


def test_crossover_prompts_fuses_parent_traits(mutator):
    """
    Test 2: Cross-breeding fuses genes from Lead Scoring (Parent A) and Content Factory (Parent B).
    """
    parent_a = "Скоринг B2B лидов: выяви бюджет ARR, полномочия ЛПР и срочность внедрения."
    parent_b = "Виральный контент: создай привлекательный заголовок для социальных сетей и слайдов."

    crossover = mutator.crossover_prompts(
        prompt_a=parent_a,
        prompt_b=parent_b,
        parent_a_id="Parent_LeadScoring_01",
        parent_b_id="Parent_ContentFactory_02"
    )

    assert isinstance(crossover, CrossoverResult)
    assert crossover.parent_a_id == "Parent_LeadScoring_01"
    assert crossover.parent_b_id == "Parent_ContentFactory_02"
    assert crossover.generation == 2
    assert len(crossover.inherited_genes) >= 2

    # Verify offspring contains elements from both lineages and invariants
    offspring = crossover.offspring_prompt
    assert "Zero Trust" in offspring
    assert "#00f0ff" in offspring
    assert "#d4af37" in offspring
    assert "Кросс-скрещивания" in offspring or "Гибридный" in offspring


@pytest.mark.anyio
async def test_batch_tournament_fitness_ranking_and_ledger(tournament, mutator):
    """
    Test 3: Batch API tournament evaluates candidates, ranks by fitness, and records
    complete audit trail in mutation_ledger.jsonl with -50% batch token discount.
    """
    seed_prompts = [
        "Карточка лида enterprise класса для Workspace",
        "KPI дашборд узлов кластера",
        "Инцидент безопасности Zero Trust"
    ]
    population = mutator.generate_population(seed_prompts, population_size=4)

    summary, evaluations = await tournament.execute_batch_tournament(population, generation=1)

    assert summary.candidates_count == 4
    assert len(evaluations) == 4

    # Ranking checks
    assert evaluations[0].rank == 1
    assert evaluations[0].total_score >= evaluations[1].total_score
    assert evaluations[0].schema_score > 0
    assert summary.winner_mutation_id == evaluations[0].mutation_id
    assert summary.batch_token_discount == "-50% (Google Batch API)"

    # Ledger file verification
    assert os.path.exists(tournament.ledger_path)
    with open(tournament.ledger_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) == 4
    record = json.loads(lines[0])
    assert "tournament_id" in record
    assert "mutation_id" in record
    assert "fitness_score" in record
    assert record["batch_api_discount"] == "-50%"


def test_playbook_sync_markdown_and_notebooklm_artifacts(tmp_path):
    """
    Test 4: PlaybookSync produces valid markdown report with Mermaid lineage tree,
    leaderboard, and NotebookLM knowledge section.
    """
    ledger_file = str(tmp_path / "test_ledger.jsonl")
    # Seed ledger with test entry
    with open(ledger_file, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "timestamp": 1725470000.0,
            "tournament_id": "tourn_gen1_test",
            "generation": 1,
            "mutation_id": "mut_winner_alpha",
            "rank": 1,
            "fitness_score": 96.5,
            "metrics": {
                "schema_score": 35.0,
                "speed_score": 25.0,
                "density_score": 20.0,
                "brand_score": 16.5,
                "latency_ms": 32.4
            },
            "is_valid_schema": True
        }) + "\n")

    sync = PlaybookSync(ledger_path=ledger_file)
    report_md = sync.generate_markdown_report()

    # Markdown structure verification
    assert "# 🧬 Отчет эволюционного турнира промптов" in report_md
    assert "flowchart TD" in report_md  # Mermaid lineage graph
    assert "Таблица лидеров турнира" in report_md
    assert "NotebookLM API" in report_md
    assert "Zero Trust" in report_md

    # Export test
    out_file = str(tmp_path / "PLAYBOOK_TEST.md")
    exported = sync.export_to_file(output_path=out_file)
    assert os.path.exists(exported)
    with open(exported, "r", encoding="utf-8") as f:
        saved_text = f.read()
    assert len(saved_text) > 200


@pytest.mark.anyio
async def test_evolution_start_endpoint_zero_trust_and_background_run(tmp_path):
    """
    Test 5: Validates POST /api/v1/evolution/start:
    - Rejection of invalid / missing token with 401.
    - Acceptance with 202 Accepted on valid ntn_ token.
    - Asynchronous background execution of tournament and creation of mutation records.
    """
    import httpx
    from services.integration.n8n_bridge import create_n8n_app

    test_token = "ntn_evolution_secret_999"
    app = create_n8n_app(expected_token=test_token)
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Rejection without token
        res_unauth = await client.post("/api/v1/evolution/start", json={})
        assert res_unauth.status_code == 401

        # 2. Rejection with invalid token format
        res_bad = await client.post(
            "/api/v1/evolution/start",
            json={},
            headers={"Authorization": "Bearer bad_token_no_ntn"}
        )
        assert res_bad.status_code == 401

        # 3. Successful 202 Accepted trigger
        res_ok = await client.post(
            "/api/v1/evolution/start",
            json={
                "seed_prompts": [
                    "B2B Enterprise Lead Scoring",
                    "A2UI Content Generation"
                ],
                "generations": 1,
                "population_size": 2,
                "cross_breed": True
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )

        assert res_ok.status_code == 202
        body = res_ok.json()
        assert body["status"] == "ACCEPTED"
        assert "job_id" in body
        assert "Google Batch API" in body["batch_mode"]

    # 4. Wait a brief moment for background task to complete and write ledger
    import asyncio
    await asyncio.sleep(0.3)

    ledger_path = os.path.join(os.getcwd(), "registry", "genome_vault", "mutation_ledger.jsonl")
    assert os.path.exists(ledger_path)
    with open(ledger_path, "r", encoding="utf-8") as f:
        records = [line.strip() for line in f if line.strip()]
    assert len(records) >= 1

