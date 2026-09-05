"""
============================================================================
RAZUM AI 2026 • STITCH SLIDE GENERATOR
Takes chapter data (from audio_chapter_parser) and generates
per-chapter HTML slide data for the 16:9 Playwright renderer.
============================================================================
"""

import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
OUTPUT_DIR = ROOT_DIR / "05_Content" / "Video" / "rendered_podcasts"
VISUALS_DIR = ROOT_DIR / "assets" / "launch_visuals"

# Chapter type heuristics: map keywords to visual styles
CHAPTER_STYLES = {
    "проблем": {"color": "rose", "icon": "⚠️", "label": "ПРОБЛЕМА"},
    "риск": {"color": "rose", "icon": "🚨", "label": "РИСКИ"},
    "saas": {"color": "rose", "icon": "💸", "label": "ПРОБЛЕМА SaaS"},
    "решени": {"color": "cyan", "icon": "💡", "label": "РЕШЕНИЕ"},
    "архитектур": {"color": "cyan", "icon": "🏗️", "label": "АРХИТЕКТУРА"},
    "google": {"color": "cyan", "icon": "🌐", "label": "ТЕХНОЛОГИЯ"},
    "результат": {"color": "emerald", "icon": "📈", "label": "РЕЗУЛЬТАТЫ"},
    "roi": {"color": "emerald", "icon": "💰", "label": "ROI"},
    "окупаемост": {"color": "emerald", "icon": "✅", "label": "ОКУПАЕМОСТЬ"},
    "введени": {"color": "cyan", "icon": "🎯", "label": "ВВЕДЕНИЕ"},
    "агент": {"color": "violet", "icon": "🤖", "label": "AI АГЕНТЫ"},
}

# Pre-built metric sets for known chapter types
METRIC_PRESETS = {
    "РЕШЕНИЕ": [
        {"value": "72 ч", "label": "Развертывание"},
        {"value": "$0", "label": "Ежемес. подписка"},
        {"value": "99.8%", "label": "Точность AI"},
        {"value": "24/7", "label": "Автономность"},
    ],
    "ROI": [
        {"value": "4 дня", "label": "Окупаемость"},
        {"value": "78%", "label": "Маржа"},
        {"value": "6.5x", "label": "LTV / CAC"},
        {"value": "$1,200", "label": "Мин. доход/мес"},
    ],
    "ПРОБЛЕМА SaaS": [
        {"value": "$300", "label": "Стоимость / сотрудник"},
        {"value": "10+", "label": "Разных сервисов"},
        {"value": "0%", "label": "Связей между ними"},
        {"value": "∞", "label": "Риск блокировки"},
    ],
}


def generate_slide_data(chapters: list, podcast_name: str = "podcast") -> list:
    """
    Generate render-ready slide data for each chapter.
    Returns a list of dicts consumable by slide_16x9_base.html's renderSlide().
    """
    slides = []
    total_chapters = len(chapters)

    for ch in chapters:
        style = _detect_chapter_style(ch["text"])

        slide = {
            "chapter": ch["chapter"],
            "chapter_title": style["label"],
            "title": ch.get("title", f"Глава {ch['chapter']}"),
            "body": _extract_body(ch["text"]),
            "total_chapters": total_chapters,
            "start_sec": ch["start"],
            "end_sec": ch["end"],
            "duration_sec": ch.get("duration_sec", ch["end"] - ch["start"]),
            "metrics": METRIC_PRESETS.get(style["label"], []),
            "image": _find_chapter_image(ch["chapter"], podcast_name),
            "caption": _format_caption(ch["text"]),
            "words": ch.get("words", []),
            "template_html": str(TEMPLATES_DIR / "slide_16x9_base.html"),
        }

        slides.append(slide)

    return slides


def save_slide_manifest(slides: list, podcast_name: str) -> str:
    """Save slide data as JSON manifest for the renderer."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manifest_path = OUTPUT_DIR / f"{podcast_name}_slides_manifest.json"

    manifest = {
        "podcast_name": podcast_name,
        "total_slides": len(slides),
        "total_duration_sec": sum(s["duration_sec"] for s in slides),
        "slides": slides,
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"   ✓ Манифест слайдов сохранён: {manifest_path}")
    return str(manifest_path)


def _detect_chapter_style(text: str) -> dict:
    """Detect chapter visual style based on keyword matching."""
    text_lower = text.lower()
    for keyword, style in CHAPTER_STYLES.items():
        if keyword in text_lower:
            return style
    return {"color": "cyan", "icon": "📌", "label": "ОБЗОР"}


def _extract_body(text: str, max_words: int = 40) -> str:
    """Extract a concise body text from the full chapter transcript."""
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def _find_chapter_image(chapter_num: int, podcast_name: str) -> str:
    """Look for a pre-generated image for this chapter."""
    candidates = [
        VISUALS_DIR / f"{podcast_name}_ch{chapter_num}.jpg",
        VISUALS_DIR / f"sovereign_architecture.jpg",
        VISUALS_DIR / f"saas_vs_sovereign.jpg",
        VISUALS_DIR / f"ai_swarm_agents.jpg",
    ]
    # Cycle through available images
    for i, c in enumerate(candidates):
        if c.exists() and (i == 0 or (chapter_num - 1) % 3 == i - 1):
            return str(c)
    return ""


def _format_caption(text: str) -> str:
    """Format transcript text as HTML caption with word spans."""
    words = text.split()[:30]  # Limit visible caption length
    return " ".join(
        f'<span class="caption-word">{w}</span>' for w in words
    )


if __name__ == "__main__":
    # Demo mode: generate slides from stub chapters
    print("🧪 ДЕМО: Генерация слайдов из тестовых глав")

    demo_chapters = [
        {"chapter": 1, "start": 0.0, "end": 30.0, "title": "Введение в суверенный ИИ-контур...", "text": "Введение в суверенный ИИ-контур. Сегодня мы поговорим о том, как компании теряют деньги на SaaS подписках.", "words": []},
        {"chapter": 2, "start": 30.0, "end": 60.0, "title": "Проблемы SaaS-зависимости для бизнеса...", "text": "Проблемы SaaS зависимости. Каждый сотрудник стоит компании до 300 долларов в месяц на подписки разрозненных сервисов.", "words": []},
        {"chapter": 3, "start": 60.0, "end": 90.0, "title": "Архитектура решения на базе Google...", "text": "Архитектура решения на базе Google Workspace. Мы разворачиваем суверенный контур за 72 часа с точностью 99.8 процентов.", "words": []},
        {"chapter": 4, "start": 90.0, "end": 120.0, "title": "Результаты и ROI для клиентов...", "text": "Результаты и ROI. Окупаемость за 4 дня. Маржинальность 78 процентов. LTV к CAC более 6.5.", "words": []},
    ]

    slides = generate_slide_data(demo_chapters, "demo_podcast")
    manifest_path = save_slide_manifest(slides, "demo_podcast")

    for s in slides:
        print(f"   Слайд {s['chapter']}: [{s['chapter_title']}] {s['title']}")
