import pdfrw
import sqlite3
import shutil
import os
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote

COOKIES_DB = os.path.expanduser('~/.config/chromium/Default/Cookies')


def webkit_to_datetime(webkit_ts):
    if not webkit_ts:
        return 'session'
    try:
        epoch = datetime(1601, 1, 1, tzinfo=timezone.utc)
        dt = epoch + __import__('datetime').timedelta(microseconds=webkit_ts)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(webkit_ts)


def collect_cookies():
    fd, tmp = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        shutil.copy2(COOKIES_DB, tmp)
        conn = sqlite3.connect(tmp)
        cur = conn.cursor()
        cur.execute('''
            SELECT host_key, name, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies ORDER BY host_key, name
        ''')
        rows = cur.fetchall()
        conn.close()
    finally:
        os.remove(tmp)
    return rows


def build_report(rows):
    lines = [
        f'Cookie Report — {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'Total: {len(rows)} cookies',
        '=' * 60,
        '',
    ]
    current_host = None
    samesite_map = {0: 'None', 1: 'Lax', 2: 'Strict'}
    for host, name, path, expires, secure, httponly, samesite in rows:
        if host != current_host:
            current_host = host
            lines.append(f'\n[{host}]')
        flags = []
        if secure:
            flags.append('Secure')
        if httponly:
            flags.append('HttpOnly')
        flags.append(f'SameSite={samesite_map.get(samesite, samesite)}')
        lines.append(f'  {name} | {webkit_to_datetime(expires)} | {", ".join(flags)}')
    return '\n'.join(lines)


def make_pdf_with_report(report_text, output_path):
    chunk_size = 1500
    chunks = [report_text[i:i+chunk_size] for i in range(0, len(report_text), chunk_size)]
    total = len(chunks)

    parts = []
    for i, chunk in enumerate(chunks):
        # Escape PDF string special chars + encode non-Latin-1 as JS unicode escapes
        safe = ''
        for c in chunk:
            if c == '\\':
                safe += '\\\\'
            elif c == '(':
                safe += '\\('
            elif c == ')':
                safe += '\\)'
            elif c == "'":
                safe += "\\'"
            elif c == '\n':
                safe += '\\n'
            elif c == '\r':
                safe += '\\r'
            elif ord(c) > 255:
                safe += f'\\u{ord(c):04x}'
            else:
                safe += c
        parts.append(f"app.alert('Page {i+1}/{total}:\\n{safe}');")
    js = '\n'.join(parts)

    print(f'JS size: {len(js)} chars, chunks: {total}')

    template = pdfrw.PdfReader('blank.pdf')
    hex_js = js.encode('latin-1', errors='replace').hex()
    js_obj = pdfrw.PdfDict(
        S=pdfrw.PdfName('JavaScript'),
        JS=pdfrw.PdfObject(f'<{hex_js}>')
    )
    template.Root.OpenAction = js_obj
    fd = os.open(output_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'wb') as f:
        pdfrw.PdfWriter().write(f, template)
    print(f'Written: {output_path}')


if __name__ == '__main__':
    rows = collect_cookies()
    report = build_report(rows)
    make_pdf_with_report(report, 'cookie_report.pdf')
    print(f'Embedded {len(rows)} cookies into PDF')
