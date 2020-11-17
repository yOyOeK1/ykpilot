
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
          
          
          
class MySpeedMeter(SpeedMeter):
    pass
          
class Widget_niddle(WidgetHelper):
    
    def __init__(self, **kwargs):
        
        
        self.updateCount = 0
        
        self.screen = 0
        self.pos = [10,10]
        self.size = [200,200]
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
            'name': '-170 to 170',
            'thumb': 'widget_niddle_170_170.png',
            'min': -175,
            'max': 175,
            'tick': 25,
            'subtick':6,
            'start_angle': -170,
            'end_angle': 170,
            'value_font_size': 23,
            'label_font_size': 50,
            }

        self.sm = MySpeedMeter()
        self.sm.size_hint = [None,None]
        self.sm.size = self.size
        
        self.defSettings = [
            { 
                'name': '-170 to 170',
                'title': '',
                'thumb': 'widget_niddle_170_170.png',
                'min': -175,
                'max': 175,
                'tick': 25,
                'subtick':6,
                'start_angle': -170,
                'end_angle': 170,
                'value_font_size': 23,
                'label_font_size': 50,
                },
            { 
                'name': '-170 to 170 small numbers',
                'title': '',
                'thumb': 'widget_niddle_170_170.png',
                'min': -3,
                'max': 3,
                'tick': 1,
                'subtick':11,
                'start_angle': -170,
                'end_angle': 170,
                'value_font_size': 23,
                'label_font_size': 50,
                },
            { 
                'name': '-90 to 90 ',
                'thumb': 'widget_niddle_90_90.png',
                'min': -175,
                'max': 175,
                'tick': 50,
                'subtick':3,
                'start_angle': -85,
                'end_angle': 85,
                'value_font_size': 14,
                'label_font_size': 50,
                },
            { 
                'name': '-90 to 90 small numbers',
                'title': '',
                'thumb': 'widget_niddle_90_90.png',
                'min': -3,
                'max': 3,
                'tick': 1,
                'subtick':11,
                'start_angle': -85,
                'end_angle': 85,
                'value_font_size': 14,
                'label_font_size': 50,
                },
            { 
                'name': '0 to 90 small numbers',
                'title': '',
                'thumb': 'widget_niddle_corner.png',
                'min': 0,
                'max': 5,
                'tick': 1,
                'subtick':6,
                'start_angle': 90,
                'end_angle': 0,
                'value_font_size': 14,
                'label_font_size': 35,
                },
        
            
            ]
        
        self.wvfh = WidgetValFunctionHandler()
        self.wvfh.setParameters()
        
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
        print("setValuesFromDic",dic)
        self.wvfh.setParametersFromDict(dic['valHandler'])

        for k in self.smSettings.keys():
            print("key ",k," in dic is ",dic[k])
            try:
                try:
                    self.smSettings[k] = int(dic[k])
                except:
                    self.smSettings[k] = str(dic[k])
                print("set self.sm")
                exec("self.sm.{0} = {1}".format(k,self.smSettings[k]))
                print("    sm set")
            except:
                print(" pass ???")
            
        self.pos = self.sm.pos
        self.size = self.sm.size
        self.sm.pos = self.pos
        self.sm.size = self.size 
        self.sm.value = 0.0
        
        print("so niddle pos",self.pos," size",self.size)
        
    
    def getAttrFromDialog(self):
        self.updateSmSettings()
        return self.smSettings
        
        
    def addSettingsDialogPart(self,bl):
        
        presetVals = []
        for s in self.defSettings:
            presetVals.append(s['name'])
        presetDef = presetVals[0]
        
        
        #bl = BoxLayout(orientation="vertical")
        bh = self.getDialogRow()
        bh.add_widget(MyLabel(text="Preset:"))
        self.spPreset = Spinner(
            text = presetDef,
            values = presetVals,
            height = cm(1)
            )
        bh.add_widget( self.spPreset )
        bl.add_widget(bh)
        self.spPreset.bind(text=self.on_presetChange)
        
        bl,self.ti_title = self.addDialogRow(bl, "Title", "")
        bl,self.ti_min = self.addDialogRow(bl, "Min value", -175)
        bl,self.ti_max = self.addDialogRow(bl, "Max value", 175)
        bl,self.ti_tick = self.addDialogRow(bl, "Tick", 25)
        bl,self.ti_subtick = self.addDialogRow(bl, "Sub ticks", 6)
        bl,self.ti_start_angle = self.addDialogRow(bl, "Start angle", -170)
        bl,self.ti_end_angle = self.addDialogRow(bl, "End angle", 170)
        bl,self.ti_value_font_size = self.addDialogRow(bl, "Value size", 23)
        bl,self.ti_label_font_size = self.addDialogRow(bl, "Labels size", 50)
        
        
        
        return bl
       
    def updateSmSettings(self):
        print("updateSmSettings")
        for k in self.smSettings.keys():
            #print("value ",k)
            try:
                exec("self.smSettings['{0}'] = str(self.ti_{0}.text)".format(k))
                #print(" -> ",self.smSettings[k])
            except:
                print(" not pressent")
                pass 
        
    def on_presetChange(self,a='',b=''):
        print("on_presetChange")
        sp = self.spPreset.text
        for s in self.defSettings:
            if s['name']==sp:
                spO = s
                break
        
        for k in spO.keys():
            print("setting to gui",k)
            try:
                exec("self.ti_%s.text = str(%s)"%(k,spO[k]))
                #print("set")
            except:
                #print('skipp')
                pass
            try:
                self.smSettings[k] = spO[k]
            except:
                pass
        print("affter change smSettings is ",self.smSettings)
    
    def getWidget(self):
        print("getWidget () o ",self.mtitle,
                  "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                  "size:",int(self.size[0]),"x",int(self.size[1]))
        
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
            print('''update from widget_n[{}] 
                from:{}  
                gotvals:{}'''.format(
                self.mtitle, fromWho, vals
                ))
            
        v = self.wvfh.updateVal(fromWho, vals)
        if v != None:
            self.valueToDisplay = round( v, self.mround ) if self.mround > 0 else int( v ) 
            if self.smSettings['title'] != '':
                self.sm.label = "{}\n{}".format(
                    self.smSettings['title'], self.valueToDisplay)
            else: 
                self.sm.label = str(self.valueToDisplay)
            
            if self.valueToDisplay > self.smSettings['max']:
                self.valueToDisplay = self.smSettings['max']
            if self.valueToDisplay < self.smSettings['min']:
                self.valueToDisplay = self.smSettings['min']
            
            
            if self.gui.animation:            
                Animation.cancel_all(self.sm,'angle')
                anim = Animation(value=self.valueToDisplay, t='out_quad' )
                anim.start( self.sm )
            
            else:
                self.sm.value = self.valueToDisplay
            
                
        
    def setGui(self, gui):
        self.gui = gui
        
        self.size = [
            200,
            200
            ]
        print("pos ",[self.x,self.y],' size ',self.size)
        self.pos = [self.x,self.y]
        
        
        print("from widget pos:",self.pos," size:",self.size)
        #sys.exit(9)

    
        
    def getSize(self):
        return self.size
    
    def setPos(self, pos):
        #print(self.mtitle,"pos:",pos)
        print("sm.size",self.sm.size," got pos",pos," sm.pos",self.sm.pos)
        self.sm.pos = [
            pos[0]-self.sm.size[0]*.5,
            pos[1]-self.sm.size[1]*.5
            ]
        self.pos = pos
       
        
    def setRot(self, rot):
        #print(self.mtitle,"rot:",rot)
        self.rotation = rot
        self.sm.start_angle = self.smSettings['start_angle']-rot
        self.sm.end_angle = self.smSettings['end_angle']-rot
        #self.centRot.angle = self.rotation
        
    def setScale(self, scale):
        #print(self.mtitle,"scale:",scale)
        self.scale = scale
        self.sm.scale = scale
        self.sm.size = [
            self.size[0]*scale,
            self.size[1]*scale
            ]
        #self.centScale.x = self.scale
        #self.centScale.y = self.scale
         
        
    
    
    