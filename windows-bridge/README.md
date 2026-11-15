# BALA JARVIS Windows Notification Bridge

This is a foreground UWP companion prototype for Windows 10/11. It uses Microsoft's UserNotificationListener API and requires the user to grant notification access.

## What it does
- Reads Windows toast notifications while this bridge app is open.
- Looks for notifications from Phone Link, WhatsApp Desktop, and Microsoft Teams.
- Forwards only likely incoming-call notifications to the local BALA JARVIS server at http://127.0.0.1:8000/api/notifications.
- The dashboard polls the notification feed and displays received events.

## Important limitations
- This is a source project, not an installer or signed MSIX package.
- The app must remain open in the foreground. Closing it stops monitoring.
- It can only detect call alerts that the relevant Windows app actually posts as Windows toast notifications. It cannot guarantee all calls or retrieve caller details that the app does not include.
- It does not answer, reject, record, or control calls.
- Windows notification access is broad and privacy-sensitive. Grant it only if you understand and trust this local companion.

## Build
1. Install Visual Studio with the **Universal Windows Platform development** workload and a Windows 10/11 SDK.
2. Open `BalaJarvisWindowsBridge.sln`.
3. Build and deploy the app to your local PC.
4. Launch **BALA JARVIS Windows Bridge**.
5. Select **Grant notification access** and approve Windows' permission prompt.
6. In PowerShell, find the installed package family name:
   ```powershell
   Get-AppxPackage | Where-Object { $_.Name -like "*BalaJarvisWindowsBridge*" } | Select-Object Name, PackageFamilyName
   ```
7. If the bridge cannot reach the local server, add a loopback exemption for that package (run PowerShell as Administrator and replace the placeholder with the exact PackageFamilyName):
   ```powershell
   CheckNetIsolation.exe LoopbackExempt -a -n="PASTE_PACKAGE_FAMILY_NAME"
   ```
8. Keep this app open while you want the dashboard to monitor notifications.
9. Make sure `python jarvis_server.py` is running on the same PC.

The bridge sends to loopback only (127.0.0.1); it does not send Windows notifications over the network or to the Android companion.
