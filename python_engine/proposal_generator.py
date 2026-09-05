"""
============================================================================
RAZUM AI 2026 • HORMOZI GRAND SLAM COMMERCIAL PROPOSAL (КП) ENGINE
Generates Premium Interactive HTML/PDF Proposals with ROI & Security Seal
============================================================================
"""

import os
import sys
import hashlib
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPOSALS_DIR = os.path.join(ROOT_DIR, "10_PRODUCTION", "_PROPOSALS")
G_DRIVE_PROPOSALS = r"g:\Мой диск\10_PRODUCTION\_PROPOSALS"

PACKAGES = {
    "pkg-starter": {
        "name": "Spark Starter",
        "price": "$50",
        "price_val": 50,
        "monthly_savings": "$300",
        "annual_savings": "$3,600",
        "payback": "5 дней",
        "features": [
            "Парсинг вложений почты Gmail прямо в Google Таблицу",
            "Zero-Log архитектура: доступ строго по правам вашего аккаунта",
            "Развертывание через Apps Script за 15 минут без программистов",
            "Пожизненная лицензия без ежемесячных подписок"
        ]
    },
    "pkg-command": {
        "name": "Command Center",
        "price": "$100",
        "price_val": 100,
        "monthly_savings": "$650",
        "annual_savings": "$7,800",
        "payback": "4 дня",
        "features": [
            "Всё из Spark Starter ($50) включено",
            "Авто-парсер счетов, актов и накладных из PDF в единый реестр",
            "Автоматическая валидация ИНН, сумм и пересчет НДС",
            "Генерация первичных документов в Google Docs в 1 клик"
        ]
    },
    "pkg-intelligence": {
        "name": "Intelligence Module",
        "price": "$200",
        "price_val": 200,
        "monthly_savings": "$1,200",
        "annual_savings": "$14,400",
        "payback": "5 дней",
        "features": [
            "Всё из Command Center ($100) включено",
            "Hormozi 4-Factor Lead Scoring (Pain, Power, DM, Urgency)",
            "Интерактивный ROI-радар окупаемости для закрытия клиентов",
            "AI-аудит звонков менеджеров и отработка возражений",
            "AI Video Studio — конвейер генерации видео и Shorts"
        ]
    },
    "pkg-sovereign": {
        "name": "Sovereign Autopilot",
        "price": "$300",
        "price_val": 300,
        "monthly_savings": "$1,850",
        "annual_savings": "$22,200",
        "payback": "4 дня",
        "features": [
            "Всё из Intelligence Module ($200) включено",
            "5 автономных AI-агентов Antigravity Swarm (Scout, Spy, SMM, Shorts, Spark)",
            "Фоновые триггеры Google Cloud — работает 24/7 при выключенном ПК",
            "Двусторонний MCP-шлюз и Watchdog авто-восстановления",
            "Официальный паспорт безопасности контура Zero-Log",
            "60 дней инженерного сопровождения под ключ"
        ]
    },
    "pkg-genesis": {
        "name": "Genesis Enterprise",
        "price": "$500",
        "price_val": 500,
        "monthly_savings": "$3,500",
        "annual_savings": "$42,000",
        "payback": "4 дня",
        "features": [
            "Всё из Sovereign Autopilot ($300) включено",
            "White-Label лицензия с правом перепродажи под вашим брендом",
            "Индивидуальный аудит бизнес-процессов с AI-архитектором",
            "Разработка до 3 кастомных агентов под специфику вашей компании",
            "Интеграция с существующими CRM / 1C / API"
        ]
    },
    "pkg-transformation": {
        "name": "Sovereign AI Transformation",
        "price": "$2,500",
        "price_val": 2500,
        "monthly_savings": "$5,200",
        "annual_savings": "$62,400",
        "payback": "14 дней",
        "features": [
            "Аудит бизнес-процессов (2 часа Zoom): карта «где утекают деньги» с конкретными цифрами",
            "Business DNA Extraction (Google Pomelli): персонализированный AI-профиль вашей компании",
            "Развертывание Sovereign Контура: 5 агентов + CRM + Webhook + NotebookLM на вашем аккаунте",
            "3 кастомных AI-агента (Google Opal + Apps Script) под ваши конкретные болевые процессы",
            "AI Media Studio PRO + 6 готовых вирусных скриптов для Shorts",
            "Паспорт безопасности Zero-Log (юридический документ для бухгалтерии и аудита)",
            "Google Stitch UI: интерактивный прототип клиентского интерфейса",
            "NotebookLM: персональная база знаний обученная на ваших регламентах",
            "Includes 30-Day Setup Support & Google Cloud Transfer (Zero Monthly Fees, Pay Once, Own Forever)"
        ]
    }
}

