from socket import socket, AF_INET, SOCK_DGRAM
import json
import threading

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.modules import keybinding
from kivy.graphics import Color, Rectangle

HOST = ''
PORT = 5000
ADDRESS = "127.0.0.1" # 自分に送信

s = socket(AF_INET, SOCK_DGRAM)

# マップのクラス
class Map:

    def __init__(self):
        # マップデータ
        self.map = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,0,0,1],
                    [1,0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,0,1],
                    [1,0,0,1,1,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1],
                    [1,1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
                    [1,1,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,1],
                    [1,1,0,0,0,0,1,1,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,0,0,1,0,0,1,1,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,0,0,1,0,0,1,1,0,1,1,0,0,1,1,1,0,0,0,1],
                    [1,0,0,1,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,1],
                    [1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1],
                    [1,0,0,0,1,0,0,1,0,1,1,0,0,0,0,0,0,1,0,1],
                    [1,0,0,0,1,0,1,1,0,0,1,0,1,0,1,1,1,1,1,1],
                    [1,0,0,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
        self.row, self.col = len(self.map), len(self.map[0]) # マップの行数,列数を取得
        self.imgs = [None] * 256             # マップチップ
        self.msize = 80                      # 1マスの大きさ[px]

class MainScreen(Widget):


    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.keycode = ""
        self.keystatus = False

        self.m = Map()
        # マップの線画
        for i in range(self.m.row):
            for j in range(self.m.col):
                if self.m.map[i][j] == 0:
                    self.canvas.add(Color(0, 1, 0, .7))
                else:
                    self.canvas.add(Color(0, 0, 1, .5))
                self.canvas.add(Rectangle(size=(self.m.msize, self.m.msize), pos=(self.m.msize*j, self.m.msize*(self.m.row-i-1))))

    # キーボード入力が終了した時
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    # キーボードを押した時
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keycode = keycode
        self.keystatus = True
        # print('The key', keycode, 'have been pressed')
        # print(' - text is', text)

        # escapeが押されるとキー入力終了
        if keycode[1] == 'escape':
            keyboard.release()

        return True

    # キーボードを離した時
    def _on_keyboard_up(self, keyboard, keycode):
        self.keycode = keycode
        self.keystatus = False
        return True

    def my_callback(self, dt):
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            d = {
                "characterId": "1",
                "buttonName": button_name,
                "status": self.keystatus,
                "optional": "",
            }
            # print(d)
            s.sendto(json.dumps(d).encode(), (ADDRESS, PORT))
            self.keycode = ""
        else:
            button_name = self.keycode

class GameApp(App):

    title = "key input test"

    def on_stop(self):
        s.close()
        return True

    def on_start(self):
        # バインド
        s.bind((HOST, PORT))
        receive_udp_thread = threading.Thread(target=receive_udp, daemon=True)
        receive_udp_thread.start()
        pass

    def build(self):
        ms = MainScreen()
        Clock.schedule_interval(ms.my_callback, 0.01)
        return ms

def receive_udp():
    while True:
        # 受信
        msg, address = s.recvfrom(8192)
        print("message: {}\nfrom: {}".format(msg, address))

if __name__ == '__main__':
    GameApp().run()