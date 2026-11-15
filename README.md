# BALA JARVIS

A Windows-first local AI assistant with an Ollama brain, browser HUD, optional offline "Hey Jarvis" wake listener, and private Android access.

## Requirements
- Windows 10/11, Python 3.10+, Chrome or Edge, microphone
- [Ollama](https://ollama.com/download)
- [Tailscale](https://tailscale.com/download) on the PC and Android phone for private mobile access

## PC setup
1. Install Python and select **Add Python to PATH**.
2. Install Ollama, then run `ollama pull qwen2.5:7b`.
3. Clone this repository and open its folder.
4. Run `start_jarvis.bat`; allow microphone permission in the browser.
5. Test chat and the Listen button at `http://127.0.0.1:8000`.

## Hey Jarvis wake word
The optional offline listener uses openWakeWord's pretrained `hey_jarvis` model.
1. Run `start_wake.bat` once to test. Keep the PC microphone connected and allow desktop microphone access if Windows asks.
2. Say "Hey Jarvis". The listener opens the Jarvis page with voice recognition requested.
3. For automatic launch at Windows sign-in, right-click PowerShell and choose **Run as administrator**, then run:
   `powershell -ExecutionPolicy Bypass -File .\install_wake_startup.ps1`
4. To remove the startup task, run:
   `Unregister-ScheduledTask -TaskName "BalaJarvisWake" -Confirm:$false`

**Important:** Wake-word detection is offline, but browser speech recognition availability and hands-free auto-start vary by browser/Windows permissions. If the browser blocks automatic microphone start, tap **Listen** once. The wake listener opens the interface; it does not guarantee speech recognition on every browser.

## Android private connection
This uses Tailscale Serve so the PC's web server stays bound to localhost and receives HTTPS traffic only through your private tailnet.
1. Install Tailscale on the Windows PC and Android phone. Sign in to the same private tailnet on both.
2. Start BALA JARVIS on the PC using `start_jarvis.bat`.
3. Open a second PowerShell window and run:
   `tailscale serve 8000`
4. Tailscale prints a private HTTPS address ending in `.ts.net`. Open that exact address on your Android phone while Tailscale is connected.
5. In Chrome, use **Add to Home screen** or **Install app** to place BALA JARVIS on your home screen.

Tailscale Serve may prompt you to enable HTTPS certificates for your tailnet. Keep the server running on the PC. The phone can use chat and browser voice while the PC is online. Desktop-only tools execute on the PC.

**Never use Tailscale Funnel or router port-forwarding for this app.** Keep access inside your tailnet. Do not share your Tailscale login or device access with others.

## Current limitations
- This is a mobile-friendly installable web app, not a native Android APK.
- The PC must be on, awake, running Ollama, and connected to Tailscale.
- Browser speech recognition may require a first manual microphone permission/action.
- The wake listener runs on the PC; Android browsers do not provide reliable always-on background wake-word listening.

## Windows call notification bridge

A Windows companion source project is available in `windows-bridge/`. It uses Microsoft's UserNotificationListener API and requires a packaged UWP app plus explicit user permission. It can forward recent Windows toast notifications from Phone Link, WhatsApp Desktop, and Microsoft Teams when their notification text looks like an incoming-call alert. The companion must remain open; app notification formats and Windows settings may prevent some alerts from appearing. It is not a call-control feature. Build instructions and privacy limitations are in `windows-bridge/README.md`.

## Phone and call notification bridge (prototype)

The server now provides a local notification feed:
- `GET /api/notifications` returns recent events.
- `POST /api/notifications` accepts a small JSON event from a trusted bridge client.

### Android companion
An Android Studio project is in `android-companion/`. It uses Android's user-granted Notification Listener access and forwards only notifications identified as call-related to the PC's private Tailscale HTTPS address. It does not request call-log, contacts, microphone, or SMS permissions. See `android-companion/README.md` before installing; notification access is sensitive and caller details depend on what the dialer exposes.

### Windows incoming calls
The dashboard can display Windows-source events, but a native Windows notification listener is not included yet. Windows support depends on the calling app (for example Phone Link, Teams, or WhatsApp Desktop) and requires a separate integration. Phone Link may mirror Android call notifications, which is different from detecting native Windows app calls.

Keep the server private on your Tailscale tailnet. Do not expose it with Funnel or router port forwarding. This prototype does not include app-level pairing authentication; only use it on a tailnet you control.

## Troubleshooting
- Ollama unavailable: start Ollama and run `ollama list`.
- Missing model: `ollama pull qwen2.5:7b`.
- Wake listener dependencies: run `python -m pip install -r requirements.txt`.
- Check Tailscale Serve: `tailscale serve status`.
- Microphone: use Chrome/Edge and grant microphone permission.

## Privacy
The Python server binds to `127.0.0.1`. Tailscale Serve is the private HTTPS bridge. Do not expose port 8000 publicly.
