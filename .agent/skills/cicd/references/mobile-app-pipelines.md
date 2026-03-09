# Mobile App Pipelines: Best Practices

## Platform Overview

| Platform | Build Tool | Runner | Typical Timeout |
| --- | --- | --- | --- |
| React Native (Expo/EAS) | EAS Build (cloud) | ubuntu-latest | 5 min (trigger only) |
| React Native (bare) | Xcode / Gradle | macos-latest / ubuntu-latest | 30–45 min |
| Flutter | flutter build | ubuntu-latest / macos-latest | 20–30 min |
| iOS native | Xcode + Fastlane | macos-latest | 30–45 min |
| Android native | Gradle | ubuntu-latest | 20–30 min |

> **iOS builds require macOS runners.** GitHub-hosted `macos-latest` is significantly more expensive (10× Linux per minute). Optimize build times aggressively or use self-hosted Mac minis.

---

## React Native

### EAS Build (Recommended for Expo projects)

Offload the heavy build to Expo's cloud service; CI only triggers and monitors:

```yaml
name: React Native Build (EAS)

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'app.json'
      - 'package.json'
      - 'eas.json'
  workflow_dispatch:

permissions:
  contents: read

jobs:
  eas-build:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - uses: expo/expo-github-action@v8 # Pin to SHA in production
        with:
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}

      - name: Build for iOS
        run: eas build --platform ios --profile preview --non-interactive

      - name: Build for Android
        run: eas build --platform android --profile preview --non-interactive
```

### EAS Update (OTA updates)

```yaml
- name: Publish OTA update
  run: eas update --branch preview --message "${{ github.event.head_commit.message }}" --non-interactive
```

> **OTA vs Native Build**: Use `eas update` for JS-only changes (instant). Use `eas build` when native dependencies change (new native modules, SDK upgrade).

### Bare React Native (without Expo)

#### Android

```yaml
jobs:
  android:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
          cache: gradle

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

      - name: Build APK
        working-directory: android
        run: ./gradlew assembleRelease

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: app-release-${{ github.run_id }}
          path: android/app/build/outputs/apk/release/
```

#### iOS

```yaml
jobs:
  ios:
    runs-on: macos-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - run: npm ci

      - name: Cache CocoaPods
        uses: actions/cache@v4
        with:
          path: ios/Pods
          key: pods-${{ runner.os }}-${{ hashFiles('ios/Podfile.lock') }}

      - name: Install CocoaPods
        working-directory: ios
        run: pod install

      - name: Build iOS
        working-directory: ios
        run: |
          xcodebuild build \
            -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -configuration Release \
            -destination 'generic/platform=iOS Simulator' \
            -derivedDataPath build \
            CODE_SIGNING_ALLOWED=NO
```

---

## Flutter

### Test and Build

```yaml
name: Flutter CI

on:
  push:
    branches: [main]
    paths-ignore: ['**.md', 'docs/**']
  pull_request:
    branches: [main]
    paths-ignore: ['**.md', 'docs/**']

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2 # Pin to SHA in production
        with:
          flutter-version: '3.24'
          channel: stable
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Verify code generation
        run: |
          dart run build_runner build --delete-conflicting-outputs
          # Fail if generated files are out of date
          git diff --exit-code

      - name: Analyze
        run: flutter analyze --no-fatal-infos

      - name: Run tests
        run: flutter test --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: flutter-coverage
          path: coverage/lcov.info

  build-android:
    needs: test
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24'
          channel: stable
          cache: true

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
          cache: gradle

      - run: flutter pub get
      - run: flutter build apk --release

      - uses: actions/upload-artifact@v4
        with:
          name: flutter-apk-${{ github.run_id }}
          path: build/app/outputs/flutter-apk/app-release.apk

  build-ios:
    needs: test
    runs-on: macos-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24'
          channel: stable
          cache: true

      - run: flutter pub get

      - name: Build iOS (no codesign)
        run: flutter build ios --release --no-codesign
```

---

## iOS Native (Xcode + Fastlane)

### Code Signing in CI

