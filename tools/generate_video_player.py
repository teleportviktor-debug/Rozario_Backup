import os
import glob
import base64
import json

def generate_video_player_html():
    frames_dir = r"C:\Users\user\ГУГЛ ИМПЕРИЯ\output\rendered_videos\reel_draft_fast_frames"
    output_html = r"C:\Users\user\ГУГЛ ИМПЕРИЯ\output\rendered_videos\reel_preview_player.html"
    
    png_files = sorted(glob.glob(os.path.join(frames_dir, "*.png")))
    images_b64 = []
    for f in png_files:
        with open(f, "rb") as img_f:
            b64 = base64.b64encode(img_f.read()).decode("utf-8")
            images_b64.append(f"data:image/png;base64,{b64}")

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <title>Razum AI • B2B Video Shorts Player (1080x1920)</title>
  <style>
    :root {{
      --obsidian: #0a0a0c;
      --cyan: #00f0ff;
      --gold: #d4af37;
      --surface: #121216;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--obsidian);
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }}
    .player-container {{
      display: flex;
      flex-direction: column;
      align-items: center;
      background: var(--surface);
      border: 1px solid rgba(0, 240, 255, 0.3);
      box-shadow: 0 0 40px rgba(0, 240, 255, 0.15);
      border-radius: 20px;
      padding: 24px;
      max-width: 480px;
      width: 100%;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      width: 100%;
      margin-bottom: 16px;
      font-size: 13px;
      color: var(--cyan);
      font-weight: 700;
      letter-spacing: 1px;
    }}
    .phone-canvas {{
      width: 320px;
      height: 568px;
      border-radius: 16px;
      overflow: hidden;
      position: relative;
      border: 2px solid var(--cyan);
      background: #000;
      box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }}
    .phone-canvas img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
      transition: opacity 0.3s ease-in-out;
    }}
    .controls {{
      margin-top: 20px;
      display: flex;
      gap: 12px;
      align-items: center;
      width: 100%;
      justify-content: center;
    }}
    button {{
      background: rgba(0, 240, 255, 0.15);
      border: 1px solid var(--cyan);
      color: var(--cyan);
      padding: 10px 20px;
      border-radius: 10px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }}
    button:hover {{
      background: var(--cyan);
      color: var(--obsidian);
      box-shadow: 0 0 15px var(--cyan);
    }}
    .progress-bar {{
      width: 100%;
      height: 6px;
      background: rgba(255,255,255,0.1);
      border-radius: 3px;
      margin-top: 16px;
      overflow: hidden;
    }}
    .progress-fill {{
      height: 100%;
      width: 0%;
      background: linear-gradient(90deg, var(--cyan), var(--gold));
      transition: width 0.1s linear;
    }}
    .scene-meta {{
      margin-top: 12px;
      font-size: 12px;
      color: var(--gold);
      font-family: monospace;
    }}
  </style>
</head>
<body>
  <div class="player-container">
    <div class="header">
      <span>✦ VER SACRUM VIDEO PLAYER</span>
      <span>9:16 SHORTS</span>
    </div>
    
    <div class="phone-canvas">
      <img id="scene-img" src="{images_b64[0] if images_b64 else ''}" alt="Reel Scene">
    </div>

    <div class="progress-bar">
      <div class="progress-fill" id="progress"></div>
    </div>

    <div class="scene-meta" id="scene-label">
      Сцена 1 из {len(images_b64)} • ХУК 0-5 сек
    </div>

    <div class="controls">
      <button onclick="prevScene()">◀ Назад</button>
      <button id="play-btn" onclick="togglePlay()">⏸ Пауза</button>
      <button onclick="nextScene()">Вперед ▶</button>
    </div>
  </div>

  <script>
    const frames = {json.dumps(images_b64)};
    let currentIdx = 0;
    let isPlaying = true;
    let timer = null;
    const durationPerScene = 4000; // 4 seconds per scene

    function updateView() {{
      document.getElementById('scene-img').src = frames[currentIdx];
      document.getElementById('scene-label').innerText = 
        `Сцена ${{currentIdx + 1}} из ${{frames.length}} • ${{currentIdx === 0 ? 'ХУК 0-5 сек' : (currentIdx === frames.length - 1 ? 'ФИНАЛЬНЫЙ CTA' : 'АРХИТЕКТУРНОЕ ДОКАЗАТЕЛЬСТВО')}}`;
      
      const pct = ((currentIdx + 1) / frames.length) * 100;
      document.getElementById('progress').style.width = pct + '%';
    }}

    function nextScene() {{
      currentIdx = (currentIdx + 1) % frames.length;
      updateView();
    }}

    function prevScene() {{
      currentIdx = (currentIdx - 1 + frames.length) % frames.length;
      updateView();
    }}

    function togglePlay() {{
      isPlaying = !isPlaying;
      document.getElementById('play-btn').innerText = isPlaying ? '⏸ Пауза' : '▶ Играть';
      if (isPlaying) {{
        startLoop();
      }} else {{
        clearInterval(timer);
      }}
    }}

    function startLoop() {{
      clearInterval(timer);
      timer = setInterval(() => {{
        if (isPlaying) nextScene();
      }}, durationPerScene);
    }}

    startLoop();
    updateView();
  </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("HTML_PLAYER_CREATED:", output_html)

if __name__ == "__main__":
    generate_video_player_html()
