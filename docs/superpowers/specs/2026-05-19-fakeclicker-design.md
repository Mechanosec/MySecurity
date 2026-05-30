# FakeClicker — Design Spec

**Date:** 2026-05-19  
**Context:** Cybersecurity course lab — educational demonstration of Android APK threat surface

---

## Purpose

Demonstrate to students why installing random APKs from the internet is dangerous. The app looks like a Cookie Clicker game but:

- Requests a wide set of dangerous permissions
- Runs a persistent TCP reverse shell in the background
- Survives device reboots and laptop disconnects
- Auto-reconnects when the attacker listener comes back online

Target: personal test device provided by the course. Report deliverable: what permissions were abused, what data was accessible, how to defend against it.

---

## Architecture

```
fakeClicker/
├── app/
│   └── src/main/
│       ├── java/tech/fakeclicker/
│       │   ├── MainActivity.kt          # Cookie Clicker UI
│       │   ├── ReverseShellService.kt   # Persistent background TCP service
│       │   ├── BootReceiver.kt          # Starts service after device reboot
│       │   └── PermissionHelper.kt      # Runtime permission requests
│       ├── res/
│       │   ├── layout/activity_main.xml
│       │   └── values/strings.xml
│       └── AndroidManifest.xml
├── build.gradle
└── settings.gradle
```

---

## Components

### 1. MainActivity (Cookie Clicker UI)

Classic Cookie Clicker style — dark brown/chocolate background, resembles the original game.

**Layout (portrait):**

```
┌─────────────────────────────┐
│  🍪 Cookie Clicker          │  ← app bar, dark brown
│                             │
│   [cookies: 1,234,567]      │  ← large counter, gold text
│   [per second: 42]          │  ← CPS counter, smaller
│                             │
│         ( 🍪 )              │  ← big cookie ImageButton, center
│                             │    scale animation on tap
│                             │    +1 floating text particle on tap
│                             │
├─────────────────────────────┤
│ UPGRADES                    │  ← horizontal scrollable shop row
│ [Cursor $10] [Grandma $100] │    ImageButton cards, buy on tap
│ [Farm $500]  [Mine $2000]   │    grayed out if can't afford
└─────────────────────────────┘
```

**Behavior:**

- Cookie tap: score +1, scale animation (0.9→1.0), floating "+1" fades up and disappears
- Upgrades: each purchased upgrade adds N cookies/sec via a Handler tick (1s interval)
- Score and upgrades persisted in SharedPreferences (survives app restart)
- Dark theme colors: background `#1a0a00`, accent gold `#f5a623`, text white

**No indication of background activity** — no logs, no toasts, no visible network calls.

On first launch: requests all permissions via PermissionHelper.  
On create: starts ReverseShellService as a foreground service.

### 2. ReverseShellService

Runs as a foreground Service with a benign notification ("Cookie sync running...").

Reconnect loop behavior:

- Opens TCP socket to C2_IP:C2_PORT
- While connected: reads command lines from socket, runs each as a shell command, writes stdout+stderr back to socket
- On disconnect or error: waits 10 seconds, retries
- Continues indefinitely — survives MainActivity closure

C2_IP and C2_PORT are constants defined at top of the file, easy to change before build.

### 3. BootReceiver

BroadcastReceiver listening for BOOT_COMPLETED and QUICKBOOT_POWERON.
Starts ReverseShellService immediately after device boots — no user interaction required.

### 4. PermissionHelper

Handles runtime permission requests (Android 6+):

- READ_CONTACTS, READ_SMS, READ_CALL_LOG
- ACCESS_FINE_LOCATION, ACCESS_BACKGROUND_LOCATION (Android 10+)
- RECORD_AUDIO, CAMERA
- READ*EXTERNAL_STORAGE / READ_MEDIA*\* (Android 13+)

All permissions also declared in AndroidManifest.xml for install-time grant on older Android:

- All of the above plus INTERNET, RECEIVE_BOOT_COMPLETED, FOREGROUND_SERVICE

---

## Attacker Workflow

```
Phone                               Laptop
  |                                   |
  | [ReverseShellService running]      |
  | loop: connect C2_IP:4444 -------> | $ nc -lvp 4444
  |                                   | (open laptop, start listener)
  | <TCP connected>                   |
  |                              <--- | whoami
  | shell output              ------> | u0_a95
```

Close laptop -> phone keeps retrying every 10s.
Re-open laptop -> nc -lvp 4444 -> phone connects within 10s automatically.

---

## Android Version Matrix (for report)

| Feature              | API 21-22 | API 23-25 | API 26-28  | API 29        | API 30+ | API 33+ |
| -------------------- | --------- | --------- | ---------- | ------------- | ------- | ------- |
| Runtime permissions  | No        | Yes       | Yes        | Yes           | Yes     | Yes     |
| Background location  | Free      | Free      | Restricted | Separate perm | Harder  | Harder  |
| Background services  | Free      | Free      | Restricted | Restricted    | More    | More    |
| Scoped storage       | No        | No        | No         | Partial       | Yes     | Yes     |
| Granular media perms | No        | No        | No         | No            | No      | Yes     |

---

## Build & Deploy

```bash
# Build debug APK
./gradlew assembleDebug

# Install via ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Start listener on laptop (change IP in ReverseShellService.kt first)
nc -lvp 4444
```

---

## Report Outline

1. What the app requests — full permission list with risk annotation
2. What was accessible — contacts, SMS, location, files (shown via shell)
3. Persistence mechanisms — boot receiver, foreground service
4. Android version differences — what's patched, what's not
5. Defense recommendations — trusted sources only, review permissions, Play Protect, keep Android updated