```yaml
jobs:
  ios-build:
    runs-on: macos-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4

      - name: Install Fastlane
        run: |
          gem install bundler
          bundle install

      - name: Import certificates
        env:
          CERTIFICATE_BASE64: ${{ secrets.P12_CERTIFICATE_BASE64 }}
          CERTIFICATE_PASSWORD: ${{ secrets.P12_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # Create temporary keychain
          KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db
          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

          # Import certificate
          echo -n "$CERTIFICATE_BASE64" | base64 --decode -o $RUNNER_TEMP/certificate.p12
          security import $RUNNER_TEMP/certificate.p12 -P "$CERTIFICATE_PASSWORD" \
            -A -t cert -f pkcs12 -k $KEYCHAIN_PATH
          security list-keychain -d user -s $KEYCHAIN_PATH

      - name: Install provisioning profile
        env:
          PROVISIONING_PROFILE_BASE64: ${{ secrets.PROVISIONING_PROFILE_BASE64 }}
        run: |
          PP_PATH=$HOME/Library/MobileDevice/Provisioning\ Profiles
          mkdir -p "$PP_PATH"
          echo -n "$PROVISIONING_PROFILE_BASE64" | base64 --decode -o "$PP_PATH/profile.mobileprovision"

      - name: Build and archive
        run: bundle exec fastlane build
        # Or direct xcodebuild:
        # xcodebuild archive \
        #   -workspace MyApp.xcworkspace \
        #   -scheme MyApp \
        #   -archivePath $RUNNER_TEMP/MyApp.xcarchive \
        #   -destination 'generic/platform=iOS'

      - name: Upload to TestFlight
        if: github.ref == 'refs/heads/main'
        env:
          APP_STORE_CONNECT_API_KEY: ${{ secrets.APP_STORE_CONNECT_API_KEY }}
        run: bundle exec fastlane upload_testflight

      - name: Cleanup keychain
        if: always()
        run: security delete-keychain $RUNNER_TEMP/app-signing.keychain-db
```

### Fastlane match (recommended for team signing)

```yaml
- name: Sync certificates via match
  run: bundle exec fastlane match appstore --readonly
  env:
    MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
    MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_TOKEN }}
```

> **Fastlane match** stores encrypted certificates in a private Git repo — team members and CI share the same signing identity. Use `--readonly` in CI to prevent accidental cert regeneration.

---

## Android Native (Gradle)

### Signed APK/AAB Build

```yaml
jobs:
  android-build:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
          cache: gradle

      - name: Decode keystore
        env:
          KEYSTORE_BASE64: ${{ secrets.ANDROID_KEYSTORE_BASE64 }}
        run: echo "$KEYSTORE_BASE64" | base64 --decode > android/app/release.keystore

      - name: Build signed AAB
        working-directory: android
        env:
          KEYSTORE_PASSWORD: ${{ secrets.ANDROID_KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.ANDROID_KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.ANDROID_KEY_PASSWORD }}
        run: ./gradlew bundleRelease

      - name: Upload AAB
        uses: actions/upload-artifact@v4
        with:
          name: app-release-${{ github.run_id }}
          path: android/app/build/outputs/bundle/release/*.aab

      - name: Cleanup keystore
        if: always()
        run: rm -f android/app/release.keystore
```

---

## Version & Build Number Management

### Auto-increment build number

```yaml
- name: Set build number from run number
  run: |
    BUILD_NUMBER=${{ github.run_number }}
    echo "BUILD_NUMBER=$BUILD_NUMBER" >> $GITHUB_ENV

    # For iOS (Info.plist)
    /usr/libexec/PlistBuddy -c "Set :CFBundleVersion $BUILD_NUMBER" ios/MyApp/Info.plist

    # For Android (build.gradle)
    sed -i "s/versionCode [0-9]*/versionCode $BUILD_NUMBER/" android/app/build.gradle

    # For Flutter (pubspec.yaml)
    # flutter build apk --build-number=$BUILD_NUMBER

    # For React Native (app.json / build.gradle / Info.plist)
    # Use react-native-version or manual sed
```

---

## Mobile-Specific Key Rules

| Rule | Reason |
| --- | --- |
| Use EAS Build for Expo projects | Avoids macOS runner costs; handles signing automatically |
| Cache CocoaPods + Gradle aggressively | iOS + Android builds are slow; caching saves 5–15 min |
| Always clean up signing materials | Keychain + provisioning profiles should not persist on runners |
| Use `--readonly` for Fastlane match in CI | Prevents accidental certificate regeneration |
| Set `timeout-minutes: 45` for iOS builds | Xcode builds are significantly slower than expected |
| Store keystore/certificates as base64 secrets | Binary files cannot be stored directly in GitHub secrets |
| Use `github.run_number` for build numbers | Monotonically increasing, unique per workflow |
| Run tests BEFORE building | Fast feedback; avoid wasting build time if tests fail |
| Use `--no-codesign` for CI test builds | Skip signing for PR validation builds to save time |
