# Agent 1: Lead Scout & Hormozi Valuator
**ID:** `agent_1_lead_scout`  
**Role:** Lead Generation & Hormozi Scoring  
**Output Folder:** `03_CRM` (Drive Sync: `03_CRM`)  
**Trigger Schedule:** `cron(0 */2 * * *)` (Every 2 hours)

---

## 🎯 Role & Objectives
1. **Parse Raw Inbound/Outbound Leads:** Scrapes and ingests lead briefs from CRM webhook payloads, forms, and JSON input files.
2. **Pain / Power / Decision / Urgency (PPDU) Scoring:**
   - **Pain (1-10):** Severity of business leak (wasting hours on manual content, low SEO conversion).
   - **Power (1-10):** Decision-making authority (Founder, CEO, CMO vs mid-level).
   - **Decision (1-10):** Readiness and clarity of criteria.
   - **Urgency (1-10):** Immediate need to close this week.
3. **Hormozi Value Equation:**
   $$\text{Value} = \frac{\text{Dream Outcome} \times \text{Perceived Likelihood}}{\text{Time Delay} \times \text{Effort \& Sacrifice}}$$
4. **Google Sheets / Workspace Studio Append:**
   - Appends scored leads with TIER rating (`TIER 1 VIP`, `TIER 2 Standard`, `TIER 3 Nurture`) to the master CRM Google Sheet.
   - Triggers Telegram instant alert for TIER 1 leads.

---

## 🛠️ Execution Pipeline
* **Executable:** `python_engine/agents/agent_1_lead_scout.py`
* **Output Artifacts:** `03_CRM/leads_scored_batch.json`, `03_CRM/WORKSPACE_STUDIO_SHEETS_EXPORT.csv`
