# AI2 Blocks → Kivy/Python 매핑

| App Inventor | Kivy/Python |
|---|---|
| Screen1.Initialize | `WaterControlApp.on_start()` |
| Button1.Click | `toggle_connection()` |
| Button2~5.Click | `motor_click(1~4)` |
| Clock3~6.Timer | `_single_motor_timeout(1~4)` |
| Button7.Click | `lock_click()` |
| Button8.Click | `autostop_click()` |
| Button9.Click | `reset_click()` |
| Button10~13.Click | `choose_device(2~5)` |
| CheckBox1~3.Changed | `select_broker(1~3)` |
| CheckBox4~5.Changed | `choose_autotime(15/25)` |
| UrsPahoMqttClient.MessageReceived | `handle_message()` |
| UrsPahoMqttClient.ConnectionStateChanged | `_handle_connection_state()` / `_on_mqtt_connect()` |
| procedure BUTTONCOLOR | `_buttoncolor()` |
| procedure LOCKON | `_lockon_after_device_change()` / `lock_click()` |
| procedure init | `_init_logic()` |
| procedure delay | Kivy `Clock.schedule_once(..., 2.0)` |

## 확인된 원본 특이점

1. Designer의 MQTT Broker 기본값은 `mqtt.eclipseprojects.io`이지만, Screen1.Initialize 블록에서 `broker.emqx.io`로 다시 설정합니다.
2. CheckBox1의 화면 표시는 `서버1`이고 초기 체크 상태이지만, CheckBox1.Changed 블록에서 선택 시 브로커를 `broker.hivemq.com`으로 설정합니다.
3. 숨김 Label7에는 `test.mosquittor.org`라는 오타 형태 문자열이 있지만 실제 CheckBox2 블록은 `test.mosquitto.org`를 사용합니다.
4. `kinfo` 수신 처리는 메시지 길이가 정확히 13일 때만 상태 7개를 적용합니다.
5. 원본 더블클릭 분기에서 버튼 색상 조건과 무관하게 결과적으로 `mcN=1`을 발행합니다.
