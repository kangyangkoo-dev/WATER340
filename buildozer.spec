[app]
title = motorcontrol
package.name = water340
package.domain = org.kangyangkoo
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,avif,json,txt
version = 1.0
# Keep Android/host Python on 3.11 for pyjnius compatibility.
# Android API 26+ is required here because CPython 3.11 grp uses
# getgrent/setgrent/endgrent, which Android exposes from API 26.
requirements = python3==3.11.14,hostpython3==3.11.14,kivy==2.3.0,paho-mqtt==1.6.1
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 26
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
