[app]
title = motorcontrol
package.name = water340
package.domain = org.kangyangkoo
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,avif,json,txt
version = 1.0
requirements = python3,kivy==2.3.0,paho-mqtt==1.6.1
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 21
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
