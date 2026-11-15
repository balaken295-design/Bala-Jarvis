# BALA JARVIS

A Windows-first local voice assistant with a futuristic HUD interface. This repository is the clean home for the Jarvis project.

## Planned / starter features

- Futuristic browser HUD
- Live CPU, RAM, disk, battery and network monitoring
- English and Tamil voice interaction (browser and installed voice support dependent)
- Optional offline Windows wake-word listener for "Hey Jarvis"
- Local AI responses through Ollama

## Requirements

- Windows 10 or 11
- Python 3.10+
- Google Chrome or Microsoft Edge
- [Ollama](https://ollama.com/download)
- Microphone for voice features

## Setup

1. Install Python and enable **Add Python to PATH**.
2. Install Ollama.
3. Open Command Prompt and download the model:

   ```powershell
   ollama pull qwen2.5:7b
   ```

4. Clone this repository and open its folder.
5. Run `start_jarvis.bat`.
6. Open `http://127.0.0.1:8000` if it does not open automatically.
7. Allow microphone access in Chrome or Edge.

## Model settings

The default model is `qwen2.5:7b`. To use another model, set the `JARVIS_MODEL` environment variable before starting the server.

## Mobile support and security

Mobile access is not enabled in this starter setup. The server should remain bound to localhost until authenticated pairing and HTTPS are implemented. Do not expose port 8000 to the public internet. A phone browser may support foreground voice input, but reliable always-on wake-word listening requires a dedicated mobile app.

## Privacy

Ollama runs the language model locally on your computer. The starter server is intended for localhost use only. Review any suggested computer commands before running them.
