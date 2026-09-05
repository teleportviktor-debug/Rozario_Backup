import os
import sys
import subprocess
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "output", "linkedin_cards")
)

def find_browser_executable() -> str:
    """Finds Chrome or Edge executable on Windows."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise FileNotFoundError("Neither Google Chrome nor Microsoft Edge was found on the system.")

def render_card_to_png(html_content: str, output_filename: str = "linkedin_card_ttft_routing.png") -> str:
    """
    Renders HTML content to a 1080x1350 PNG image.
    
    Args:
        html_content: Raw HTML string with full CSS styles.
        output_filename: Filename for the PNG image (saved in output/linkedin_cards/).
        
    Returns:
        Absolute path to the rendered PNG image.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not output_filename.endswith(".png"):
        output_filename += ".png"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    browser_path = find_browser_executable()

    # Save HTML to temporary file
    temp_dir = tempfile.gettempdir()
    temp_html_path = os.path.join(temp_dir, f"temp_card_{os.getpid()}.html")
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"🎨 [CARD RENDERER] Рендеринг карточки LinkedIn 1080x1350...")
    print(f"   Движок браузера: {browser_path}")
    print(f"   Целевой файл: {output_path}")

    cmd = [
        browser_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--window-size=1080,1350",
        f"--screenshot={output_path}",
        temp_html_path
    ]

    try:
        # Run process without text decoding pipe issues
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_b, stderr_b = process.communicate(timeout=20)
        ret_code = process.returncode
    finally:
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise RuntimeError(f"Failed to generate PNG screenshot. Chrome exit code: {ret_code}")

    file_size = os.path.getsize(output_path)
    print(f"✅ [SUCCESS] Карточка успешно отрендерена! Размер: {file_size:,} байт")
    print(f"📍 Путь: {output_path}")

    return output_path

if __name__ == "__main__":
    from services.linkedin.content_generator import generate_card_html
    html = generate_card_html()
    rendered_path = render_card_to_png(html, "test_render.png")
    print("Rendered:", rendered_path)
