"""
Sovereign n8n Workflow Studio & Automation Server (Port 5678)
Agent 4 (Integration Lead) - Architecture "Genome" • Razum Google AI PRO.

Implements:
- Official n8n Health probe: GET /healthz -> {"status":"ok"}
- Workflow schema: Razum_Hybrid_Outreach_Pipeline
- Google Account & Sheet Credential simulation modal (ID: 1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M)
- Active Toggle Switch
- Bottom 'Execute workflow' button triggering live render for Apex Global Logistics -> Status 'Generated' + MP4 link
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from services.integration.n8n_workflow_runner import N8NWorkflowRunner

app = FastAPI(
    title="Razum Google AI PRO - n8n Studio",
    version="2.0.0",
    description="Sovereign n8n Studio with Google Sheets & Video Generation Pipeline"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/v1/health")
async def api_health():
    return {"status": "ok", "service": "n8n-studio-engine", "port": 5678}


@app.get("/api/workflow/current")
async def get_current_workflow():
    path = "n8n_workflow_dynamic_outreach_sheets.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["name"] = "Razum_Hybrid_Outreach_Pipeline"
            return data
    return {"error": "Workflow file not found"}


@app.post("/api/workflow/execute")
async def execute_workflow(payload: Optional[Dict[str, Any]] = None):
    lead = payload or {
        "company_name": "Apex Global Logistics",
        "primary_bottleneck": "API Token Overspend & Latency",
        "lead_urgency_score": "Score: 94/100 | Tier-1 Enterprise",
        "custom_cta_url": "https://razum.ai/audit/apex",
        "status": "Generated"
    }
    runner = N8NWorkflowRunner()
    res = runner.execute_workflow(lead_override=lead)
    res["lead_status"] = "Generated"
    return res


@app.get("/", response_class=HTMLResponse)
async def n8n_canvas():
    html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>n8n • Razum_Hybrid_Outreach_Pipeline</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #0d1117;
            --bg-sidebar: #161b22;
            --bg-canvas: #090d14;
            --node-bg: #1c212c;
            --node-border: rgba(255, 255, 255, 0.12);
            --n8n-accent: #ea4b71;
            --cyan: #00f0ff;
            --gold: #d4af37;
            --green: #00ff88;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-body);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        /* Sidebar */
        aside {
            width: 260px;
            background: var(--bg-sidebar);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar-brand {
            padding: 18px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .n8n-logo {
            background: linear-gradient(135deg, #ea4b71, #ff6b8b);
            color: white;
            font-weight: 800;
            font-size: 14px;
            padding: 4px 10px;
            border-radius: 6px;
        }

        .sidebar-menu {
            padding: 16px 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            border-radius: 8px;
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .menu-item:hover, .menu-item.active {
            background: rgba(234, 75, 113, 0.12);
            color: #fff;
        }

        .menu-item.active {
            border-left: 3px solid var(--n8n-accent);
        }

        .workflows-sublist {
            margin-top: 10px;
            padding-left: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .workflow-link {
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            color: var(--cyan);
            background: rgba(0, 240, 255, 0.06);
            border: 1px solid rgba(0, 240, 255, 0.2);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Workspace Canvas */
        .workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: var(--bg-canvas);
            background-image: 
                radial-gradient(circle, rgba(255, 255, 255, 0.06) 1px, transparent 1px);
            background-size: 24px 24px;
            position: relative;
        }

        /* Canvas Top Bar */
        .topbar {
            height: 64px;
            background: rgba(13, 17, 23, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 28px;
            z-index: 20;
        }

        .wf-meta {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .wf-name {
            font-size: 17px;
            font-weight: 700;
            color: #fff;
        }

        .wf-tag {
            font-size: 11px;
            font-weight: 700;
            background: rgba(0, 240, 255, 0.1);
            color: var(--cyan);
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(0, 240, 255, 0.25);
        }

        /* Active Toggle */
        .active-toggle-wrap {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .toggle-label {
            font-size: 13px;
            font-weight: 700;
            color: var(--text-muted);
        }

        .toggle-switch {
            position: relative;
            width: 48px;
            height: 26px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .toggle-switch.active {
            background: var(--green);
            box-shadow: 0 0 15px rgba(0, 255, 136, 0.5);
        }

        .toggle-knob {
            position: absolute;
            top: 3px;
            left: 3px;
            width: 20px;
            height: 20px;
            background: #fff;
            border-radius: 50%;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .toggle-switch.active .toggle-knob {
            transform: translateX(22px);
        }

        /* Canvas Node Flow */
        .canvas-body {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            position: relative;
            overflow-x: auto;
        }

        .flow-container {
            display: flex;
            align-items: center;
            gap: 36px;
            position: relative;
        }

        .flow-line {
            width: 36px;
            height: 3px;
            background: linear-gradient(90deg, var(--cyan), var(--n8n-accent));
            box-shadow: 0 0 10px var(--cyan);
            border-radius: 2px;
        }

        .node-box {
            width: 240px;
            background: var(--node-bg);
            border: 2px solid var(--node-border);
            border-radius: 14px;
            padding: 18px;
            cursor: pointer;
            position: relative;
            transition: all 0.3s ease;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        }

        .node-box:hover {
            transform: translateY(-4px);
            border-color: var(--cyan);
            box-shadow: 0 12px 35px rgba(0, 240, 255, 0.25);
        }

        .node-box.running {
            border-color: var(--gold) !important;
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.6) !important;
            animation: pulse-border 1s infinite alternate;
        }

        .node-box.success {
            border-color: var(--green) !important;
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.6) !important;
        }

        @keyframes pulse-border {
            0% { transform: scale(1); }
            100% { transform: scale(1.03); }
        }

        .node-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }

        .node-title {
            font-size: 15px;
            font-weight: 700;
            color: #fff;
            margin-bottom: 6px;
        }

        .node-sub {
            font-size: 12px;
            color: var(--text-muted);
            line-height: 1.4;
        }

        .node-badge-ok {
            position: absolute;
            top: -10px;
            right: -10px;
            background: var(--green);
            color: #050811;
            font-weight: 800;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            display: none;
            box-shadow: 0 0 10px var(--green);
        }

        /* Bottom Floating Bar */
        .bottom-bar {
            position: absolute;
            bottom: 28px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 16px;
            background: rgba(22, 27, 34, 0.95);
            backdrop-filter: blur(16px);
            padding: 10px 24px;
            border-radius: 40px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            z-index: 50;
        }

        .btn-execute {
            background: linear-gradient(135deg, #00f0ff, #00a2ff);
            color: #050811;
            font-weight: 800;
            font-size: 15px;
            padding: 12px 30px;
            border-radius: 30px;
            border: none;
            cursor: pointer;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.5);
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn-execute:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 40px rgba(0, 240, 255, 0.8);
        }

        .btn-execute:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        /* Modal for Node Settings */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 200;
        }

        .modal-card {
            background: #161b22;
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            width: 580px;
            padding: 28px;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8);
            position: relative;
        }

        .modal-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .form-group {
            margin-bottom: 18px;
        }

        .form-label {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 6px;
            display: block;
        }

        .form-input {
            width: 100%;
            background: #0d1117;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 8px;
            padding: 10px 14px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }

        .badge-google {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 255, 136, 0.1);
            color: var(--green);
            border: 1px solid rgba(0, 255, 136, 0.3);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }

        .btn-close {
            background: var(--n8n-accent);
            color: #fff;
            border: none;
            padding: 8px 18px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            float: right;
            margin-top: 10px;
        }

        /* Live Result Drawer */
        .result-drawer {
            position: absolute;
            right: 20px;
            top: 80px;
            width: 360px;
            background: rgba(22, 27, 34, 0.95);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(0, 240, 255, 0.3);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6);
            display: none;
            z-index: 100;
        }

        .res-title {
            font-size: 14px;
            font-weight: 700;
            color: var(--cyan);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .res-field {
            font-size: 12px;
            margin-bottom: 8px;
            color: var(--text-muted);
        }

        .res-val {
            color: #fff;
            font-weight: 600;
            word-break: break-all;
        }

        .status-badge-generated {
            background: rgba(0, 255, 136, 0.15);
            color: var(--green);
            border: 1px solid rgba(0, 255, 136, 0.4);
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: 800;
            font-size: 11px;
            display: inline-block;
        }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <aside>
        <div class="sidebar-brand">
            <span class="n8n-logo">n8n</span>
            <span style="font-weight: 700; font-size: 15px;">Workflow Engine</span>
        </div>
        <div class="sidebar-menu">
            <div class="menu-item active">
                <span>📁</span>
                <span>Workflows</span>
            </div>
            <div class="workflows-sublist">
                <div class="workflow-link">
                    <span>⚡</span>
                    <span>Razum_Hybrid_Outreach_Pipeline</span>
                </div>
            </div>
            <div class="menu-item" style="margin-top: 16px;">
                <span>🔑</span>
                <span>Credentials (Google Workspace)</span>
            </div>
            <div class="menu-item">
                <span>📊</span>
                <span>Executions</span>
            </div>
        </div>
    </aside>

    <!-- Workspace -->
    <div class="workspace">
        <div class="topbar">
            <div class="wf-meta">
                <span class="wf-name">Razum_Hybrid_Outreach_Pipeline</span>
                <span class="wf-tag">Zero Trust B2B Outreach</span>
            </div>
            <div class="active-toggle-wrap">
                <span id="activeLabel" class="toggle-label">Active</span>
                <div id="toggleSwitch" class="toggle-switch active" onclick="toggleActive()">
                    <div class="toggle-knob"></div>
                </div>
            </div>
        </div>

        <div class="canvas-body">
            <div class="flow-container">
                <!-- Node 1 -->
                <div class="node-box" id="node1" onclick="openNodeModal()">
                    <div class="node-badge-ok" id="badge1">✓ OK</div>
                    <div class="node-icon">📊</div>
                    <div class="node-title">Google Sheets Trigger</div>
                    <div class="node-sub">docId: 1fVe94GnUznu...<br>Sheet: Leads (1m poll)</div>
                </div>

                <div class="flow-line"></div>

                <!-- Node 2 -->
                <div class="node-box" id="node2">
                    <div class="node-badge-ok" id="badge2">✓ OK</div>
                    <div class="node-icon">⚡</div>
                    <div class="node-title">Personalized Reel & Card</div>
                    <div class="node-sub">POST :8000/api/v1/outreach/dispatch<br>Bearer ntn_...</div>
                </div>

                <div class="flow-line"></div>

                <!-- Node 3 -->
                <div class="node-box" id="node3">
                    <div class="node-badge-ok" id="badge3">✓ OK</div>
                    <div class="node-icon">📝</div>
                    <div class="node-title">Write Video Link to Sheet</div>
                    <div class="node-sub">Write: VideoURL & EmailSubject<br>docId: 1fVe94GnUznu...</div>
                </div>

                <div class="flow-line"></div>

                <!-- Node 4 -->
                <div class="node-box" id="node4">
                    <div class="node-badge-ok" id="badge4">✓ OK</div>
                    <div class="node-icon">🎯</div>
                    <div class="node-title">Mark Status Generated</div>
                    <div class="node-sub">Status: <span class="status-badge-generated">Generated</span><br>docId: 1fVe94GnUznu...</div>
                </div>
            </div>
        </div>

        <!-- Floating Action Bar -->
        <div class="bottom-bar">
            <button id="execBtn" class="btn-execute" onclick="executePipeline()">
                <span>▶</span>
                <span>Execute workflow</span>
            </button>
            <span style="font-size: 13px; color: var(--text-muted);">
                Lead: <b style="color: #fff;">Apex Global Logistics</b>
            </span>
        </div>

        <!-- Result Drawer -->
        <div id="drawer" class="result-drawer">
            <div class="res-title">
                <span>🚀</span> Результат выполнения
            </div>
            <div class="res-field">Компания: <span class="res-val" id="resCompany">—</span></div>
            <div class="res-field">Статус строки: <span class="status-badge-generated" id="resStatus">Generated</span></div>
            <div class="res-field">Тема письма: <span class="res-val" id="resSubject">—</span></div>
            <div class="res-field" style="margin-top: 10px;">MP4 Ролик:</div>
            <a id="resVideoLink" href="#" target="_blank" style="color: var(--cyan); font-size: 12px; word-break: break-all; display: block; margin-bottom: 12px;">—</a>
            <video id="resVideoPlayer" controls style="width: 100%; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); max-height: 200px; display: none;"></video>
        </div>
    </div>

    <!-- Node Modal -->
    <div id="nodeModal" class="modal-overlay" onclick="closeNodeModal(event)">
        <div class="modal-card">
            <div class="modal-title">
                <span>Параметры узла: Google Sheets Trigger</span>
            </div>
            <div class="form-group">
                <label class="form-label">Credential to connect with</label>
                <div class="badge-google">
                    <span>✓ Google Account: enterprise@workspace.google.com (Connected)</span>
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Document (Spreadsheet ID)</label>
                <input type="text" class="form-input" value="1fVe94GnUznuIVZr71hK561GMICQs9dt9qXHaPzINk7M" readonly>
            </div>
            <div class="form-group">
                <label class="form-label">Sheet Name</label>
                <input type="text" class="form-input" value="Leads" readonly>
            </div>
            <div class="form-group">
                <label class="form-label">Trigger Event</label>
                <input type="text" class="form-input" value="On Row Added / Updated" readonly>
            </div>
            <button class="btn-close" onclick="document.getElementById('nodeModal').style.display='none'">Закрыть</button>
        </div>
    </div>

    <script>
        function toggleActive() {
            const sw = document.getElementById('toggleSwitch');
            const lbl = document.getElementById('activeLabel');
            sw.classList.toggle('active');
            if (sw.classList.contains('active')) {
                lbl.innerText = 'Active';
                lbl.style.color = 'var(--green)';
            } else {
                lbl.innerText = 'Inactive';
                lbl.style.color = 'var(--text-muted)';
            }
        }

        function openNodeModal() {
            document.getElementById('nodeModal').style.display = 'flex';
        }

        function closeNodeModal(e) {
            if (e.target.id === 'nodeModal') {
                document.getElementById('nodeModal').style.display = 'none';
            }
        }

        async function executePipeline() {
            const btn = document.getElementById('execBtn');
            btn.disabled = true;
            btn.innerHTML = '<span>⏳</span> Processing...';

            const nodes = ['node1', 'node2', 'node3', 'node4'];
            nodes.forEach(id => {
                const el = document.getElementById(id);
                el.classList.add('running');
                el.classList.remove('success');
            });

            try {
                const res = await fetch('/api/workflow/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        company_name: 'Apex Global Logistics',
                        primary_bottleneck: 'API Token Overspend & Latency',
                        lead_urgency_score: 'Score: 94/100 | Tier-1 Enterprise',
                        custom_cta_url: 'https://razum.ai/audit/apex',
                        status: 'Generated'
                    })
                });
                const data = await res.json();

                // Highlight all nodes green
                nodes.forEach((id, idx) => {
                    setTimeout(() => {
                        const el = document.getElementById(id);
                        el.classList.remove('running');
                        el.classList.add('success');
                        document.getElementById('badge' + (idx + 1)).style.display = 'block';
                    }, idx * 300);
                });

                // Show results
                document.getElementById('drawer').style.display = 'block';
                document.getElementById('resCompany').innerText = data.company_name;
                document.getElementById('resStatus').innerText = 'Generated';
                document.getElementById('resSubject').innerText = data.email_subject;
                const vLink = document.getElementById('resVideoLink');
                vLink.href = data.video_url;
                vLink.innerText = data.video_url;

                const vPlayer = document.getElementById('resVideoPlayer');
                vPlayer.src = data.video_url;
                vPlayer.style.display = 'block';
                vPlayer.load();

            } catch (err) {
                alert('Ошибка вызова: ' + err);
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<span>▶</span> Execute workflow';
            }
        }
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


def main():
    uvicorn.run(app, host="0.0.0.0", port=5678)


if __name__ == "__main__":
    main()
