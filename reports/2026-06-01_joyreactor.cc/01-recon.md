# Recon — joyreactor.cc

**Дата:** 2026-06-01  
**Ціль:** https://api.joyreactor.cc/graphql

---

## HTTP Fingerprinting

```bash
curl -sI https://api.joyreactor.cc/graphql
```

### Відповідь

```
HTTP/2 200
server: nginx
content-type: application/json
cache-control: no-cache, private
vary: Origin
set-cookie: joyreactor_api_session=...; secure; httponly; samesite=none
x-frame-options: SAMEORIGIN
x-xss-protection: 1; mode=block
x-content-type-options: nosniff
```

### Висновки

| Заголовок         | Значення                 | Висновок                                                      |
| ----------------- | ------------------------ | ------------------------------------------------------------- |
| `server`          | nginx                    | Reverse proxy або напряму nginx                               |
| `content-type`    | application/json         | GraphQL API                                                   |
| `set-cookie`      | `joyreactor_api_session` | Laravel/PHP сесія (формат шифрування характерний для Laravel) |
| `samesite=none`   | —                        | Cookie доступна в cross-site запитах                          |
| `x-frame-options` | SAMEORIGIN               | Захист від clickjacking є                                     |

**Стек:** nginx + Laravel (PHP) + GraphQL (швидше за все Lighthouse або Rebing)

---

## Nmap scan

```
Host: api.joyreactor.cc (51.68.155.228)
rDNS: serv48.identityworks.ru

PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
5555/tcp open  (VPN — ідентифіковано як vpn.serv48.idwrx.com)
```

### Порт 5555

```bash
openssl s_client -connect 51.68.155.228:5555
# CN=vpn.serv48.idwrx.com — self-signed сертифікат
```

Це VPN endpoint хостера (identityworks.ru / idwrx.com), не пов'язаний з joyreactor.cc. Не є вектором атаки.

---

## GraphQL базова перевірка

```bash
curl -s -X POST https://api.joyreactor.cc/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}'
```

**Відповідь:** `{"data":{"__typename":"Query"}}` — API активне, відповідає на запити без авторизації.
