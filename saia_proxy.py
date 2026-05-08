"""
Tiny local CORS proxy for SAIA / Academic Cloud API.
Run once: python saia_proxy.py
Then open plotter_studio.html in your browser.
The proxy listens on http://localhost:8765 and forwards to chat-ai.academiccloud.de.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request, urllib.error, json, sys

TARGET = "https://chat-ai.academiccloud.de"
PORT   = 8765

CORS = {
    "Access-Control-Allow-Origin":  "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS,DELETE,PUT",
    "Access-Control-Allow-Headers": "Authorization,Content-Type,Accept",
}

class Proxy(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} → {fmt % args}")

    def _cors(self):
        for k, v in CORS.items():
            self.send_header(k, v)

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length) if length else b""
        url    = TARGET + self.path

        fwd_headers = {}
        for h in ("Authorization", "Content-Type", "Accept"):
            if self.headers.get(h):
                fwd_headers[h] = self.headers[h]

        req = urllib.request.Request(url, data=body, headers=fwd_headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

    def do_GET(self):
        url = TARGET + self.path
        fwd_headers = {}
        for h in ("Authorization", "Accept"):
            if self.headers.get(h):
                fwd_headers[h] = self.headers[h]
        req = urllib.request.Request(url, headers=fwd_headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(resp.status)
                self._cors()
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Proxy)
    print(f"SAIA proxy running on http://localhost:{PORT}")
    print(f"Forwarding to {TARGET}")
    print("Set proxy URL in Plotter Studio to:  http://localhost:8765/")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProxy stopped.")
        sys.exit(0)
