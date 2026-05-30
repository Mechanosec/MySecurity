package tech.fakeclicker

import org.junit.Assert.*
import org.junit.Test

class ShellExecutorTest {

    @Test
    fun `run echo returns output`() {
        val result = ShellExecutor.run("echo hello")
        assertEquals("hello", result.trim())
    }

    @Test
    fun `run pwd returns non-empty path`() {
        val result = ShellExecutor.run("pwd")
        assertTrue(result.trim().startsWith("/"))
    }

    @Test
    fun `run invalid command returns error text`() {
        val result = ShellExecutor.run("notarealcommand_xyz")
        assertTrue(result.isNotEmpty())
    }

    @Test
    fun `run empty string returns empty`() {
        val result = ShellExecutor.run("")
        assertEquals("", result.trim())
    }
}
