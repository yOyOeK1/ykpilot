# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
#from OpenGL.GL import *
from kivy.app import App
from Screen3dtextures import Screen3dtextures
from kivy.uix.boxlayout import BoxLayout


class KTApp(App):
    def build_mesh(self):
        return self
    
    def build(self):
        s = Screen3dtextures()
        bl = BoxLayout()
        bl.add_widget(s.l)
        
        return bl


if __name__ == "__main__":
    KTApp().run()


