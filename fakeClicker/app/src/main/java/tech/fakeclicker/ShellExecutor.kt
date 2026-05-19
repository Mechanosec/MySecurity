package tech.fakeclicker

object ShellExecutor {
    fun run(cmd: String): String {
        if (cmd.isBlank()) return ""
        return try {
            val proc = ProcessBuilder("sh", "-c", cmd)
                .redirectErrorStream(true)
                .start()
            val output = proc.inputStream.bufferedReader().readText()
            proc.waitFor()
            output
        } catch (e: Exception) {
            "error: ${e.message}\n"
        }
    }
}
