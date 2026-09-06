# WATER340 Kivy 변환 프로젝트

MIT App Inventor 프로젝트 `WATER340C_251219_2_copy.aia`의 Screen1 UI와 Blocks 로직을 Python/Kivy로 재구성한 프로젝트입니다.

## 변환된 핵심 기능

- MQTT 연결/해제
- 브로커 선택: `broker.hivemq.com`, `test.mosquitto.org`, `broker.emqx.io`
- V2~V5 장치 선택: `Kangyangkoo2` ~ `Kangyangkoo5`
- MQTT publish 토픽
  - `in{device}/mc1` ~ `mc4`
  - `in{device}/mc_lock`
  - `in{device}/autostop`
  - `in{device}/kreset2`
- MQTT subscribe 토픽
  - `out{device}/kinfo` QoS 0
  - `out{device}/ktemp` QoS 1
- `kinfo` 13문자/쉼표 구분 상태값에 따른 모터/Lock/Autostop 색상 반영
- 모터 버튼 단일 클릭: 1초 후 현재 상태를 기준으로 0/1 토글 발행
- 모터 버튼 더블 클릭: 1초 안에 두 번 클릭하면 무조건 1 발행
- Lock mode 토글
- Autostop 15분/25분 선택값(1/2) 발행
- 리셋 `kreset2=1`

## 원본과 달라진 구현 방식

App Inventor의 `delay` 프로시저는 2초 동안 `SystemTime`을 반복 검사하는 busy-wait입니다. 안드로이드/Kivy에서 그대로 구현하면 UI가 멈출 수 있으므로 `Clock.schedule_once(..., 2.0)` 비동기 지연으로 바꿨습니다. 기능 목적은 동일합니다.

원본은 `clickCount`를 모터 1~4가 모두 공유합니다. 이 프로젝트도 전역 카운터를 유지하지만, 예약된 1초 타이머는 클릭한 모터별로 관리해 UI 멈춤 없이 의도된 단일/더블 클릭 동작을 구현했습니다.

## PC에서 테스트

```bash
python -m pip install -r requirements.txt
python main.py
```

## Android APK 빌드 (Ubuntu 권장)

Buildozer 설치 후 프로젝트 폴더에서:

```bash
buildozer android debug
```

완료되면 `bin/` 폴더에 APK가 생성됩니다.

## 중요

이 프로젝트는 원본 AI2의 UrsPahoMqttClient 확장을 Python의 `paho-mqtt`로 대체했습니다. MQTT 브로커가 익명 TCP 1883 접속을 허용한다는 원본 조건을 그대로 가정합니다. 브로커가 TLS, 사용자명/비밀번호 인증을 요구하면 `main.py`의 MQTT 연결 설정을 추가해야 합니다.

## GitHub Actions로 APK 자동 빌드

이 배포본에는 `.github/workflows/build-apk.yml`이 포함되어 있습니다. GitHub 저장소에 업로드하면 Android APK를 자동 빌드할 수 있습니다. 자세한 순서는 `GITHUB_APK_BUILD.md`를 참고하세요.
