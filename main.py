from __future__ import annotations

import os
import time
from typing import Optional

import paho.mqtt.client as mqtt
from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout


GREEN = (0.0, 1.0, 0.0, 1.0)          # AI2 #00ff00
BRIGHT_GREEN = (0.2, 1.0, 0.2, 1.0)   # AI2 #33ff33
GRAY = (0.8, 0.8, 0.8, 1.0)           # AI2 #cccccc
DARK_GRAY = (0.533, 0.533, 0.533, 1.0) # AI2 #888888
RED = (1.0, 0.0, 0.0, 1.0)
YELLOW = (1.0, 1.0, 0.0, 1.0)
WHITE = (1.0, 1.0, 1.0, 1.0)


class RootView(BoxLayout):
    pass


class WaterControlApp(App):
    title = "Remote Control(V251217)"

    broker = StringProperty("broker.emqx.io")
    device_id = StringProperty("Kangyangkoo2")
    connection_status = StringProperty("Disconnected")
    message_log = StringProperty("서버가 변경되었습니다 ==> broker.emqx.io")
    connected = BooleanProperty(False)
    autotime = NumericProperty(1)

    # AI2 globals
    TIMMER = NumericProperty(0)
    clickCount = NumericProperty(0)
    delaytime = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client: Optional[mqtt.Client] = None
        self._motor_timer_events = {}
        self._clock2_event = None
        self.font_name = self._register_korean_font()

    def _register_korean_font(self) -> str:
        # Windows / Android / Linux에서 사용 가능한 한글 폰트를 자동 탐색합니다.
        # 폰트 파일을 프로젝트에 포함하지 않아도 Windows에서는 기본 '맑은 고딕'을 사용합니다.
        win_dir = os.environ.get("WINDIR", r"C:\Windows")
        candidates = [
            os.path.join(win_dir, "Fonts", "malgun.ttf"),       # 맑은 고딕
            os.path.join(win_dir, "Fonts", "malgunsl.ttf"),     # 맑은 고딕 Semilight
            os.path.join(win_dir, "Fonts", "gulim.ttc"),        # 굴림
            os.path.join(win_dir, "Fonts", "batang.ttc"),       # 바탕
            "/system/fonts/NotoSansCJK-Regular.ttc",
            "/system/fonts/NotoSansKR-Regular.otf",
            "/system/fonts/NotoSans-Regular.ttf",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    LabelBase.register(name="AppFont", fn_regular=path)
                    return "AppFont"
                except Exception:
                    pass
        return "Roboto"

    def build(self):
        Builder.load_file(os.path.join(os.path.dirname(__file__), "water340.kv"))
        return RootView()

    def on_start(self):
        # Screen1.Initialize 블록과 동일한 초기 상태
        self.connected = False
        self.connection_status = "Disconnected"
        self.TIMMER = 0
        self.clickCount = 0
        self.delaytime = 0
        self.autotime = 1
        self.broker = "broker.emqx.io"
        self.message_log = "서버가 변경되었습니다 ==> broker.emqx.io"
        Clock.schedule_once(lambda dt: self._sync_initial_ui(), 0)

    def on_stop(self):
        self.disconnect_mqtt()

    def _sync_initial_ui(self):
        r = self.root.ids
        r.server1.active = True
        r.server2.active = False
        r.server3.active = False
        r.auto15.active = True
        r.auto25.active = False
        r.connect_btn.background_color = RED
        r.connect_btn.text = "MQTT Connect."
        for i in range(1, 8):
            wid = r.get(f"state{i}")
            if wid is not None:
                wid.background_color = GRAY
        self._set_device_selector_colors(2)

    # ---------------- MQTT ----------------
    def connect_mqtt(self, clean_session: bool = True):
        if self.connected:
            return
        self.connection_status = f"Connecting: {self.broker}"
        try:
            # paho-mqtt 1.6.x API; clean_session corresponds to AI2 Connect(true)
            self.client = mqtt.Client(clean_session=clean_session)
            self.client.on_connect = self._on_mqtt_connect
            self.client.on_disconnect = self._on_mqtt_disconnect
            self.client.on_message = self._on_mqtt_message
            self.client.connect_async(self.broker, 1883, 60)
            self.client.loop_start()
        except Exception as exc:
            self.connected = False
            self.connection_status = f"Connect error: {exc}"
            Clock.schedule_once(lambda dt: self._set_connect_ui(False), 0)

    def disconnect_mqtt(self):
        client = self.client
        self.client = None
        if client is not None:
            try:
                client.disconnect()
            except Exception:
                pass
            try:
                client.loop_stop()
            except Exception:
                pass
        self.connected = False
        self.connection_status = "Disconnected"
        if self.root:
            self._set_connect_ui(False)

    def toggle_connection(self):
        # Button1.Click
        if not self.connected:
            self.connect_mqtt(True)
        else:
            self.disconnect_mqtt()

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        ok = (rc == 0)
        Clock.schedule_once(lambda dt: self._handle_connection_state(ok, rc), 0)
        if ok:
            client.subscribe(f"out{self.device_id}/kinfo", qos=0)
            client.subscribe(f"out{self.device_id}/ktemp", qos=1)

    def _on_mqtt_disconnect(self, client, userdata, rc):
        Clock.schedule_once(lambda dt: self._handle_connection_state(False, rc), 0)

    def _on_mqtt_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8", errors="replace")
        except Exception:
            payload = str(msg.payload)
        Clock.schedule_once(lambda dt: self.handle_message(msg.topic, payload), 0)

    def _handle_connection_state(self, is_connected: bool, rc):
        self.connected = is_connected
        self.connection_status = "Connected" if is_connected else "Disconnected"
        self._set_connect_ui(is_connected)

    def _set_connect_ui(self, is_connected: bool):
        if not self.root:
            return
        btn = self.root.ids.connect_btn
        btn.background_color = GREEN if is_connected else RED
        btn.text = "MQTT Disconnect." if is_connected else "MQTT Connect."

    def publish(self, suffix: str, value) -> bool:
        if not self.connected or self.client is None:
            self.message_log = "MQTT가 연결되어 있지 않습니다."
            return False
        topic = f"in{self.device_id}/{suffix}"
        try:
            info = self.client.publish(topic, str(value))
            if info.rc != mqtt.MQTT_ERR_SUCCESS:
                self.message_log = f"Publish error rc={info.rc}: {topic}"
                return False
            return True
        except Exception as exc:
            self.message_log = f"Publish error: {exc}"
            return False

    # ---------------- Incoming data ----------------
    def handle_message(self, topic: str, message: str):
        # UrsPahoMqttClient1.MessageReceived
        if topic == f"out{self.device_id}/kinfo":
            # 원본 AI2는 message length == 13일 때만 7개 상태를 적용한다.
            if len(message) == 13:
                data = message.split(",")
                if len(data) >= 7:
                    for idx in range(1, 8):
                        self._set_state_color(idx, GREEN if data[idx - 1] == "0" else GRAY)
            return
        self.message_log = message

    def _set_state_color(self, idx: int, color):
        wid = self.root.ids.get(f"state{idx}")
        if wid is not None:
            wid.background_color = color

    def _is_green(self, idx: int) -> bool:
        wid = self.root.ids.get(f"state{idx}")
        if wid is None:
            return False
        c = tuple(round(x, 3) for x in wid.background_color)
        g = tuple(round(x, 3) for x in GREEN)
        return c == g

    # ---------------- Motor buttons ----------------
    def motor_click(self, motor_index: int):
        """Button2~5.Click.

        Intended AI2 behaviour is preserved:
        - 1 click: wait 1 second, then toggle based on last received status color.
        - 2 clicks within 1 second: always publish value 1.
        """
        self.clickCount += 1

        if self.clickCount == 1:
            ev = Clock.schedule_once(
                lambda dt, i=motor_index: self._single_motor_timeout(i), 1.0
            )
            self._motor_timer_events[motor_index] = ev
            return

        if self.clickCount == 2:
            ev = self._motor_timer_events.pop(motor_index, None)
            if ev is not None:
                ev.cancel()
            if self.connected:
                self.publish(f"mc{motor_index}", 1)
            self.clickCount = 0

    def _single_motor_timeout(self, motor_index: int):
        self._motor_timer_events.pop(motor_index, None)
        if self.connected:
            # AI2 Clock3~6: green -> 0, otherwise -> 1
            value = 0 if self._is_green(motor_index) else 1
            self.publish(f"mc{motor_index}", value)
        self.clickCount = 0

    # ---------------- Lock / Auto stop / Reset ----------------
    def lock_click(self):
        if self.connected:
            self.publish("mc_lock", 0 if self._is_green(6) else 1)

    def autostop_click(self):
        if not self.connected or not self._is_green(6):
            return
        btn = self.root.ids.state7
        # AI2 Button8.Click compares against #cccccc.
        if tuple(round(x, 3) for x in btn.background_color) == tuple(round(x, 3) for x in GRAY):
            btn.background_color = BRIGHT_GREEN
            self.publish("autostop", int(self.autotime))
        else:
            btn.background_color = GRAY
            self.publish("autostop", 0)

    def reset_click(self):
        if self.connected:
            self.publish("kreset2", 1)

    def choose_autotime(self, minutes: int):
        r = self.root.ids
        if minutes == 15:
            r.auto15.active = True
            r.auto25.active = False
            self.autotime = 1
        else:
            r.auto15.active = False
            r.auto25.active = True
            self.autotime = 2

    # ---------------- Broker selection ----------------
    def select_broker(self, which: int):
        r = self.root.ids
        if which == 1:
            r.server1.active, r.server2.active, r.server3.active = True, False, False
            # CheckBox1.Changed in the original blocks uses broker.hivemq.com
            self.broker = "broker.hivemq.com"
        elif which == 2:
            r.server1.active, r.server2.active, r.server3.active = False, True, False
            self.broker = "test.mosquitto.org"
        else:
            r.server1.active, r.server2.active, r.server3.active = False, False, True
            self.broker = "broker.emqx.io"
        self.message_log = f"서버가 변경되었습니다 ==> {self.broker}"

    # ---------------- V2~V5 device selection ----------------
    def choose_device(self, number: int):
        # Button10~13.Click + init + BUTTONCOLOR + delay + LOCKON
        self._init_logic()
        self._set_device_selector_colors(number)
        self.device_id = f"Kangyangkoo{number}"

        if self.connected:
            self.disconnect_mqtt()

        self._buttoncolor()
        self.connect_mqtt(True)

        # Original delay procedure busy-waits for 2 sec. Kivy must not block UI.
        Clock.schedule_once(lambda dt: self._lockon_after_device_change(), 2.0)

    def _init_logic(self):
        if self._clock2_event is not None:
            self._clock2_event.cancel()
            self._clock2_event = None

    def _buttoncolor(self):
        # Original BUTTONCOLOR sets Button2~7 gray.
        for idx in range(1, 7):
            self._set_state_color(idx, GRAY)

    def _lockon_after_device_change(self):
        if self.connected:
            self.publish("mc_lock", 0 if self._is_green(6) else 1)

    def _set_device_selector_colors(self, number: int):
        r = self.root.ids
        for n in range(2, 6):
            btn = r.get(f"v{n}")
            if btn is not None:
                # V2 original uses #00ff00; V3-V5 use #33ff33 when selected.
                btn.background_color = (GREEN if n == 2 else BRIGHT_GREEN) if n == number else GRAY


if __name__ == "__main__":
    WaterControlApp().run()
