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
| 3   | Sensitive fields в User типі (`token`, `phone`, `privateMessages`) | TBD      | Перевіряється |
