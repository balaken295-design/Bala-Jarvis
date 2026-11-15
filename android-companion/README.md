# BALA JARVIS Android notification bridge (prototype)

This is a native Android companion project, not an APK. Build it with Android Studio (JDK 17 and Android SDK 35).

## Setup
1. Open this `android-companion` folder in Android Studio.
2. Let Gradle sync and build the app.
3. On the PC, run BALA JARVIS and enable private Tailscale Serve: `tailscale serve 8000`.
4. Copy the exact HTTPS `.ts.net` address printed by Tailscale into the app and save it.
5. Tap **Enable notification access** and explicitly enable BALA JARVIS Bridge in Android Settings.
6. Keep both devices signed in to the same private tailnet.

The app forwards only notifications recognised as call alerts (Android call category or a small set of call-related phrases). It does not request contacts, call-log, microphone, or SMS permissions, and it cannot answer or reject calls. Caller details depend on what the calling app exposes in its notification.

## Limitations
- Android notification access is powerful. Grant it only if you trust this app and understand that it can read notifications; this prototype filters before forwarding.
- Some manufacturers or dialer apps do not expose caller details in notifications.
- Windows notifications are not yet connected. Windows Phone Link may mirror Android call notifications to the PC, but native Windows calling-app notifications need a separate Windows notification-listener implementation.
- This prototype has no app-level pairing token. Keep the service reachable only inside your private Tailscale network; do not use Tailscale Funnel or router port forwarding.
