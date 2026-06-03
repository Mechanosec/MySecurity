# Pentest Report — joyreactor.cc

**Дата:** 2026-06-01  
**Ціль:** joyreactor.cc / api.joyreactor.cc  
**Тип:** Black-box  
**Статус:** In Progress

---

## Структура звіту

| Файл                                                       | Зміст                                    |
| ---------------------------------------------------------- | ---------------------------------------- |
| [01-recon.md](01-recon.md)                                 | Fingerprinting, технологічний стек       |
| [02-graphql-introspection.md](02-graphql-introspection.md) | GraphQL схема, знайдені типи і поля      |
| [03-findings.md](03-findings.md)                           | Знайдені вразливості з описом і доказами |

---

## Короткий підсумок (оновлюється)

| #   | Вразливість                                                        | Severity | Статус        |
| --- | ------------------------------------------------------------------ | -------- | ------------- |
| 1   | GraphQL Introspection увімкнена                                    | Low      | Підтверджено  |
| 2   | User Enumeration через `checkEmail`                                | Medium   | Підтверджено  |
| 3   | IDOR: поля профілю доступні через `selfOrAdmin: true` без авторизації | Low   | Підтверджено  |
| 4   | SSH: відсутня підтримка post-quantum key exchange                     | Info  | Підтверджено  |
| 5   | Auth cookie `jr_auth`: відсутні HttpOnly, Secure, SameSite атрибути  | High  | Підтверджено  |
| 6   | Captcha bypass через мобільний субдомен `m.joyreactor.cc`            | Medium | Підтверджено  |
| 7   | Авторизація без підтвердження email (`active: false`)                | Low    | Підтверджено  |
| 8   | Неактивні акаунти можуть голосувати — накрутка рейтингу              | Medium | Підтверджено  |
| 9   | SSRF через `post` mutation — file:// redirect bypass, port 3000/3001 non-HTTP відкриті, Redis/MySQL доступні | Critical | Поглиблено  |
| 10  | Stored HTML Injection — `<a href>` рендериться без санітизації в постах | High  | Підтверджено  |
| 11  | Stored XSS у полях профілю `fullName`/`about` — HTML зберігається без санітизації | High | Підтверджено (рендер не підтверджено) |
| 12  | IDOR розширений — приватні поля адмін-акаунтів через `selfOrAdmin: true` | Medium | Підтверджено |
