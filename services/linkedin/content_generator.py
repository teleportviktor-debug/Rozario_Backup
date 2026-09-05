import os
import sys
import json
import re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def generate_linkedin_post(topic: str = "Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)", keyword: str = "ROUTER") -> dict:
    """
    Generates high-impact technical LinkedIn post text following:
    Hook -> Scaling Problem -> Architectural Solution -> Lead Magnet CTA.
    """
    # Try Gemini if API key is provided
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"""Write a viral, high-authority B2B LinkedIn post for senior AI engineers and CTOs on:
Topic: {topic}
Structure:
1. Irresistible Hook (first 2 lines before 'see more'): Problem with streaming latency.
2. The Scaling Bottleneck: Why routing every request to massive reasoning models destroys TTFT and explodes token bills.
3. The Architecture Solution: Tiered Routing using Gemini 1.5 Flash for speculative instant first token (<380ms) and Gemini 1.5 Pro for heavy multi-step tool reasoning.
4. Concrete numbers: TTFT dropped from 2,450ms to 380ms (-84%), token costs cut by ~85%.
5. Call to Action: Ask readers to comment "{keyword}" to get our 3-page architectural teardown + routing benchmarks PDF.
Keep tone direct, technical, punchy (no fluff, no emojis on every word, clean line breaks).
"""
            resp = model.generate_content(prompt)
            if resp.text and len(resp.text.strip()) > 200:
                return {
                    "topic": topic,
                    "keyword": keyword,
                    "post_text": resp.text.strip()
                }
        except Exception as e:
            print(f"ℹ️ [Gemini Notice]: {e}. Using deterministic architectural generator.")

    # High-authority deterministic B2B copy
    post_text = f"""Streaming latency kills conversion before your user even reads the first token.

If your AI stack sends every user query straight to a monolithic reasoning model, you are paying a 2,000ms+ latency tax on every interaction.

Here is the architectural reality we uncovered across 40+ production AI deployments:

❌ The Monolithic Trap:
Routing conversational or simple operational queries through a heavy reasoning model creates severe queue saturation.
• TTFT (Time to First Token): 2,450ms
• Average Cost: $0.042 per interaction
• User churn during initial stream buffering: 31%

⚡ The Solution: Tiered Model Routing (Gemini 1.5 Flash + Pro)
Instead of a single model bottleneck, implement an intelligent speculative edge router:

1. Sub-15ms Ingress Classifier:
Evaluates prompt complexity, tool intent, and token budget in memory.

2. Fast-Lane Route (82% of traffic):
Directed immediately to Gemini 1.5 Flash. Sub-380ms TTFT with instantaneous token streaming.

3. Deep-Lane Escalation (18% of traffic):
Queries requiring complex multi-agent planning or multi-tool execution route seamlessly to Gemini 1.5 Pro.

4. Speculative KV-Cache Reuse:
Shared system prompts and conversation context are pre-warmed, eliminating redundant prompt ingestion time.

📈 The Production Numbers:
• TTFT: 2,450ms ➔ 380ms (-84% latency drop)
• Token cost: $0.042 ➔ $0.006 per request (7.1x cost efficiency)
• Zero perceived stream stutter for end users

Architecture shouldn't be about buying bigger GPUs—it's about smart routing.

---
🎁 Want the complete blueprint?
We compiled a 3-page Architectural Teardown PDF with:
• Full Python FastAPI / LiteLLM routing matrix
• Latency benchmark comparisons (P50, P95, P99)
• Edge classifier code template

Drop "{keyword}" in the comments and I will DM you the PDF directly.

#AIInfrastructure #MachineLearning #LLM #Latency #SoftwareArchitecture #Gemini #DevOps"""

    return {
        "topic": topic,
        "keyword": keyword,
        "post_text": post_text
    }

