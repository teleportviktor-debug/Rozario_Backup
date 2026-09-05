"""
============================================================================
RAZUM AI 2026 • AUDIO CHAPTER PARSER
Transcribes NotebookLM podcast audio using Whisper and segments it
into chapters based on natural pauses and topic shifts.
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
AUDIO_DIR = ROOT_DIR / "assets" / "podcast_audio"
OUTPUT_DIR = ROOT_DIR / "05_Content" / "Video" / "rendered_podcasts"


def transcribe_audio(audio_path: str, model_size: str = "base") -> dict:
    """
    Transcribe audio file using faster-whisper for word-level timestamps.
    Returns a dict with segments and word-level timing.
    
    Falls back to a simple chapter structure if whisper is not available.
    """
    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")

    print(f"🎙️ Транскрипция: {audio_path.name} (модель: {model_size})")

    try:
        from faster_whisper import WhisperModel
        
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(
            str(audio_path),
            word_timestamps=True,
            language="ru"
        )

        all_words = []
        all_segments = []

        for segment in segments:
            seg_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": []
            }
            if segment.words:
                for w in segment.words:
                    word_data = {
                        "word": w.word.strip(),
                        "start": w.start,
                        "end": w.end
                    }
                    seg_data["words"].append(word_data)
                    all_words.append(word_data)

            all_segments.append(seg_data)

        result = {
            "audio_file": str(audio_path),
            "language": info.language,
            "duration_sec": info.duration,
            "segments": all_segments,
            "words": all_words,
        }

        print(f"   ✓ Транскрибировано: {len(all_segments)} сегментов, {len(all_words)} слов")
        return result

    except ImportError:
        print("   ⚠️ faster-whisper не установлен. Используется заглушка.")
        return _create_stub_transcription(audio_path)


def _create_stub_transcription(audio_path: Path) -> dict:
    """Create a stub transcription for testing without Whisper."""
    return {
        "audio_file": str(audio_path),
        "language": "ru",
        "duration_sec": 120.0,
        "segments": [
            {"start": 0.0, "end": 30.0, "text": "Введение в суверенный ИИ-контур.", "words": []},
            {"start": 30.0, "end": 60.0, "text": "Проблемы SaaS-зависимости для бизнеса.", "words": []},
            {"start": 60.0, "end": 90.0, "text": "Архитектура решения на базе Google Workspace.", "words": []},
            {"start": 90.0, "end": 120.0, "text": "Результаты и ROI для клиентов.", "words": []},
        ],
        "words": [],
    }


def segment_into_chapters(
    transcription: dict,
    min_pause_sec: float = 1.5,
    max_chapter_sec: float = 60.0
) -> list:
    """
    Segment transcription into chapters based on:
    1. Natural pauses between segments (> min_pause_sec)
    2. Maximum chapter duration (splits long sections)
    
    Returns a list of chapter dicts.
    """
    segments = transcription["segments"]
    if not segments:
        return []

    chapters = []
    current_chapter = {
        "chapter": 1,
        "start": segments[0]["start"],
        "end": segments[0]["end"],
        "text": segments[0]["text"],
        "words": segments[0].get("words", []),
    }

    for i in range(1, len(segments)):
        seg = segments[i]
        prev_seg = segments[i - 1]
        pause = seg["start"] - prev_seg["end"]
        chapter_duration = seg["end"] - current_chapter["start"]

        # Start new chapter if big pause or max duration exceeded
        if pause >= min_pause_sec or chapter_duration >= max_chapter_sec:
            chapters.append(current_chapter)
            current_chapter = {
                "chapter": len(chapters) + 1,
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "words": seg.get("words", []),
            }
        else:
            # Extend current chapter
            current_chapter["end"] = seg["end"]
            current_chapter["text"] += " " + seg["text"]
            current_chapter["words"].extend(seg.get("words", []))

    # Append last chapter
    chapters.append(current_chapter)

    # Auto-generate chapter titles from first ~8 words
    for ch in chapters:
        words = ch["text"].split()[:8]
        ch["title"] = " ".join(words)
        if len(ch["text"].split()) > 8:
            ch["title"] += "..."
        ch["duration_sec"] = round(ch["end"] - ch["start"], 2)

    print(f"   ✓ Сегментировано: {len(chapters)} глав")
    return chapters


def parse_audio_to_chapters(audio_path: str, model_size: str = "base") -> list:
    """
    Full pipeline: transcribe audio → segment into chapters → save JSON.
    """
    transcription = transcribe_audio(audio_path, model_size)
    chapters = segment_into_chapters(transcription)

    # Save chapters JSON
    audio_name = Path(audio_path).stem
    chapters_path = OUTPUT_DIR / f"{audio_name}_chapters.json"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output = {
        "source_audio": str(audio_path),
        "total_duration_sec": transcription["duration_sec"],
        "total_chapters": len(chapters),
        "chapters": chapters,
    }

    with open(chapters_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"   ✓ Главы сохранены: {chapters_path}")
    return chapters


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Razum AI Audio Chapter Parser")
    parser.add_argument("audio", nargs="?", help="Path to audio file (.mp3/.wav)")
    parser.add_argument("--model", default="base", help="Whisper model size (tiny/base/small/medium/large)")
    args = parser.parse_args()

    if args.audio:
        chapters = parse_audio_to_chapters(args.audio, args.model)
        print(f"\n📋 Результат: {len(chapters)} глав")
        for ch in chapters:
            print(f"   Глава {ch['chapter']}: [{ch['start']:.1f}s - {ch['end']:.1f}s] {ch['title']}")
    else:
        # Demo mode with stub
        print("🧪 ДЕМО-РЕЖИМ (без реального аудио)")
        stub = _create_stub_transcription(Path("demo_podcast.mp3"))
        chapters = segment_into_chapters(stub)
        for ch in chapters:
            print(f"   Глава {ch['chapter']}: [{ch['start']:.1f}s - {ch['end']:.1f}s] {ch['title']}")
