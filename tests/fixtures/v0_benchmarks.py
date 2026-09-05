"""
v0 Benchmarks & Fixtures (Agent 5 - QA & Testing)
10 Reference React/Tailwind components representative of v0 outputs for Razum Google AI PRO.
Colors:
- Obsidian: #0a0a0c
- Neon Cyan: #00f0ff
- Gold: #d4af37
"""

# 1. Lead Dossier Card
BENCHMARK_LEAD_CARD = """
import React from 'react';

export default function LeadDossier() {
  return (
    <div className="bg-[#0a0a0c] text-white p-6 rounded-2xl border border-[#00f0ff]/30 shadow-2xl">
      <div className="flex items-center gap-4">
        <img src="https://razum.ai/avatars/lead_01.png" alt="Chief Architect" className="w-12 h-12 rounded-full border-2 border-[#d4af37]" />
        <div>
          <h2 className="text-xl font-bold text-[#00f0ff]">Alexander Wright</h2>
          <p className="text-sm text-[#d4af37]">VP of Enterprise Infrastructure @ CyberCorp</p>
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between py-1 border-b border-gray-800">
          <span className="text-gray-400">Deal Value</span>
          <span className="font-bold text-[#d4af37]">$185,000 ARR</span>
        </div>
        <div className="flex justify-between py-1 border-b border-gray-800">
          <span className="text-gray-400">Intent Score</span>
          <span className="font-bold text-[#00f0ff]">98.4 / 100</span>
        </div>
      </div>
      <p className="mt-4 text-gray-300 text-sm">
        Client requested urgent architecture audit for Google Workspace autonomous migration.
      </p>
      <div className="mt-6 flex gap-3">
        <a href="https://razum.ai/leads/alexander" className="bg-[#00f0ff] text-black font-semibold px-4 py-2 rounded-lg">Review Dossier</a>
        <button className="border border-[#d4af37] text-[#d4af37] px-4 py-2 rounded-lg">Schedule Briefing</button>
      </div>
    </div>
  );
}
"""

# 2. KPI Metrics Dashboard
BENCHMARK_KPI_DASHBOARD = """
export default function KpiDashboard() {
  return (
    <div className="bg-[#0a0a0c] p-6 text-slate-100 rounded-xl border border-gray-800">
      <h1 className="text-2xl font-bold text-[#00f0ff]">Q3 Sovereign AI Throughput</h1>
      <p className="text-xs text-gray-400">Real-time telemetry cluster stats</p>
      <div className="grid grid-cols-3 gap-4 my-4">
        <div className="p-3 bg-[#121216] rounded-lg border border-[#00f0ff]/20">
          <span className="text-xs text-gray-400">Inference Latency</span>
          <p className="text-lg font-bold text-[#00f0ff]">38ms</p>
        </div>
        <div className="p-3 bg-[#121216] rounded-lg border border-[#d4af37]/20">
          <span className="text-xs text-gray-400">Cost Reduction</span>
          <p className="text-lg font-bold text-[#d4af37]">-44.2%</p>
        </div>
      </div>
      <p className="text-sm text-gray-300">
        All worker nodes operating at peak efficiency under Zero Trust policy enforcement.
      </p>
      <div className="mt-4">
        <a href="https://console.cloud.google.com" className="text-[#00f0ff] underline text-sm">Open Cloud Telemetry</a>
      </div>
    </div>
  );
}
"""

# 3. Call Session Status
BENCHMARK_CALL_STATUS = """
export default function CallSessionStatus() {
  return (
    <div className="bg-[#0a0a0c] text-white p-5 rounded-lg border-l-4 border-[#00f0ff]">
      <h3 className="text-lg font-semibold text-[#00f0ff]">AI Voice Synthesis Complete</h3>
      <p className="text-xs text-[#d4af37]">Session ID: VOC-2026-9810</p>
      <div className="mt-3 flex justify-between">
        <span className="text-gray-400 text-sm">Duration</span>
        <span className="text-white font-mono text-sm">04:32</span>
      </div>
      <div className="flex justify-between">
        <span className="text-gray-400 text-sm">Sentiment Score</span>
        <span className="text-emerald-400 font-bold text-sm">Positive (0.94)</span>
      </div>
      <p className="mt-3 text-xs text-gray-400">
        Caller confirmed appointment for tomorrow at 14:00 GMT+3.
      </p>
      <div className="mt-4 flex gap-2">
        <a href="https://audio.razum.ai/rec/9810.mp3" className="bg-[#00f0ff] text-black text-xs font-bold px-3 py-1.5 rounded">Listen Audio</a>
        <a href="https://razum.ai/crm/transcript/9810" className="border border-gray-700 text-gray-300 text-xs px-3 py-1.5 rounded">Read Transcript</a>
      </div>
    </div>
  );
}
"""

