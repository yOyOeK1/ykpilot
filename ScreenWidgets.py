from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color
from ScreenCompass import ScreenCompass
from ScreenRace import ScreenRace
import sys
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen


from WidgetsAEDV import WidgetsAEDV

from Widget_n import Widget_n
from Widget_cn import Widget_cn
from Widget_cnDiff import Widget_cnDiff
from WidgetBubble import WidgetBubble
from FileActions import FileActions
from DataSaveRestore import DataSR_save, DataSR_restore



class MyScatterWidgetOnScatter(Scatter):
    pass
        
        
class ScreenWidgets:
    
    def makeSensorsList(self):
        sl = self.gui.sen.sensorsList
        print("have now: ",len(sl)," sensors registered")
        for s in sl:
            print('''    sensor: {}        class:{}
        values: {}
        '''.format(
                s.getTitle(), type(s), s.getValuesOptions()
                ))
            
         
        #sys.exit(0)
        
        
    def getWidgetsTypeList(self):
        return [
            {   'name': "Numeric",
                'obj': Widget_cn(),
                'thumb': 'widget_numeric.png'
                },
                
            {   'name': 'Bubble',
                'obj': WidgetBubble(),
                'thumb': 'widget_bubble.png'
                },
            {   'name': "Compass",
                'obj' : ScreenCompass(),
                'thumb': 'widget_compass.png' 
                },
            ]
    
    def saveConfig(self):
        print("saveConfig",self.wConfig)
        
        for s in self.wConfig:
            for w in s:
                w['obj'] = ''
                
        print("-------------------------------------------")
        print(self.wConfig)
        
        print("save config Widgets res:",
              DataSR_save(self.wConfig, self.wConfigPath)
              )
    
    def setGui(self, gui):
        #b = Builder.load_file('MyScatterWidget.kv')
        #self.w = MyWidgets()
        
        #sys.exit(0)
        
        b = Builder.load_file('MyScatterWidget.kv')
        
        self.wConfigPath = 'ykpilotWidgets.conf'
        self.fa = FileActions()
        if self.fa.isFile(self.wConfigPath) == False:
            print("screen widgets no config file setting default")
            self.wConfig = [[
                {
                'name': 'ScreenCompass',
                'obj': None,
                'objName': 'ScreenCompass',
                'callback': ['gpsD','comCal', 'comCalAccelGyro'],
                'pos': [200,200],
                'scale':1.0,
                'rotation':0.0
                }
                ]]
        else:
            print("screen widgets resuming config")
            self.wConfig = DataSR_restore(self.wConfigPath)
            print(self.wConfig)
            print("------------------------------") 
            #sys.exit(0)

        self.screen = 0
        self.screens = len(self.wConfig)+1
        
        self.gui = gui
        self.editMode = False
        self.clockUWFS = None
        
        
        #self.makeSensorsList()
        
        self.buildW()
        return 0
    
    
        
        nSOG = Widget_cn()
        nSOG.setValues('SOG', 'gps', 'speed', 'kts', 1,4)
        
        #nCOG = Widget_cn()
        #nCOG.setValues('COG', 'gps', 'bearing', '`', 0,4)
        
        cnHDG = Widget_cn()
        cnHDG.setValues('HDG', 'comCal', 2, '`', 1, 4)
        
        #cnHeel = Widget_cn()
        #cnHeel.setValues('heel', 'orientation', 4, '`', 0, 3)
        
        cnPitch = Widget_cn()
        cnPitch.setValues('pitch', 'orientation', 3, '`', 0, 3)
        
        cnDiffHDG_COG = Widget_cnDiff()
        cnDiffHDG_COG.setValues('HDG-COG', None, 0, '`', 1, 3)
        cnDiffHDG_COG.setDiffs('gps', 'bearing', 'comCal', 0, angleNormalize=True)
        
        bubble = WidgetBubble()
        
        aeoueaou= '''
        self.widgets = [
         {   
                'name': "bubble",
                'obj': bubble,
                'callback': ['orientation']
                },
            {   
                'name': "diffHDG_COG",
                'obj': cnDiffHDG_COG,
                'callback': ['gpsD','comCal']
                },
            
        
            {   
                'name': "nSOG",
                'obj': nSOG,
                'callback': ['gpsD']
                },
            
            {   
                'name': "cnHDG",
                'obj': cnHDG,
                'callback': ['comCal']
                },
            {   
                'name': "pitch",
                'obj': cnPitch,
                'callback': ['orientation']
                },
            {
                'name': 'ScreenCompass',
                'obj': ScreenCompass(),
                'callback': ['gpsD','comCal', 'comCalAccelGyro']
                },
            ]
        '''
        
    def buildW(self):
        print("buildW")
        
        print("- screens now count is",self.screens)
        self.fls = []
        self.flsOrgs = []
        for si in range(self.screens):
            screen = Screen(name="Widgets%s"%si)
            self.flsOrgs.append(None)
            fl = FloatLayout()
            self.fls.append(fl)
            fl.add_widget(Label(text="widgets%s"%si))
            self.flsOrgs[si] = fl.on_touch_down 
            fl.on_touch_down = self.on_touch
            screen.add_widget(fl)
            
            try:
                self.setUpGui( si, fl , self.wConfig[si])
            except:
                self.setUpGui( si, fl , [])
            
            self.gui.rl.add_widget(screen)
        
        print("    DONE")
           
        
        
      
    def addWidgetOnScreen(self, wObj, callbaks=None):
        print("add widget on screen",wObj)
        
        if len(self.wConfig)<=self.screen:
            print("adding first widget on screen !",self.screen)
            self.wConfig.append([])
        
        
        
        self.wConfig[self.screen].append({
            'name': 'ScreenCompass',
            'obj': ScreenCompass(),
            'objName': 'ScreenCompass',
            'callback': ['gpsD','comCal', 'comCalAccelGyro'],
            'pos': [200,200],
            'scale':1.0,
            'rotation':0.0
            })
        
         
         
        
    def updateWidgetFromScatter(self,a=0):
        if self.editMode:
            o = self.widgetEdit
            i = self.widgetEditI
            s = self.s
            print("s.pos",s.pos)
            try:
                o.setPos( [s.center_x,s.center_y] )
                o.setScale( s.scale )
                o.setRot( s.rotation )
                self.wConfig[self.screen][i]['pos'] = o.pos
                self.wConfig[self.screen][i]['scale'] = o.scale
                self.wConfig[self.screen][i]['rotation'] = o.rotation
                o.updateIt()
            except:
                print("EE - static widget no set POS")
        else:
            if self.clockUWFS != None:
                self.clockUWFS.cancel()
                self.clockUWFS = None
       
       
    def updateIt(self,a='',b=''):
        if self.gui.rl.current == "Widgets":
            self.gui.screenChange("Widgets0")
            return 0
        
        print("ScreenWidgets.updateIt",self.gui.rl.current[7:])
        self.screen = int(self.gui.rl.current[7:])
        
        if len(self.wConfig) <= self.screen:
            print("ScreenWidget.updateIt")
            for w in self.wConfig[self.screen]:
                o = w['obj']
                try:
                    o.updateIt()
                except:
                    pass
        else:
            print("EE - nothing to update :( no widgets in screen",self.screen)
        
        
    def clikOn(self, clickPos, opos, osize):
        if( clickPos[0]>=opos[0] 
                    and clickPos[0]<= (opos[0]+osize[0]) 
                    and clickPos[1]>=opos[1]
                    and clickPos[1]<= (opos[1]+osize[1])
            ):
            return True
        else:
            return False
        
        
    def on_navigation(self, pos):
        btH = self.gui.btH
        if self.clikOn( pos, [0,0],[ btH, btH ] ) :
            print("edit Clik <<")
            s = self.screen-1
            if s < 0:
                s = self.screens-1
            self.screen = s
            self.gui.screenChange( "Widgets%s"%s )
            return True
        
             
        if self.clikOn( pos, [btH,0], [ btH, btH ] ):
            print("edit Clik +")
            self.on_addEditDelButton()
            return True
        
          
        if self.clikOn( pos, [btH*2.0,0], [ btH, btH ] ):
            print("edit Clik >>")
            s = self.screen+1
            if s >= self.screens:
                s = 0
            self.screen = s
            self.gui.screenChange( "Widgets%s"%s )
            return True
        
    def on_touch(self,a=0):
        print("screeWidgets.on_touch screen:",self.screen)
        pos = a.pos
        btH = self.gui.btH
        print("    pos ",a.pos," -------------------")
        
        if self.on_navigation(pos):
            return True
        
        if len(self.wConfig) <= self.screen:
            return False
        
        for i,w in enumerate(self.wConfig[self.screen]):
            o = w['obj']
            print("screen:",self.screen," widget nr:",i," objName:",w['objName'])
            try:
                osize = o.getSize()
                print("    pos",o.pos,"\n    size",o.size,"\n    getSize", osize)
                try:
                    print(o.mtitle)
                except:
                    print("EE - widget don't have mtitle?")
                    pass
                
                opos = [o.pos[0]-osize[0]*.5, o.pos[1]-osize[1]*.5]
                
                if self.clikOn( pos , opos, osize):
                    print("klik!!")
                    
                    try:
                        s = self.s
                        par = self.s.parent
                        if par:
                            if self.sIsOnScreen != self.screen:
                                par.remove_widget(s)
                            
                        else:
                            print("EE - no parent :/")
                            sys.exit(9)
                        
                    except:
                        print("no self.s make IT!")
                        self.s = MyScatterWidgetOnScatter(
                            pos=(-100,-100),
                            size=(1,1),
                            size_hint=(None,None),
                            )
                        print("DONE")
                    
                        
                    self.fls[self.screen].add_widget(self.s)
                    self.sIsOnScreen = self.screen
                    
                    self.widgetEdit = o
                    self.widgetEditI = i
                    self.fls[self.screen].on_touch_down = self.flsOrgs[self.screen]
                    self.s.size = osize
                    self.s.scale = o.scale
                    self.s.rotation = o.rotation
                    self.s.center_x = o.pos[0]
                    self.s.center_y = o.pos[1]
                    self.editMode = True
                    
                    if self.clockUWFS == None:
                        self.clockUWFS = Clock.schedule_interval( self.updateWidgetFromScatter,0.1)
                    
                    
                    return False
                
            except:
                print("ee - no pos  or size")
                        
        
        return False
        
    def on_btEdit(self,a=''):
        print("on_btEdit")
        self.fls[self.screen].on_touch_down = self.on_touch
        self.editMode = False
        self.s.pos = [0,0]
        self.s.size = [0,0]
        self.s.scale = 1.0
        self.s.rotation = 0.0
        
    def on_bgRelease(self,a='',b=''):
        print("on_bgRelease")
        if self.editMode == True:
            self.on_btEdit(a)
            return True
        
    def setPSR(self,obj,val):
        obj.setPos( val['pos'] )
        obj.setScale( val['scale'] )
        obj.setRot( val['rotation'] )
        return obj
        
    def setUpGui(self, screen, bWidget, widgets):  
        print("set up gui ",bWidget," widgets\n",widgets)      
        btEdit = Button(
            background_color = (1,1,1,0.1)
            )
        btEdit.bind( on_release = self.on_btEdit)
        bWidget.add_widget(btEdit)
        
        #self.flsOrgs[screen] = bWidget.on_touch_down
        #bWidget.on_touch_down = self.on_touch
        
        
        for i,w in enumerate( widgets ):
            
            bl = BoxLayout(
                orientation = "vertical",
                padding = 5,
                spacing = 5
                )
            print("building widget [",w['name'],"]")
            exec("widgets[i]['obj'] = %s()"%w['objName'])
            o = widgets[i]['obj']
            o.setGui(self.gui)
            
            
            bWidget.add_widget( o.getWidget() )
            try:
                o = self.setPSR(o,w)
                self.wConfig[screen][i]['pos'] = o.pos
                self.wConfig[screen][i]['scale'] = o.scale
                self.wConfig[screen][i]['rotation'] = o.rotation
           
            except:
                print("EE - widget build no pos or .....")
            
            
            print("\- - adding callbacks:")
            for c in w['callback']:
                print(c)
                eval("self.gui.sen.%s.addCallBack(o)"%(
                    c
                    ))
        
        
        self.addNavBts( bWidget )          
        self.updateWidgetFromScatter()
    
    
    def addNavBts(self, w):
        btAdd = Button(
            text="<",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None)
            )
        w.add_widget(btAdd)
        
        btAdd = Button(
            text="+",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None)
            )
        w.add_widget(btAdd)
        btAdd.x = self.gui.btH
        
        
        btAdd = Button(
            text=">",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None)
            )
        w.add_widget(btAdd)
        btAdd.x = self.gui.btH*2.0 
    
    def on_addEditDelButton(self,a='',b=''):
        print("on_addEditDelButton")
        self.WAEDV = WidgetsAEDV(self)
        self.WAEDV.startWizard()
        
    
    
    def on_widRel(self,nr):
        print("on_widRel",nr)     
        
    
        