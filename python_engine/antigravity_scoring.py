"""
============================================================================
ANTIGRAVITY AIR-GAPPED PYTHON COMPUTATION ENGINE (HORMOZI SCORER & ROI)
Zero-Hallucination Mathematical Pipeline (Pure Python UTF-8 Safe)
============================================================================
"""

import sys
import json
import math

# Ensure UTF-8 output on Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def calculate_hormozi_score(pain: float, purchasing_power: float, decision_making: float, urgency: float) -> dict:
    """
    Computes exact weighted Hormozi Score (0 to 100%)
    Weights: Pain 35%, Purchasing Power 25%, Decision Making 20%, Urgency 20%
    """
    weights = [0.35, 0.25, 0.20, 0.20]
    factors = [pain, purchasing_power, decision_making, urgency]
    
    raw_score = sum(w * f for w, f in zip(weights, factors))
    score_pct = int(round((raw_score / 10.0) * 100))
    
    if score_pct >= 80:
        tier = "TIER 1: VIP ПРИОРИТЕТ (ЗАКРЫВАТЬ СЕГОДНЯ)"
        rec = "Высокая боль и бюджет. Назначать демо-созвон с фаундером. Пакет AI-Геном Бизнеса."
    elif score_pct >= 60:
        tier = "TIER 2: ВЫСОКАЯ ВЕРОЯТНОСТЬ (СДЕЛКА 48 ЧАСОВ)"
        rec = "Квалифицированный лид. Предлагать пакет Автопилот Бухгалтерии или Hormozi Qualifier."
    elif score_pct >= 40:
        tier = "TIER 3: ПРОГРЕВ И АВТОМАТИЗАЦИЯ"
        rec = "Низкая срочность. Направить трипваер Express Start 990 руб."
    else:
        tier = "НЕ ЦЕЛЕВОЙ (ОТКЛОНИТЬ)"
        rec = "Отправить бесплатные материалы, не тратить время менеджеров."
        
    return {
        "score_percent": score_pct,
        "raw_score": float(round(raw_score, 2)),
        "tier": tier,
        "recommendation": rec
    }

def calculate_roi_metrics(employees_count: int, avg_salary_rub: float, manual_hours_per_day: float, package_cost_rub: float) -> dict:
    """
    Computes mathematically rigorous ROI and payback duration
    """
    hourly_rate = avg_salary_rub / (21.0 * 8.0)
    monthly_saved_hours = employees_count * manual_hours_per_day * 21.0 * 0.8 # 80% automated
    monthly_savings_rub = int(round(monthly_saved_hours * hourly_rate))
    annual_savings_rub = monthly_savings_rub * 12
    net_first_year_profit = annual_savings_rub - package_cost_rub
    payback_days = max(1, int(round(package_cost_rub / (monthly_savings_rub / 30.0))))
    roi_multiplier = int(round((annual_savings_rub / package_cost_rub) * 100.0))
    
    return {
        "hourly_rate_rub": int(round(hourly_rate)),
        "monthly_saved_hours": int(round(monthly_saved_hours)),
        "monthly_savings_rub": monthly_savings_rub,
        "annual_savings_rub": annual_savings_rub,
        "net_first_year_profit": net_first_year_profit,
        "payback_days": payback_days,
        "roi_multiplier_pct": roi_multiplier
    }

if __name__ == "__main__":
    score = calculate_hormozi_score(9, 8, 9, 8)
    roi = calculate_roi_metrics(5, 80000, 2.5, 14900)
    print("=== ANTIGRAVITY PYTHON CORE READY ===")
    print("=== HORMOZI SCORE RESULT ===")
    print(json.dumps(score, ensure_ascii=False, indent=2))
    print("\n=== ROI CALCULATION RESULT ===")
    print(json.dumps(roi, ensure_ascii=False, indent=2))
