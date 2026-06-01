# GraphQL Introspection — joyreactor.cc

---

## Статус: Introspection УВІМКНЕНА

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { queryType { name } } }"}'
```

**Відповідь:** `{"data":{"__schema":{"queryType":{"name":"Query"}}}}` — повна схема доступна без авторизації.

---

## Query типи

| Query             | Тип повернення | Примітка                            |
| ----------------- | -------------- | ----------------------------------- |
| `tagAutocomplete` | LIST           |                                     |
| `me`              | User           | Поточний авторизований юзер         |
| `user`            | User           | Юзер за username — потенційний IDOR |
| `tag`             | Tag            |                                     |
| `weekTopPosts`    | LIST           |                                     |
| `yearTopPosts`    | LIST           |                                     |
| `changedPosts`    | LIST           |                                     |
| `search`          | SearchResult   |                                     |
| `initialTags`     | LIST           |                                     |
| `checkEmail`      | Boolean        | **User enumeration**                |
| `searchHistory`   | SearchHistory  |                                     |
| `node`            | Node           |                                     |
| `donated`         | Int            |                                     |
| `trends`          | LIST           |                                     |

---

## User тип — поля

| Поле                  | Тип          | Чутливість               |
| --------------------- | ------------ | ------------------------ |
| `id`                  | ID           | —                        |
| `username`            | String       | —                        |
| `token`               | String       | 🔴 Auth токен            |
| `phone`               | Phone        | 🔴 Номер телефону        |
| `privateMessages`     | LIST         | 🔴 Особисті повідомлення |
| `contacts`            | LIST         | 🟠 Контакти              |
| `lastLogin`           | DateTimeTz   | 🟡                       |
| `settings`            | UserSettings | 🟡                       |
| `banLogs`             | LIST         | 🟡                       |
| `blockedUsers`        | LIST         | —                        |
| `friends`             | LIST         | —                        |
| `active`              | Boolean      | —                        |
| `about`               | String       | —                        |
| `createdAt`           | Date         | —                        |
| `rating`              | Float        | —                        |
| `goldStatus`          | Boolean      | —                        |
| `platinumStatus`      | Boolean      | —                        |
| `postsBannedUntil`    | DateTimeTz   | —                        |
| `commentsBannedUntil` | DateTimeTz   | —                        |

---

## Field suggestions

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ nonExistentField }"}'
```

**Відповідь:** `{"errors":[{"message":"Cannot query field \"nonExistentField\" on type \"Query\"."}]}`  
Field suggestions не повертають підказки — але introspection і так дає повну схему.