# 4. Security Zero Trust Alert
BENCHMARK_ALERT_SECURITY = """
export default function SecurityAlert() {
  return (
    <div className="bg-[#0a0a0c] p-6 border-2 border-red-500/50 rounded-xl">
      <div className="flex items-center gap-3">
        <span className="text-red-500 font-black text-lg">CRITICAL_ALERT</span>
        <h2 className="text-xl font-bold text-white">Anomalous Workspace Access Attempt</h2>
      </div>
      <p className="text-sm text-[#d4af37] mt-1">Gateway: Zero-Trust Proxy East-1</p>
      <div className="my-3 p-3 bg-red-950/20 border border-red-800 rounded">
        <p className="text-xs font-mono text-red-300">Origin IP: 198.51.100.42 (Untrusted ASN)</p>
        <p className="text-xs font-mono text-red-300">Target: Internal Integration Token Service</p>
      </div>
      <p className="text-sm text-gray-300">
        The request was intercepted and quarantined before accessing sensitive Google Workspace APIs.
      </p>
      <div className="mt-4 flex gap-3">
        <button className="bg-red-600 text-white font-bold px-4 py-2 rounded-lg">Block Host Immediately</button>
        <a href="https://security.razum.ai/logs" className="border border-[#00f0ff] text-[#00f0ff] px-4 py-2 rounded-lg text-sm">Inspect Security Logs</a>
      </div>
    </div>
  );
}
"""

# 5. Meeting Schedule Card
BENCHMARK_MEETING_SCHEDULE = """
export default function MeetingSchedule() {
  return (
    <div className="bg-[#0a0a0c] text-white p-6 rounded-2xl border border-cyan-900">
      <h2 className="text-xl font-bold text-[#00f0ff]">Executive Strategy Briefing</h2>
      <p className="text-xs text-[#d4af37]">September 5, 2026 • 15:00 MSK (45 min)</p>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between py-1">
          <span className="text-gray-400 text-sm">Host</span>
          <span className="text-gray-200 text-sm font-medium">Smarty Marketing Lead</span>
        </div>
        <div className="flex justify-between py-1">
          <span className="text-gray-400 text-sm">Room</span>
          <span className="text-[#00f0ff] text-sm">Google Meet / Workspace Room Alpha</span>
        </div>
      </div>
      <p className="mt-3 text-sm text-gray-300">
        Discussion topics: Genome architecture rollout, n8n webhook pipelines, and client ROI tracking.
      </p>
      <div className="mt-5 flex gap-3">
        <a href="https://meet.google.com/abc-defg-hij" className="bg-[#00f0ff] text-black font-bold px-5 py-2.5 rounded-xl">Join Google Meet</a>
        <button className="border border-gray-600 text-gray-300 px-4 py-2.5 rounded-xl">Reschedule</button>
      </div>
    </div>
  );
}
"""

