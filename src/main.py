from socket import socket, AF_INET, SOCK_DGRAM
import json
import threading

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.modules import keybinding
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.animation import Animation

from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.lang import Builder


Builder.load_file('./main.kv')

HOST = ''
PORT = 5000
ADDRESS = "127.0.0.1" # 自分に送信

s = socket(AF_INET, SOCK_DGRAM)

# マップのクラス
class Map:

    def __init__(self):
        # マップデータ
        self.map = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    [1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                    [1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1],
                    [1,0,0,1,0,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1],
                    [1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,1],
                    [1,1,0,0,0,0,1,0,0,0,1,0,0,0,1,1,0,0,0,1],
                    [1,1,0,0,0,0,1,1,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,0,0,1,0,0,1,1,0,1,0,0,0,0,0,1,0,0,0,1],
                    [1,0,0,1,0,0,1,1,0,1,1,0,0,1,1,1,0,0,0,1],
                    [1,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,1],
                    [1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1],
                    [1,0,0,0,1,0,0,1,0,1,1,0,0,0,0,0,0,1,0,1],
                    [1,1,1,0,1,0,1,1,0,0,1,0,1,0,1,1,1,1,1,1],
                    [1,0,0,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]]
        # マップの行数,列数を取得
        self.row, self.col = len(self.map), len(self.map[0])
        # マップチップ
        self.imgs = [None] * 256
        # 1マスの大きさ[px]
        self.msize = 80

class Player(Widget):

    move_x = NumericProperty(2)
    move_y = NumericProperty(1)

    def move(self, addpos):
        self.pos = (addpos[0]+self.pos[0], addpos[1]+self.pos[1])
        # print(addpos[0]/20*0.25, addpos[1]/20*0.25)

# プレイヤーの向いている方向
class PlayerAngle(Widget):

    def angle_change(self, player_pos, angle):
        if angle[0]!=0 or angle[1]!=0:
            self.pos[0] = player_pos[0] + 30 + angle[0]*2
            self.pos[1] = player_pos[1] + 30 + angle[1]*2

class MainScreen(Widget):
    p = ObjectProperty(None)
    pa = ObjectProperty(None)

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

        # マップの線画
        self.m = Map()
        for i in range(self.m.row):
            for j in range(self.m.col):
                if self.m.map[i][j] == 0:
                    self.canvas.add(Color(0, 1, 0, .5))
                else:
                    self.canvas.add(Color(0, 0, 1, .3))
                self.canvas.add(Rectangle(size=(self.m.msize, self.m.msize), pos=(self.m.msize*j, self.m.msize*(self.m.row-i-1))))

        # プレイヤー移動pexel
        self.move_pexel = self.m.msize/4

    # キーボード入力が終了した時
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    # キーボードを押した時
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        self.keycode = keycode
        self.keystatus = True

        # escapeが押されるとキー入力終了
        if keycode[1] == 'escape':
            keyboard.release()

        return True

    # キーボードを離した時
    def _on_keyboard_up(self, keyboard, keycode):
        self.keycode = keycode
        self.keystatus = False
        return True

    def update(self):
        pass

    def my_callback(self, dt):
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            y = self.p.move_y
            x = self.p.move_x

            move_total = [0, 0]

            # upキーが押された時
            if self.keystatus and button_name == "up":
                if self.m.map[-(int(y//1)+2)][int(x//1)] == 0 and self.m.map[-(int(y//1)+2)][int((x+0.75)//1)] == 0:
                    self.p.move_y += .25
                    move_total[1] += self.move_pexel

            # downキーが押された時
            if self.keystatus and button_name == "down":
                if self.m.map[-int((y+0.75)//1)][int(x//1)] == 0 and self.m.map[-int((y+0.75)//1)][int((x+0.75)//1)] == 0:
                    self.p.move_y -= .25
                    move_total[1] -= self.move_pexel
            
            # rightキーが押された時
            if self.keystatus and button_name == "right":
                if self.m.map[-int(y)-1][int(x//1)+1] == 0 and self.m.map[-int(y+0.75)-1][int(x//1)+1] == 0:
                    self.p.move_x += .25
                    move_total[0] += self.move_pexel

            # leftキーが押された時
            if self.keystatus and button_name == "left":                
                if self.m.map[-int(y)-1][int((x+0.75)//1)-1] == 0 and self.m.map[-int(y+0.75)-1][int((x+0.75)//1)-1] == 0:
                    self.p.move_x -= .25
                    move_total[0] -= self.move_pexel

            # プレイヤーの移動処理
            if self.keystatus:
                self.p.move(move_total)
                self.pa.angle_change(self.p.pos, move_total)

            # プレイヤー位置確認用
            # if self.keystatus == False:
            #     print("x:", self.p.move_x)
            #     print("y:", self.p.move_y)
            #     print("player:", y, x)
            #     print()

            input_key_message = {
                "characterId": "1",
                "buttonName": button_name,
                "status": self.keystatus,
                "optional": "",
            }
            s.sendto(json.dumps(input_key_message).encode(), (ADDRESS, PORT))
            self.keycode = ""
        else:
            button_name = self.keycode

class GameApp(App):

    title = "Main screen"

    def on_stop(self):
        s.close()
        return True

    def on_start(self):
        # バインド
        s.bind((HOST, PORT))
        receive_udp_thread = threading.Thread(target=receive_udp, daemon=True)
        receive_udp_thread.start()
        login_message = {
                "characterId": "",
                "buttonName": "login",
                "status": False,
                "optional": {"id": "1", "password": "1234567890"},
            }
        s.sendto(json.dumps(login_message).encode(), (ADDRESS, PORT))
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