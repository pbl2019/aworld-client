# coding:utf-8

from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from itertools import cycle
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_file('./main.kv')

class Root(BoxLayout):pass
class ControlPad(BoxLayout):pass
class Game(RelativeLayout):pass
class Character(Image):pass

class GameApp(App):
    # def __init__(self, **kwargs):
    #     self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
    #     self._keyboard.bind(on_key_down=self._on_keyboard_down)

    # def _keyboard_closed(self):
    #     self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    #     self._keyboard = None

    # def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    #     pass
    #     if keycode[1] == 'w':
    #         self.player1.center_y += 10
    #     elif keycode[1] == 's':
    #         self.player1.center_y -= 10
    #     elif keycode[1] == 'up':
    #         self.player2.center_y += 10
    #     elif keycode[1] == 'down':
    #         self.player2.center_y -= 10
    #     return True

    def cycle(self, iter=cycle(list('0123'))):
        it = next(iter)
        print(it)
        return it

    def reload(self, anim, ch, progress):
        ch.source = 'atlas://chara/{}{}'.format(ch.drct,self.cycle())
        ch.reload()

    def clear(self, anim, ch):
        self.moving = False

    def move(self, drct, *args):
        if self.moving:
            return False
        self.moving = True
        # キャラクターを移動
        self.anim = Animation(
            d=2./3., s=1./4., t='linear',
            x=self.ch.x+(drct=='E')*192-(drct=='W')*192,
            y=self.ch.y+(drct=='N')*256-(drct=='S')*256)
        self.ch.drct = drct
        # キャラクターのアニメーション
        self.anim.bind(on_progress=self.reload)
        self.anim.bind(on_complete=self.clear)
        self.anim.start(self.ch)
        return False

    def build(self):
        root = Root()
        self.moving = False
        self.ch = Character()
        self.ch.pos = (256*2, 192*2)
        # self.ch.drct = 'S'
        root.game.add_widget(self.ch)
        return root

if __name__ == '__main__':
    GameApp().run()
