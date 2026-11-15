"""BALA JARVIS local web server.
Run: python jarvis_server.py, then open http://127.0.0.1:8000
The server intentionally binds to localhost; mobile/LAN access needs a secure
pairing/authentication layer and is not enabled in this version.
"""
import json
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

import psutil
import jarvis_ollama as brain

PAGE = Path(__file__).with_name("jarvis_ui.html")
messages = [{"role": "system", "content": brain.SYSTEM_PROMPT}]
chat_lock = threading.Lock()
stats_lock = threading.Lock()
previous_net = [psutil.net_io_counters(), time.monotonic()]


def get_stats():
    now = time.monotonic()
    current = psutil.net_io_counters()
    with stats_lock:
        elapsed = max(now - previous_net[1], 0.1)
        upload = (current.bytes_sent - previous_net[0].bytes_sent) / elapsed / 1024
        download = (current.bytes_recv - previous_net[0].bytes_recv) / elapsed / 1024
        previous_net[:] = [current, now]

    battery = psutil.sensors_battery()
    root = Path.home().anchor or "/"
    return {
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(root).percent,
        "battery": (
            {"pct": round(battery.percent), "plugged": battery.power_plugged}
            if battery else None
        ),
        "up": round(upload),
        "down": round(download),
    }


class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_bytes(body, "application/json; charset=utf-8", status)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/stats":
            return self.send_json(get_stats())
        if path not in ("/", "/index.html"):
            return self.send_json({"error": "Not found"}, 404)
        try:
            return self.send_bytes(PAGE.read_bytes(), "text/html; charset=utf-8")
        except OSError:
            return self.send_json({"error": "jarvis_ui.html is missing"}, 500)

    def do_POST(self):
        if self.path != "/chat":
            return self.send_json({"error": "Not found"}, 404)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 12_000:
                return self.send_json({"reply": "Message size is invalid."}, 413)
            payload = json.loads(self.rfile.read(length))
            prompt = payload.get("message", "")
            if not isinstance(prompt, str):
                return self.send_json({"reply": "Message must be text."}, 400)
            prompt = prompt.strip()
            if not prompt:
                return self.send_json({"reply": "Please say or type a message."})
            with chat_lock:
                messages.append({"role": "user", "content": prompt[:4_000]})
                if len(messages) > 41:
                    del messages[1:21]
                try:
                    reply = brain.chat_turn(messages)
                except Exception as exc:
                    messages.pop()
                    reply = (
                        "My local AI could not respond. Check that Ollama is running "
                        f"and model {brain.MODEL!r} is installed. Details: {exc}"
                    )
            return self.send_json({"reply": reply})
        except (ValueError, json.JSONDecodeError):
            return self.send_json({"reply": "The request was not valid JSON."}, 400)
        except Exception:
            return self.send_json({"reply": "I could not process that request."}, 500)

    def log_message(self, *_args):
        pass


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print(f"BALA JARVIS online at http://127.0.0.1:8000 (model: {brain.MODEL})")
    webbrowser.open("http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nBALA JARVIS shutting down.")
    finally:
        server.server_close()
