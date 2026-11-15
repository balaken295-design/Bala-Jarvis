@echo off
echo Start BALA JARVIS first using start_jarvis.bat.
echo This creates a private HTTPS address for devices on your Tailscale network.
where tailscale >nul 2>nul
if errorlevel 1 (
  echo Tailscale CLI not found. Install Tailscale and sign in on this PC.
  pause
  exit /b 1
)
tailscale serve 8000
pause