def generate_omnichannel_pack(topic: str = "Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)", keyword: str = "ROUTER") -> dict:
    """
    Generates tailored multiplatform content across LinkedIn, X/Grok thread, Facebook Tech Groups,
    and a cinematic video teaser prompt.
    """
    # 1. LinkedIn post
    li_bundle = generate_linkedin_post(topic=topic, keyword=keyword)
    li_post = li_bundle["post_text"]

    # 2. X / Twitter thread (3-4 tweets)
    is_caching = "cache" in topic.lower() or "token" in topic.lower()
    
    if is_caching:
        tweet1 = f"Most AI apps bleed 40% of compute budget re-evaluating identical prompt contexts.\n\nEvery static system prompt or document chunk re-tokenized is pure margin destruction.\n\nHere is how we implement Context Caching & Token Economics to drop latency by 80%: 🧵👇"
        tweet2 = f"1/ The Inefficiency:\nWithout cache tiering, a 10k token system prompt incurs full TTFT overhead on every turn.\n\nSolution: KV-Cache prefix sharing & TTL sliding context.\n\nStatic prefixes are pinned in GPU VRAM, bypassing inference prefill entirely."
        tweet3 = f"2/ The Benchmarks:\n• Prefill TTFT: 1,850ms ➔ 190ms (-89%)\n• Input token cost: cut by 75-80%\n• Concurrency ceiling: 3.5x higher before queue saturation\n\nScale throughput, not your AWS GPU bill."
        tweet4 = f"3/ We put together a 3-page Architectural Teardown PDF covering prefix caching setups + Python router boilerplate.\n\nReply '{keyword}' below and I'll send it over in DM.\n\n#BuildInPublic #AIInfra #vLLM #LLMOps #Gemini"
    else:
        tweet1 = f"Streaming latency kills conversion before your user even reads the first token.\n\nIf you route 100% of user traffic to a massive reasoning model, you're paying a 2,000ms+ latency tax.\n\nHow we slashed TTFT from 2.4s to 380ms with Tiered Routing: 🧵👇"
        tweet2 = f"1/ Monolithic routing is broken.\n\nSending operational queries to a heavy 70B+ model creates massive queue saturation.\n\nArchitecture: Sub-15ms edge classifier routing 82% of requests to Gemini 1.5 Flash (<380ms), escalating only complex reasoning to Gemini 1.5 Pro."
        tweet3 = f"2/ Production Impact:\n• TTFT: 2,450ms ➔ 380ms (-84%)\n• Cost per interaction: $0.042 ➔ $0.006 (7.1x reduction)\n• User drop-off during stream buffer: 0%\n\nSmart routing beats buying bigger clusters."
        tweet4 = f"3/ Want the full 3-page Architectural Teardown + FastAPI speculative router matrix?\n\nReply '{keyword}' below and I'll DM you the breakdown.\n\n#BuildInPublic #AIInfra #vLLM #MachineLearning #DevOps"

    x_thread = "\n\n--- [Tweet Break] ---\n\n".join([tweet1, tweet2, tweet3, tweet4])

    # 3. Facebook Tech Groups Case Study Format (First person founder perspective)
    if is_caching:
        fb_post = f"""Here is how we tackled an 80% token cost and latency bottleneck for a high-traffic AI platform last week (and why context caching changes the game for SaaS founders).

The founder came to us with a familiar problem: as multi-turn conversations and document RAG scaled up, their prompt token bill was growing faster than their MRR. Users were also complaining about a 2-3 second delay before streaming text even started.

When we profiled the network traces:
- 78% of all processed tokens were identical static context (system instructions, tool schemas, and shared document chunks).
- Every single request was forcing the inference engine to recompute the entire KV attention matrix from scratch.

What we implemented:
1. Two-Tier Prefix Caching: Pinned immutable system instructions in VRAM with deterministic cache keys.
2. Sliding Window Session Buffering: Only incremental delta tokens hit the active inference pipeline.
3. Speculative Cache Prefill: Pre-warming sessions on WebSocket connection before the user finishes typing.

The result:
• Time to First Token (TTFT) dropped from 1,850ms to 190ms.
• Token cost slashed by 74% within the first 48 hours.
• Handled 3x more concurrent users on the exact same GPU cluster.

If you are running high-volume LLM workloads, stop paying for repeated prefill compute.

Have you implemented prefix or KV-caching in production yet? Happy to share our 3-page architecture breakdown and benchmarks with anyone building in this space—just drop "{keyword}" in the comments!"""
    else:
        fb_post = f"""Here is how we tackled a 2.5-second streaming latency bottleneck for an enterprise client (and why monolithic model architecture is quietly killing user retention).

A few weeks ago, an enterprise client building customer-facing AI agents noticed a 31% drop-off rate during conversation turns. The culprit was invisible in traditional error logs: a 2,450ms Time to First Token (TTFT). Users were staring at a blank screen waiting for the reasoning model to start streaming.

They were doing what most teams do: routing 100% of incoming user prompts to a single, monolithic reasoning model.

Here is the tiered speculative routing architecture we deployed:
1. Sub-15ms Ingress Classifier: A lightweight semantic classifier at the edge that scores prompt complexity and tool intent.
2. Fast-Lane Execution (82% of queries): Directed immediately to Gemini 1.5 Flash. Delivers sub-380ms TTFT with instant token streaming.
3. Deep-Lane Escalation (18% of queries): Multi-turn reasoning and tool orchestration route seamlessly to Gemini 1.5 Pro.

The impact after 48 hours in production:
- TTFT dropped from 2,450ms to 380ms (-84% latency reduction).
- Cost dropped from $0.042 to $0.006 per query (7.1x cost efficiency).
- Buffer churn dropped to zero.

The biggest lesson: you don't need to sacrifice reasoning to achieve sub-second latency. You just need an intelligent routing layer.

Curious how others in the group are handling streaming TTFT at scale? Drop "{keyword}" in the comments if you'd like our 3-page engineering teardown with the routing matrix!"""

    # 4. Cinematic Video Teaser Prompt (for Grok / Luma / Runway / Kling)
    video_teaser_prompt = (
        f"Cinematic 4K hyper-realistic 3D technical animation, dark cyberpunk server vault background with obsidian glass floor. "
        f"Glowing holographic glowing neon data packets ({'cyan #00f0ff' if not is_caching else 'emerald #00ffa3'}) flowing rapidly through transparent optical microchips. "
        f"Camera starts in a slow pan showing a congested red glowing bottleneck lane with label '2450ms TTFT', then snaps at warp speed into a streamlined dual-lane fiber optic highway labeled 'Gemini 1.5 Flash + Pro: 380ms TTFT'. "
        f"Volumetric atmospheric fog, anamorphic lens flares, Octane render 60fps, clean futuristic minimalist tech aesthetic."
    )

    return {
        "topic": topic,
        "keyword": keyword,
        "linkedin_post": li_post,
        "x_thread": x_thread,
        "facebook_post": fb_post,
        "video_teaser_prompt": video_teaser_prompt
    }

