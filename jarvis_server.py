"""Local BALA JARVIS HTTP server. Run: python jarvis_server.py"""
import json,sys,time,webbrowser
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import psutil
import jarvis_ollama as brain
PAGE=Path(__file__).with_name("jarvis_ui.html")
history=[{"role":"system","content":brain.SYSTEM_PROMPT}]
net=[psutil.net_io_counters(),time.time()]
def stats():
    now,io=time.time(),psutil.net_io_counters();dt=max(now-net[1],.1)
    up=(io.bytes_sent-net[0].bytes_sent)/dt/1024;down=(io.bytes_recv-net[0].bytes_recv)/dt/1024
    net[:]=[io,now];bat=psutil.sensors_battery()
    return {"cpu":psutil.cpu_percent(),"ram":psutil.virtual_memory().percent,"disk":psutil.disk_usage(Path.home().anchor or "/").percent,"battery":{"pct":round(bat.percent),"plugged":bat.power_plugged} if bat else None,"up":round(up),"down":round(down)}
class Handler(BaseHTTPRequestHandler):
    def send_data(self,data,ctype="application/json; charset=utf-8"):
        body=json.dumps(data).encode() if isinstance(data,dict) else data
        self.send_response(200);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path=="/stats":return self.send_data(stats())
        if self.path not in ("/","/index.html"):return self.send_error(404)
        return self.send_data(PAGE.read_bytes(),"text/html; charset=utf-8")
    def do_POST(self):
        if self.path!="/chat":return self.send_error(404)
        try:
            n=min(int(self.headers.get("Content-Length","0")),12000)
            prompt=json.loads(self.rfile.read(n) or b"{}").get("message","").strip()
            if not prompt:return self.send_data({"reply":"Please say or type a message."})
            history.append({"role":"user","content":prompt[:4000]})
            if len(history)>25:del history[1:11]
            try:
                answer=brain.chat_turn(history);history.append({"role":"assistant","content":answer})
            except Exception as exc:
                history.pop();answer="Local AI unavailable. Start Ollama and install the selected model. "+str(exc)
            return self.send_data({"reply":answer})
        except Exception:return self.send_data({"reply":"I could not process that request."})
    def log_message(self,*args):pass
if __name__=="__main__":
    server=ThreadingHTTPServer(("127.0.0.1",8000),Handler)
    print(f"BALA JARVIS: http://127.0.0.1:8000 (model {brain.MODEL})")
    if "--no-browser" not in sys.argv:webbrowser.open("http://127.0.0.1:8000")
    server.serve_forever()
