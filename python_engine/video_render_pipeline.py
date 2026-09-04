"""
============================================================================
RAZUM AI 2026 • VIRAL PROMO SHORTS & REELS RENDER PIPELINE (9:16)
Generates High-Retention 15-30s Video Scripts, Audio Cues & Render Commands
Aesthetic: Stitch Design System (Obsidian Dark, Neon Emerald, Cyan)
============================================================================
"""

import os
import sys
import json
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "05_Content", "Video")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROMO_REELS = [
    {
        "id": "reel_01_saas_trap",
        "title": "Ловушка SaaS-подписок 2026",
        "duration_sec": 24,
        "aspect_ratio": "9:16",
        "target_audience": "Владельцы бизнеса, CEO, Интеграторы",
        "soundtrack_bpm": 128,
        "scenes": [
            {
                "time": "0:00 - 0:03",
                "scene_type": "HOOK",
                "sound_cue": "🚨 BASS DROP + GLITCH SFX",
                "visual": "Анимированный счетчик списаний с карты: -$80, -$120, -$300 с красным свечением",
                "text_overlay": "ПОДПИСКИ СЖИРАЮТ ВАШ БЮДЖЕТ?",
                "voiceover": "Вы посчитали, сколько денег ваша компания дарит чужим сервисам каждый месяц?"
            },
            {
                "time": "0:03 - 0:10",
                "scene_type": "AGITATION",
                "sound_cue": "⚡ WHOOSH + SOFT TICK",
                "visual": "Перечеркнутые логотипы 10 разрозненных SaaS платформ. Хаос проводов.",
                "text_overlay": "10 СЕРВИСОВ = 0 СВЯЗИ МЕЖДУ НИМИ",
                "voiceover": "За каждого менеджера вы платите снова и снова. А данные хранятся на чужих серверах."
            },
            {
                "time": "0:10 - 0:18",
                "scene_type": "SOLUTION",
                "sound_cue": "💎 DIGITAL CHIME + CYAN NEON GLOW",
                "visual": "Появление 3D консоли Google Workspace: чистая таблица, мгновенный парсер счетов за 2 секунды.",
                "text_overlay": "СУВЕРЕННЫЙ ИИ-КОНТУР 2026",
                "voiceover": "В 2026 году мы разворачиваем автономный контур на вашем аккаунте. Один раз. Без подписок."
            },
            {
                "time": "0:18 - 0:24",
                "scene_type": "CALL_TO_ACTION",
                "sound_cue": "🔔 SUCCESS SYNTH CHIME",
                "visual": "Кнопка 'РАССЧИТАТЬ ОКУПАЕМОСТЬ' с неоновым пульсом и стрелкой вниз.",
                "text_overlay": "ОКУПАЕМОСТЬ: 4 ДНЯ. ССЫЛКА В ШАПКЕ",
                "voiceover": "Окупаемость — 4 дня. Пишите 'КОНТУР' в директ — пришлем расчет для вашей компании!"
            }
        ]
    },
    {
        "id": "reel_02_invoice_autopilot",
        "title": "Бухгалтер тратит 5 минут вместо 8 часов",
        "duration_sec": 20,
        "aspect_ratio": "9:16",
        "target_audience": "Главные бухгалтеры, финдиректоры",
        "soundtrack_bpm": 120,
        "scenes": [
            {
                "time": "0:00 - 0:03",
                "scene_type": "HOOK",
                "sound_cue": "📄 PAPER TEAR + BEEP",
                "visual": "Гора бумажных счетов и открытая пустая таблица 1С",
                "text_overlay": "РУЧНОЙ ВВОД СЧЕТОВ МЕРТВ",
                "voiceover": "Если ваш бухгалтер всё ещё перебивает ИНН из PDF руками — вы теряете часы."
            },
            {
                "time": "0:03 - 0:12",
                "scene_type": "DEMO",
                "sound_cue": "⚡ HIGH SPEED SCANNER SFX",
                "visual": "Входящее письмо в Gmail -> скрипт за 2.4 секунды заполняет 15 колонок Google Таблицы",
                "text_overlay": "2.4 СЕКУНДЫ НА 1 СЧЕТ В GOOGLE SHEETS",
                "voiceover": "Zero-Leakage Gemini парсит любые первичные документы прямо из почты без задержек."
            },
            {
                "time": "0:12 - 0:20",
                "scene_type": "CALL_TO_ACTION",
                "sound_cue": "💎 EMERALD SPARK",
                "visual": "QR-код и бейдж 'ТАРИФ ОТ $50 РАЗОВО'",
                "text_overlay": "ПАКЕТ ОТ $50. РАЗ И НАВСЕГДА.",
                "voiceover": "Подключение за 24 часа. Ссылка на демо в профиле!"
            }
        ]
    },
    {
        "id": "reel_03_ai_swarm_agents",
        "title": "5 ИИ-Агентов пока вы спите",
        "duration_sec": 28,
        "aspect_ratio": "9:16",
        "target_audience": "Фаундеры, B2B директора",
        "soundtrack_bpm": 135,
        "scenes": [
            {
                "time": "0:00 - 0:04",
                "scene_type": "HOOK",
                "sound_cue": "🌌 DEEP SPACE WHOOSH",
                "visual": "Ночной город, спящий офис, экран ноутбука светится неоновыми связями",
                "text_overlay": "КТО РАБОТАЕТ В ВАШЕЙ КОМПАНИИ В 3 ЧАСА НОЧИ?",
                "voiceover": "Пока вы спите — ваша система может приносить готовые B2B лиды."
            },
            {
                "time": "0:04 - 0:18",
                "scene_type": "BREAKDOWN",
                "sound_cue": "⚡ 5 PULSE BEATS (По одному на каждого агента)",
                "visual": "Голографическая схема 5 агентов: Scout -> Spy -> SMM -> Video -> Spark Watchdog",
                "text_overlay": "РОЙ ИЗ 5 АВТОНОМНЫХ АГЕНТОВ",
                "voiceover": "Разведка контактов, анализ конкурентов, контент и проверка CRM. Автономно 24/7."
            },
            {
                "time": "0:18 - 0:28",
                "scene_type": "CALL_TO_ACTION",
                "sound_cue": "🚀 FINAL RISER",
                "visual": "Логотип Razum Google AI PRO и форма записи на архитектурный аудит",
                "text_overlay": "СУВЕРЕННЫЙ РОЙ ПОД КЛЮЧ",
                "voiceover": "Хотите автономную систему? Пишите 'РОЙ' — покажем архитектуру на созвоне!"
            }
        ]
    }
]

