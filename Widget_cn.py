
from kivy.uix.widget import Widget
from kivy.core.text import Label as textLabel
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.properties import ObjectProperty
import sys
import math

class WidgetProto(Widget):
    
    inEditMode = False
    
    
    def on_touch_down(self, touch):
        print( "on_touch_down" )
        if self.collide_point( *touch.pos):
            #touch.grab(self)
            print("collide")
            self.inEditMode = True
            #return True
        else:
            self.inEditMode = False
            
            
class Widget_cn(WidgetProto):
    
    pos = ObjectProperty(None)
    size = ObjectProperty(None)
    scale = ObjectProperty(None)
    rotation = ObjectProperty(None)
    size_hint = None, None
    
    
    def __init__(self, **kwargs):
        super(Widget_cn, self).__init__(**kwargs)
        
        self.drawItC = 0
        
        self.pos = [0,0]
        self.size = [0,0]
        self.scale = 1.0
        self.rotation = 0.0
        #self.bind(x=self.bin,y=self.bin)
        #self.bind(pos=self.bin)
        #self.bind(size=self.binS)
    
    def bin(self,a='',b=''):
        print("bin a:[",a,"] b[",b,"]")    
    
    def binS(self,a='',b=''):
        print("binS [",self.mtitle,"] a:[",a,"] b[",b,"]")
    
    def getWidget(self):
        
        print("getWidget () o ",self.mtitle,
                  "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                  "size:",int(self.size[0]),"x",int(self.size[1]))
        
        return self
        
    def update(self, fromWho, vals):
        if 0:
            print("update from widget_n[{}] from:{} callback:{} gotvals:{}".format(
                self.mtitle, fromWho, self.mcallback, vals
                ))
        if fromWho == self.mcallback:
            
            if self.mcallback == 'comCal':
                vals = {
                    self.mvalk: vals
                    }
            
            self.l.text = str( "%s%s%s"%( 
                round( vals[self.mvalk], self.mround ) if self.mround > 0 else int( vals[self.mvalk] ), 
                self.munit,
                'E' if self.inEditMode else '' 
                ) )
            self.l.refresh()
            if self.drawItC > 0:
                self.recL.texture = self.l.texture
                #print("recl size",self.l.texture.size)
                self.recL.size = self.l.texture.size
                
            if 0:
                print("o ",self.mtitle,
                        "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                        "size:",int(self.size[0]),"x",int(self.size[1]))
            
        if self.drawItC == 1:
            self.setPos(self.pos)
            self.drawItC+=1
        
    def setGui(self, gui):
        self.gui = gui
        
        lsize = 2.0
        self.msize = [self.maxnum*self.gui.lineH*lsize, self.gui.lineH*lsize]
        
        self.title = textLabel(
            text = self.mtitle,
            font_size = self.gui.lineH*1.2,
            bold = "bold" 
            )
        self.title.refresh()        

        self.valEmpty = ""
        for v in range(self.maxnum):
            self.valEmpty+="0"

        self.l = textLabel(
            text=self.valEmpty,
            font_size=self.gui.lineH*lsize
            )
        self.l.refresh()
        
        self.size = self.l.texture.size
        print("pos ",[self.x,self.y],' size ',self.size)
        self.pos = [self.x,self.y]
        
        
        print("from widget pos:",self.pos," size:",self.size)
        self.drawIt()
        #sys.exit(9)

    
    def setValues(self, 
        title, callback, valk, unit, round_ ,maxnum ):
        self.mtitle = title
        self.mcallback = callback
        self.mvalk = valk
        self.munit = unit
        self.mround = round_
        self.maxnum = maxnum
        
        
    def getSize(self):
        return self.size
    
    def calcPos(self, pos):
        pos = list(pos)
        #print("calcPos:",pos[0]," , ",pos[1]," rota",self.rotation)
        x = pos[0]
        y = pos[1]
        return x,y
        
    def setPos(self, pos):
        #print(self.mtitle,"pos:",pos)
        self.pos = pos
        dpos = self.calcPos(pos)
        #print("dpos",dpos)
        self.centPos.x = dpos[0]
        self.centPos.y = dpos[1]
        
    def setRot(self, rot):
        #print(self.mtitle,"rot:",rot)
        self.rotation = rot
        self.centRot.angle = self.rotation
        
    def setScale(self, scale):
        #print(self.mtitle,"scale:",scale)
        self.scale = scale
        self.centScale.x = self.scale
        self.centScale.y = self.scale
         
        
    def setColor(self,t):
        if t == "w":
            Color(1,1,1,1)
        elif t == "title":
            Color(.6,.6,.6,.5)
        elif t == "b":
            Color(1,1,1,1)
        elif t == "cog":
            Color(0,1,0,1)
        elif t == "hdg":
            Color(1,0,0,1)
        elif t == 'bg':
            Color(.3,0,0,.1)
            
            
    def drawIt(self):
        self.drawItC+=1
            
        with self.canvas:
            PushMatrix()
            self.centPos = Translate( 0.0, 0.0, 0.0 )
            
            self.centRot = Rotate(0,0,0,1)
            self.centScale = Scale(1,1,1)
            #Translate(-self.size[0]*0.5,-self.size[0]*0.5,0)
            #self.centPosM = Translate( 0.0, 0.0, 0.0 )
            
            
            Translate( -self.size[0]*.5, -self.size[1]*.5,0.0 )
            
            
            #self.setColor('bg')
            #Rectangle(
            #    size = self.size,
            #    pos = (0,0)
            #    )
            
            PushMatrix()
            self.setColor("title")
            Translate(-5,self.size[1],0)
            Rotate(-90,0,0,1)
            Rectangle(
                size = self.title.texture.size,
                pos = (0,0),
                texture = self.title.texture
                )
            PopMatrix()
            
            self.setColor('w')
            self.recL = Rectangle(
                size = (self.size),
                pos = (0,0),
                texture = self.l.texture
                )
            
            PopMatrix()
    
    
    