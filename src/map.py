import random
from kivy.core.window import Window
# マップのクラス
class Map:

    def __init__(self, width=20, height=15, data=None):
        if data == None:
            self.map = [[random.randint(0, 1) for _ in range(width)] for _ in range(height)]
        else:
            self.map = [data[idx:idx + width] for idx in range(0,len(data), width)]
        self.row = self.height = height
        self.col = self.width = width
        # マップチップ
        self.imgs = [None] * 256
        # 1マスの大きさ[px]
        if Window.width > Window.height:
            self.msize = Window.width / width
        else:
            self.msize = Window.height / height
