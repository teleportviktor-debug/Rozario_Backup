"""
============================================================================
AGENT 1: LEAD SCOUT & HORMOZI SCORING ENGINE
Autonomous Lead Parsing, PPDU Scoring & Workspace Studio Sheets Integration
============================================================================
"""

import os
import json
import csv
from datetime import datetime

def calculate_ppdu_score(pain, power, decision, urgency):
    """
    Calculates Pain, Power, Decision, Urgency (PPDU) and Alex Hormozi Value score.
    Returns normalized 0-100 score, tier level, and ROI estimation.
    """
    pain = max(1, min(10, pain))
    power = max(1, min(10, power))
    decision = max(1, min(10, decision))
    urgency = max(1, min(10, urgency))

    # PPDU Composite Score
    composite = (pain * 0.35) + (power * 0.25) + (decision * 0.20) + (urgency * 0.20)
    score_pct = int(composite * 10)

    if score_pct >= 80:
        tier = "TIER 1 (VIP - CLOSE TODAY)"
        priority = "URGENT"
        action = "DISPATCH_PROPOSAL_IMMEDIATELY"
    elif score_pct >= 60:
        tier = "TIER 2 (QUALIFIED - SCHEDULE DEMO)"
        priority = "HIGH"
        action = "SEND_SPRINT_TEARDOWN_DEMO"
    else:
        tier = "TIER 3 (NURTURE - SMM SEQUENCE)"
        priority = "NORMAL"
        action = "ENROLL_IN_CONTENT_LOOP"

    return {
        "score_percent": score_pct,
        "tier": tier,
        "priority": priority,
        "recommended_action": action,
        "metrics": {
            "pain": pain,
            "power": power,
            "decision": decision,
            "urgency": urgency
        }
    }

def run_lead_scout(input_data=None, output_dir=None):
    if output_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(root_dir, "03_CRM_LEADS")
        if not os.path.exists(output_dir):
            output_dir = os.path.join(root_dir, "03_CRM")

    os.makedirs(output_dir, exist_ok=True)

    # Sample incoming leads if none provided
    if not input_data:
        input_data = [
            {
                "lead_id": "LEAD-2026-001",
                "name": "Анна Смирнова",
                "company": "Smarty Marketing SEO",
                "niche": "SEO & Digital Growth Agency",
                "contact": "+380 50 789 45 12 / t.me/anna_smarty_seo",
                "pain_description": "Команда тратит 40+ часов в неделю на ручной контент и аудит. Конверсия оффера 2.1%.",
                "pain": 9,
                "power": 10,
                "decision": 9,
                "urgency": 9,
                "estimated_deal_rub": 149000
            },
            {
                "lead_id": "LEAD-2026-002",
                "name": "Михаил Романов",
                "company": "Nexus B2B Software",
                "niche": "SaaS Cloud Solutions",
                "contact": "m.romanov@nexus-ai.io",
                "pain_description": "Отсутствует регулярный постинг Shorts и видео-воронка. Нужен телесуфлер и автопостинг.",
                "pain": 8,
                "power": 8,
                "decision": 8,
                "urgency": 7,
                "estimated_deal_rub": 89000
            },
            {
                "lead_id": "LEAD-2026-003",
                "name": "Елена Григорьева",
                "company": "Beauty & Health Hub",
                "niche": "E-Commerce",
                "contact": "elena_ghub@mail.ru",
                "pain_description": "Интересуется ИИ-ботами, но пока нет выделенного бюджета на внедрение.",
                "pain": 5,
                "power": 4,
                "decision": 5,
                "urgency": 3,
                "estimated_deal_rub": 35000
            }
        ]

    scored_results = []
    for lead in input_data:
        scoring = calculate_ppdu_score(lead["pain"], lead["power"], lead["decision"], lead["urgency"])
        scored_entry = {
            **lead,
            "processed_at": datetime.now().isoformat(),
            "scoring": scoring
        }
        scored_results.append(scored_entry)

    # Save to JSON
    json_path = os.path.join(output_dir, "leads_scored_batch.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"agent": "agent_1_lead_scout", "timestamp": datetime.now().isoformat(), "leads": scored_results}, f, ensure_ascii=False, indent=2)

    # Save CSV for Google Sheets / Workspace Studio Append
    csv_path = os.path.join(output_dir, "WORKSPACE_STUDIO_SHEETS_EXPORT.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Company", "Niche", "Contact", "PPDU Score %", "Tier", "Priority", "Recommended Action", "Est Deal (RUB)", "Processed At"])
        for item in scored_results:
            writer.writerow([
                item["lead_id"],
                item["name"],
                item["company"],
                item["niche"],
                item["contact"],
                f"{item['scoring']['score_percent']}%",
                item["scoring"]["tier"],
                item["scoring"]["priority"],
                item["scoring"]["recommended_action"],
                item["estimated_deal_rub"],
                item["processed_at"]
            ])

    return {
        "status": "SUCCESS",
        "agent_id": "agent_1_lead_scout",
        "leads_processed": len(scored_results),
        "json_output": json_path,
        "csv_output": csv_path,
        "vip_leads_count": sum(1 for x in scored_results if x["scoring"]["score_percent"] >= 80)
    }

if __name__ == "__main__":
    res = run_lead_scout()
    print(f"✓ [agent_1_lead_scout] Processed {res['leads_processed']} leads. VIP: {res['vip_leads_count']}")
