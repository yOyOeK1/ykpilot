
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
from kivy_garden.speedmeter import SpeedMeter
from kivy.uix.spinner import Spinner
from WidgetHelper import WidgetHelper
from MyLabel import MyLabel
from kivy.animation import Animation
from kivy.uix.progressbar import ProgressBar
          
          
class CircularProgressBar(ProgressBar):

    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        self.thickness = 40
        self.label = textLabel(text="0%", font_size=self.thickness)
        self.texture_size = None
        self.refresh_text()
        self.draw()

    def draw(self):

        with self.canvas:
            
            # Empty canvas instructions
            self.canvas.clear()

            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)
            Ellipse(pos=self.pos, size=self.size)

            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(1, 0, 0)
            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(0.001 if self.value_normalized == 0 else self.value_normalized*360))

            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))

            # Center and draw the progress text
            Color(1, 1, 1, 1)
            #added pos[0]and pos[1] for centralizing label text whenever pos_hint is set
            Rectangle(texture=self.label.texture, size=self.texture_size,
                  pos=(self.size[0] / 2 - self.texture_size[0] / 2 + self.pos[0], self.size[1] / 2 - self.texture_size[1] / 2 + self.pos[1]))


    def refresh_text(self):
        # Render the label
        self.label.refresh()

        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value, title, unit):
        # Update the progress bar value
        self.value = value

        # Update textual value and refresh the texture
        lText = ''
        if title != '':
            lText = "%s\n"%title
        lText+= str(value)
        if unit != '':
            lText+= unit 
        self.label.text = lText
        self.refresh_text()

        # Draw all the elements
        self.draw()

          
class Widget_circularProgress(WidgetHelper):
    
    def __init__(self, **kwargs):
        
        
        self.updateCount = 0
        
        self.screen = 0
        self.size = [200,200]
        self.pos = [0,0]
        self.scale = 1.0
        self.rotation = 0.0
        self.x = 0
        self.y = 0
        
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
        self.valueToDisplay = 0.0
        
        
        self.smSettings = {
            'title': '',
            'min': -175,
            'max': 175,
            'unit': '',
            'round': 1
        }

        self.sm = CircularProgressBar()
        self.sm.size_hint = [None,None]
        self.sm.width = self.size[0]
        self.sm.height = self.size[1]
        self.sm.size = self.size
        self.sm.max = self.smSettings['max']
        self.sm.min = self.smSettings['min']
        self.sm.set_value(0.0,'','')
        
        
        self.wvfh = WidgetValFunctionHandler()
        #self.wvfh.setParameters()
        
    def setValues(self, 
        screen, title, unit, round_ ,maxnum ):
        self.screen = screen
        self.mtitle = title
        self.munit = unit
        self.mround = round_
        self.maxnum = maxnum
        
    def settingsDoneStore(self):
        pass
        
    def settingsNeedIt(self):
        return True
    
    def setValuesFromDic(self,dic):
        print("Widget_circularProgress.setValuesFromDic",dic)
        self.smSettings['title'] = dic['title']
        self.smSettings['min'] = int(dic['min'])
        self.smSettings['max'] = int(dic['max'])
        self.smSettings['unit'] = dic['unit']
        self.smSettings['round'] = int(dic['round'])
        self.wvfh.setParametersFromDict(dic['valHandler'])

        self.sm.min = self.smSettings['min']
        self.sm.max = self.smSettings['max']
        
        print("so circular progress pos",self.pos," size",self.size)
        #sys.exit(0)
    
    def getAttrFromDialog(self):
        self.smSettings['title'] = self.ti_title.text
        self.smSettings['min'] = self.ti_min.text
        self.smSettings['max'] = self.ti_max.text
        self.smSettings['unit'] = self.ti_unit.text
        self.smSettings['round'] = self.ti_round.text
        
        return self.smSettings
        
        
    def addSettingsDialogPart(self,bl, inWConf = None):
        
        bl,self.ti_title = self.addDialogRow(bl, "Title", 
            "" if inWConf == None else inWConf['atr']['title'] )
        bl,self.ti_min = self.addDialogRow(bl, "Min value", 
            -175 if inWConf == None else str(inWConf['atr']['min']) )
        bl,self.ti_max = self.addDialogRow(bl, "Max value", 
            175 if inWConf == None else str(inWConf['atr']['max']) )
        bl, self.ti_round = self.addDialogRow(bl, "Round to", 
            "1" if inWConf == None else inWConf['atr']['round'] )
        bl, self.ti_unit = self.addDialogRow(bl, "Unit", 
            "%" if inWConf == None else inWConf['atr']['unit'] )
        
        
        return bl
       
    def getWidget(self):
        '''print("getWidget () o ",self.mtitle,
                  "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                  "size:",int(self.size[0]),"x",int(self.size[1]))
        '''
        return self.sm
    
    def updateIt(self, fromWho = '',vals = ''):
        self.update(fromWho, vals)
        self.setPos(self.pos)
        self.setScale(self.scale)
        self.setRot(self.rotation)
        
    def update(self, fromWho, vals):
        if self.gui.rl.current[:7] != 'Widgets':
            return 0
        
        if 0:
            print('''
            
update from widget_circularProgress[{}] 
                from:{}  
                gotvals:{}'''.format(
                self.mtitle, fromWho, vals
                ))
            
        v = self.wvfh.updateVal(fromWho, vals)
        if v != None:
            self.valueToDisplay = round( v, self.smSettings['round'] ) if self.smSettings['round'] > 0 else int( v ) 
            self.sm.set_value(self.valueToDisplay,self.smSettings['title'],self.smSettings['unit'])
            
         
        
    def setGui(self, gui):
        self.gui = gui
        
        self.size = [
            200,
            200
            ]
        self.pos = [self.x,self.y]
        
    
        
    def getSize(self):
        return self.size
    
    