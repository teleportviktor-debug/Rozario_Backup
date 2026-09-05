"""
Framer Motion & Sound Design Showcase Generator
Architecture "Genome" - Razum Google AI PRO.

Compiles:
- output/rendered_videos/framer_style_showcase_h264.mp4 (1080x1920, 60 fps, H.264 + AAC)
With:
1. Visual standard: Canvas #050508, floating rounded cards (24px radius), rgba(15,18,28,0.75),
   multilayer neon edge glow (Cobalt #0055ff to Cyan #00f0ff), interactive input with
   «Razum 3.8 / A2UI» badge and animated typing.
2. Three-layer audio engine:
   - Voiceover (deep baritone)
   - UI SFX (typing clicks 0-3s, haptic pops on cards, air whooshes on scene cuts)
   - BGM (cyber tech beat with -14dB sidechain ducking)
"""

import os
import sys
import time
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from services.content_genome.audio_designer import AudioDesigner, get_ffmpeg_executable
from services.content_genome.video_synthesizer import (
    draw_framer_glow_card, draw_interactive_input,
    COLOR_OBSIDIAN_FRAMER, COLOR_COBALT, COLOR_CYAN, COLOR_GOLD, COLOR_CARD_FILL_RGBA
)


def get_font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("calibri.ttf", size)
        except Exception:
            return ImageFont.load_default()


def draw_cyber_subtle_grid(draw: ImageDraw.Draw, width: int, height: int, step: int = 90):
    for x in range(0, width, step):
        draw.line([(x, 0), (x, height)], fill=(12, 16, 24), width=1)
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=(12, 16, 24), width=1)


def draw_klimt_golden_corners(draw: ImageDraw.Draw, width: int, height: int):
    size = 60
    # Top Left
    draw.line([(35, 35), (35 + size, 35)], fill=COLOR_GOLD, width=2)
    draw.line([(35, 35), (35, 35 + size)], fill=COLOR_GOLD, width=2)
    draw.rectangle([42, 42, 52, 52], outline=COLOR_GOLD, width=1)
    # Top Right
    draw.line([(width - 35, 35), (width - 35 - size, 35)], fill=COLOR_GOLD, width=2)
    draw.line([(width - 35, 35), (width - 35, 35 + size)], fill=COLOR_GOLD, width=2)
    draw.rectangle([width - 52, 42, width - 42, 52], outline=COLOR_GOLD, width=1)
    # Bottom Left
    draw.line([(35, height - 35), (35 + size, height - 35)], fill=COLOR_GOLD, width=2)
    draw.line([(35, height - 35), (35, height - 35 - size)], fill=COLOR_GOLD, width=2)
    draw.rectangle([42, height - 52, 52, height - 42], outline=COLOR_GOLD, width=1)
    # Bottom Right
    draw.line([(width - 35, height - 35), (width - 35 - size, height - 35)], fill=COLOR_GOLD, width=2)
    draw.line([(width - 35, height - 35), (width - 35, height - 35 - size)], fill=COLOR_GOLD, width=2)
    draw.rectangle([width - 52, height - 52, width - 42, height - 42], outline=COLOR_GOLD, width=1)


# --- High-Performance Pre-rendered Base Plates ---

