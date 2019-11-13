from socket import socket, AF_INET, SOCK_DGRAM
import json
import threading
import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.modules import keybinding
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.animation import Animation

from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.lang import Builder

import random

# Builder.load_file('./main.kv')
SALT = int(round(time.time() * 1000))
HOST = ''
PORT = 34255
ADDRESS = "127.0.0.1" # 自分に送信

s = socket(AF_INET, SOCK_DGRAM)

objects = {
    "character_id": "",
    "terrain": [],
    "characters": []
    }

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

    def __init__(self):
        self.move_x = 2.
        self.move_y = 1.
        self.pos = 80*2, 80*1

    def move(self, addpos):
        self.pos = (addpos[0]+self.pos[0], addpos[1]+self.pos[1])
        # print("move:", addpos[0]/20*0.25, addpos[1]/20*0.25)

# プレイヤーの向いている方向
class PlayerAngle(Widget):

    def __init__(self):
        self.pos = [80*2+30, 80*1+70]
        self.size = 20, 20

    def angle_change(self, player_pos, angle_name):
        # 上を向く
        if angle_name == "up":
            self.pos[0] = player_pos[0] + 30 + 0*2
            self.pos[1] = player_pos[1] + 30 + 20*2
        # 下を向く
        elif angle_name == "down":
            self.pos[0] = player_pos[0] + 30 + 0*2
            self.pos[1] = player_pos[1] + 30 + -20*2
        # 左を向く
        elif angle_name == "left":
            self.pos[0] = player_pos[0] + 30 + -20*2
            self.pos[1] = player_pos[1] + 30 + 0*2
        # 右を向く
        elif angle_name == "right":
            self.pos[0] = player_pos[0] + 30 + 20*2
            self.pos[1] = player_pos[1] + 30 + 0*2

