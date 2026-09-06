# WATER340 Android API 26 build fix

The previous GitHub Actions build used Android NDK target API 21 and failed while compiling CPython 3.11 `grp`.
Android exposes `getgrent`, `setgrent`, and `endgrent` from API level 26.

This revision changes:

- `android.minapi = 21` -> `android.minapi = 26`
- keeps Android/host Python pinned to 3.11.14
- keeps arm64-v8a and Android API 35
- adds workflow logging of the selected API settings before the build

After upload, run **Actions -> Build WATER340 APK -> Run workflow**.
In the log, paths should show `ndk_target_26` rather than `ndk_target_21`.
