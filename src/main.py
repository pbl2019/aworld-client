# coding:utf-8

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# 画面の見た目や機能を構成するクラス
class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        btn = Button(text="hello")
        self.add_widget(btn)

# アプリを構成するクラス
class MainApp(App):
    def build(self):
        MS = MainScreen()
        return MS
    
    # アプリ起動時
    def on_start(self):
        print("App Start!!")

    # アプリ終了時
    def on_stop(self):
        print("App End!!")

if __name__=="__main__":
    MainApp().run()