def build_phase1_static_base(width: int, height: int) -> Image.Image:
    """Pre-renders Phase 1 background, cards with Gaussian blur glow, and model badge."""
    base = Image.new("RGB", (width, height), COLOR_OBSIDIAN_FRAMER)
    draw = ImageDraw.Draw(base)
    draw_cyber_subtle_grid(draw, width, height)
    draw_klimt_golden_corners(draw, width, height)

    f_tag = get_font(26)
    f_badge = get_font(30)
    f_h1 = get_font(48)
    f_sub = get_font(24)

    # Top Brand Bar
    draw.text((80, 80), "[ SOVEREIGN AI RUNTIME • FRAMER SPEC ]", fill=COLOR_CYAN, font=f_tag)
    draw.text((width - 380, 80), "STATUS: SCANNING", fill=COLOR_GOLD, font=f_tag)

    # Header Card with Neon Glow
    base = draw_framer_glow_card(
        base_img=base,
        box=(70, 140, width - 70, 320),
        radius=24,
        fill_rgba=(18, 22, 34, 200),
        border_outer=COLOR_CYAN,
        border_inner=COLOR_COBALT,
        glow_color=(0, 140, 255, 170),
        glow_radius=20
    )
    d = ImageDraw.Draw(base)
    d.text((105, 175), "ENTERPRISE THREAT RADAR:", fill=COLOR_GOLD, font=f_tag)
    d.text((105, 225), "Public Cloud AI Data Leak Scanner", fill=(245, 248, 255), font=f_h1)

    # Interactive Input Container with Glow
    base = draw_interactive_input(
        base_img=base,
        box=(70, 360, width - 70, 560),
        model_badge_text="Razum 3.8 / A2UI",
        prompt_text="",
        blink_cursor=False,
        radius=24
    )

    # Threat Warning Alert Card
    base = draw_framer_glow_card(
        base_img=base,
        box=(70, 600, width - 70, 880),
        radius=24,
        fill_rgba=(32, 12, 18, 210),
        border_outer=(255, 0, 60, 230),
        border_inner=(160, 0, 40, 140),
        glow_color=(255, 0, 60, 180),
        glow_radius=22
    )
    d = ImageDraw.Draw(base)
    d.text((105, 635), "CRITICAL LEAK RISK DETECTED:", fill=(255, 0, 60), font=f_badge)
    d.text((105, 695), "\"Your employees are pasting company secrets\n into public AI APIs right now.\"", fill=(245, 245, 250), font=f_h1)
    d.text((105, 820), "• 147 API Tokens exposed across unmonitored webhooks", fill=COLOR_CYAN, font=f_sub)

    # Bottom Branding
    d.text((width // 2 - 240, 1820), "VER SACRUM FRAMER MOTION • REEL #2", fill=COLOR_GOLD, font=f_tag)
    return base


def build_phase2_static_base(width: int, height: int) -> Tuple[Image.Image, Image.Image]:
    """Pre-renders Phase 2 base and Card 2 with glow."""
    base = Image.new("RGB", (width, height), COLOR_OBSIDIAN_FRAMER)
    draw = ImageDraw.Draw(base)
    draw_cyber_subtle_grid(draw, width, height)
    draw_klimt_golden_corners(draw, width, height)

    f_tag = get_font(26)
    f_badge = get_font(32)
    f_body = get_font(28)
    f_code = get_font(25)

    draw.text((80, 80), "[ ARCHITECTURAL TOPOLOGY • PROOF ]", fill=COLOR_CYAN, font=f_tag)

    # Card 1: Vulnerable SaaS Middleware Mesh
    base = draw_framer_glow_card(
        base_img=base,
        box=(70, 140, width - 70, 720),
        radius=24,
        fill_rgba=(30, 14, 20, 200),
        border_outer=(255, 0, 60, 220),
        border_inner=(120, 10, 25, 140),
        glow_color=(255, 0, 60, 160),
        glow_radius=20
    )
    d = ImageDraw.Draw(base)
    d.text((105, 175), "VULNERABLE SAAS MESH (Zapier / Make / Public Proxies)", fill=(255, 0, 60), font=f_badge)
    d.text((105, 240), "❌ 5 Unencrypted cloud hops between user prompt and LLM", fill=(240, 240, 245), font=f_body)
    d.text((105, 295), "❌ API Tokens and Bearer keys stored in 3rd-party databases", fill=(240, 240, 245), font=f_body)
    d.text((105, 350), "❌ Sensitive customer PII retained for external model training", fill=(240, 240, 245), font=f_body)
    d.text((105, 405), "❌ Latency penalty: +480ms to +1,200ms overhead", fill=(240, 240, 245), font=f_body)

    d.rectangle([105, 480, width - 105, 660], fill=(16, 8, 12), outline=(255, 0, 60), width=1)
    d.text((125, 510), "ROUTE: Client -> SaaS Webhook -> Public LLM -> SaaS -> Client", fill=(255, 0, 60), font=f_code)
    d.text((125, 560), "THREAT STATUS: CRITICAL DATA LEAK VECTOR", fill=COLOR_GOLD, font=f_code)
    d.text((125, 610), "PII MASKING: DISABLED (Raw payload exposed)", fill=(200, 200, 210), font=f_code)

    draw.text((width // 2 - 240, 1820), "VER SACRUM FRAMER MOTION • REEL #2", fill=COLOR_GOLD, font=f_tag)

    # Card 2 (Floating overlay patch)
    card2_img = Image.new("RGBA", (width, 860), (0, 0, 0, 0))
    glow_l = Image.new("RGBA", (width, 860), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_l)
    gd.rounded_rectangle([70, 10, width - 70, 830], radius=24, outline=(0, 160, 255, 200), width=6)
    blurred = glow_l.filter(ImageFilter.GaussianBlur(radius=20))

    body_l = Image.new("RGBA", (width, 860), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body_l)
    bd.rounded_rectangle([70, 10, width - 70, 830], radius=24, fill=(14, 22, 34, 225), outline=COLOR_CYAN, width=2)
    bd.rounded_rectangle([73, 13, width - 73, 827], radius=21, outline=COLOR_COBALT, width=1)

    bd.text((105, 45), "SOVEREIGN ZERO TRUST CONTOUR", fill=COLOR_CYAN, font=f_badge)
    bd.text((105, 105), "Google Workspace + Vertex In-VPC Boundary:", fill=COLOR_GOLD, font=f_body)
    bd.text((105, 165), "✓ 0 Public Middleware Hops (Strict VPC-SC Air Gap)", fill=(240, 244, 250), font=f_body)
    bd.text((105, 220), "✓ Hardware-Bound Secret: Bearer ntn_... Token", fill=COLOR_CYAN, font=f_body)
    bd.text((105, 275), "✓ Sub-20ms PaliGemma 2 Native PII Masking Engine", fill=(240, 244, 250), font=f_body)
    bd.text((105, 330), "✓ Native A2UI CardService Transpiler in Gmail", fill=COLOR_GOLD, font=f_body)

    bd.rectangle([105, 410, width - 105, 600], fill=(8, 16, 26), outline=COLOR_CYAN, width=1)
    bd.text((125, 440), "AIR-GAP ROUTE: Gmail/Docs <-> n8n Bridge <-> Vertex AI VPC", fill=COLOR_CYAN, font=f_code)
    bd.text((125, 490), "SECURITY: Bearer ntn_... [ENCRYPTED IN HARDWARE KEYSTORE]", fill=COLOR_GOLD, font=f_code)
    bd.text((125, 540), "LATENCY: 18ms Transpile | 0 Bounded Data Leakage", fill=(240, 244, 250), font=f_code)

    bd.rounded_rectangle([105, 640, width - 105, 730], radius=16, fill=(0, 45, 90), outline=COLOR_CYAN, width=2)
    bd.text((width // 2 - 220, 665), "100% AIR-GAPPED CONTROL CERTIFIED", fill=(255, 255, 255), font=f_badge)

    card2_composite = Image.alpha_composite(blurred, body_l)
    return base, card2_composite


def build_phase3_static_base(width: int, height: int) -> Image.Image:
    """Pre-renders Phase 3 base cards with glow."""
    base = Image.new("RGB", (width, height), COLOR_OBSIDIAN_FRAMER)
    draw = ImageDraw.Draw(base)
    draw_cyber_subtle_grid(draw, width, height)
    draw_klimt_golden_corners(draw, width, height)

    f_tag = get_font(26)
    f_badge = get_font(34)
    f_h1 = get_font(46)
    f_body = get_font(30)
    f_code = get_font(26)

    draw.text((80, 80), "[ A2UI TECHNOLOGY • INBOX EMBEDDED ]", fill=COLOR_CYAN, font=f_tag)

    card_box = (70, 140, width - 70, 1100)
    base = draw_framer_glow_card(
        base_img=base,
        box=card_box,
        radius=24,
        fill_rgba=(15, 20, 32, 220),
        border_outer=COLOR_CYAN,
        border_inner=COLOR_COBALT,
        glow_color=(0, 160, 255, 190),
        glow_radius=22
    )
    d = ImageDraw.Draw(base)
    d.text((105, 175), "NATIVE GMAIL CARDSERVICE AUDIT WIDGET", fill=COLOR_GOLD, font=f_badge)
    d.text((105, 240), "Real-time Zero Trust Compliance in Inbox", fill=(245, 245, 250), font=f_h1)

    items_y = 540
    inspections = [
        ("• Automated PII Redaction", "PASS (12ms execution)"),
        ("• Token Encryption", "PASS (Bearer ntn_...)"),
        ("• Gateway Exposure", "ZERO (0 Public Hops)"),
        ("• Model Training Isolation", "100% SOVEREIGN BOUNDARY")
    ]
    for title, val in inspections:
        d.text((105, items_y), title, fill=(240, 240, 245), font=f_body)
        d.text((width - 420, items_y), val, fill=COLOR_GOLD, font=f_body)
        items_y += 65

    d.rectangle([105, 840, width - 105, 1020], fill=(8, 16, 26), outline=COLOR_GOLD, width=1)
    d.text((125, 865), "TRANSPILER: v0 JSX -> Google Apps Script CardService", fill=COLOR_CYAN, font=f_code)
    d.text((125, 915), "SPEED: 18ms Autonomous Assembly | 0 External Iframes", fill=COLOR_GOLD, font=f_code)
    d.text((125, 965), "STATUS: FULLY COMPLIANT WITH ZERO TRUST CHARTER", fill=(240, 244, 250), font=f_code)

    banner_box = (70, 1200, width - 70, 1620)
    base = draw_framer_glow_card(
        base_img=base,
        box=banner_box,
        radius=24,
        fill_rgba=(20, 26, 40, 210),
        border_outer=COLOR_GOLD,
        border_inner=COLOR_CYAN,
        glow_color=COLOR_GOLD,
        glow_radius=20
    )
    d = ImageDraw.Draw(base)
    d.text((105, 1240), "THE SOVEREIGN ADVANTAGE:", fill=COLOR_GOLD, font=f_badge)
    d.text((105, 1310), "\"Monitor and enforce compliance directly in employee inboxes.\nSanitize tokens and PII in under twenty milliseconds\nbefore requests ever leave your boundary.\"", fill=(245, 248, 255), font=f_body)

    d.text((width // 2 - 240, 1820), "VER SACRUM FRAMER MOTION • REEL #2", fill=COLOR_GOLD, font=f_tag)
    return base


def build_phase4_static_base(width: int, height: int) -> Image.Image:
    """Pre-renders Phase 4 golden finale cards with glow."""
    base = Image.new("RGB", (width, height), COLOR_OBSIDIAN_FRAMER)
    draw = ImageDraw.Draw(base)
    draw_cyber_subtle_grid(draw, width, height)
    draw_klimt_golden_corners(draw, width, height)

    f_tag = get_font(28)
    f_h1 = get_font(54)
    f_h2 = get_font(40)
    f_cta = get_font(38)
    f_body = get_font(32)
    f_sub = get_font(24)

    draw.text((width // 2 - 200, 90), "VER SACRUM ARCHITECTURE", fill=COLOR_GOLD, font=f_tag)

    # 3D Gold Shield / Emblem
    cx, cy = width // 2, 430
    for offset in range(0, 16, 2):
        draw.polygon([
            (cx, cy - 190 + offset),
            (cx + 190 - offset, cy),
            (cx, cy + 190 - offset),
            (cx - 190 + offset, cy)
        ], outline=COLOR_GOLD, fill=None)

    draw.rectangle([cx - 95, cy - 95, cx + 95, cy + 95], outline=COLOR_GOLD, width=3)
    draw.rectangle([cx - 75, cy - 75, cx + 75, cy + 75], fill=(32, 26, 12), outline=COLOR_CYAN, width=2)
    draw.text((cx - 50, cy - 28), "ZERO", fill=COLOR_GOLD, font=f_tag)
    draw.text((cx - 60, cy + 12), "TRUST", fill=COLOR_CYAN, font=f_tag)

    draw.text((width // 2 - 390, 710), "SECURE YOUR ENTERPRISE AI", fill=(245, 248, 255), font=f_h1)
    draw.text((width // 2 - 280, 785), "WITHOUT PUBLIC GATEWAYS", fill=COLOR_CYAN, font=f_h2)

    feat_box = (70, 890, width - 70, 1290)
    base = draw_framer_glow_card(
        base_img=base,
        box=feat_box,
        radius=24,
        fill_rgba=(16, 22, 34, 210),
        border_outer=COLOR_CYAN,
        border_inner=COLOR_GOLD,
        glow_color=(0, 140, 255, 170),
        glow_radius=20
    )
    d = ImageDraw.Draw(base)
    d.text((105, 925), "ENTERPRISE SOVEREIGN GUARANTEE:", fill=COLOR_GOLD, font=f_tag)

    features = [
        "100% In-VPC Data Residency & Hardware Token Keystore",
        "Sub-20ms PaliGemma 2 Automated PII Redaction",
        "Native Google Workspace A2UI Direct Transpilation",
        "Zero 3rd-Party SaaS Middleware Vulnerabilities",
        "Complete Model Training Data Protection"
    ]
    fy = 990
    for feat in features:
        d.ellipse([105, fy + 7, 123, fy + 25], fill=COLOR_CYAN)
        d.text((140, fy), feat, fill=(240, 244, 250), font=f_body)
        fy += 56

    # Pulsing Floating CTA Button
    btn_box = (80, 1370, width - 80, 1510)
    base = draw_framer_glow_card(
        base_img=base,
        box=btn_box,
        radius=24,
        fill_rgba=(0, 240, 255, 240),
        border_outer=(255, 255, 255, 255),
        border_inner=COLOR_GOLD,
        glow_color=COLOR_CYAN,
        glow_radius=22,
        border_width=3
    )
    d = ImageDraw.Draw(base)
    d.text((120, 1415), "AUDIT YOUR AI PERIMETER IN 60 SECONDS", fill=(8, 10, 14), font=f_cta)

    d.text((width // 2 - 270, 1545), "Instant audit report • Zero code changes • No credit card", fill=(200, 210, 225), font=f_sub)

    d.rectangle([70, 1630, width - 70, 1750], fill=(12, 16, 24), outline=COLOR_GOLD, width=1)
    d.text((100, 1655), "TRUST & COMPLIANCE:", fill=COLOR_CYAN, font=f_sub)
    d.text((100, 1695), "ISO 27001 • SOC2 TYPE II • HIPAA READY • GOOGLE CLOUD PARTNER", fill=COLOR_GOLD, font=f_body)

    d.text((width // 2 - 240, 1820), "VER SACRUM FRAMER MOTION • REEL #2", fill=COLOR_GOLD, font=f_tag)
    return base


def generate_framer_showcase_video():
    print("===================================================================")
    print("✨ [FRAMER MOTION & SOUND DESIGN] Ultra-Smooth 60fps B2B Reel")
    print("===================================================================")

    width, height = 1080, 1920
    fps = 60
    duration_sec = 15.0
    total_frames = int(duration_sec * fps)  # 900 frames

    output_dir = os.path.join(WORKSPACE_ROOT, "output", "rendered_videos")
    os.makedirs(output_dir, exist_ok=True)
    final_mp4 = os.path.join(output_dir, "framer_style_showcase_h264.mp4")
    raw_video_mp4 = os.path.join(output_dir, "temp_framer_raw_60fps.mp4")

    # 1. Sound Design Engine Setup
    print("🎵 Initializing Audio Designer...")
    audio_designer = AudioDesigner(output_dir=os.path.join(output_dir, "framer_audio_assets"))

    voiceover_script = (
        "Your employees are pasting company secrets into public AI APIs right now. "
        "Stop data leaks with a sovereign Zero Trust contour inside Google Workspace. "
        "Audit your enterprise AI security perimeter in sixty seconds."
    )

    print("🎙️ Generating Layer 1: Neural Baritone Voiceover...")
    voice_path = audio_designer.generate_voiceover_track(voiceover_script, duration_sec=duration_sec)
    print(f"  ✓ Voiceover Track: {voice_path} ({os.path.getsize(voice_path)} bytes)")

    print("🥁 Generating Layer 3: Minimalist Cyber Tech BGM (120 BPM)...")
    bgm_path = audio_designer.generate_bgm_track(duration_sec=duration_sec, bpm=120.0)
    print(f"  ✓ BGM Track: {bgm_path} ({os.path.getsize(bgm_path)} bytes)")

    print("🎹 Generating Layer 2: Synchronized UI SFX Track...")
    sfx_path = audio_designer.build_sfx_timeline_track(
        duration_sec=duration_sec,
        scene_timestamps=[3.5, 8.5, 12.0],
        typing_intervals=[(0.35, 3.0)],
        card_reveal_times=[0.25, 3.2, 4.3, 8.9, 12.3]
    )
    print(f"  ✓ SFX Timeline Track: {sfx_path} ({os.path.getsize(sfx_path)} bytes)")

    # 2. Pre-render base plates (Glow computed once for maximum performance)
    print("🎨 Pre-rendering Framer Glow Base Plates...")
    t_pre = time.time()
    p1_base = build_phase1_static_base(width, height)
    p2_base, p2_card2 = build_phase2_static_base(width, height)
    p3_base = build_phase3_static_base(width, height)
    p4_base = build_phase4_static_base(width, height)
    print(f"  ✓ All 4 Framer Glow Plates ready in {time.time() - t_pre:.2f}s")

    # 3. Render 60fps Video Stream directly to FFmpeg stdin
    print("🎬 Rendering 60 FPS Framer Motion Frames directly to FFmpeg pipe...")
    ffmpeg_exe = get_ffmpeg_executable()

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-crf", "19",
        raw_video_mp4
    ]

    pipe_proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    target_prompt = "Isolate Google Workspace AI: Block rogue cloud tokens..."
    prompt_len = len(target_prompt)
    f_body = get_font(30)
    f_badge = get_font(34)

    # Frame generation loop (900 frames)
    t0 = time.time()
    for frame_idx in range(total_frames):
        cur_time = frame_idx / fps

        # Phase 1: 0.0s - 3.5s (Frames 0 - 210)
        if cur_time < 3.5:
            img = p1_base.copy()
            d = ImageDraw.Draw(img)

            # Typing effect
            type_progress = max(0.0, min(1.0, (cur_time - 0.35) / 2.5))
            chars_shown = int(type_progress * prompt_len)
            typed = target_prompt[:chars_shown]
            cursor_on = (frame_idx // 12) % 2 == 0
            cursor_str = " |" if cursor_on else ""
            d.text((98, 440), f"{typed}{cursor_str}", fill=(245, 248, 255), font=f_body)

            # Scanner Radar in center
            cx, cy = width // 2, 1180
            for r in [90, 180, 270]:
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 60, 90), width=1)
            d.line([(cx - 280, cy), (cx + 280, cy)], fill=(0, 70, 100), width=1)
            d.line([(cx, cy - 280), (cx, cy + 280)], fill=(0, 70, 100), width=1)

            angle = (cur_time / 3.5) * 2.0 * np.pi
            rx = int(cx + 250 * np.cos(angle))
            ry = int(cy + 250 * np.sin(angle))
            d.line([(cx, cy), (rx, ry)], fill=COLOR_CYAN, width=3)
            d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=COLOR_GOLD)

            # Button popup at end of phase
            if cur_time > 3.0:
                d.rounded_rectangle([100, 1550, width - 100, 1680], radius=24, fill=(0, 85, 255), outline=COLOR_CYAN, width=2)
                d.text((width // 2 - 210, 1595), "ISOLATING PERIMETER...", fill=(255, 255, 255), font=f_badge)

        # Phase 2: 3.5s - 8.5s (Frames 210 - 510)
        elif cur_time < 8.5:
            img = p2_base.copy()
            # Animate Card 2 sliding up smoothly
            slide_t = min(1.0, (cur_time - 3.5) / 0.8)
            ease_out = 1.0 - (1.0 - slide_t) ** 3
            card2_y = int(1200 - ease_out * 420)  # slides from 1200 down to 780

            # Paste card 2 RGBA overlay onto img
            img.paste(p2_card2, (0, card2_y), p2_card2)

        # Phase 3: 8.5s - 12.0s (Frames 510 - 720)
        elif cur_time < 12.0:
            img = p3_base.copy()
            d = ImageDraw.Draw(img)

            # Gauge fills up smoothly
            gauge = min(1.0, (cur_time - 8.5) / 1.5)
            gauge_eased = 1.0 - (1.0 - gauge) ** 2
            gauge_w = int(gauge_eased * (width - 250))

            d.rounded_rectangle([105, 340, width - 105, 410], radius=16, fill=(10, 14, 22), outline=COLOR_COBALT, width=2)
            if gauge_w > 10:
                d.rounded_rectangle([105, 340, 105 + gauge_w, 410], radius=16, fill=COLOR_CYAN)
            score_val = int(gauge_eased * 100)
            d.text((width // 2 - 160, 440), f"PERIMETER SCORE: {score_val} / 100", fill=COLOR_CYAN, font=f_badge)

        # Phase 4: 12.0s - 15.0s (Frames 720 - 900)
        else:
            img = p4_base.copy()
            d = ImageDraw.Draw(img)
            # Subtle breathing pulse on the CTA button border
            phase4_t = (cur_time - 12.0) / 3.0
            pulse_ring = int(6 * np.sin(2.0 * np.pi * 1.5 * phase4_t))
            if pulse_ring > 0:
                d.rounded_rectangle([80 - pulse_ring, 1370 - pulse_ring, width - 80 + pulse_ring, 1510 + pulse_ring], radius=24 + pulse_ring, outline=COLOR_CYAN, width=1)

        raw_bytes = img.tobytes()
        pipe_proc.stdin.write(raw_bytes)

        if frame_idx % 180 == 0:
            print(f"  • Piped frame {frame_idx}/{total_frames} ({cur_time:.1f}s)...")

    pipe_proc.stdin.close()
    pipe_proc.wait()
    render_dur = time.time() - t0
    raw_size = os.path.getsize(raw_video_mp4)
    print(f"✓ Video Stream Encoded: {raw_video_mp4} ({raw_size} bytes in {render_dur:.1f}s, {total_frames/render_dur:.1f} fps)")

    # 4. Audio Mixing with Automated Sidechain Ducking (-14dB)
    print("🎚️ Mixing Three-Layer Audio into Final MP4 with Sidechain Ducking...")
    audio_designer.mix_audio_into_video(
        video_input=raw_video_mp4,
        voiceover_wav=voice_path,
        bgm_wav=bgm_path,
        sfx_wav=sfx_path,
        output_mp4=final_mp4,
        ducking_db=14.0
    )
    final_size = os.path.getsize(final_mp4)
    print(f"✓ Final Framer Motion MP4 Created: {final_mp4} ({final_size} bytes)")

    # Clean up raw temp video
    if os.path.exists(raw_video_mp4):
        try:
            os.remove(raw_video_mp4)
        except Exception:
            pass

    # 5. Save Keyframe preview snapshots for immediate QA
    frames_dir = os.path.join(output_dir, "framer_showcase_frames")
    os.makedirs(frames_dir, exist_ok=True)
    p1_base.save(os.path.join(frames_dir, "framer_01_hook_input.png"))
    # Save phase 2 snapshot with card pasted
    p2_snap = p2_base.copy()
    p2_snap.paste(p2_card2, (0, 780), p2_card2)
    p2_snap.save(os.path.join(frames_dir, "framer_02_card_assembly.png"))
    p3_base.save(os.path.join(frames_dir, "framer_03_a2ui_audit.png"))
    p4_base.save(os.path.join(frames_dir, "framer_04_golden_cta.png"))
    print(f"✓ Saved 4 Keyframe snapshots in {frames_dir}")

    # 6. Update Preview Player HTML
    player_html = os.path.join(output_dir, "reel_preview_player.html")
    with open(player_html, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ver Sacrum • Framer Motion & Sound Design Showcase</title>
    <style>
        body {{
            background-color: #050508;
            color: #f0f4f8;
            font-family: 'Segoe UI', -apple-system, sans-serif;
            margin: 0;
            padding: 30px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        h1 {{
            color: #d4af37;
            letter-spacing: 2px;
            margin-bottom: 5px;
        }}
        .badge {{
            background: rgba(0, 85, 255, 0.2);
            color: #00f0ff;
            border: 1px solid #00f0ff;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 13px;
            margin-bottom: 25px;
        }}
        .container {{
            display: flex;
            gap: 40px;
            max-width: 1350px;
            width: 100%;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .video-card {{
            background: rgba(15, 18, 28, 0.85);
            border: 2px solid #00f0ff;
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 10px 40px rgba(0, 140, 255, 0.25);
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        video {{
            width: 360px;
            height: 640px;
            border-radius: 16px;
            border: 1px solid #0055ff;
            background: #000;
        }}
        .frames-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            max-width: 780px;
        }}
        .frame-thumb {{
            background: rgba(15, 18, 28, 0.75);
            border: 1px solid #0055ff;
            border-radius: 16px;
            padding: 12px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0, 85, 255, 0.15);
        }}
        .frame-thumb img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        .frame-title {{
            font-size: 13px;
            color: #d4af37;
            margin-top: 8px;
        }}
        .audio-specs {{
            background: rgba(12, 16, 24, 0.9);
            border: 1px solid #d4af37;
            border-radius: 16px;
            padding: 18px;
            margin-top: 20px;
            width: 100%;
            box-sizing: border-box;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <h1>VER SACRUM GENOME • FRAMER MOTION & SOUND</h1>
    <div class="badge">SPEC: 1080x1920 @ 60 FPS | 3-LAYER AUDIO (Voice + UI SFX + Sidechain Ducked BGM)</div>

    <div class="container">
        <div class="video-card">
            <h3 style="margin-top:0; color:#00f0ff;">Broadcast 60fps MP4 Player</h3>
            <video controls autoplay loop>
                <source src="framer_style_showcase_h264.mp4" type="video/mp4">
                Your browser does not support video.
            </video>
            <div class="audio-specs">
                <div style="color:#00f0ff; font-weight:bold; margin-bottom:6px;">Three-Layer Sound Engine:</div>
                <div>• <b>Voiceover:</b> Deep Baritone (en-US-Christopher -6Hz)</div>
                <div>• <b>UI SFX:</b> Typing clicks (0-3s), haptic pops, air whooshes</div>
                <div>• <b>BGM:</b> 120 BPM Cyber Tech Beat with -14dB Sidechain Ducking</div>
                <div style="margin-top:6px; color:#d4af37;">• <b>Visuals:</b> Canvas #050508, 24px Blur Glow Cards</div>
            </div>
        </div>

        <div>
            <h3 style="color:#d4af37; margin-top:0;">Framer Specification Keyframes</h3>
            <div class="frames-grid">
                <div class="frame-thumb">
                    <img src="framer_showcase_frames/framer_01_hook_input.png" alt="Hook Input">
                    <div class="frame-title">1. Input with «Razum 3.8 / A2UI» Badge</div>
                </div>
                <div class="frame-thumb">
                    <img src="framer_showcase_frames/framer_02_card_assembly.png" alt="Card Assembly">
                    <div class="frame-title">2. Floating Card Assembly (SaaS vs Sovereign)</div>
                </div>
                <div class="frame-thumb">
                    <img src="framer_showcase_frames/framer_03_a2ui_audit.png" alt="A2UI Audit">
                    <div class="frame-title">3. Live Inbox A2UI Security Card</div>
                </div>
                <div class="frame-thumb">
                    <img src="framer_showcase_frames/framer_04_golden_cta.png" alt="Golden CTA">
                    <div class="frame-title">4. Golden Emblem & 60s Audit CTA</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
""")
    print(f"✓ Preview player updated: {player_html}")

    print("===================================================================")
    print("✨ FRAMER MOTION & SOUND DESIGN PIPELINE COMPLETED SUCCESSFULLY")
    print("===================================================================\n")


if __name__ == "__main__":
    generate_framer_showcase_video()