class MainScreen(Widget):
    # pa = ObjectProperty(None)

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
        self.player = Player()
        self.player_angle = PlayerAngle()
        # マップの線画
        for i in range(self.m.row):
            for j in range(self.m.col):
                if self.m.map[i][j] == 0:
                    self.canvas.add(Color(0, 1, 0, .5))
                elif self.m.map[i][j] == 1:
                    self.canvas.add(Color(0, 0, 1, .3))
                self.canvas.add(Rectangle(size=(self.m.msize, self.m.msize), pos=(self.m.msize*j, self.m.msize*(self.m.row-i-1))))
        # キャラクターの線画
        self.canvas.add(Color(1,1,1,1))
        self.canvas.add(Ellipse(size=(self.m.msize, self.m.msize), pos=self.player.pos))
        # キャラクターアングルの線画
        self.canvas.add(Color(1,0,0,1))
        self.canvas.add(Rectangle(size=(self.player_angle.size[0], self.player_angle.size[1]), pos=self.player_angle.pos))

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

    def other_update(self, dt):
        action = ["wait", "up", "left", "right"]
        a = random.choice(action)
        # print(a)
        pass

    def update(self, dt):
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            y = self.player.move_y
            x = self.player.move_x

            move_total = [0, 0]

            # upキーが押された時
            if self.keystatus and button_name == "up":
                if self.m.map[-(int(y//1)+2)][int(x//1)] == 0 and self.m.map[-(int(y//1)+2)][int((x+0.75)//1)] == 0:
                    self.player.move_y += .25
                    move_total[1] += self.move_pexel

            # downキーが押された時
            if self.keystatus and button_name == "down":
                if self.m.map[-int((y+0.75)//1)][int(x//1)] == 0 and self.m.map[-int((y+0.75)//1)][int((x+0.75)//1)] == 0:
                    self.player.move_y -= .25
                    move_total[1] -= self.move_pexel
            
            # rightキーが押された時
            if self.keystatus and button_name == "right":
                if self.m.map[-int(y)-1][int(x//1)+1] == 0 and self.m.map[-int(y+0.75)-1][int(x//1)+1] == 0:
                    self.player.move_x += .25
                    move_total[0] += self.move_pexel

            # leftキーが押された時
            if self.keystatus and button_name == "left":                
                if self.m.map[-int(y)-1][int((x+0.75)//1)-1] == 0 and self.m.map[-int(y+0.75)-1][int((x+0.75)//1)-1] == 0:
                    self.player.move_x -= .25
                    move_total[0] -= self.move_pexel

            # プレイヤーの移動処理
            if self.keystatus:
                self.player.move(move_total)
                self.player_angle.angle_change(self.player.pos, self.keycode[1])

                # 線画後状態のモック
                # drow = {
                #     "character_id": "1",
                #     "terrain": {
                #         "start": {"x": 2, "y": 1},
                #         "data": self.m.map,
                #     },
                #     "characters": [
                #         {
                #         "character_id": "1",
                #         "x": self.player.pos[0],
                #         "y": self.player.pos[1],
                #         },
                #         {
                #         "character_id": "2",
                #         "x": self.player.pos[0]+80*5,
                #         "y": self.player.pos[1]+80*3,
                #         },
                #     ]
                # }
                # s.sendto(json.dumps(drow).encode(), (ADDRESS, PORT))

            # キャンバスのリセット
            self.canvas.clear()
            # マップの線画
            for i in range(self.m.row):
                for j in range(self.m.col):
                    if self.m.map[i][j] == 0:
                        self.canvas.add(Color(0, 1, 0, .5))
                    else:
                        self.canvas.add(Color(0, 0, 1, .3))
                    self.canvas.add(Rectangle(size=(self.m.msize, self.m.msize), pos=(self.m.msize*j, self.m.msize*(self.m.row-i-1))))
            # キャラクターの線画
            for o in objects["characters"]:
                self.canvas.add(Color(1,1,1,1))
                # self.canvas.add(Ellipse(size=(self.m.msize, self.m.msize), pos=self.player.pos))
                self.canvas.add(Ellipse(size=(self.m.msize, self.m.msize), pos=(o["x"], o["y"])))
            # キャラクターアングルの線画
            self.canvas.add(Color(1,0,0,1))
            self.canvas.add(Rectangle(size=(self.player_angle.size[0], self.player_angle.size[1]), pos=self.player_angle.pos))

            # プレイヤー位置確認用
            # if self.keystatus == False:
            #     print("x:", self.player.move_x)
            #     print("y:", self.player.move_y)
            #     print("player:", y, x)
            #     print()

            optional = {}
            if button_name == "up":
                optional["speed"] = 1.0
            elif button_name == "left":
                optional["angle"] = 0.01
            elif button_name == "right":
                optional["angle"] = 0.01
            elif button_name == "down":
                optional["speed"] = 0.5
            input_key_message = {
                "salt": SALT,
                "character_id": "unused",
                "button_name": button_name,
                "status": self.keystatus,
                "optional": optional,
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
        #s.bind((HOST, PORT))
        receive_udp_thread = threading.Thread(target=receive_udp, daemon=True)
        receive_udp_thread.start()
        login_message = {
                "salt": SALT,
                "character_id": "unused",
                "button_name": "login",
                "status": True,
                "optional": {},
            }
        s.sendto(json.dumps(login_message).encode(), (ADDRESS, PORT))
        pass

    def build(self):
        ms = MainScreen()
        Clock.schedule_interval(ms.update, 0.01)
        Clock.schedule_interval(ms.other_update, 100.)
        return ms

def receive_udp():
    while True:
        # 受信
        msg, address = s.recvfrom(34253)
        # print("message: {}\nfrom: {}".format(msg, address))
        # print("address:", address)
        game_data = json.loads(msg.decode('utf-8'))
        if "character_id" in game_data.keys():
            objects["character_id"] = game_data["character_id"]
        if "characters" in game_data.keys():
            objects["characters"] = game_data["characters"]
        if "terrain" in game_data.keys():
            objects["terrain"] = game_data["terrain"]

if __name__ == '__main__':
    GameApp().run()
