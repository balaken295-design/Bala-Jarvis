# BALA JARVIS

A Windows-first local AI voice assistant with a futuristic browser HUD.

## Features
- Local AI chat through Ollama
- Live CPU, RAM, disk, battery and network statistics
- Browser speech input/output (English/Tamil support depends on browser voices)
- Optional offline Windows wake-word listener for "Hey Jarvis"
- Localhost-only server by default

## Requirements
- Windows 10/11, Python 3.10+, Chrome or Edge
- [Ollama for Windows](https://ollama.com/download)
- Microphone for voice features

## Setup
1. Install Python and enable **Add Python to PATH**.
2. Install Ollama and run `ollama pull qwen2.5:7b`.
3. Clone/download this repository.
4. Run `start_jarvis.bat`.
5. Open http://127.0.0.1:8000 and allow microphone access.

Manual setup:
```powershell
python -m pip install -r requirements.txt
python jarvis_server.py
```

## "Hey Jarvis" on Windows
Run `python jarvis_wake.py` to test the offline listener. To start at login, put a shortcut to `start_wake.bat` in the Windows Startup folder (Win+R, then `shell:startup`). The first run may download the wake-word model.

## Mobile access
Mobile/LAN access is intentionally not enabled yet. The server binds to `127.0.0.1` because a desktop assistant must not be exposed to other devices without authentication and encrypted transport. A future phone pairing feature should use HTTPS and revocable device tokens. A mobile browser cannot reliably listen for wake words continuously in the background; that generally requires a dedicated mobile app.

## Troubleshooting
- Ollama connection error: open Ollama and check `ollama list`.
- Missing model: run `ollama pull qwen2.5:7b`.
- Microphone blocked: use Chrome/Edge and allow microphone permission.
- NVIDIA GPU readings require `nvidia-smi`; CPU temperature may not be exposed.

## Privacy
The server listens only on this computer by default. Do not expose port 8000 to the public internet. Review any suggested action before running it.