def export_scripts_markdown():
    path = os.path.join(OUTPUT_DIR, "VIRAL_REELS_SCRIPTS_PACK.md")
    lines = [
        "# 🎬 ПАКЕТ ВИРУСНЫХ 15-30с ПРОМО-РОЛИКОВ (Reels / Shorts / TikTok)",
        f"**Дата создания:** {datetime.now().strftime('%Y-%m-%d')} • **Стиль:** Stitch Design System (9:16 Vertical)\n",
        "---\n"
    ]
    for r in PROMO_REELS:
        lines.append(f"## 🎥 {r['title']} ({r['duration_sec']} сек)")
        lines.append(f"- **ID:** `{r['id']}`")
        lines.append(f"- **Аудитория:** {r['target_audience']}")
        lines.append(f"- **Музыкальный темп:** {r['soundtrack_bpm']} BPM (Lo-Fi / Cyberpunk Beat)")
        lines.append("\n### ⏱️ Раскадровка и сценарий:\n")
        lines.append("| Время | Тип сцены | Звуковой триггер (SFX) | Визуал | Титр на экране (Stitch) | Озвучка (Voiceover) |")
        lines.append("|---|---|---|---|---|---|")
        for s in r['scenes']:
            lines.append(f"| {s['time']} | {s['scene_type']} | {s['sound_cue']} | {s['visual']} | **{s['text_overlay']}** | «{s['voiceover']}» |")
        lines.append("\n---\n")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"✓ Сценарии промо-роликов экспортированы в: {path}")
    return path

