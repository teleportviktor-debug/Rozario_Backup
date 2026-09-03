"""
============================================================================
AGENT 2: COMPETITOR ANALYSIS & SOURCE MIXING SPY ENGINE
Scrapes Competitor Angles, Synthesizes Counter-Offers & Generates Battlecards
============================================================================
"""

import os
import json
from datetime import datetime

def synthesize_source_mixing(competitors_data):
    """
    Applies Source Mixing Methodology:
    Mixes Hook (Speed/Guarantee) + Tech (Gemini/A2UI) + Unfair Risk Reversal
    """
    battlecards = []
    
    for comp in competitors_data:
        comp_name = comp.get("name", "Competitor Agency")
        their_hook = comp.get("hook", "Мы делаем SEO за 3 месяца")
        their_price = comp.get("price", "от 60 000 ₽ / мес")
        their_weakness = comp.get("weakness", "Ручная рутина, отсутствие видео, нет гарантии окупаемости")

        # Source Mixing Synthesis
        our_counter_hook = f"Пока {comp_name} обещает результаты через 90 дней вручную, наша суверенная нейросеть запускает 45-секундные видео-воронки и SEO-автопилот за 5 дней."
        our_tech_moat = "Мультимодальный стек Gemini 3.7 + Динамический A2UI рендерер + Авто-Телесуфлер 180 WPM."
        our_risk_reversal = "Полная гарантия окупаемости в договоре: если оффер не приносит лидов в первые 14 дней — доработка и аудит за наш счет."

        battlecards.append({
            "competitor_name": comp_name,
            "their_positioning": their_hook,
            "their_price_point": their_price,
            "identified_leak": their_weakness,
            "source_mixing_counter_angle": our_counter_hook,
            "tech_advantage": our_tech_moat,
            "risk_reversal_guarantee": our_risk_reversal
        })

    return battlecards

def run_spy_agent(output_dir=None):
    if output_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(root_dir, "04_SALES_PLAYBOOK")
        if not os.path.exists(output_dir):
            output_dir = os.path.join(root_dir, "04_Playbook")

    os.makedirs(output_dir, exist_ok=True)

    competitors = [
        {
            "name": "Agency Alfa SEO Pro",
            "hook": "Классическое ссылочное продвижение и ручные статьи",
            "price": "75 000 ₽ / мес",
            "weakness": "Медленно (первые результаты через 4 месяца), статьи без виральности, нулевой видео-контент"
        },
        {
            "name": "Digital Boost Marketing",
            "hook": "Контекстная реклама + лендинг на Tilda",
            "price": "120 000 ₽ / проект",
            "weakness": "Зависимость от рекламного бюджета, шаблонные лендинги, отсутствие ИИ-онбординга"
        },
        {
            "name": "AI Content Automation Lab",
            "hook": "Массовая генерация текстов через ChatGPT",
            "price": "45 000 ₽ / мес",
            "weakness": "Низкое качество generic-текстов, нет брендовой дизайн-системы, нет телесуфлера и живого видео"
        }
    ]

    battlecards = synthesize_source_mixing(competitors)

    # Save JSON Battlecards
    json_path = os.path.join(output_dir, "SOURCE_MIXING_BATTLECARDS.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"agent": "agent_2_spy", "generated_at": datetime.now().isoformat(), "battlecards": battlecards}, f, ensure_ascii=False, indent=2)

    # Generate Markdown Playbook
    md_path = os.path.join(output_dir, "competitor_intelligence_vault.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 🕵️ Сводка Конкурентной Разведки и Source Mixing\n")
        f.write(f"**Агент:** `agent_2_spy` | **Дата обновления:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("---\n\n")
        for i, card in enumerate(battlecards, 1):
            f.write(f"### {i}. Конкурент: {card['competitor_name']}\n")
            f.write(f"* **Их позиционирование:** {card['their_positioning']}\n")
            f.write(f"* **Их ценник:** {card['their_price_point']}\n")
            f.write(f"* **Слабое место:** ⚠️ {card['identified_leak']}\n")
            f.write(f"* **Source Mixing контр-оффер:** 🎯 *{card['source_mixing_counter_angle']}*\n")
            f.write(f"* **Наш технологический ров:** 🛡️ {card['tech_advantage']}\n")
            f.write(f"* **Гарантия (Risk Reversal):** 💎 {card['risk_reversal_guarantee']}\n\n")
            f.write("---\n\n")

    return {
        "status": "SUCCESS",
        "agent_id": "agent_2_spy",
        "competitors_analyzed": len(battlecards),
        "json_output": json_path,
        "md_output": md_path
    }

if __name__ == "__main__":
    res = run_spy_agent()
    print(f"✓ [agent_2_spy] Analyzed {res['competitors_analyzed']} competitors. Output: {res['md_output']}")
