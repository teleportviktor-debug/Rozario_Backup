import os
import sys
import re
import json
import urllib.parse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

def extract_founder_or_cto(text: str, company: str) -> str:
    """Extracts founder or CTO name if explicitly mentioned in the job posting."""
    patterns = [
        r"(?:i'm|i am)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)[,\s]+(?:the\s+)?(?:founder|co-founder|cto|ceo)",
        r"(?:founder|co-founder|cto|ceo)[:\s\-]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:founded by|started by)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        r"(?:reach out to|contact)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:\(|at\s+)?(?:founder|cto|ceo|head of)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if len(candidate) > 2 and not any(w in candidate.lower() for w in ["hiring", "team", "engineer", "software", "company"]):
                return candidate

    return "Founding Team / CTO"

def analyze_intent_heuristics(lead: dict) -> dict:
    """Domain-specific architectural analyzer for AI hiring signals."""
    company = lead.get("company", "Tech Startup")
    role = lead.get("role", "AI Engineer")
    text = (lead.get("full_text", "") + " " + lead.get("tech_stack", "")).lower()
    keywords = [k.lower() for k in lead.get("keywords", [])]

    # 1. Identify specific engineering pain point & bottleneck
    if "streaming" in keywords or "webrtc" in text or "voice" in text or "audio" in text:
        pain = "Sub-second Voice/Audio Streaming Latency & Real-time WebRTC Inference Drift"
        short_pain = "real-time audio streaming latency"
    elif "context caching" in keywords or "cache" in text or "rag" in text or "embeddings" in text:
        pain = "Unbounded Context Window Token Overhead & KV-Cache Eviction Inefficiencies"
        short_pain = "context caching and token efficiency"
    elif "agentic" in keywords or "autonomous" in text or "multi-agent" in text or "workflow" in text:
        pain = "Multi-Agent State Drift, Loop Latency & Tool Calling Microservice Timeouts"
        short_pain = "agentic execution latency and tool orchestration"
    elif "inference" in keywords or "throughput" in text or "gpu" in text or "vllm" in text:
        pain = "GPU Inference Bottlenecks, High TTFT (Time to First Token) & Concurrency Spikes"
        short_pain = "high inference TTFT and concurrency bottlenecks"
    elif "latency" in keywords or "speed" in text or "real-time" in text:
        pain = "Unbounded LLM Streaming Latency Spikes & Token Cost Overruns"
        short_pain = "streaming latency and edge response times"
    else:
        pain = "Production LLM Token Budget Overrun & Unbounded API Gateway Latency"
        short_pain = "production LLM latency and token throughput"

    # 2. Extract Founder / CTO
    founder_name = extract_founder_or_cto(lead.get("full_text", ""), company)

    # 3. Formulate LinkedIn Search URL
    encoded_query = urllib.parse.quote(f"{company} founder OR cto")
    linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={encoded_query}"

    # 4. Formulate Intent Angle
    # Format: "Saw you are hiring a [Job Title] to tackle [Pain Point]..."
    intent_angle = (
        f"Saw you are hiring a {role} to tackle {short_pain} at {company}. "
        f"We drafted a quick 3-page teardown showing how to optimize streaming throughput and cut latency by ~30-40%."
    )

    return {
        "core_pain": pain,
        "founder_name": founder_name,
        "linkedin_url": linkedin_url,
        "intent_angle": intent_angle
    }

def analyze_intent_gemini(lead: dict, api_key: str) -> dict:
    """Uses Gemini API to analyze the hiring intent if API key is provided."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""You are a principal AI infrastructure architect analyzing a job vacancy for B2B outreach.
Company: {lead.get('company')}
Role: {lead.get('role')}
Job Posting Snippet:
{lead.get('full_text', '')[:1200]}

Analyze the posting and respond ONLY with a JSON object:
{{
  "core_pain": "A precise 5-10 word technical engineering bottleneck they are hiring to solve (e.g. 'Sub-second Streaming Latency & Real-time WebRTC Drift' or 'Context Window Cache Eviction & Token Overrun')",
  "founder_name": "Name of Founder/CTO if mentioned in text, otherwise 'Founding Team / CTO'",
  "short_pain": "2-4 words summarizing the core pain (e.g. 'streaming latency', 'inference throughput')",
  "intent_angle": "Saw you are hiring a [Job Title] to tackle [short_pain] at [Company]. We drafted a 3-page breakdown showing how to cut latency by 30-40%."
}}
"""
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        match = re.search(r"\{.*\}", text_resp, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
            company = lead.get("company", "Tech Startup")
            role = lead.get("role", "AI Engineer")
            founder = parsed.get("founder_name", "Founding Team / CTO")
            pain = parsed.get("core_pain", "LLM Streaming Latency & Token Budget Overrun")
            angle = parsed.get("intent_angle", f"Saw you are hiring a {role} to tackle {pain} at {company}.")
            
            encoded_query = urllib.parse.quote(f"{company} founder OR cto")
            linkedin_url = f"https://www.linkedin.com/search/results/all/?keywords={encoded_query}"
            
            return {
                "core_pain": pain,
                "founder_name": founder,
                "linkedin_url": linkedin_url,
                "intent_angle": angle
            }
    except Exception as e:
        print(f"  [GEMINI NOTICE] Fallback to domain heuristics: {e}")
    
    return analyze_intent_heuristics(lead)

def analyze_intent(lead: dict) -> dict:
    """
    Main entry point for intent analysis and enrichment.
    Analyzes hiring signal, core architectural pain, founder info, and creates personalized intent angle.
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if api_key:
        enriched = analyze_intent_gemini(lead, api_key)
    else:
        enriched = analyze_intent_heuristics(lead)

    return {
        "company": lead.get("company", "Startup"),
        "website": lead.get("website", ""),
        "hiring_role": lead.get("role", "AI Engineer"),
        "tech_stack_core_pain": enriched["core_pain"],
        "founder_name": enriched["founder_name"],
        "linkedin_search_url": enriched["linkedin_url"],
        "contact_email": lead.get("email", ""),
        "intent_angle": enriched["intent_angle"],
        "status": "Qualified Intent"
    }

if __name__ == "__main__":
    test_lead = {
        "company": "LiveKit",
        "website": "https://livekit.io",
        "role": "Real-time AI Audio & Streaming Engineer",
        "keywords": ["Streaming", "Latency", "AI Engineer"],
        "email": "careers@livekit.io",
        "tech_stack": "LiveKit is building open source WebRTC and VoiceAI infrastructure. Managing WebRTC video and audio pipelines at global edge scale with lowest latency.",
        "full_text": "LiveKit is looking for an AI engineer to optimize WebRTC real-time voice latency. Founded by Suhail Doshi."
    }
    result = analyze_intent(test_lead)
    print("Enrichment Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
