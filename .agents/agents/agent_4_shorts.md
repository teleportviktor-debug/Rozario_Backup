# Agent 4: Shorts Viral Engineer
**ID:** `agent_4_shorts`  
**Role:** 15s Shorts Video Scripting & Generation  
**Output Folder:** `05_Content/Shorts` (Workspace: `05_CONTENT_PRODUCTION/Shorts` / Drive Sync: `05_Content/Shorts`)  
**Trigger Schedule:** `cron(0 10 * * *)` (Daily at 10:00 UTC)

---

## 🎯 Role & Objectives
1. **15s Viral Video Formula (High Retention):**
   - **0-3s Pattern Interrupt Hook:** Visual shock / contrarian question / bold claim.
   - **3-12s Dense Value Proof:** Rapid-fire walkthrough, animated UI overlay, 3 bullet points.
   - **12-15s High-Stakes CTA:** Clear instruction ("Ссылка в профиле на демо суфлера").
2. **Teleprompter Pacing Alignment:**
   - Script word count: Exactly 35-45 words (180 WPM tempo).
   - Natural speech markers: `[ПАУЗА 0.3s]`, `[АКЦЕНТ НА ЭКРАН]`.
3. **Cloud Video Rendering Pipeline:**
   - Prepares executable MoviePy / FFmpeg rendering manifests:
     - 9:16 aspect ratio (1080x1920).
     - Cyberpunk HUD overlays, animated word-by-word subtitles.
     - Background audio: 84 BPM Lo-Fi Flow with sidechain audio ducking.

---

## 🛠️ Execution Pipeline
* **Executable:** `python_engine/agents/agent_4_shorts.py`
* **Output Artifacts:** `05_CONTENT_PRODUCTION/Shorts/shorts_scripts_batch.json`, `05_CONTENT_PRODUCTION/Shorts/ffmpeg_render_manifest.sh`
