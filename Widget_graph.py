
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
from kivy_garden.graph import MeshLinePlot, SmoothLinePlot, BarPlot, Graph,\
    ScatterPlot
from TimeHelper import TimeHelper
from kivy.uix.checkbox import CheckBox
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
          

          
class Widget_graph(WidgetHelper):
    
    def __init__(self, **kwargs):
        
        self.th = TimeHelper()
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
        
        self.valsHistory = []
        self.gSettings = {
            'title': '',
            'xlabel': 'time',
            'ylabel': 'kts',
            'graphType': 'BarPlot',
            'timeOnGraph': 300,
            'shape': '1:1',
            'border': 1,
            'grid': 0
            }
        self.gObj = Graph(
            xmin = 0.0,
            draw_border = True if self.gSettings['border'] == 1 else False,
            )
        #self.gObj.size = self.size
        #self.gObj.x_grid_label = 'abc'
        #self.gObj.y_ticks_major=10.0
        #self.gObj.tick_color = [1,0,0,1]
        
        
        self.gShapes = {
            '1:1':[200,200],
            '2:1':[400,200],
            '1:2':[200,400]
           }
        
        self.gTypes = {
            'line' : MeshLinePlot(color=[1,1,0,1]),
            'smooth line': SmoothLinePlot(color=[1,1,0,1]),
            'BarPlot': BarPlot(color=[1,1,0,1]),
            'Scatter': ScatterPlot(color=[1,1,0,1]),
            }
        
        self.gPlot = None  
        self.points = [] 
        
        self.wvfh = WidgetValFunctionHandler()
        self.wvfh.setParameters()
        
    def setValues(self, 
        screen, title, xlabel,ylabel,graphType,timeOnGraph,shape,border,grid ):
        self.screen = str(screen)
        self.mtitle = title
        #self.munit = unit
        #self.mround = round
        #self.maxnum = maxnum
        self.gSettings['title'] = title
        self.gSettings['xlabel'] = xlabel
        self.gSettings['ylabel'] = ylabel
        self.gSettings['graphType'] = graphType
        self.gSettings['timeOnGraph'] = timeOnGraph
        self.gSettings['shape'] = shape
        self.gSettings['border'] = border
        self.gSettings['grid'] = grid
        
        self.setGrid(grid)
        self.gObj.draw_border = True if border == 1 else False
        self.gObj.size = self.gShapes[shape]
        self.gObj.xmin = 0
        self.gObj.xmax = timeOnGraph*10
        self.size = self.gObj.size
         
        self.setPlot(self.gTypes[graphType])
       
    def setGrid(self, status ):
        if status:
            self.gObj.x_ticks_minor=5.0
            self.gObj.x_ticks_major=5.0
            self.gObj.y_ticks_minor = 10.0
            self.gObj.y_ticks_major=1.0
            #self.gObj.y_grid_label=True
            #self.gObj.x_grid_label=True
            self.gObj.x_grid=True
            self.gObj.y_grid=True
        else:
            #self.gObj.y_grid_label=False
            #self.gObj.x_grid_label=False
            self.gObj.x_grid=False
            self.gObj.y_grid=False
        
        
    def setPlot(self, plot):
        if self.gPlot != None:
            for p in self.gObj.plots:
                self.gObj.remove_plot(p)
        self.gPlot = plot
        self.gObj.add_plot(self.gPlot)
        self.gObj.xlabel = "{} {}".format(
            self.gSettings['xlabel'],self.gSettings['title']
            )
        self.gObj.ylabel = self.gSettings['ylabel']
        
        
    def settingsDoneStore(self):
        pass
        
    def settingsNeedIt(self):
        return True
    
    def setValuesFromDic(self,dic):
        print("setValuesFromDic",dic)
        self.wvfh.setParametersFromDict(dic['valHandler'])
        self.screen = str(dic['screen'])
        self.setPlot(self.gTypes[dic['graphType']])
        for k in self.gSettings.keys():
            try:
                print("key ",k," in dic is ",dic[k])
            except:
                print("EE - no dic key [",k,"] :/ old config ?")
                print("    I will add missing option to dic")
                dic[k] = self.gSettings[k]
                print("    now dic is ",dic)
                
            try:
                
                try:
                    self.gSettings[k] = int(dic[k])
                except:
                    try:
                        self.gSettings[k] = str(dic[k])
                    except:
                        print("EE - old settings comparing to app")
                
                if k == 'grid':
                    self.setGrid(True if dic[k] == 1 else False)    
                
                if k == 'border':
                    self.gObj.draw_border = True if dic[k] == 1 else False
                    
                if k == 'shape':
                    self.gObj.size = self.gShapes[dic[k]]
                    self.size = self.gObj.size
                    
                if k == 'timeOnGraph':
                    self.gObj.xmin = 0
                    self.gObj.xmax = int(dic[k])*10
                    
                #print("set self.sm")
                if k == 'xlabel':
                    self.gObj.xlabel = "{} {}".format(
                        str(dic[k]),str(dic['title'])
                        ) 
                
                elif k == 'ylabel':
                    self.gObj.ylabel = str(dic[k])
                #print("    sm set")
                
            except:
                print("EE - in graph when setValuesFromDic pass ???")
            
        print(" DONE OK")
        #print("so niddle pos",self.pos," size",self.size)
        
    
    def getAttrFromDialog(self):
        self.updateGSettings()
        return self.gSettings
        
        
    def addSettingsDialogPart(self,bl, inWConf = None):
        
        presetVals = []
        for k in list(self.gTypes.keys()):
            presetVals.append(k)
        presetDef = presetVals[0] if inWConf == None else str(inWConf['atr']['graphType'])
        
        shapeVals = []
        for k in list(self.gShapes.keys()):
            shapeVals.append(k)
        shapeDef = shapeVals[0] if inWConf == None else str(inWConf['atr']['shape'])
        
        
        #bl = BoxLayout(orientation="vertical")
        bh = self.getDialogRow()
        bh.add_widget(MDLabel(text="Graph type:"))
        self.spPreset = Spinner(
            text = presetDef,
            values = presetVals,
            size_hint = [None,None],
            height = cm(1)
            )
        bh.add_widget( self.spPreset )
        bl.add_widget(bh)
        self.spPreset.bind(text=self.on_presetChange)
        
        bh = self.getDialogRow()
        bh.add_widget(MDLabel(text="Graph shape:"))
        self.spShape = Spinner(
            text = shapeDef,
            values = shapeVals,
            size_hint = [None,None],
            height = cm(1)
            )
        bh.add_widget( self.spShape )
        bl.add_widget(bh)
        
        if inWConf:
            self.spPreset.text = inWConf['atr']['graphType']
        
        
        #bl.add_widget(
        #    MDTextField(
        #        hint_text="ala ma kota",
        #        text="123"
        #        )
        #    )
        
        
        #bl,self.ti_title = self.addDialogRow(bl, "Title", 
        #    "" if inWConf == None else inWConf['atr']['title'] )
        self.ti_title = MDTextField(
            text = ("" if inWConf == None else inWConf['atr']['title'] ),
            )
        self.ti_title.hint_text = 'Title'
        bl.add_widget(self.ti_title)
        
        
        #bl,self.ti_xlabel = self.addDialogRow(bl, "X label", 
        #    'time' if inWConf == None else str(inWConf['atr']['xlabel']) )
        self.ti_xlabel = MDTextField(
            text = 'time' if inWConf == None else str(inWConf['atr']['xlabel']) 
            )
        self.ti_xlabel.hint_text = "X axis label:"
        bl.add_widget(self.ti_xlabel)
        
        bl,self.ti_ylabel = self.addDialogRow(bl, "Y label", 
            'kts' if inWConf == None else str(inWConf['atr']['ylabel']) )
        
        
        bh = self.getDialogRow()
        bh.add_widget(MDLabel(text="Draw borders"))
        self.cb_gDrawBorders = CheckBox(
            size=[ cm(1),cm(1)],
            size_hint=  [None,None]
            )
        active = False
        if inWConf == None:
            active = True if self.gSettings['border'] else False
        else:
            active = True if inWConf['atr']['border'] else False
        self.cb_gDrawBorders.active =  active
        bh.add_widget(self.cb_gDrawBorders)
        bl.add_widget(bh)
        
        bh = self.getDialogRow()
        bh.add_widget(MDLabel(text="Draw grid"))
        self.cb_gDrawGrid = CheckBox(
            size=[ cm(1),cm(1)],
            size_hint=  [None,None]
            )
        active = False
        if inWConf == None:
            active = True if self.gSettings['grid'] else False
        else:
            active = True if inWConf['atr']['grid'] else False
        self.cb_gDrawGrid.active =  active
        bh.add_widget(self.cb_gDrawGrid)
        bl.add_widget(bh)
        
        
        bl,self.ti_timeOnGraph = self.addDialogRow(bl, "Time on graph (sec.)", 
            30  if inWConf == None else str(inWConf['atr']['timeOnGraph']) )

        
        
        return bl
       
    def updateGSettings(self):
        print("updateGSettings")
        for k in self.gSettings.keys():
            print("value ",k)
            try:
                exec("self.gSettings['{0}'] = str(self.ti_{0}.text)".format(k))
                #print(" -> ",self.smSettings[k])
                if k == 'xlabel':
                    self.gObj.xlabel = self.gSettings[k]
                elif k == 'ylabel':
                    self.gObj.ylabel = self.gSettings[k]
            except:
                print(" not pressent")
                pass 
            try:
                print("    ",self.gSettings[k])
            except:
                print("EE - no key",k," in gSettings")
        self.gSettings['shape'] = self.spShape.text
        self.gSettings['graphType'] = self.spPreset.text
        self.gSettings['border'] = 1 if self.cb_gDrawBorders.active else 0
        self.gSettings['grid'] = 1 if self.cb_gDrawGrid.active else 0
            
    def on_presetChange(self,a='',b=''):
        print("on_presetChange")
        sp = self.spPreset.text
        for k in list(self.gTypes.keys()):
            if k==sp:
                spObj = self.gTypes[k]
                spText = k
                self.gSettings['graphType'] = spText
                break
            
            
            
            
        print("affter change gSettings is ",self.gSettings)
    
    def getWidget(self):
        '''print("getWidget () o ",self.mtitle,
                  "pos:",int(self.pos[0]),"x",int(self.pos[1]),
                  "size:",int(self.size[0]),"x",int(self.size[1]))
        '''
        return self.gObj
    
    def updateIt(self, fromWho = '',vals = ''):
        self.update(fromWho, vals)
        self.setPos(self.pos)
        self.setScale(self.scale)
        self.setRot(self.rotation)
        
    gIter = 0
    def update(self, fromWho, vals):
        if( self.gui.rl.current[:7] != 'Widgets' or 
            self.screen != self.gui.rl.current[7:]
             ):
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
                v = float(v)
            except:
                vAsInt = False
            
            if vAsInt:
                ms = self.th.getTimestamp(True)
                self.valsHistory.append([v,ms])
                tp = []
                msS = (ms-1000000)-(self.gSettings['timeOnGraph']*1000000)
                ii = 0
                ymin = None
                ymax = None
                while len(self.valsHistory) > 0:
                    if ii > (len(self.valsHistory)-1):
                        break
                    
                    vh = self.valsHistory[ii]
                    addedMs = (ms-vh[1])/100000
                    if vh[1] < msS:
                        self.valsHistory.pop(0)
                    else:
                        if ymin == None:
                            ymin = vh[0]
                            ymax = vh[0]
                        elif ymin > vh[0]:
                            ymin = vh[0]
                        elif ymax < vh[0]:
                            ymax = vh[0]
                        
                        if tp==[] or (
                            len(tp) > 0 and tp[-1] != vh[0] 
                            ):
                            tp.append([addedMs,vh[0]])
                            
                        ii+=1
                
                        
                if ymin != None and ymax != None:
                    print(ymin,",,",ymax)
                    ymin = round(float(ymin),2)
                    ymax = round(float(ymax),2)
                    #print("y min max ",ymin, " max ",ymax)
                    #print("gObj x min max", self.gObj.xmin," x ",self.gObj.xmax)
                    if ymax == ymin and ymax == 0.0:
                        ymax+=0.1
                    ymin*=0.99
                    ymax*=1.01
                    if self.gSettings['grid']:
                        ydif = (ymax - ymin)*0.25
                        self.gObj.y_ticks_major = ydif
                        self.gObj.y_ticks_minor = 2.0
                        
                    self.gObj.ymin = ymin
                    self.gObj.ymax = ymax
                    
                    
                self.gPlot.points = tp
                self.gIter+=1
            
        
    def setGui(self, gui):
        self.gui = gui
        #self.pos = [self.x,self.y]
        
        
    def getSize(self):
        return [self.gObj.size[0], self.gObj.size[1], 0.5, -1.0 ]
    
    