# 6. Payment & Financial Invoice
BENCHMARK_TRANSACTION_PAYMENT = """
export default function PaymentReceipt() {
  return (
    <div className="bg-[#0a0a0c] text-slate-100 p-6 rounded-xl border border-gray-800">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold text-white">Invoice #INV-2026-089</h2>
        <span className="px-2 py-1 bg-emerald-950 text-emerald-400 text-xs font-bold rounded">PAID</span>
      </div>
      <p className="text-xs text-gray-400 mt-1">Billed to: FinTech Group LLC</p>
      <div className="my-4 space-y-2 border-t border-b border-gray-800 py-3">
        <div className="flex justify-between text-sm">
          <span>Sovereign AI Engine (Monthly)</span>
          <span className="font-mono text-white">$12,500.00</span>
        </div>
        <div className="flex justify-between text-sm">
          <span>Enterprise CardService A2UI Add-on</span>
          <span className="font-mono text-white">$3,200.00</span>
        </div>
        <div className="flex justify-between text-base font-bold pt-2 border-t border-gray-800">
          <span className="text-[#d4af37]">Total Settled</span>
          <span className="text-[#d4af37] font-mono">$15,700.00</span>
        </div>
      </div>
      <p className="text-xs text-gray-400">Payment method: Corporate Card ending in 4092</p>
      <div className="mt-5">
        <a href="https://billing.razum.ai/pdf/089" className="text-[#00f0ff] font-medium text-sm underline">Download PDF Receipt</a>
      </div>
    </div>
  );
}
"""

# 7. Support Ticket Escalation
BENCHMARK_SUPPORT_TICKET = """
export default function SupportTicket() {
  return (
    <div className="bg-[#0a0a0c] text-white p-6 rounded-xl border-l-4 border-[#d4af37]">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-[#d4af37]">Ticket #8492: API Token Mismatch</h2>
        <span className="text-xs bg-amber-900/50 text-amber-300 px-2 py-0.5 rounded font-mono">P1_URGENT</span>
      </div>
      <p className="text-xs text-gray-400 mt-1">Submitted by: DevOps Lead (12 minutes ago)</p>
      <div className="mt-3 flex justify-between text-sm">
        <span className="text-gray-400">SLA Remaining</span>
        <span className="text-red-400 font-bold">18 minutes</span>
      </div>
      <p className="mt-3 text-sm text-gray-300">
        Customer reports intermittent 401 Unauthorized errors when dispatching cards via n8n integration webhook.
      </p>
      <div className="mt-5 flex gap-3">
        <button className="bg-[#d4af37] text-black font-bold px-4 py-2 rounded-lg">Acknowledge & Assign</button>
        <a href="https://jira.razum.ai/browse/TICK-8492" className="border border-[#00f0ff] text-[#00f0ff] px-4 py-2 rounded-lg text-sm">Open in JIRA</a>
      </div>
    </div>
  );
}
"""

# 8. AI Prompt Mutation Card
BENCHMARK_AI_PROMPT_MUTATION = """
export default function PromptMutation() {
  return (
    <div className="bg-[#0a0a0c] text-white p-6 rounded-2xl border border-cyan-500/30">
      <div className="flex items-center gap-3">
        <img src="https://razum.ai/icons/dna_gold.png" alt="Genome Mutation" className="w-8 h-8" />
        <div>
          <h2 className="text-lg font-bold text-[#00f0ff]">Genome Mutation #294 Approved</h2>
          <p className="text-xs text-[#d4af37]">Autonomous Agent Prompt Evolution</p>
        </div>
      </div>
      <div className="mt-4 p-3 bg-[#121216] rounded-lg text-xs font-mono text-gray-300">
        <span className="text-emerald-400">+ Added Zero Trust card verification filter</span>
        <br />
        <span className="text-red-400">- Removed legacy unauthenticated endpoint</span>
      </div>
      <p className="mt-3 text-xs text-gray-400">
        Mutation validated across 500 synthetic test benchmarks without regressions.
      </p>
      <div className="mt-4 flex gap-3">
        <a href="https://git.razum.ai/mutations/294" className="bg-[#00f0ff] text-black text-xs font-bold px-4 py-2 rounded">View Commit</a>
        <button className="border border-red-500 text-red-400 text-xs px-4 py-2 rounded">Rollback</button>
      </div>
    </div>
  );
}
"""

