# coding:utf-8

from kivy.app import App
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from itertools import cycle

from kivy.lang import Builder

Builder.load_file('./main.kv')

class Root(BoxLayout):pass
class ControlPad(BoxLayout):pass
class Game(RelativeLayout):pass
class Character(Image):pass

class GameApp(App):

    def cycle(self, iter=cycle(list('0123'))):
        return iter.next()

    def reload(self, anim, ch, progress):
        ch.source = 'atlas://chara/%s%s' % (ch.drct,self.cycle())
        ch.reload()

    def clear(self, anim, ch):
        self.moving = False

    def move(self, drct, *args):
        if self.moving:
            return False
        self.moving = True
        self.anim = Animation(
            d=1./1., s=1./8., t='linear',
            x=self.ch.x+(drct=='E')*192-(drct=='W')*192,
            y=self.ch.y+(drct=='N')*256-(drct=='S')*256)
        self.ch.drct = drct
        self.anim.bind(on_progress=self.reload)
        self.anim.bind(on_complete=self.clear)
        self.anim.start(self.ch)
        return False

    def on_touch_down(self, touch):
        print(touch)

    def build(self):
        root = Root()
        self.moving = False
        self.ch = Character()
        self.ch.pos = (0, 0)
        self.ch.drct = 'S'
        root.game.add_widget(self.ch)
        return root

if __name__ == '__main__':
    GameApp().run()
