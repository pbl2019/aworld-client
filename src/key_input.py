from socket import socket, AF_INET, SOCK_DGRAM
import json

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.modules import keybinding

HOST = ''
PORT = 5000
ADDRESS = "127.0.0.1" # 自分に送信

s = socket(AF_INET, SOCK_DGRAM)

class MyKeyboardListener(Widget):

    def __init__(self, **kwargs):
        super(MyKeyboardListener, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.keycode = ""
        self.key_status = False

    # キーボード入力が終了した時
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    # キーボードを押した時
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keycode = keycode
        self.key_status = True
        # print('The key', keycode, 'have been pressed')
        # print(' - text is', text)

        # escapeが押されるとキー入力終了
        if keycode[1] == 'escape':
            keyboard.release()

        return True

    # キーボードを離した時
    def _on_keyboard_up(self, keyboard, keycode):
        self.keycode = keycode
        self.key_status = False
        return True

    def my_callback(self, dt):
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            d = {
                "characterId": "1",
                "buttonName": button_name,
                "status": self.key_status,
                "optional": "",
            }
            print(d)
            s.sendto(json.dumps(d).encode(), (ADDRESS, PORT))
            self.keycode = ""
        else:
            button_name = self.keycode

class GameApp(App):

    title = "key input test"

    def on_stop(self):
        s.close()
        return True

    def build(self):
        mykl = MyKeyboardListener()
        Clock.schedule_interval(mykl.my_callback, 0.01)
        return mykl

if __name__ == '__main__':
    GameApp().run()