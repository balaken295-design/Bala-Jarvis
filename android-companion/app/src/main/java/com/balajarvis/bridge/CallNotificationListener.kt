package com.balajarvis.bridge

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.app.Notification
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

class CallNotificationListener : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val n = sbn.notification ?: return
        val extras = n.extras ?: return
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString()?.take(120).orEmpty()
        val text = (extras.getCharSequence(Notification.EXTRA_TEXT)
            ?: extras.getCharSequence(Notification.EXTRA_BIG_TEXT))?.toString()?.take(240).orEmpty()
        val combined = (title + " " + text).lowercase()
        val isCall = n.category == Notification.CATEGORY_CALL ||
            listOf("incoming call", "calling", "ongoing call", "video call").any { combined.contains(it) }
        if (!isCall) return

        val prefs = getSharedPreferences("bridge", MODE_PRIVATE)
        val base = prefs.getString("server_url", null)?.trimEnd('/') ?: return
        if (!base.startsWith("https://") || !base.endsWith(".ts.net")) return

        val payload = JSONObject().apply {
            put("source", "android")
            put("kind", "call")
            put("title", if (title.isBlank()) "Incoming call" else title)
            put("detail", text)
            put("app", sbn.packageName)
        }.toString()

        thread(name = "JarvisCallBridge") {
            var connection: HttpURLConnection? = null
            try {
                connection = (URL("$base/api/notifications").openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 5000
                    readTimeout = 5000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json; charset=utf-8")
                }
                connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }
                connection.inputStream.close()
            } catch (_: Exception) {
                // Keep notifications private on-device if the PC is offline.
            } finally {
                connection?.disconnect()
            }
        }
    }
}
