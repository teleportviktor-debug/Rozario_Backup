"""
============================================================================
RAZUM AI 2026 • LIVE ECOSYSTEM DEV SERVER & INSTANT ORDER PACKAGER
Serves UI & Automatically Generates Client ZIP Packages on Webhook Orders
============================================================================
"""

import os
import sys
import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from python_engine.client_packager import generate_client_package
from python_engine.telegram_crm_bot import dispatch_new_lead
from python_engine.proposal_generator import generate_proposal_html

PORT = 8080

class RazumServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def do_POST(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/generate_proposal":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                c_name = data.get("name", "Клиент")
                c_niche = data.get("niche", "B2B")
                pkg_id = data.get("package_id", "pkg-sovereign")
                
                out_path = generate_proposal_html(c_name, c_niche, pkg_id)
                rel_url = "/" + os.path.relpath(out_path, ROOT_DIR).replace("\\", "/")
                
                print(f"[PROPOSAL ENGINE] 📄 КП успешно сгенерировано для: {c_name} -> {rel_url}")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                resp = {"status": "ok", "url": rel_url, "client": c_name}
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                print(f"❌ Ошибка генерации КП: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        if parsed.path == "/api/order":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            
            try:
                data = json.loads(body)
                client_name = data.get("name", "Клиент с сайта")
                client_email = data.get("email", "client@company.com")
                client_phone = data.get("phone", "—")
                pkg_name = data.get("package", "Sovereign Autopilot ($300)")
                pkg_id = data.get("package_id", "pkg-sovereign")
                price_usd = data.get("price_usd", 300)
                niche = data.get("niche", "B2B Бизнес")

                print(f"\n[AUTO-PACKAGER] 🚀 Получен новый заказ: {client_name} ({pkg_name}) - ${price_usd}")
                
                saved = dispatch_new_lead(
                    name=client_name,
                    email=client_email,
                    phone=client_phone,
                    package_name=pkg_name,
                    price_usd=price_usd,
                    niche=niche,
                    auto_build_package=True
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                resp = {"status": "ok", "lead_id": saved["id"], "package_built": True}
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode("utf-8"))
                return
            except Exception as e:
                print(f"❌ Ошибка обработки заказа: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode("utf-8"))
                return

        super().do_POST()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), RazumServerHandler) as httpd:
        print(f"=================================================================")
        print(f"  ⚡ RAZUM AI SERVER WITH AUTO-PACKAGER RUNNING ON PORT {PORT}")
        print(f"  Web Dashboard: http://localhost:{PORT}/index.html")
        print(f"  Packages Store: http://localhost:{PORT}/store_packages.html")
        print(f"  Sprints Landing: http://localhost:{PORT}/templates/product_landing/index.html")
        print(f"=================================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен.")

if __name__ == "__main__":
    run_server()
