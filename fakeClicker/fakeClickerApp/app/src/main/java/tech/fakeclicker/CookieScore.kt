package tech.fakeclicker

class CookieScore {
    var cookies: Long = 0L
        private set
    var cookiesPerSecond: Long = 0L
        private set

    fun tap() { cookies++ }

    fun canAfford(cost: Long): Boolean = cookies >= cost

    fun buyUpgrade(cost: Long, cps: Long) {
        cookies -= cost
        cookiesPerSecond += cps
    }

    fun tick() { cookies += cookiesPerSecond }
}