def generate_html_player():
    """Генерирует мобильный веб-проигрыватель для превью сценариев вертикальных роликов."""
    path = os.path.join(ROOT_DIR, "video_studio.html")
    # Also save dedicated player in OUTPUT_DIR
    player_path = os.path.join(OUTPUT_DIR, "reels_preview_studio.html")
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reels & Shorts Preview Studio 2026 | Stitch UI</title>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(15, 23, 42, 0.9);
      --emerald: #10b981;
      --cyan: #06b6d4;
    }}
    * {{ box-sizing: border-box; margin:0; padding:0; }}
    body {{
      background: var(--bg);
      color: #fff;
      font-family: 'Plus Jakarta Sans', sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 30px 16px;
    }}
    .phone-mockup {{
      width: 320px;
      height: 570px;
      background: #000;
      border: 3px solid rgba(255,255,255,0.15);
      border-radius: 36px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 30px rgba(16, 185, 129, 0.2);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 24px;
    }}
    .hook-badge {{
      background: rgba(16,185,129,0.2);
      color: var(--emerald);
      border: 1px solid var(--emerald);
      border-radius: 999px;
      padding: 4px 12px;
      font-size: 11px;
      font-weight: 800;
      align-self: flex-start;
      text-transform: uppercase;
    }}
    .scene-text {{
      font-size: 20px;
      font-weight: 800;
      line-height: 1.3;
      text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    }}
    .sfx-pill {{
      background: rgba(6, 182, 212, 0.15);
      border: 1px solid rgba(6, 182, 212, 0.4);
      color: var(--cyan);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      padding: 6px 12px;
      border-radius: 8px;
    }}
  </style>
</head>
<body>
  <h1 style="font-size:24px; font-weight:800; margin-bottom:16px;">🎬 Вирусные Промо-Ролики (Stitch 9:16)</h1>
  <div style="display:flex; gap:8px; margin-bottom:24px;">
    {''.join(f'<button onclick="switchReel({i})" style="background:rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); color:#fff; padding:8px 16px; border-radius:10px; cursor:pointer; font-weight:700;">Reel #{i+1}</button>' for i in range(len(PROMO_REELS)))}
  </div>

  <div class="phone-mockup" id="phone">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div class="hook-badge" id="badge">ХУК 0-3 СЕК</div>
      <div style="font-family:'JetBrains Mono'; font-size:12px; color:#94a3b8;" id="timer">0:00</div>
    </div>
    
    <div style="margin: auto 0;">
      <div class="scene-text" id="overlay-text">ПОДПИСКИ СЖИРАЮТ ВАШ БЮДЖЕТ?</div>
      <p style="font-size:13px; color:#cbd5e1; margin-top:12px; line-height:1.4;" id="voiceover">
        «Вы посчитали, сколько денег ваша компания дарит чужим сервисам каждый месяц?»
      </p>
    </div>

    <div class="sfx-pill" id="sfx">
      🚨 BASS DROP + GLITCH SFX
    </div>
  </div>

  <script>
    const reels = {json.dumps(PROMO_REELS, ensure_ascii=False)};
    let currentReel = 0;
    let sceneIdx = 0;

    function switchReel(idx) {{
      currentReel = idx;
      sceneIdx = 0;
      renderScene();
    }}

    function renderScene() {{
      const reel = reels[currentReel];
      const scene = reel.scenes[sceneIdx];
      document.getElementById('badge').innerText = scene.scene_type;
      document.getElementById('timer').innerText = scene.time;
      document.getElementById('overlay-text').innerText = scene.text_overlay;
      document.getElementById('voiceover').innerText = '«' + scene.voiceover + '»';
      document.getElementById('sfx').innerText = scene.sound_cue;
    }}

    setInterval(() => {{
      const reel = reels[currentReel];
      sceneIdx = (sceneIdx + 1) % reel.scenes.length;
      renderScene();
    }}, 4000);

    renderScene();
  </script>
</body>
</html>"""
    with open(player_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Превью-плеер роликов создан: {player_path}")
    return player_path

if __name__ == "__main__":
    export_scripts_markdown()
    generate_html_player()
