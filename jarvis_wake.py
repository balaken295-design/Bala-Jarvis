"""Optional offline Windows wake-word listener for 'Hey Jarvis'."""
import subprocess,sys,time,urllib.request
from pathlib import Path
import sounddevice as sd
from openwakeword.model import Model
HERE=Path(__file__).parent;URL="http://127.0.0.1:8000";THRESHOLD=.5;COOLDOWN=6;NOWIN=0x08000000
def server_up():
    try:urllib.request.urlopen(URL+"/stats",timeout=1.5);return True
    except Exception:return False
def wake():
    if not server_up():
        py=Path(sys.executable);hidden=py.with_name("pythonw.exe")
        subprocess.Popen([str(hidden if hidden.exists() else py),str(HERE/"jarvis_server.py"),"--no-browser"],cwd=HERE,creationflags=NOWIN)
        for _ in range(30):
            time.sleep(.5)
            if server_up():break
    if server_up():subprocess.Popen(f'start "" msedge --app={URL}',shell=True)
def main():
    model=Model(wakeword_models=["hey_jarvis"],inference_framework="onnx");last=0
    print('Listening offline for "Hey Jarvis". Ctrl+C to stop.')
    with sd.InputStream(samplerate=16000,channels=1,dtype="int16",blocksize=1280) as stream:
        while True:
            audio,_=stream.read(1280);score=max(model.predict(audio[:,0]).values())
            if score>THRESHOLD and time.time()-last>COOLDOWN:
                last=time.time();wake()
                if hasattr(model,"reset"):model.reset()
if __name__=="__main__":
    if sys.platform!="win32":raise SystemExit("Windows only.")
    main()