def generate_card_html(topic: str = "Slashing Streaming TTFT via Tiered Model Routing (Gemini 1.5 Flash + Pro)", keyword: str = "ROUTER") -> str:
    """
    Generates pixel-perfect 1080x1350 HTML card for LinkedIn with cyber-minimalism dark theme.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{topic}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    width: 1080px;
    height: 1350px;
    background: #090d16;
    color: #f8fafc;
    font-family: 'Inter', -apple-system, sans-serif;
    padding: 60px 64px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  /* Cyber Glow Background Elements */
  body::before {{
    content: '';
    position: absolute;
    top: -120px;
    right: -120px;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(0, 240, 255, 0.15) 0%, rgba(9, 13, 22, 0) 70%);
    z-index: 0;
    pointer-events: none;
  }}

  body::after {{
    content: '';
    position: absolute;
    bottom: -150px;
    left: -150px;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(16, 185, 129, 0.12) 0%, rgba(9, 13, 22, 0) 70%);
    z-index: 0;
    pointer-events: none;
  }}

  .content-layer {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    height: 100%;
    justify-content: space-between;
  }}

  /* Top Bar */
  .top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
  }}

  .badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.3);
    padding: 8px 18px;
    border-radius: 9999px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #00f0ff;
    letter-spacing: 1.5px;
    text-transform: uppercase;
  }}

  .pulse-dot {{
    width: 8px;
    height: 8px;
    background: #00f0ff;
    border-radius: 50%;
    box-shadow: 0 0 10px #00f0ff;
  }}

  .brand-logo {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
    font-size: 18px;
    letter-spacing: 2px;
    color: #94a3b8;
  }}
  .brand-logo span {{
    color: #00f0ff;
  }}

  /* Header */
  .header {{
    margin-bottom: 36px;
  }}

  .main-title {{
    font-size: 48px;
    font-weight: 900;
    line-height: 1.15;
    letter-spacing: -1px;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .subtitle {{
    font-size: 20px;
    font-weight: 500;
    color: #94a3b8;
    line-height: 1.4;
  }}
  .subtitle b {{
    color: #38bdf8;
  }}

  /* Comparison Grid (Before vs After) */
  .comparison-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 32px;
  }}

  .card {{
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 18px;
    padding: 24px 26px;
    backdrop-filter: blur(12px);
  }}

  .card-before {{
    border-top: 3px solid #ef4444;
  }}

  .card-after {{
    border-top: 3px solid #10b981;
    background: linear-gradient(180deg, rgba(16, 185, 129, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
  }}

  .card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }}

  .card-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1px;
  }}
  .card-before .card-title {{ color: #f87171; }}
  .card-after .card-title {{ color: #34d399; }}

  .card-metric {{
    font-size: 38px;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 6px;
  }}
  .card-before .card-metric {{ color: #fca5a5; }}
  .card-after .card-metric {{ color: #6ee7b7; }}

  .metric-label {{
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 14px;
  }}

  .card-list {{
    list-style: none;
    font-size: 14px;
    color: #cbd5e1;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}
  .card-list li {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .card-before .card-list li::before {{
    content: '✕';
    color: #ef4444;
    font-weight: 900;
  }}
  .card-after .card-list li::before {{
    content: '✓';
    color: #10b981;
    font-weight: 900;
  }}

  /* Architecture Pipeline Flow */
  .pipeline-container {{
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 20px;
    padding: 26px 28px;
    margin-bottom: 28px;
  }}

  .pipeline-title {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #00f0ff;
    letter-spacing: 1px;
    margin-bottom: 18px;
    text-transform: uppercase;
  }}

  .flow-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 14px;
  }}

  .flow-node {{
    flex: 1;
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
  }}

  .flow-node-highlight {{
    border-color: #00f0ff;
    background: rgba(0, 240, 255, 0.08);
  }}

  .node-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 4px;
  }}

  .node-sub {{
    font-size: 11px;
    color: #94a3b8;
  }}

  .flow-arrow {{
    color: #00f0ff;
    font-size: 18px;
    font-weight: 900;
  }}

  .routes-split {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 10px;
  }}

  .route-box {{
    border-radius: 12px;
    padding: 14px 16px;
  }}
  .route-fast {{
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.3);
  }}
  .route-deep {{
    background: rgba(168, 85, 247, 0.08);
    border: 1px solid rgba(168, 85, 247, 0.3);
  }}

  .route-badge {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    margin-bottom: 6px;
    text-transform: uppercase;
  }}
  .route-fast .route-badge {{ background: #10b981; color: #022c22; }}
  .route-deep .route-badge {{ background: #a855f7; color: #3b0764; }}

  .route-name {{
    font-weight: 700;
    font-size: 15px;
    color: #ffffff;
    margin-bottom: 4px;
  }}
  .route-desc {{
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.3;
  }}

  /* Stats Highlights Banner */
  .stats-banner {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 28px;
  }}

  .stat-card {{
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
  }}

  .stat-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 900;
    color: #00f0ff;
    margin-bottom: 4px;
  }}

  .stat-lbl {{
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
  }}

  /* Footer */
  .footer {{
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .author-info {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .author-avatar {{
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, #00f0ff, #3b82f6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    color: #090d16;
    font-size: 20px;
    font-family: 'JetBrains Mono', monospace;
  }}

  .author-name {{
    font-weight: 700;
    font-size: 15px;
    color: #f1f5f9;
  }}

  .author-title {{
    font-size: 12px;
    color: #64748b;
  }}

  .cta-box {{
    background: linear-gradient(135deg, rgba(0, 240, 255, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
    border: 1px solid rgba(0, 240, 255, 0.4);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 700;
    color: #e0f2fe;
  }}
  .cta-box span {{
    color: #00f0ff;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 800;
  }}
</style>
</head>
<body>
  <div class="content-layer">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="badge">
        <div class="pulse-dot"></div>
        <span>Architecture Teardown #01</span>
      </div>
      <div class="brand-logo">RAZUM<span>.AI</span></div>
    </div>

    <!-- Header -->
    <div class="header">
      <h1 class="main-title">SLASHING STREAMING TTFT</h1>
      <p class="subtitle">Tiered Model Routing Architecture: <b>Gemini 1.5 Flash + Pro</b></p>
    </div>

    <!-- Before vs After -->
    <div class="comparison-grid">
      <div class="card card-before">
        <div class="card-header">
          <div class="card-title">MONOLITHIC ROUTING</div>
          <span style="color: #ef4444; font-size: 18px;">⚠️</span>
        </div>
        <div class="card-metric">2,450ms</div>
        <div class="metric-label">Time to First Token (TTFT)</div>
        <ul class="card-list">
          <li>100% traffic hits monolithic 70B+ model</li>
          <li>$0.042 average cost per query</li>
          <li>High queue stalls on concurrent spikes</li>
          <li>31% user drop-off before stream starts</li>
        </ul>
      </div>

      <div class="card card-after">
        <div class="card-header">
          <div class="card-title">TIERED SPECULATIVE ROUTING</div>
          <span style="color: #10b981; font-size: 18px;">⚡</span>
        </div>
        <div class="card-metric">380ms</div>
        <div class="metric-label">Time to First Token (-84%)</div>
        <ul class="card-list">
          <li>Sub-15ms Ingress Intent Classifier</li>
          <li>82% queries handled by Flash (<380ms)</li>
          <li>18% deep queries escalated to Pro</li>
          <li>$0.006 average cost (7.1x reduction)</li>
        </ul>
      </div>
    </div>

    <!-- Pipeline Architecture -->
    <div class="pipeline-container">
      <div class="pipeline-title">
        <span>⚡ Intelligent Edge Router Pipeline</span>
      </div>
      <div class="flow-row">
        <div class="flow-node">
          <div class="node-title">USER REQUEST</div>
          <div class="node-sub">Edge Gateway</div>
        </div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node flow-node-highlight">
          <div class="node-title">ROUTER &amp; CLASSIFIER</div>
          <div class="node-sub">&lt;15ms Intent Check</div>
        </div>
        <div class="flow-arrow">➔</div>
        <div class="flow-node">
          <div class="node-title">KV-CACHE REUSE</div>
          <div class="node-sub">Pre-warmed Context</div>
        </div>
      </div>

      <div class="routes-split">
        <div class="route-box route-fast">
          <span class="route-badge">82% FAST-LANE</span>
          <div class="route-name">Gemini 1.5 Flash</div>
          <div class="route-desc">Sub-second streaming TTFT, high token throughput, instant user feedback.</div>
        </div>
        <div class="route-box route-deep">
          <span class="route-badge">18% DEEP-LANE</span>
          <div class="route-name">Gemini 1.5 Pro</div>
          <div class="route-desc">Multi-step reasoning, tool orchestrations &amp; long-form synthesis.</div>
        </div>
      </div>
    </div>

    <!-- Stats Banner -->
    <div class="stats-banner">
      <div class="stat-card">
        <div class="stat-val">-84%</div>
        <div class="stat-lbl">TTFT Latency</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: #10b981;">7.1x</div>
        <div class="stat-lbl">Cost Efficiency</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: #a855f7;">99.4%</div>
        <div class="stat-lbl">SLA Uptime</div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      <div class="author-info">
        <div class="author-avatar">V</div>
        <div>
          <div class="author-name">Viktor</div>
          <div class="author-title">AI Infrastructure &amp; Latency Optimization</div>
        </div>
      </div>
      <div class="cta-box">
        Comment <span>"{keyword}"</span> for 3-Page Architecture PDF
      </div>
    </div>
  </div>
</body>
</html>"""
    return html_content

if __name__ == "__main__":
    post = generate_linkedin_post()
    print("Generated Post:")
    print(post["post_text"][:300] + "...")
    html = generate_card_html()
    print(f"Generated HTML template: {len(html)} chars")
