import sqlite3
import shutil
import os
import tempfile
from datetime import datetime, timezone

COOKIES_DB = os.path.expanduser('~/.config/chromium/Default/Cookies')
OUTPUT_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies_report.txt')


def webkit_to_datetime(webkit_ts):
    if not webkit_ts:
        return 'session'
    epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
    try:
        dt = epoch + __import__('datetime').timedelta(microseconds=webkit_ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(webkit_ts)


def collect():
    # Chrome locks the DB while running — work on a copy
    fd, tmp = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        shutil.copy2(COOKIES_DB, tmp)
        conn = sqlite3.connect(tmp)
        cur = conn.cursor()
        cur.execute('''
            SELECT host_key, name, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            ORDER BY host_key, name
        ''')
        rows = cur.fetchall()
        conn.close()
    finally:
        os.remove(tmp)
    return rows


def write_report(rows):
    lines = [
        f'Chrome Cookie Report — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'Total cookies: {len(rows)}',
        '=' * 70,
        '',
    ]
    current_host = None
    for host, name, path, expires, secure, httponly, samesite in rows:
        if host != current_host:
            current_host = host
            lines.append(f'\n[{host}]')
        flags = []
        if secure:
            flags.append('Secure')
        if httponly:
            flags.append('HttpOnly')
        samesite_map = {0: 'None', 1: 'Lax', 2: 'Strict'}
        flags.append(f'SameSite={samesite_map.get(samesite, samesite)}')
        exp = webkit_to_datetime(expires)
        lines.append(f'  {name} | path={path} | expires={exp} | {", ".join(flags)}')

    with open(OUTPUT_PDF, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Report saved: {OUTPUT_PDF} ({len(rows)} cookies)')


if __name__ == '__main__':
    rows = collect()
    write_report(rows)
