package com.balajarvis.bridge

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val prefs = getSharedPreferences("bridge", MODE_PRIVATE)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(28, 36, 28, 28)
            setBackgroundColor(0xFF07121B.toInt())
        }
        fun label(text: String, size: Float = 16f) = TextView(this).apply {
            this.text = text; textSize = size; setTextColor(0xFFBDEEFF.toInt())
            setPadding(0, 12, 0, 12)
        }
        root.addView(label("BALA JARVIS // ANDROID BRIDGE", 20f))
        root.addView(label("Paste the private HTTPS address shown by Tailscale Serve on your PC. Do not use a public URL."))
        val url = EditText(this).apply {
            hint = "https://your-device.tailnet.ts.net"
            setSingleLine(true); setText(prefs.getString("server_url", ""))
            setTextColor(0xFFFFFFFF.toInt()); setHintTextColor(0xFF78909C.toInt())
        }
        root.addView(url)
        val status = label("Status: save your PC address, then enable notification access.")
        val save = Button(this).apply {
            text = "SAVE PC ADDRESS"
            setOnClickListener {
                val value = url.text.toString().trim().trimEnd('/')
                if (value.startsWith("https://") && value.endsWith(".ts.net")) {
                    prefs.edit().putString("server_url", value).apply()
                    status.text = "Private PC address saved."
                } else status.text = "Enter the HTTPS .ts.net address from Tailscale Serve."
            }
        }
        root.addView(save)
        val permission = Button(this).apply {
            text = "ENABLE NOTIFICATION ACCESS"
            setOnClickListener { startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)) }
        }
        root.addView(permission)
        root.addView(status)
        root.addView(label("Only notifications recognised as call alerts are forwarded. Notification access is controlled by Android Settings."))
        setContentView(root)
    }
}
