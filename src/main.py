from socket import socket, AF_INET, SOCK_DGRAM
import json
import math
import threading
import time

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.modules import keybinding
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.animation import Animation

from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.lang import Builder
from kivy.config import Config

import random
from map import Map
from constants import WINDOWSIZE

Config.set('graphics', 'width', WINDOWSIZE[0])
Config.set('graphics', 'height', WINDOWSIZE[1])

Builder.load_file('./main.kv')
SALT = int(round(time.time() * 1000))
HOST = ''
PORT = 34255
ADDRESS = "127.0.0.1" # 自分に送信

s = socket(AF_INET, SOCK_DGRAM)

objects = {
    "character_id": "",
    "terrain": Map(),
    "characters": {},
    "items": {},
    }
should_terrain_redraw = False
should_objects_redraw = False


class Player(Widget):

    def __init__(self):
        self.move_x = 0.
        self.move_y = 0.
        self.pos = 80*0, 80*0

    def move(self, addpos):
        self.pos = (addpos[0]+self.pos[0], addpos[1]+self.pos[1])
        # print("move:", addpos[0]/20*0.25, addpos[1]/20*0.25)

class Terrain(Widget):

    def __init__(self, **kwargs):
        super(Terrain, self).__init__(**kwargs)
        self.redraw()

    def redraw(self):
        m = objects["terrain"]
        # キャンバスのリセット
        self.canvas.clear()
        # マップの線画
        self.canvas.add(Color(0, 1, 0, .5))
        for i in range(m.row):
            for j in range(m.col):
                if m.map[i][j] == 0:
                    self.canvas.add(Rectangle(size=(m.msize, m.msize), pos=(m.msize*j, Window.height-m.msize*(m.row-i-1))))
        self.canvas.add(Color(0, 0, 1, .3))
        for i in range(m.row):
            for j in range(m.col):
                if m.map[i][j] == 1:
                    self.canvas.add(Rectangle(size=(m.msize, m.msize), pos=(m.msize*j, Window.height-m.msize*(m.row-i-1))))

class ObjectLayer(Widget):

    def __init__(self, **kwargs):
        super(ObjectLayer, self).__init__(**kwargs)
        self.redraw()

    def angle_pos(self, o):
        radius = objects["terrain"].msize*0.4
        x = o["x"] + radius * math.sin(o["angle"])
        y = o["y"] + radius * math.cos(o["angle"])
        return x, y

    def redraw(self):
        m = objects["terrain"]
        self.canvas.clear()
        for o in objects["items"].values():
            if o["is_dropped"]:
                self.canvas.add(Color(1,1,0,1))
                self.canvas.add(Ellipse(size=(m.msize, m.msize), pos=(o["x"]-m.msize/2, o["y"]-m.msize/2)))
        for o in objects["characters"].values():
            # キャラクターの線画
            self.canvas.add(Color(1,1,1,1))
            self.canvas.add(Ellipse(size=(m.msize, m.msize), pos=(o["x"]-m.msize/2, o["y"]-m.msize/2)))
            # キャラクターアングルの線画
            self.canvas.add(Color(1,0,0,1))
            ap = self.angle_pos(o)
            self.canvas.add(Ellipse(size=(m.msize*0.2, m.msize*0.2), pos=(ap[0]-m.msize*0.1, ap[1]-m.msize*0.1)))

class MainScreen(FloatLayout):

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

        self.m = objects["terrain"]
        self.player = Player()
        self.terrain = getattr(self.ids, "terrain")
        self.object_layer = getattr(self.ids, "objects")

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

    def check_redraw(self, dt):
        global should_terrain_redraw, should_objects_redraw
        if should_terrain_redraw:
            self.terrain.redraw()
            should_terrain_redraw = False
        if should_objects_redraw:
            self.object_layer.redraw()
            should_objects_redraw = False

    def other_update(self, dt):
        action = ["wait", "up", "left", "right"]
        a = random.choice(action)
        # print(a)
        pass

    def update(self, dt):
        m = objects["terrain"]
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            optional = {}
            if button_name == "up":
                optional["speed"] = 0.25
            elif button_name == "left":
                optional["angle"] = 0.01
            elif button_name == "right":
                optional["angle"] = 0.01
            elif button_name == "down":
                optional["speed"] = 0.1

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
        Clock.schedule_interval(ms.check_redraw, 1/60)
        Clock.schedule_interval(ms.update, 0.01)
        Clock.schedule_interval(ms.other_update, 100.)
        return ms

def receive_udp():
    global should_terrain_redraw, should_objects_redraw
    while True:
        # 受信
        msg, address = s.recvfrom(34253)
        # print("address:", address)
        game_data = json.loads(msg.decode('utf-8'))
        if "character_id" in game_data.keys():
            objects["character_id"] = game_data["character_id"]
        if "characters" in game_data.keys():
            should_objects_redraw = True
            for character in game_data["characters"]:
                objects["characters"][character["character_id"]] = character
        if "terrain" in game_data.keys() and game_data["terrain"]:
            terrain = game_data["terrain"]
            width = terrain["width"]
            height = terrain["height"]
            ox = terrain["origin"]["x"]
            oy = terrain["origin"]["y"]
            data = terrain["data"]
            if width != objects["terrain"].width or height != objects["terrain"].height:
                print("Overwrite terrain")
                objects["terrain"] = Map(width=width, height=height, data=data)
                should_terrain_redraw = True
            else:
                pass
        if "items" in game_data.keys():
            should_objects_redraw = True
            for item in game_data["items"]:
                objects["items"][item["item_id"]] = item

if __name__ == '__main__':
    GameApp().run()
