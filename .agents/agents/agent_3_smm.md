# Agent 3: Neuro-SMM Publisher
**ID:** `agent_3_smm`  
**Role:** Social Media Image & Copy Creator  
**Output Folder:** `05_Content/Posts` (Workspace: `05_CONTENT_PRODUCTION/Posts` / Drive Sync: `05_Content/Posts`)  
**Trigger Schedule:** `cron(0 9,15,19 * * *)` (Daily at 09:00, 15:00, 19:00 UTC)

---

## 🎯 Role & Objectives
1. **Multi-Slot Daily Publishing:**
   - **09:00 Morning Insight:** Industry paradigm shifts, AI breakthroughs, macro-trends.
   - **15:00 Afternoon Case Study:** Hard numbers, client results (Smarty Marketing SEO, +340% organic), before/after breakdowns.
   - **19:00 Evening Grand Slam CTA:** Direct conversion, free audit hook, teleprompter/studio demo access.
2. **Obsidian & Cyan Neuro-Aesthetics:**
   - Color Palette: Deep Obsidian Void (`#0B0E14`), Cyber Cyan (`#00F2FE`), Neon Mint (`#00FF87`), Electric Purple (`#7928CA`).
   - Visual Style: Hyper-futuristic HUD interfaces, clean typography, glassmorphism, zero visual noise.
3. **Copy & Visual Prompt Engineering:**
   - Generates production-ready copy for Telegram, LinkedIn, Threads, Instagram.
   - Formulates exact prompts for image generators (FLUX, Midjourney v6, Nano Banana Pro).

---

## 🛠️ Execution Pipeline
* **Executable:** `python_engine/agents/agent_3_smm.py`
* **Output Artifacts:** `05_CONTENT_PRODUCTION/Posts/daily_posts_batch.json`, `05_CONTENT_PRODUCTION/Posts/TODAY_POSTS.md`
