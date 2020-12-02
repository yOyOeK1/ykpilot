from Widget_cn import Widget_cn
from kivy.core.text import Label as textLabel

from kivy.graphics.opengl import *
from kivy.graphics import *

class Widget_cnValue(Widget_cn):
    def setGuiDoMore(self):
        self.textUtin = textLabel(
            text = self.munit,
            font_size = (self.gui.lineH)/self.subPix,
            #font_name='Segment7-4Gml.otf'
            #bold = "bold" 
            )
        self.textUtin.refresh() 
        
    def formatValue(self, v):
        return str(v)
        
    def drawItMore(self):
        PushMatrix()
        self.setColor("title")
        Translate(self.size[0]+(self.gui.lineH*.5),0,0)
        Rotate(90,0,0,1)
        Rectangle(
            size = [
                self.textUtin.texture.size[0]*.5*self.subPix,
                self.textUtin.texture.size[1]*.5*self.subPix
                ],
            pos = (0,0),
            texture = self.textUtin.texture
            )
        PopMatrix()