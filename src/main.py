from aworld_client_core import Core

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
from kivy.core.text import Label

from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.lang import Builder
from kivy.config import Config
import japanize_kivy

import random
from map import Map
from constants import WINDOWSIZE

Config.set('graphics', 'width', WINDOWSIZE[0])
Config.set('graphics', 'height', WINDOWSIZE[1])

Builder.load_file('./main.kv')

core = Core()

class Player(Widget):

    def __init__(self):
        self.move_x = 0.
        self.move_y = 0.
        self.pos = 80*0, 80*0

    def move(self, addpos):
        self.pos = (addpos[0]+self.pos[0], addpos[1]+self.pos[1])
        # print("move:", addpos[0]/20*0.25, addpos[1]/20*0.25)

class TerrainLayer(Widget):

    def __init__(self, **kwargs):
        super(TerrainLayer, self).__init__(**kwargs)
        self.redraw()

    def redraw(self, msize=32):
        m = core.data.terrain
        # キャンバスのリセット
        self.canvas.clear()
        # マップの線画
        self.canvas.add(Color(0, 1, 0, .5))
        for i in range(m.row):
            for j in range(m.col):
                if m.map[i][j] == 0:
                    self.canvas.add(Rectangle(size=(msize, msize), pos=(msize*j, msize*i)))
        self.canvas.add(Color(0, 0, 1, .3))
        for i in range(m.row):
            for j in range(m.col):
                if m.map[i][j] == 1:
                    self.canvas.add(Rectangle(size=(msize, msize), pos=(msize*j, msize*i)))


class ObjectLayer(Widget):
    def __init__(self, **kwargs):
        super(ObjectLayer, self).__init__(**kwargs)
        self.redraw()

    def angle_pos(self, o, msize):
        radius = msize*0.4
        x = o["x"] * msize + radius * math.sin(o["angle"])
        y = o["y"] * msize + radius * math.cos(o["angle"])
        return x, y

    def redraw(self, msize=32):
        cid = core.data.character_id
        self.canvas.clear()

        for o in core.data.items.values():
            if o["is_dropped"]:
                self.canvas.add(Color(1,1,0,1))
                self.canvas.add(Ellipse(size=(msize, msize), pos=(o["x"]*msize-msize/2, o["y"]*msize-msize/2)))
        for key, o in core.data.characters.items():
            if o["is_dead"]:
                continue
            if key == cid:
                self.canvas.add(Color(1,1,1,1))
            else:
                self.canvas.add(Color(1,0,0,1))
            # キャラクターの線画
            self.canvas.add(Ellipse(size=(msize, msize), pos=(o["x"]*msize-msize/2, o["y"]*msize-msize/2)))
            # キャラクターアングルの線画
            self.canvas.add(Color(0,0,0,1))
            ap = self.angle_pos(o, msize)
            self.canvas.add(Ellipse(size=(msize*0.2, msize*0.2), pos=(ap[0]-msize*0.1, ap[1]-msize*0.1)))
        if cid and cid in core.data.characters:
            self.canvas.add(Color(1,1,1,1))
            # render item names
            for idx,item_id in enumerate(core.data.characters[cid]["items"]):
                label = Label(text=core.data.items[item_id]["name"], font_size=msize*2)
                label.refresh()
                self.canvas.add(Rectangle(size=label.texture.size, pos=(0, idx*msize*2), texture=label.texture))
            # render position
            label = Label(text="{}, {}, {}".format(core.data.characters[cid]["x"], core.data.characters[cid]["y"], core.data.characters[cid]["attack_charge"]), font_size=msize*2)
            label.refresh()
            self.canvas.add(Rectangle(size=label.texture.size, pos=(0, WINDOWSIZE[1]-msize*2), texture=label.texture))


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

        self.terrain = getattr(self.ids, "terrain")
        self.object_layer = getattr(self.ids, "objects")
        self.should_terrain_redraw = False
        self.should_objects_redraw = False
        self.msize = 32
        core.mutation_callback = self.mutation_callback

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

    def mutation_callback(self, mutations):
        if mutations.terrain:
            self.should_terrain_redraw = True
        if mutations.characters or mutations.items:
            self.should_objects_redraw = True

    def check_redraw(self, _dt):
        if self.should_terrain_redraw:
            if Window.width > Window.height:
                self.msize = Window.width / core.data.terrain.width
            else:
                self.msize = Window.height / core.data.terrain.height
            self.terrain.redraw(msize=self.msize)
            self.should_terrain_redraw = False
        if self.should_objects_redraw:
            self.object_layer.redraw(msize=self.msize)
            self.should_objects_redraw = False

    def update(self, _dt):
        if len(self.keycode) == 2:
            button_name = self.keycode[1]
            optional = {}
            if button_name == "up":
                optional["speed"] = 0.025
            elif button_name == "left":
                optional["angle"] = 0.01
            elif button_name == "right":
                optional["angle"] = 0.01
            elif button_name == "down":
                optional["speed"] = 0.005
            elif button_name == "i":
                optional["item_index"] = 0

            core.send_key(button_name, self.keystatus, optional)
            self.keycode = ""
        else:
            button_name = self.keycode


class GameApp(App):
    title = "Main screen"

    def on_stop(self):
        core.close_socket()
        return True

    def on_start(self):
        core.spawn_thread(secure=False)
        core.send_key("login")
        pass

    def build(self):
        ms = MainScreen()
        Clock.schedule_interval(ms.check_redraw, 1/60)
        Clock.schedule_interval(ms.update, 0.01)
        return ms


if __name__ == '__main__':
    GameApp().run()
