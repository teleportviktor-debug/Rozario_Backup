"""
============================================================================
RAZUM AI 2026 • SLIDE AUDIO SYNC (Pipeline 1)
Orchestrates the horizontal 16:9 Podcast rendering.
Uses Playwright to capture animated HTML slides and FFmpeg to 
concatenate them and overlay the original NotebookLM audio.
============================================================================
"""

import os
import sys
import json
import asyncio
import subprocess
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "05_Content" / "Video" / "rendered_podcasts"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Import parser and generator
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audio_chapter_parser import parse_audio_to_chapters, _create_stub_transcription, segment_into_chapters
from stitch_slide_generator import generate_slide_data, save_slide_manifest


async def render_podcast_video(manifest_path: str, audio_path: str = None) -> str:
    """
    Render a complete 16:9 Podcast video from a slide manifest.
    Uses Playwright to capture animated HTML slides, then FFmpeg to compose.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright не установлен. Запустите: pip install playwright && playwright install chromium")
        return ""

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    podcast_name = manifest["podcast_name"]
    final_output = str(OUTPUT_DIR / f"{podcast_name}_FINAL.mp4")
    slide_videos = []

    print(f"\n🎬 Рендеринг Подкаста: {podcast_name}")
    print(f"   Слайдов: {manifest['total_slides']}, Длительность: {manifest['total_duration_sec']} сек")

    template_url = (TEMPLATES_DIR / "slide_16x9_base.html").as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for slide in manifest["slides"]:
            slide_idx = slide["chapter"]
            # Convert to ms, add small buffer
            duration_ms = int(slide["duration_sec"] * 1000)
            
            # Bound duration for safety during tests
            if duration_ms > 300000: # Max 5 mins per slide
                 duration_ms = 300000

            slide_video_path = str(OUTPUT_DIR / f"{podcast_name}_slide_{slide_idx:02d}.webm")

            print(f"   📹 Слайд {slide_idx}: {slide['chapter_title']} ({slide['duration_sec']}s)...", end=" ", flush=True)

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                device_scale_factor=1,
                record_video_dir=str(OUTPUT_DIR),
                record_video_size={"width": 1920, "height": 1080}
            )

            page = await context.new_page()
            await page.goto(template_url, wait_until="networkidle")

            # Inject slide data
            slide_json = json.dumps(slide, ensure_ascii=False)
            await page.evaluate(f"window.renderSlide({slide_json})")

            # Simulate live caption highlighting based on word timings
            # In a real scenario with Whisper timestamps, we'd trigger highlights over time
            # For this MVP, we just wait the duration
            await page.wait_for_timeout(duration_ms)

            video_path = await page.video.path()
            await context.close()

            if Path(video_path).exists():
                shutil.move(str(video_path), slide_video_path)
                slide_videos.append(slide_video_path)
                print("✓")
            else:
                print("⚠️ Видео не записано")

        await browser.close()

    if not slide_videos:
        print("❌ Ни один слайд не был отрендерен.")
        return ""

    # Compose final video
    final_path = _ffmpeg_compose(slide_videos, podcast_name, final_output, audio_path)
    return final_path


def _ffmpeg_compose(slide_videos: list, podcast_name: str, output_path: str, audio_path: str) -> str:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
            os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe"),
        ]
        for cp in common_paths:
            if os.path.exists(cp):
                ffmpeg_path = cp
                break

    if not ffmpeg_path:
        print("⚠️ FFmpeg не найден в PATH. Пропускаем композитинг.")
        return slide_videos[0] if slide_videos else ""

    print(f"\n🔧 FFmpeg композитинг ({len(slide_videos)} слайдов)...")

    concat_file = str(OUTPUT_DIR / f"{podcast_name}_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for sv in slide_videos:
            safe_path = sv.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    concat_output = str(OUTPUT_DIR / f"{podcast_name}_concat.mp4")
    cmd_concat = [
        ffmpeg_path, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        concat_output
    ]

    result = subprocess.run(cmd_concat, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"⚠️ FFmpeg concat ошибка: {result.stderr[:200]}")
        return slide_videos[0]

    # Resolve audio path
    final_audio = audio_path
    if not final_audio:
        candidates = [
            ROOT_DIR / "assets" / "podcast_audio" / f"{podcast_name}.mp3",
            ROOT_DIR / "assets" / "podcast_audio" / f"{podcast_name}.wav",
        ]
        for c in candidates:
            if c.exists():
                final_audio = str(c)
                break

    if final_audio and Path(final_audio).exists():
        cmd_audio = [
            ffmpeg_path, "-y",
            "-i", concat_output,
            "-i", final_audio,
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            output_path
        ]
        result = subprocess.run(cmd_audio, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            print(f"⚠️ FFmpeg audio overlay ошибка: {result.stderr[:200]}")
            shutil.copy2(concat_output, output_path)
        else:
            print(f"   🎵 Аудиодорожка наложена: {final_audio}")
    else:
        shutil.copy2(concat_output, output_path)
        print(f"   ℹ️ Аудио не найдено — видео без звука")

    try:
        os.remove(concat_file)
        os.remove(concat_output)
    except OSError:
        pass

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ ФИНАЛЬНЫЙ ПОДКАСТ: {output_path}")
    print(f"   📏 Размер: {file_size_mb:.1f} MB")
    return output_path


async def run_pipeline(audio_path: str = None, podcast_name: str = "demo_podcast", test_mode: bool = False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Parse Audio to Chapters
    if audio_path and Path(audio_path).exists():
        chapters = parse_audio_to_chapters(audio_path)
    else:
        print("ℹ️ Аудио не предоставлено. Используем тестовые данные (Stub).")
        stub = _create_stub_transcription(Path("demo_podcast.mp3"))
        chapters = segment_into_chapters(stub)

    if test_mode:
        chapters = chapters[:1]  # Only render first chapter in test mode
        # Make duration short so test is fast
        chapters[0]["duration_sec"] = 5.0
        chapters[0]["end"] = chapters[0]["start"] + 5.0

    # 2. Generate Slide Data
    slides = generate_slide_data(chapters, podcast_name)
    
    # 3. Save Manifest
    manifest_path = save_slide_manifest(slides, podcast_name)
    
    # 4. Render Video
    result = await render_podcast_video(manifest_path, audio_path)
    return result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Razum AI Podcast Renderer")
    parser.add_argument("--audio", type=str, default=None, help="Path to input audio file")
    parser.add_argument("--name", type=str, default="demo_podcast", help="Name of the podcast")
    parser.add_argument("--test", action="store_true", help="Render only 1 test slide (5 seconds)")
    args = parser.parse_args()

    asyncio.run(run_pipeline(args.audio, args.name, args.test))