def generate_proposal_html(client_name: str, niche: str, package_id: str = "pkg-sovereign"):
    pkg = PACKAGES.get(package_id, PACKAGES["pkg-sovereign"])
    os.makedirs(PROPOSALS_DIR, exist_ok=True)

    clean_name = "".join(c for c in client_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    proposal_filename = f"PROPOSAL_{pkg['name'].replace(' ', '_')}_{clean_name}.html"
    proposal_path = os.path.join(PROPOSALS_DIR, proposal_filename)

    now_str = datetime.now().strftime("%d.%m.%Y")
    hash_str = f"{client_name}|{pkg['name']}|{pkg['price']}|{now_str}"
    sha256 = hashlib.sha256(hash_str.encode("utf-8")).hexdigest()[:24].upper()

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Коммерческое Предложение | {client_name} • {pkg['name']}</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(15, 23, 42, 0.85);
      --emerald: #10b981;
      --cyan: #06b6d4;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --border: rgba(255, 255, 255, 0.1);
    }}
    * {{ box-sizing: border-box; margin:0; padding:0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 40px 20px;
      display: flex;
      justify-content: center;
    }}
    .proposal-card {{
      max-width: 860px;
      width: 100%;
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 48px;
      box-shadow: 0 20px 50px rgba(0,0,0,0.6);
      position: relative;
      overflow: hidden;
    }}
    .proposal-card::before {{
      content: '';
      position: absolute;
      top: -100px; right: -100px;
      width: 300px; height: 300px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.2), transparent 70%);
      pointer-events: none;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .badge {{
      display: inline-block;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      background: rgba(16, 185, 129, 0.15);
      color: var(--emerald);
      border: 1px solid rgba(16, 185, 129, 0.3);
      margin-bottom: 12px;
    }}
    .title {{ font-size: 32px; font-weight: 800; line-height: 1.2; margin-bottom: 8px; }}
    .subtitle {{ color: var(--text-muted); font-size: 16px; }}
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin: 32px 0;
    }}
    .metric-box {{
      background: rgba(0,0,0,0.3);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 20px;
      text-align: center;
    }}
    .metric-val {{
      font-size: 24px;
      font-weight: 800;
      color: var(--cyan);
      font-family: 'JetBrains Mono', monospace;
      margin-bottom: 4px;
    }}
    .features-list {{
      list-style: none;
      margin: 24px 0 36px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}
    .features-list li {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 15px;
      color: #cbd5e1;
    }}
    .features-list li::before {{
      content: '✓';
      color: var(--emerald);
      font-weight: 800;
    }}
    .offer-box {{
      background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(99,102,241,0.12));
      border: 1px solid rgba(16, 185, 129, 0.4);
      border-radius: 18px;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .btn-action {{
      display: inline-block;
      padding: 14px 28px;
      background: var(--emerald);
      color: #000;
      font-weight: 800;
      border-radius: 12px;
      text-decoration: none;
      font-size: 15px;
      transition: 0.2s ease;
    }}
  </style>
</head>
<body>
  <div class="proposal-card">
    <div class="header">
      <div>
        <div class="badge">💎 ПЕРСОНАЛЬНЫЙ GRAND SLAM ОФФЕР</div>
        <div class="title">Автоматизация для «{client_name}»</div>
        <div class="subtitle">Отрасль: <strong>{niche}</strong> • Дата: <strong>{now_str}</strong></div>
      </div>
      <div style="text-align:right;">
        <div style="font-family:'JetBrains Mono', monospace; font-size:11px; color:var(--text-muted);">HASH: {sha256}</div>
        <div style="color:var(--emerald); font-size:12px; font-weight:700; margin-top:4px;">🛡️ SOVEREIGN VERIFIED</div>
      </div>
    </div>

    <p style="color:#cbd5e1; font-size:15px; line-height:1.6;">
      Предлагаем внедрение суверенного контура <strong>{pkg['name']}</strong> на базе защищенного облака Google Workspace. 
      Все данные компании обрабатываются изолированно без риска утечек и без скрытых ежемесячных подписок.
    </p>

    <div class="metrics-grid">
      <div class="metric-box">
        <div class="metric-val">{pkg['monthly_savings']}/мес</div>
        <div style="font-size:12px; color:var(--text-muted);">Базовая экономия</div>
      </div>
      <div class="metric-box">
        <div class="metric-val">{pkg['payback']}</div>
        <div style="font-size:12px; color:var(--text-muted);">Срок окупаемости</div>
      </div>
      <div class="metric-box">
        <div class="metric-val">{pkg['annual_savings']}</div>
        <div style="font-size:12px; color:var(--text-muted);">Чистая выгода / год</div>
      </div>
    </div>

    <!-- ИНТЕРАКТИВНЫЙ ROI КАЛЬКУЛЯТОР ДЛЯ КЛИЕНТА -->
    <div style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 18px; padding: 24px; margin-bottom: 32px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px;">
        <h3 style="font-size:17px; font-weight:800; color:var(--cyan); display:flex; align-items:center; gap:8px;">
          🧮 Интерактивный Калькулятор Окупаемости (ROI) для вашей команды
        </h3>
        <span style="font-size:12px; color:var(--emerald); font-weight:700; background:rgba(16,185,129,0.15); padding:4px 10px; border-radius:999px;">
          Динамический расчет
        </span>
      </div>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 16px;">
        <div>
          <label style="font-size:13px; color:var(--text-muted); display:block; margin-bottom:6px;">Сотрудников на рутине: <strong id="lbl-team-size" style="color:#fff;">5 чел</strong></label>
          <input type="range" id="slider-team" min="1" max="50" value="5" style="width:100%; accent-color:var(--emerald);">
        </div>
        <div>
          <label style="font-size:13px; color:var(--text-muted); display:block; margin-bottom:6px;">Средняя зарплата: <strong id="lbl-salary" style="color:#fff;">$800/мес</strong></label>
          <input type="range" id="slider-salary" min="300" max="3000" step="50" value="800" style="width:100%; accent-color:var(--cyan);">
        </div>
      </div>
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:12px; background:rgba(0,0,0,0.4); padding:16px; border-radius:12px; text-align:center;">
        <div>
          <div style="font-size:11px; color:var(--text-muted);">Часов сэкономлено:</div>
          <div id="calc-hours" style="font-size:18px; font-weight:800; color:var(--cyan); font-family:'JetBrains Mono', monospace;">125 ч/мес</div>
        </div>
        <div>
          <div style="font-size:11px; color:var(--text-muted);">Ваша выгода:</div>
          <div id="calc-savings" style="font-size:18px; font-weight:800; color:var(--emerald); font-family:'JetBrains Mono', monospace;">$625/мес</div>
        </div>
        <div>
          <div style="font-size:11px; color:var(--text-muted);">Окупаемость инвестиции:</div>
          <div id="calc-payback" style="font-size:18px; font-weight:800; color:#f59e0b; font-family:'JetBrains Mono', monospace;">{pkg['payback']}</div>
        </div>
      </div>
    </div>

    <h3 style="font-size:18px; font-weight:800; margin-bottom:12px; color:#fff;">📦 Что входит в комплект поставки под ключ:</h3>
    <ul class="features-list">
      {''.join(f'<li>{f}</li>' for f in pkg['features'])}
    </ul>

    <div class="offer-box">
      <div>
        <div style="font-size:13px; color:var(--text-muted);">Единоразовая инвестиция (без подписок):</div>
        <div style="font-size:32px; font-weight:800; color:#fff; font-family:'JetBrains Mono', monospace;">
          {pkg['price']} <span style="font-size:14px; color:var(--emerald); font-weight:600;">(Разово навсегда)</span>
        </div>
      </div>
      <a href="mailto:ceo@company.com?subject=Согласование внедрения {pkg['name']}" class="btn-action">
        Утвердить и Развернуть 🚀
      </a>
    </div>
  </div>

  <script>
    const packageCost = {pkg['price_val']};
    const sTeam = document.getElementById('slider-team');
    const sSalary = document.getElementById('slider-salary');
    const lTeam = document.getElementById('lbl-team-size');
    const lSalary = document.getElementById('lbl-salary');
    const cHours = document.getElementById('calc-hours');
    const cSavings = document.getElementById('calc-savings');
    const cPayback = document.getElementById('calc-payback');

    function updateCalc() {{
      const team = parseInt(sTeam.value);
      const salary = parseInt(sSalary.value);
      lTeam.innerText = team + ' чел';
      lSalary.innerText = '$' + salary + '/мес';

      // 25 hours saved per employee per month (~1.2h / day)
      const hoursSaved = team * 25;
      const hourlyRate = salary / 160;
      const monthlySavings = Math.round(hoursSaved * hourlyRate);
      const annualSavings = monthlySavings * 12;
      const dailySavings = monthlySavings / 22;
      const paybackDays = Math.max(1, Math.round(packageCost / (dailySavings || 1)));

      cHours.innerText = hoursSaved + ' ч/мес';
      cSavings.innerText = '$' + monthlySavings.toLocaleString() + '/мес';
      cPayback.innerText = paybackDays + (paybackDays === 1 ? ' день' : (paybackDays < 5 ? ' дня' : ' дней'));
    }}

    sTeam.addEventListener('input', updateCalc);
    sSalary.addEventListener('input', updateCalc);
    updateCalc();
  </script>
</body>
</html>"""

    with open(proposal_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n🎉 КОММЕРЧЕСКОЕ ПРЕДЛОЖЕНИЕ СФОРМИРОВАНО: {proposal_path}")

    # Mirror to Google Drive
    if os.path.exists(r"g:\Мой диск"):
        try:
            os.makedirs(G_DRIVE_PROPOSALS, exist_ok=True)
            drive_dest = os.path.join(G_DRIVE_PROPOSALS, proposal_filename)
            with open(drive_dest, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"☁️ Зеркало КП на Google Диске: {drive_dest}")
        except Exception as e:
            print(f"⚠️ Drive proposal note: {e}")

    return proposal_path

def generate_all_proposals(client_name: str = "Партнер", niche: str = "B2B"):
    """Генерирует коммерческие предложения для всех доступных тарифов."""
    created = []
    for pkg_id in PACKAGES.keys():
        p = generate_proposal_html(client_name, niche, pkg_id)
        created.append(p)
    return created

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hormozi Proposal Engine")
    parser.add_argument("--client", type=str, default="ООО «ПромТехИнвест»", help="Client name")
    parser.add_argument("--niche", type=str, default="Производство и Поставки", help="Industry/Niche")
    parser.add_argument("--pkg", type=str, default="pkg-sovereign", help="Package ID")
    parser.add_argument("--all", action="store_true", help="Generate for all tiers")
    args = parser.parse_args()

    if args.all:
        print(f"🚀 Генерация КП по всем тарифам для: {args.client}")
        results = generate_all_proposals(args.client, args.niche)
        print(f"✅ Создано {len(results)} предложений.")
    else:
        generate_proposal_html(args.client, args.niche, args.pkg)
