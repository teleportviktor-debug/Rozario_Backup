"""
============================================================================
AGENT 3: SOCIAL MEDIA IMAGE & COPY CREATOR (NEURO-SMM)
Obsidian Void & Cyan Aesthetics, Tri-Slot Daily Schedule (09:00, 15:00, 19:00)
============================================================================
"""

import os
import json
from datetime import datetime

def generate_daily_smm_pack():
    slots = [
        {
            "slot": "09:00 MORNING PARADIGM SHIFT",
            "theme": "Будущее SEO и AI в 2026: почему старые агентства теряют до 70% клиентов",
            "hook": "🚨 9 из 10 SEO-агентств в 2026 году закрываются по одной и той же глупой причине.",
            "body": (
                "Они продолжают продавать ручные ссылки и бесконечные 90-дневные аудиты, "
                "когда клиенту нужен автономный поток лидов за 5 дней.\n\n"
                "Разница между выживанием и доминированием — в суверенном ИИ-конвейере:\n"
                "1. Генерация 45-секундных виральных офферов.\n"
                "2. Телесуфлер со скоростью 180 WPM для идеального дубля с первого раза.\n"
                "3. Автоматический скоринг лидов по формуле Алекса Хормози."
            ),
            "cta": "👇 Напишите 'СУФЛЕР' в комментарии или откройте демо-студию по ссылке в профиле.",
            "visual_prompt": {
                "engine": "Nano Banana Pro / FLUX 1.1",
                "prompt": (
                    "Hyper-futuristic cybernetic office in 2026, glowing obsidian glass desk, "
                    "holographic UI floating with neon cyan (#00F2FE) and mint green (#00FF87) graphs, "
                    "cinematic lighting, ultra-detailed 8k render, octane render style, dark mood --ar 1:1"
                ),
                "palette": ["#0B0E14", "#00F2FE", "#00FF87", "#7928CA"]
            }
        },
        {
            "slot": "15:00 AFTERNOON CASE BREAKDOWN",
            "theme": "Разбор кейса: Как Smarty Marketing SEO сократил время производства контента на 82%",
            "hook": "📊 Реальные цифры: от 40 часов рутины до 4 часов контроля в неделю.",
            "body": (
                "Кейс агентства Smarty Marketing SEO:\n\n"
                "❌ До внедрения: 3 копирайтера, постоянные срывы дедлайнов, средняя конверсия оффера 2.1%.\n"
                "✅ После развертывания Razum AI Work System:\n"
                "• 15 готовых сценариев рилс в неделю генерируются за 3 минуты.\n"
                "• Голосовой скоринг лидов в CRM с мгновенным пушем в Telegram.\n"
                "• Окупаемость системы составила ровно 4 календарных дня."
            ),
            "cta": "💡 Хотите рассчитать окупаемость для вашего агентства? Калькулятор доступен на нашем портале.",
            "visual_prompt": {
                "engine": "FLUX / Midjourney",
                "prompt": (
                    "Sleek analytics dashboard mockup on high-end bezel-less tablet, "
                    "dark UI with vibrant neon green upward trends (+340%), neon cyan accents, "
                    "studio depth of field, photorealistic, minimal cyberpunk aesthetic --ar 1:1"
                ),
                "palette": ["#0B0E14", "#00FF87", "#00F2FE"]
            }
        },
        {
            "slot": "19:00 EVENING GRAND SLAM CONVERSION",
            "theme": "Предложение, от которого глупо отказаться: Тест-драйв суверенной студии",
            "hook": "🔥 Бесплатный доступ в закрытую Веб-Студию Телесуфлера 2026 открыт на 24 часа.",
            "body": (
                "Вы когда-нибудь записывали видео с 1-го дубля без запинок и монтажа?\n\n"
                "Наша Студия Телесуфлера автоматически рассчитывает темп (5 секунд на каждые 15 слов), "
                "накладывает веб-камеру прямо в браузере и экспортирует чистовой ролик в 1 клик.\n\n"
                "Без установки тяжелых программ. Без абонентских плат за сторонний софт."
            ),
            "cta": "🚀 Переходите по ссылке и протестируйте прямо сейчас: Teleprompter Studio Live.",
            "visual_prompt": {
                "engine": "Nano Banana Pro / Veo 3.1",
                "prompt": (
                    "Close-up of a professional modern video creator studio, teleprompter monitor reflecting "
                    "glowing green and cyan text lines, high-end 4K cinema lens, moody neon background bokeh --ar 1:1"
                ),
                "palette": ["#0B0E14", "#00F2FE", "#7928CA"]
            }
        }
    ]
    return slots

def run_smm_agent(output_dir=None):
    if output_dir is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(root_dir, "05_CONTENT_PRODUCTION", "Posts")
        if not os.path.exists(output_dir):
            output_dir = os.path.join(root_dir, "05_Content", "Posts")

    os.makedirs(output_dir, exist_ok=True)

    posts = generate_daily_smm_pack()

    # Save JSON batch
    json_path = os.path.join(output_dir, "daily_posts_batch.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"agent": "agent_3_smm", "created_at": datetime.now().isoformat(), "posts": posts}, f, ensure_ascii=False, indent=2)

    # Save Markdown file
    md_path = os.path.join(output_dir, "TODAY_POSTS.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📱 Дневной План Публикаций (Neuro-SMM Obsidian/Cyan)\n")
        f.write(f"**Агент:** `agent_3_smm` | **Дата:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("---\n\n")
        for p in posts:
            f.write(f"## 🕒 Слот: {p['slot']}\n")
            f.write(f"**Тема:** {p['theme']}\n\n")
            f.write(f"### 📝 Текст публикации:\n")
            f.write(f"**{p['hook']}**\n\n")
            f.write(f"{p['body']}\n\n")
            f.write(f"**{p['cta']}**\n\n")
            f.write(f"### 🎨 Промпт для ИИ-визуала ({p['visual_prompt']['engine']}):\n")
            f.write(f"```text\n{p['visual_prompt']['prompt']}\n```\n")
            f.write(f"*Палитра:* `{', '.join(p['visual_prompt']['palette'])}`\n\n")
            f.write("---\n\n")

    return {
        "status": "SUCCESS",
        "agent_id": "agent_3_smm",
        "posts_generated": len(posts),
        "json_output": json_path,
        "md_output": md_path
    }

if __name__ == "__main__":
    res = run_smm_agent()
    print(f"✓ [agent_3_smm] Created {res['posts_generated']} SMM posts. File: {res['md_output']}")
