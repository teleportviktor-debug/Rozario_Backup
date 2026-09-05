"""
============================================================================
RAZUM AI 2026 • SHORTS RENDERER (Playwright + FFmpeg)
Renders 9:16 vertical Shorts by:
  1. Opening the Stitch HTML template in headless Chromium
  2. Injecting scene data via page.evaluate()
  3. Capturing each scene as a video segment
  4. Compositing all segments + audio via FFmpeg
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
OUTPUT_DIR = ROOT_DIR / "05_Content" / "Video" / "rendered_shorts"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Try importing scene builder
sys.path.insert(0, str(Path(__file__).resolve().parent))
from shorts_scene_builder import build_scene_manifest, build_all_manifests


async def render_single_short(manifest: dict, output_path: str = None) -> str:
    """
    Render a complete Short video from a scene manifest.
    Uses Playwright to capture animated HTML frames, then FFmpeg to compose.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright не установлен. Запустите: pip install playwright && playwright install chromium")
        return ""

    reel_id = manifest["reel_id"]
    final_output = output_path or str(OUTPUT_DIR / f"{reel_id}_FINAL.mp4")
    scene_videos = []

    print(f"\n🎬 Рендеринг Short: {manifest['title']}")
    print(f"   Сцен: {len(manifest['scenes'])}, Длительность: {manifest['total_duration_sec']} сек")

    template_url = (TEMPLATES_DIR / "short_9x16_base.html").as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for scene in manifest["scenes"]:
            scene_idx = scene["index"]
            duration_ms = int(scene["duration_sec"] * 1000)
            scene_video_path = str(OUTPUT_DIR / f"{reel_id}_scene_{scene_idx:02d}.webm")

            print(f"   📹 Сцена {scene_idx}: {scene['scene_type']} ({scene['duration_sec']}s)...", end=" ")

            # Create context with video recording
            context = await browser.new_context(
                viewport={"width": 1080, "height": 1920},
                device_scale_factor=1,
                record_video_dir=str(OUTPUT_DIR),
                record_video_size={"width": 1080, "height": 1920}
            )

            page = await context.new_page()
            await page.goto(template_url, wait_until="networkidle")

            # Inject scene data into the template
            scene_json = json.dumps(scene, ensure_ascii=False)
            await page.evaluate(f"window.renderScene({scene_json})")

            # Wait for animations to play + scene duration
            # Add 500ms buffer for CSS animations to start
            await page.wait_for_timeout(min(duration_ms + 500, 12000))

            # Close context to finalize video
            video_path = await page.video.path()
            await context.close()

            # Move recorded video to expected location
            if Path(video_path).exists():
                shutil.move(str(video_path), scene_video_path)
                scene_videos.append(scene_video_path)
                print("✓")
            else:
                print("⚠️ Видео не записано")

        await browser.close()

    if not scene_videos:
        print("❌ Ни одна сцена не была отрендерена.")
        return ""

    # Compose final video with FFmpeg
    final_path = _ffmpeg_compose(scene_videos, manifest, final_output)
    return final_path


def _ffmpeg_compose(scene_videos: list, manifest: dict, output_path: str) -> str:
    """
    Use FFmpeg to concatenate scene videos and optionally add audio.
    """
    # Check if ffmpeg is available
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        # Try common Windows paths
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
        print("   Сцены сохранены как отдельные .webm файлы.")
        return scene_videos[0] if scene_videos else ""

    print(f"\n🔧 FFmpeg композитинг ({len(scene_videos)} сцен)...")

    # Create concat list file
    concat_file = str(OUTPUT_DIR / f"{manifest['reel_id']}_concat.txt")
    with open(concat_file, "w", encoding="utf-8") as f:
        for sv in scene_videos:
            # FFmpeg concat requires forward slashes or escaped backslashes
            safe_path = sv.replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    # Step 1: Concatenate all scene videos
    concat_output = str(OUTPUT_DIR / f"{manifest['reel_id']}_concat.mp4")
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
        return scene_videos[0]

    # Step 2: Check for audio track
    audio_candidates = [
        ROOT_DIR / "assets" / "podcast_audio" / f"{manifest['reel_id']}.mp3",
        ROOT_DIR / "assets" / "podcast_audio" / f"{manifest['reel_id']}.wav",
    ]
    audio_path = None
    for ac in audio_candidates:
        if ac.exists():
            audio_path = str(ac)
            break

    if audio_path:
        # Overlay audio
        cmd_audio = [
            ffmpeg_path, "-y",
            "-i", concat_output,
            "-i", audio_path,
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
            print(f"   🎵 Аудиодорожка наложена: {audio_path}")
    else:
        # No audio — just rename concat output
        shutil.copy2(concat_output, output_path)
        print(f"   ℹ️ Аудио не найдено — видео без звука")

    # Cleanup temp files
    try:
        os.remove(concat_file)
        os.remove(concat_output)
    except OSError:
        pass

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ ФИНАЛЬНОЕ ВИДЕО: {output_path}")
    print(f"   📏 Размер: {file_size_mb:.1f} MB")
    return output_path


async def render_all_shorts():
    """Render all reels from PROMO_REELS as vertical Shorts."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manifests = build_all_manifests()

    results = []
    for m in manifests:
        result = await render_single_short(m)
        if result:
            results.append(result)

    print(f"\n{'=' * 65}")
    print(f"🏁 РЕНДЕРИНГ ЗАВЕРШЁН: {len(results)}/{len(manifests)} Shorts готовы")
    print(f"{'=' * 65}")
    return results


async def test_render():
    """Quick test: render only the first scene of the first reel."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    manifest = build_scene_manifest(0)
    # Trim to first scene only for testing
    manifest["scenes"] = manifest["scenes"][:1]
    manifest["total_duration_sec"] = manifest["scenes"][0]["duration_sec"]

    print("🧪 ТЕСТОВЫЙ РЕНДЕР: 1 сцена из первого ролика")
    result = await render_single_short(manifest, str(OUTPUT_DIR / "TEST_render.mp4"))
    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Razum AI Shorts Renderer")
    parser.add_argument("--test", action="store_true", help="Render only 1 test scene")
    parser.add_argument("--reel", type=int, default=None, help="Render specific reel by index (0-based)")
    args = parser.parse_args()

    if args.test:
        asyncio.run(test_render())
    elif args.reel is not None:
        manifest = build_scene_manifest(args.reel)
        asyncio.run(render_single_short(manifest))
    else:
        asyncio.run(render_all_shorts())