# 9. Server Telemetry Cluster
BENCHMARK_SYSTEM_TELEMETRY = """
export default function SystemTelemetry() {
  return (
    <div className="bg-[#0a0a0c] text-slate-100 p-6 rounded-xl border border-gray-800">
      <h2 className="text-xl font-bold text-white">Cluster Health Telemetry</h2>
      <p className="text-xs text-[#00f0ff]">Region: europe-west1 (Google Cloud)</p>
      <div className="mt-4 space-y-2">
        <div className="flex justify-between py-1 border-b border-gray-800">
          <span className="text-gray-400 text-sm">Pod Uptime</span>
          <span className="text-emerald-400 font-semibold text-sm">99.995% (32 days)</span>
        </div>
        <div className="flex justify-between py-1 border-b border-gray-800">
          <span className="text-gray-400 text-sm">Memory Usage</span>
          <span className="text-[#d4af37] font-mono text-sm">3.4 GB / 8.0 GB</span>
        </div>
        <div className="flex justify-between py-1 border-b border-gray-800">
          <span className="text-gray-400 text-sm">Error Rate</span>
          <span className="text-cyan-400 font-mono text-sm">0.002%</span>
        </div>
      </div>
      <p className="mt-4 text-xs text-gray-400">
        Surgeon Transpiler and Racing Router pods responding within healthy parameters.
      </p>
      <div className="mt-5">
        <a href="https://grafana.razum.ai/dashboard/genome" className="bg-[#00f0ff] text-black font-semibold text-sm px-4 py-2 rounded-lg">View Grafana</a>
      </div>
    </div>
  );
}
"""

# 10. Complex Edge-Case: Nested Spans, Ternaries, SVG Icons, Conditional Markup
BENCHMARK_COMPLEX_EDGE_CASE = """
import React, { useState } from 'react';

export default function ComplexEdgeCase({ isOnline = true, hasAccess = true }) {
  return (
    <div className="bg-[#0a0a0c] p-6 rounded-3xl border-2 border-[#d4af37]">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <svg className="w-6 h-6 text-[#00f0ff]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h2 className="text-xl font-extrabold text-white">
            <span>Razum </span>
            <span className="text-[#00f0ff]">Quantum </span>
            <span className="text-[#d4af37]">Node</span>
          </h2>
        </div>
        <span className="px-3 py-1 text-xs font-mono rounded-full bg-cyan-950 text-[#00f0ff]">
          {isOnline ? "NODE_ACTIVE" : "NODE_STANDBY"}
        </span>
      </div>

      <p className="mt-3 text-sm text-gray-300">
        System authorization level: <span className="font-bold text-[#d4af37]">LEVEL_5_SOVEREIGN</span>.
        {hasAccess ? " Full cryptographic keys mounted." : " Restricted read-only sandbox."}
      </p>

      <div className="my-4 flex justify-between items-center p-3 bg-[#121216] rounded-xl">
        <span className="text-gray-400 text-sm">Verification Hash</span>
        <span className="font-mono text-xs text-[#00f0ff]">0x9f83...bc12</span>
      </div>

      <div className="mt-5 flex gap-3">
        <a href="https://razum.ai/verify?token=ntn_9812" className="bg-[#00f0ff] text-black font-bold px-4 py-2 rounded-xl">
          <span>Authorize Access</span>
        </a>
        <button onClick={() => console.log('triggered')} className="border border-[#d4af37] text-[#d4af37] px-4 py-2 rounded-xl">
          Secondary Action
        </button>
      </div>
    </div>
  );
}
"""

# Invalid Malformed JSX for Fallback Resilience Testing
BENCHMARK_INVALID_MALFORMED_JSX = """
<div className="bg-[#0a0a0c]
  <unclosed tag without closing
  <<>>?? broken JSX syntax {&&
"""

ALL_BENCHMARKS = [
    BENCHMARK_LEAD_CARD,
    BENCHMARK_KPI_DASHBOARD,
    BENCHMARK_CALL_STATUS,
    BENCHMARK_ALERT_SECURITY,
    BENCHMARK_MEETING_SCHEDULE,
    BENCHMARK_TRANSACTION_PAYMENT,
    BENCHMARK_SUPPORT_TICKET,
    BENCHMARK_AI_PROMPT_MUTATION,
    BENCHMARK_SYSTEM_TELEMETRY,
    BENCHMARK_COMPLEX_EDGE_CASE,
]
