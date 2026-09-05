import subprocess
import re
import sys
import os

url_file = os.path.join(os.path.dirname(__file__), "..", "registry", "tunnel_url.txt")

cmd = [
    "ssh",
    "-o", "StrictHostKeyChecking=no",
    "-o", "ServerAliveInterval=30",
    "-p", "443",
    "-R0:localhost:8000",
    "a.pinggy.io"
]

print("Starting Pinggy tunnel...")
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

url_found = False
while True:
    line = proc.stdout.readline()
    if not line:
        break
    sys.stdout.write(line)
    sys.stdout.flush()
    matches = re.findall(r'https://[^\s]+\.pinggy\.[^\s]+', line)
    if matches and not url_found:
        tunnel_url = matches[0].strip()
        url_found = True
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(tunnel_url + "\n")
        print(f"\n==========================================")
        print(f"TUNNEL READY: {tunnel_url}")
        print(f"==========================================\n")
