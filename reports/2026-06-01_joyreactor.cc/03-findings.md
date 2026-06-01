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

## FIND-003 — Sensitive fields в User типі (перевіряється)

**Severity:** TBD  
**CWE:** CWE-200 — Exposure of Sensitive Information, CWE-639 — IDOR

### Опис

User тип містить поля `token`, `phone`, `privateMessages`, `contacts`. Якщо query `user(username: ...)` повертає ці поля для довільного юзера без авторизації — це критична IDOR вразливість.

### Статус

Потребує перевірки — чи доступні чутливі поля через `user` query без авторизації, чи тільки через `me`.

### Команда для перевірки

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ user(username: \"admin\") { id username token phone { number } privateMessages { totalCount } } }"}'
```

---

## TODO — Перевірити додатково

- [ ] Mutation типи — які операції доступні без авторизації
- [ ] Query batching — чи можна надсилати масив запитів (DoS / rate limit bypass)
- [ ] Deeply nested queries — DoS через рекурсивні запити
- [ ] `me` query без авторизації — що повертає
- [ ] Rate limiting на `checkEmail`
