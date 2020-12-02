
import kivy
from kivy.uix.widget import Widget
from kivy.core.text import Label as textLabel
from kivy.uix.label import Label as KiLabel
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.scatter import Scatter
from kivy.graphics.opengl import *
from kivy.graphics import *
from kivy.properties import ObjectProperty
import sys
import math
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import cm
from WidgetValFunctionHandler import WidgetValFunctionHandler
from WidgetHelper import WidgetHelper

class WidgetProto(Widget):
    pass    
            
class Widget_cn(WidgetProto,WidgetHelper):
    
    pos = ObjectProperty(None)
    size = ObjectProperty(None)
    scale = ObjectProperty(None)
    rotation = ObjectProperty(None)
    size_hint = None, None
    
    
    def __init__(self, **kwargs):
        super(Widget_cn, self).__init__(**kwargs)
        
        self.drawItC = 0
        
        self.screen = 0
        self.pos = [0,0]
        self.size = [0,0]
        self.scale = 1.0
        self.rotation = 0.0
        
        self.myValue = None
        self.stat = {
            'skip': 0,
            'update': 0
            }
        self.subPix = 1.25
        
        self.mtitle = ""
        self.mcallback = None
        self.mvalk = ""
        self.munit = 1
        self.mround = 1
        self.maxnum = 4
        self.wvfh = WidgetValFunctionHandler()
        
    
    def setValues(self, 
        screen, title, unit, round_ ,maxnum ):
        self.screen = screen
        self.mtitle = title
        self.munit = unit
        self.mround = round_
        self.maxnum = maxnum
        
    def settingsNeedIt(self):
        return True
    
    
    def settingsDoneStore(self):
        pass
        
    def setValuesFromDic(self,dic):
        self.setValues(
            screen = dic['screen'], 
            title = dic['title'], 
            unit = dic['unit'], 
            round_ = dic['round'], 
            maxnum = dic['maxnum']
            )
        self.wvfh.setParametersFromDict(dic['valHandler'])
        
    
    def getAttrFromDialog(self): 
        atr = {
            'title': str(self.tiTitle.text),
            'round': int(self.tiRound.text),
            'unit': self.tiUnit.text,
            'maxnum': int(self.tiMaxnum.text)
            }
        return atr
        
    def addSettingsDialogPart(self,bl, wConf=None):
        bl, self.tiTitle = self.addDialogRow(bl, "Title", 
            "" if wConf == None else wConf['atr']['title'] )
        bl, self.tiRound = self.addDialogRow(bl, "Round to", 
            "1" if wConf == None else wConf['atr']['round'] )
        bl, self.tiUnit = self.addDialogRow(bl, "Unit", 
            "kts" if wConf == None else wConf['atr']['unit'] )
        bl, self.tiMaxnum = self.addDialogRow(bl, "Max characters", 
            "4"  if wConf == None else wConf['atr']['maxnum'] )
        
        return bl
    
    def getWidget(self):
        '''print("getWidget () o ",self.mtitle,
                  "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                  "size:",int(self.size[0]),"x",int(self.size[1]))
        '''
        return self
    
    def updateIt(self, fromWho = '',vals = ''):
        self.update(fromWho, vals)
        
    def formatValue(self,v ):
        return str( "%s%s"%( v, self.munit) )
        
    def update(self, fromWho, vals):
        if self.gui.rl.current[:7] != 'Widgets':
            return 0
        
        if 0:
            print('''update from widget_n[{}] 
                from:{}  
                gotvals:{}'''.format(
                self.mtitle, fromWho, vals
                ))
            
        v = self.wvfh.updateVal(fromWho, vals)
        if v != None:
            vAsInt = True
            try:
                vi = int(v)
            except:
                vAsInt = False
            
            if vAsInt:
                v = str( round( v, self.mround ) if self.mround > 0 else int( v ) )
            else:
                v = str(v)
                
            if self.myValue == None or self.myValue != v:
                self.myValue = v
            
                self.l.text = self.formatValue(v)
                self.l.refresh()
                self.recL.texture = self.l.texture
                
                #print("recl size",self.l.texture.size)
                self.recL.size = [ 
                    self.l.texture.size[0]*self.subPix,
                    self.l.texture.size[1]*self.subPix
                    ]
                #off = self.msize[0]*.55-(self.l.texture.size[0]*self.subPix) 
                #self.posL.x = off
                
                    
                if 0:
                    print("o ",self.mtitle,
                            "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                            "size:",int(self.size[0]),"x",int(self.size[1]))
                self.stat['update']+=1
            else:
                self.stat['skip']+=1
                if (self.stat['skip']%50)==0:
                    print("widget stat",self.mtitle," -> ",self.stat)
            
            if self.drawItC == 1:
                self.drawItC+=1
            
    def setGuiDoMore(self):
        pass
        
    def setGui(self, gui):
        self.gui = gui
        
        lsize = 2.0
        
        self.msize = [
            (self.maxnum+len(self.munit))*self.gui.lineH*lsize, 
            self.gui.lineH*lsize
            ]
        
        self.setGuiDoMore()
        
        
        self.title = textLabel(
            text = self.mtitle,
            font_size = (self.gui.lineH*1.2)/self.subPix,
            font_name='Segment7-4Gml.otf',
            #bold = "bold" 
            )
        self.title.refresh()        

        self.valEmpty = ""
        for v in range(self.maxnum):
            self.valEmpty+="0"

        self.l = textLabel(
            text=self.formatValue(self.valEmpty),
            font_size=(self.gui.lineH*lsize)/self.subPix,
            font_name='Segment7-4Gml.otf',
            )
        self.l.refresh()
        
        self.size = [
            self.l.texture.size[0]*self.subPix,
            self.l.texture.size[1]*self.subPix
            ]
        self.pos = [self.x,self.y]
        
        self.drawIt()
        #sys.exit(9)

    
        
    def getSize(self):
        return [self.size[0],self.size[1], -1.0, 1.0/12.0 ]
    
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
            
            
    def drawItMore(self):
        pass
            
    def drawIt(self):
        self.drawItC+=1
            
        with self.canvas:
            PushMatrix()
            self.centPos = Translate( 0.0, 0.0, 0.0 )
            
            self.drawItMore()
            
            PushMatrix()
            self.setColor("title")
            Translate(0,self.size[1]*.7,0)
            Rotate(0,0,0,1)
            Rectangle(
                size = [
                    self.title.texture.size[0]*.5*self.subPix,
                    self.title.texture.size[1]*.5*self.subPix
                    ],
                pos = (0,0),
                texture = self.title.texture
                )
            PopMatrix()
            
            
            self.setColor('w')
            self.posL = Translate(0,self.size[1]*-0.2,0)
            self.recL = Rectangle(
                size = [
                    self.size[0],
                    self.size[1]
                    ],
                pos = (0,0),
                texture = self.l.texture
                )
            
            PopMatrix()
    
    
    