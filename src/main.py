from game_client.tools import GameClient

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

gc = GameClient()

gc.set_port(34255, 34253)
gc.set_address("127.0.0.1")

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
        m = gc.objects["terrain"]
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
        radius = gc.objects["terrain"].msize*0.4
        x = o["x"] + radius * math.sin(o["angle"])
        y = o["y"] + radius * math.cos(o["angle"])
        return x, y

    def redraw(self):
        m = gc.objects["terrain"]
        self.canvas.clear()
        # アングルマーカーの位置
        for o in gc.objects["characters"].values():
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

        self.m = gc.objects["terrain"]
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
        if gc.should_terrain_redraw:
            self.terrain.redraw()
            gc.should_terrain_redraw = False
        if gc.should_objects_redraw:
            self.object_layer.redraw()
            gc.should_objects_redraw = False

    def other_update(self, dt):
        action = ["wait", "up", "left", "right"]
        a = random.choice(action)
        # print(a)
        pass

    def update(self, dt):
        m = gc.objects["terrain"]
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

            gc.send_key_message(SALT, 'unused', button_name, self.keystatus, optional)
            self.keycode = ""
        else:
            button_name = self.keycode

class GameApp(App):

    title = "Main screen"

    def on_stop(self):
        gc.game_client_close()
        return True

    def on_start(self):
        receive_udp_thread = threading.Thread(target=receive_udp, daemon=True)
        receive_udp_thread.start()
        gc.send_key_message(SALT, 'unused', "login", True, {})
        pass

    def build(self):
        ms = MainScreen()
        Clock.schedule_interval(ms.check_redraw, 1/60)
        Clock.schedule_interval(ms.update, 0.01)
        Clock.schedule_interval(ms.other_update, 100.)
        return ms

def receive_udp():
    while True:
        # 受信
        print(gc.recieve())

if __name__ == '__main__':
    GameApp().run()
