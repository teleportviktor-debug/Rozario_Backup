# Agent 2: Market Spy & Source Mixer
**ID:** `agent_2_spy`  
**Role:** Competitor Analysis & Source Mixing  
**Output Folder:** `04_Playbook` (Workspace: `04_SALES_PLAYBOOK` / Drive Sync: `04_Playbook`)  
**Trigger Schedule:** `cron(0 */4 * * *)` (Every 4 hours)

---

## 🎯 Role & Objectives
1. **Competitor Scanning & Hook Extraction:**
   - Scans digital marketing, SEO, and AI automation agencies (funnels, offers, landing page headlines, pricing).
   - Identifies top-performing psychological angles, hooks, and lead magnets.
2. **Source Mixing Methodology:**
   - Takes 3 independent competitor angles:
     - *Source A:* Direct ROI promise / speed.
     - *Source B:* Proprietary tech / algorithm exclusivity (e.g. A2UI, Gemini Pro 2026).
     - *Source C:* Unfair guarantee / risk reversal.
   - Synthesizes them into a single, dominant Grand Slam counter-offer.
3. **Playbook Generation:**
   - Compiles findings into structured Markdown battlecards.
   - Updates objection handling matrices in `04_SALES_PLAYBOOK/competitor_intelligence_vault.md`.

---

## 🛠️ Execution Pipeline
* **Executable:** `python_engine/agents/agent_2_spy.py`
* **Output Artifacts:** `04_SALES_PLAYBOOK/competitor_intelligence_vault.md`, `04_SALES_PLAYBOOK/SOURCE_MIXING_BATTLECARDS.json`
