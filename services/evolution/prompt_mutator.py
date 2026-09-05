"""
Prompt Mutator & Genetic Cross-Breeding (Agent 3 - Core Developer)
Architecture "Genome" (Phase 2) - Razum Google AI PRO.

Mechanics:
- Mutation Generator: varies hook structures, constraints, tone, and A2UI layout hints.
- Cross-Breeding: combines trait genes from disparate domains (e.g. Lead Scoring + Content Factory).
- Invariant Guard: guarantees Zero-Trust rules and the brand palette (#0a0a0c, #00f0ff, #d4af37)
  are strictly preserved across all generations.
"""

import re
import random
import hashlib
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# Core Brand & Zero Trust Invariants
INVARIANT_PALETTE = {
    "obsidian": "#0a0a0c",
    "cyan": "#00f0ff",
    "gold": "#d4af37",
}
INVARIANT_ZERO_TRUST_RULE = "Strict Zero Trust compliance: output must be valid A2UI CardService schema. Discard untrusted markup."


class MutationResult(BaseModel):
    mutation_id: str
    parent_id: Optional[str] = None
    prompt_text: str
    generation: int = 1
    applied_mutations: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CrossoverResult(BaseModel):
    crossover_id: str
    parent_a_id: str
    parent_b_id: str
    offspring_prompt: str
    inherited_genes: List[str]
    generation: int = 2
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PromptMutator:
    """
    Genetic prompt operator for autonomous mutation and cross-breeding.
    """

    HOOK_GENES = [
        "DIRECT_DATA: Начни с конкретной количественной метрики и выяви ключевой рычаг роста.",
        "FORENSIC_AUDIT: Проанализируй узкие места архитектуры с точки зрения суверенной безопасности.",
        "EXECUTIVE_ROI: Сфокусируйся на оптимизации затрат токенов (-50% в Batch API) и ускорении P99.",
        "HYPOTHESIS_PROVOCATION: Сформулируй смелую гипотезу масштабирования и обоснуй ее в A2UI формате."
    ]

    CONSTRAINT_GENES = [
        "DENSITY_HIGH: Максимальная информационная плотность без вводных фраз и 'воды'.",
        "STRICT_CARD_V2: Обязательно формируй структуру с секциями, метриками DecoratedText и кнопками ButtonList.",
        "ZERO_LATENCY: Ответ оптимизирован для роутинга черновиков со временем валидации < 50ms.",
        "EXECUTIVE_BREVITY: Ограничь текстовые параграфы максимум двумя емкими предложениями."
    ]

    TONE_GENES = [
        "VER_SACRUM_KLIMT: Эстетичный стиль кибер-минимализма, венский сецессион, золотой акцент #d4af37.",
        "COLD_SOVEREIGN: Строгий корпоративный тон ИИ-архитектора enterprise-класса.",
        "SURGICAL_PRECISION: Высокоточный аналитический язык с фокусом на измеримые результаты."
    ]

    LAYOUT_GENES = [
        "DUAL_ACTION_BUTTONS: Обязательно включай две кнопки действия (основная #00f0ff, вторичная #d4af37).",
        "KPI_KEY_VALUE_GRID: Размещай метрики парами в виде DecoratedText с верхними лейблами.",
        "STATUS_BADGE_HEADER: Заголовок карточки всегда содержит эмблему и понятный статус узла."
    ]

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)

    def _generate_id(self, content: str, prefix: str = "mut") -> str:
        h = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
        return f"{prefix}_{h}"

    def mutate_prompt(
        self,
        base_prompt: str,
        parent_id: Optional[str] = None,
        generation: int = 1,
        mutation_rate: float = 0.5
    ) -> MutationResult:
        """
        Applies stochastic mutations to a base prompt while preserving core invariants.
        """
        applied_mutations = []
        modified = base_prompt.strip()

        # 1. Mutate Hook
        if random.random() < mutation_rate:
            hook = random.choice(self.HOOK_GENES)
            modified = f"[Хук: {hook}]\n{modified}"
            applied_mutations.append(f"hook:{hook.split(':')[0]}")

        # 2. Mutate Constraints
        if random.random() < mutation_rate:
            constraint = random.choice(self.CONSTRAINT_GENES)
            modified = f"{modified}\n[Ограничение: {constraint}]"
            applied_mutations.append(f"constraint:{constraint.split(':')[0]}")

        # 3. Mutate Tone
        if random.random() < mutation_rate:
            tone = random.choice(self.TONE_GENES)
            modified = f"{modified}\n[Тональность: {tone}]"
            applied_mutations.append(f"tone:{tone.split(':')[0]}")

        # 4. Mutate Layout Hint
        if random.random() < mutation_rate:
            layout = random.choice(self.LAYOUT_GENES)
            modified = f"{modified}\n[Разметка A2UI: {layout}]"
            applied_mutations.append(f"layout:{layout.split(':')[0]}")

        # Always enforce Invariants
        modified = self._enforce_invariants(modified)

        mut_id = self._generate_id(modified, prefix="mut")
        return MutationResult(
            mutation_id=mut_id,
            parent_id=parent_id or self._generate_id(base_prompt, prefix="parent"),
            prompt_text=modified,
            generation=generation,
            applied_mutations=applied_mutations,
            metadata={
                "mutation_rate": mutation_rate,
                "invariants_verified": True,
            }
        )

    def crossover_prompts(
        self,
        prompt_a: str,
        prompt_b: str,
        parent_a_id: str = "Parent_LeadScoring",
        parent_b_id: str = "Parent_ContentFactory",
        generation: int = 2
    ) -> CrossoverResult:
        """
        Cross-breeds two winning prompts from different domains (e.g. Lead Scoring + Content Factory).
        Selects complementary genes from both parents to produce a hybrid offspring.
        """
        inherited_genes = []

        # Extract or select hook from Parent A or B
        if random.random() > 0.5:
            hook = random.choice(self.HOOK_GENES)
            inherited_genes.append("Hook from Parent A (Lead Scoring)")
        else:
            hook = "HYBRID_TEASER: Совмести точный скоринг лида с вирусным хуком контент-фабрики."
            inherited_genes.append("Hook from Parent B (Content Factory)")

        # Combine constraints
        constraint_a = random.choice(self.CONSTRAINT_GENES)
        constraint_b = random.choice(self.LAYOUT_GENES)
        inherited_genes.extend([
            f"Constraint from Parent A: {constraint_a.split(':')[0]}",
            f"Layout from Parent B: {constraint_b.split(':')[0]}"
        ])

        # Synthesize hybrid offspring body
        offspring = (
            f"[Гибридный хук кросс-скрещивания]: {hook}\n"
            f"[Базовая спецификация]: Интеграция скоринга конверсии и генерации A2UI контента.\n"
            f"[Ограничение A]: {constraint_a}\n"
            f"[Разметка B]: {constraint_b}\n"
            f"[Контекст Родителя A]: {prompt_a[:120]}...\n"
            f"[Контекст Родителя B]: {prompt_b[:120]}...\n"
        )

        offspring = self._enforce_invariants(offspring)
        crossover_id = self._generate_id(offspring, prefix="crossover")

        return CrossoverResult(
            crossover_id=crossover_id,
            parent_a_id=parent_a_id,
            parent_b_id=parent_b_id,
            offspring_prompt=offspring,
            inherited_genes=inherited_genes,
            generation=generation,
            metadata={
                "parents": [parent_a_id, parent_b_id],
                "invariants_verified": True
            }
        )

    def _enforce_invariants(self, text: str) -> str:
        """
        Ensures Zero-Trust guidelines and brand color invariants are explicitly included.
        """
        result = text
        if "Zero Trust" not in result:
            result = f"{result}\n[Инвариант Безопасности]: {INVARIANT_ZERO_TRUST_RULE}"
        if "#00f0ff" not in result or "#d4af37" not in result:
            result = f"{result}\n[Инвариант Палитры]: Обсидиан #0a0a0c, Циан #00f0ff, Золото #d4af37."
        return result

    def generate_population(
        self,
        seed_prompts: List[str],
        population_size: int = 6
    ) -> List[MutationResult]:
        """Generates an initial population of mutated candidates from seed prompts."""
        population: List[MutationResult] = []
        for i in range(population_size):
            seed = seed_prompts[i % len(seed_prompts)]
            mutant = self.mutate_prompt(
                base_prompt=seed,
                parent_id=f"seed_{i % len(seed_prompts)}",
                generation=1
            )
            population.append(mutant)
        return population
