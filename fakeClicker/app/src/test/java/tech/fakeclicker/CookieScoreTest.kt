package tech.fakeclicker

import org.junit.Assert.*
import org.junit.Test

class CookieScoreTest {

    @Test
    fun `tap increments score by 1`() {
        val score = CookieScore()
        score.tap()
        assertEquals(1L, score.cookies)
    }

    @Test
    fun `multiple taps accumulate`() {
        val score = CookieScore()
        repeat(5) { score.tap() }
        assertEquals(5L, score.cookies)
    }

    @Test
    fun `can afford upgrade when score equals cost`() {
        val score = CookieScore()
        repeat(10) { score.tap() }
        assertTrue(score.canAfford(10L))
    }

    @Test
    fun `cannot afford upgrade when score is less than cost`() {
        val score = CookieScore()
        repeat(9) { score.tap() }
        assertFalse(score.canAfford(10L))
    }

    @Test
    fun `buying upgrade deducts cost and adds cps`() {
        val score = CookieScore()
        repeat(100) { score.tap() }
        score.buyUpgrade(cost = 10L, cps = 5L)
        assertEquals(90L, score.cookies)
        assertEquals(5L, score.cookiesPerSecond)
    }

    @Test
    fun `multiple upgrades accumulate cps`() {
        val score = CookieScore()
        repeat(1000) { score.tap() }
        score.buyUpgrade(cost = 10L, cps = 1L)
        score.buyUpgrade(cost = 100L, cps = 5L)
        assertEquals(6L, score.cookiesPerSecond)
    }

    @Test
    fun `tick adds cookiesPerSecond to total`() {
        val score = CookieScore()
        repeat(1000) { score.tap() }
        score.buyUpgrade(cost = 10L, cps = 3L)
        score.tick()
        assertEquals(993L, score.cookies)
    }
}
