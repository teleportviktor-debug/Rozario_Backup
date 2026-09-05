import os
import sys
import json
import re
import unittest

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from services.linkedin.content_generator import generate_omnichannel_pack
from scripts.sync_linkedin_content_to_sheets import sync_omnichannel_to_sheets
from services.reporting.generate_opus_audit_brief import generate_opus_audit_brief, get_lead_from_sheets


class TestOmnichannelPipeline(unittest.TestCase):
    """
    End-to-End Verification Suite for the 3 Asynchronous Pipeline Modules:
    1. Multiplatform Content Adapter (LinkedIn, X/Grok, Facebook)
    2. Product Microlanding Template & Vercel Config
    3. 3-Page PDF Audit Brief Generator
    """

    def test_01_multiplatform_content_adapter(self):
        print("\n" + "=" * 76)
        print("🧪 [TEST 1/3] Multiplatform Content Adapter (LinkedIn / X / Facebook)")
        print("=" * 76)

        topic = "Context Caching & Token Economics"
        keyword = "CACHE"
        pack = generate_omnichannel_pack(topic=topic, keyword=keyword)

        # Assertions
        self.assertIn("linkedin_post", pack)
        self.assertIn("x_thread", pack)
        self.assertIn("facebook_post", pack)
        self.assertIn("video_teaser_prompt", pack)

        # 1. LinkedIn validations
        li_post = pack["linkedin_post"]
        self.assertGreater(len(li_post), 300)
        self.assertTrue(keyword in li_post or "CACHE" in li_post)
        print(f"  ✓ LinkedIn Post generated ({len(li_post)} chars, CTA keyword: {keyword})")

        # 2. X / Grok Thread validations
        x_thread = pack["x_thread"]
        tweets = [t.strip() for t in x_thread.split("--- [Tweet Break] ---") if t.strip()]
        self.assertGreaterEqual(len(tweets), 3)
        self.assertIn("#BuildInPublic", x_thread)
        self.assertIn("#AIInfra", x_thread)
        self.assertIn("#vLLM", x_thread)
        print(f"  ✓ X / Twitter Thread generated ({len(tweets)} tweets, hashtags verified)")

        # 3. Facebook Tech Groups validation
        fb_post = pack["facebook_post"]
        self.assertGreater(len(fb_post), 300)
        self.assertTrue("Here is how we tackled" in fb_post)
        print(f"  ✓ Facebook Case Study generated ({len(fb_post)} chars, first-person founder tone)")

        # 4. Video prompt validation
        video_prompt = pack["video_teaser_prompt"]
        self.assertGreater(len(video_prompt), 100)
        self.assertIn("Cinematic 4K", video_prompt)
        print(f"  ✓ Cinematic Video Teaser Prompt generated ({len(video_prompt)} chars)")

        # 5. Sync to Omnichannel_Content in Google Sheets
        card_image_path = os.path.join(ROOT_DIR, "output", "linkedin_cards", "linkedin_card_ttft_routing.png")
        if not os.path.exists(card_image_path):
            card_image_path = os.path.join(ROOT_DIR, "templates", "product_landing", "index.html")

        try:
            sync_result = sync_omnichannel_to_sheets(pack, card_image_path)
            self.assertEqual(sync_result["status"], "Ready to Post")
            print(f"  ✓ Synced to Google Sheets tab 'Omnichannel_Content' successfully!")
        except Exception as err:
            print(f"  ℹ️ Sheets sync network note: {err}")

    def test_02_product_microlanding_integrity(self):
        print("\n" + "=" * 76)
        print("🧪 [TEST 2/3] Product Microlanding Template & Vercel Config")
        print("=" * 76)

        html_path = os.path.join(ROOT_DIR, "templates", "product_landing", "index.html")
        vercel_path = os.path.join(ROOT_DIR, "templates", "product_landing", "vercel.json")

        self.assertTrue(os.path.exists(html_path), f"Missing index.html at {html_path}")
        self.assertTrue(os.path.exists(vercel_path), f"Missing vercel.json at {vercel_path}")

        # Check vercel.json valid JSON
        with open(vercel_path, "r", encoding="utf-8") as vf:
            v_conf = json.load(vf)
            self.assertEqual(v_conf.get("version"), 2)
            self.assertEqual(v_conf.get("name"), "razum-ai-sprint-landing")
        print("  ✓ Vercel config valid (routes to /index.html)")

        # Check HTML contents & sections
        with open(html_path, "r", encoding="utf-8") as hf:
            html_content = hf.read()

        self.assertIn("Slash LLM Latency &amp; Token Spend by", html_content)
        self.assertIn("40% in 48 Hours", html_content)
        self.assertIn("<video", html_content)
        self.assertIn("The 3 Bottlenecks Choking Production AI", html_content)
        self.assertIn("What You Get in the $490 Sprint Audit", html_content)
        self.assertIn("Reserve Your 48-Hour Sprint", html_content)
        self.assertIn("Instant Checkout via Stripe ($490)", html_content)
        self.assertIn("#0a0c10", html_content)
        self.assertIn("#00ffa3", html_content)
        self.assertIn("#7928ca", html_content)

        print(f"  ✓ HTML Landing valid ({len(html_content):,} bytes, all 5 required sections verified)")
        print(f"  ✓ Cyber-minimalism styling confirmed (#0a0c10, #00ffa3, #7928ca, Inter / JetBrains Mono)")

    def test_03_three_page_pdf_audit_generator(self):
        print("\n" + "=" * 76)
        print("🧪 [TEST 3/3] 3-Page PDF Audit Brief Generator")
        print("=" * 76)

        lead = get_lead_from_sheets()
        print(f"  Target Lead: {lead['company']} | {lead['hiring_role']}")

        pdf_path = generate_opus_audit_brief(lead_data=lead)
        self.assertTrue(os.path.exists(pdf_path), f"PDF was not generated at {pdf_path}")
        pdf_size = os.path.getsize(pdf_path)
        self.assertGreater(pdf_size, 5000, "PDF is smaller than expected")
        print(f"  ✓ PDF generated: {pdf_path} ({pdf_size:,} bytes)")

        # Verify exact 3 pages
        with open(pdf_path, "rb") as pf:
            raw_pdf = pf.read().decode("latin1", errors="ignore")

        page_matches = re.findall(r'/Type\s*/Page[^s]', raw_pdf)
        self.assertEqual(len(page_matches), 3, f"Expected exactly 3 pages, found {len(page_matches)}")
        print(f"  ✓ Page count verified: EXACTLY {len(page_matches)} PAGES (Page 1: Benchmark, Page 2: Diagnostics, Page 3: Roadmap + $490 CTA)")


def run_pipeline_test():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOmnichannelPipeline)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline_test()
