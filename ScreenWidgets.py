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
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.properties import ObjectProperty


from WidgetsAEDV import WidgetsAEDV

from Widget_n import Widget_n
from Widget_cn import Widget_cn
from Widget_cnDiff import Widget_cnDiff
from WidgetBubble import WidgetBubble
from FileActions import FileActions
from DataSaveRestore import DataSR_save, DataSR_restore
from QueryPopup import QueryPopup



class MyScatterWidgetOnScatter(Scatter):
    pass
        
        
class ScreenWidgets:
    
    def makeSensorsList(self):
        print("ScreenWidgets.makeSensorsList")
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
        print("ScreenWidgets.getWidgetsTypeList")
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
        print("ScreenWidgets.saveConfig",self.wConfig)
        
        for s in self.wConfig:
            for w in s:
                w['obj'] = ''
                
        print("-------------------------------------------")
        print(self.wConfig)
        
        print("save config Widgets res:",
              DataSR_save(self.wConfig, self.wConfigPath)
              )
    
    def setGui(self, gui):
        print("ScreenWidgets.setGui")
        #b = Builder.load_file('MyScatterWidget.kv')
        #self.w = MyWidgets()
        
        #sys.exit(0)
        
        self.flSize = ObjectProperty([.0,.0])
        self.btActionText = ObjectProperty("+")
        
        
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
        #self.clockUWFS = None
        
        
        #self.makeSensorsList()
        
        self.s = MyScatterWidgetOnScatter(
            pos=(-100,-100),
            size=(1,1),
            size_hint=(None,None),
            )
        
        
        self.buildW()
        return 0
    
    
        
        aeoueaou= '''
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
       
    def bindScatter(self):
        self.s.bind(pos = self.updateWidgetFromScatter)
        self.s.bind(scale = self.updateWidgetFromScatter)
        self.s.bind(rotation = self.updateWidgetFromScatter)
        
    def unbindScatter(self):
        self.s.unbind(pos = self.updateWidgetFromScatter)
        self.s.unbind(scale = self.updateWidgetFromScatter)
        self.s.unbind(rotation = self.updateWidgetFromScatter)
        
    def rebuildWs(self,a='',b=''):
        print("ScreenWidgets.rebuildWs")
        
        print("--- so cleanAll !!")
        self.cleanAll()
        print("--- so cleanAll !! DONE")
        
        print("--- so build !!")
        self.buildW()
        print("--- so build !! DONE")
        self.updateIt()    
        
        
        
    def cleanAll(self,a='',b=''):
        print("ScreenWidgets.cleanAll")
        if self.editMode:
            print("is in edit mode exiting ...")
            self.on_btEdit()
        
        print("goint by widgets in wConfig")
        for s in self.wConfig:
            for w in s:
                obj = w['obj']
                print("widget",w['objName'])
                p = obj.parent
                print("remove from parent [",p,"]...")
                if p == None:
                    break
                p.remove_widget(obj)
                print("remove callbacks...")
                for cal in w['callback']:
                    print("sensor",cal)
                    unSub = "self.gui.sen.{}.removeCallBack(obj)".format(cal)
                    #print("go with:",unSub)
                    exec(unSub)
                w['obj'] = None
        
        
        print("chk on scatter ...")
        parent = self.s.parent
        if parent == None:
            print("no parent")
        else:
            parent.remove_widget(self.s)
            
        
        print("going by nav bt's...")
        for bt in self.navBts:
            p = bt.parent
            p.remove_widget(bt)
        
        print("so now fls...")
        for fl in self.fls:
            p = fl.parent
            p.remove_widget(fl)
        
        
        self.gui.rl.current = "Widgets"
        print("so now screens...")
        for scr in self.screenObjs:
            self.gui.rl.remove_widget(scr)
            
            
        print("DONE")
        #sys.exit(0)
        
    def buildW(self):
        print("ScreenWidgets.buildW")
        
        print("- screens now count is",self.screens)
        self.fls = []
        self.screenObjs = []
        self.flsOrgs = []
        self.navBts = []
        self.navAddBts = []
        for si in range(self.screens):
            screen = Screen(name="Widgets%s"%si)
            self.screenObjs.append(screen)
            self.flsOrgs.append(None)
            fl = FloatLayout()
            fl.bind(size=self.flChangeSize)
            self.fls.append(fl)
            #fl.add_widget(Label(text="widgets%s"%si))
            self.flsOrgs[si] = fl.on_touch_down 
            #fl.on_touch_down = self.on_touch
            screen.add_widget(fl)
            
            try:
                self.setUpGui( si, fl , self.wConfig[si])
            except:
                self.setUpGui( si, fl , [])
            
            self.gui.rl.add_widget(screen)
        
        print("    DONE")
           
        
        
    def flChangeSize(self,a='',b=''):
        print("flChangeSize",a,"\n",b)
        self.flSize = b
        y = b[1]-self.gui.btH
        for b in self.navBts:
            b.y = y
      
    def addWidgetOnScreen(self, wObj, callbaks=None):
        print("ScreenWidgets.add widget on screen",wObj)
        
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
        
        
        tScreen = self.screen 
        self.rebuildWs()
        self.gui.screenChange(("Widgets%s"%tScreen))
        
         
        
    def updateWidgetFromScatter(self,a=0,b=0):
        print("ScreenWidgets.updateWidgetFromScatter")
        if self.gui.rl.current[:7] != "Widgets":
            print("EE - should not work !!!!")
            self.on_btEdit()
        
        if self.editMode:
            
            o = self.widgetEdit
            i = self.widgetEditI
            s = self.s
            #print("s.pos",s.pos)
            #try:
            o.setPos( [s.center_x,s.center_y] )
            o.setScale( s.scale )
            o.setRot( s.rotation )
            self.wConfig[self.screen][i]['pos'] = o.pos
            self.wConfig[self.screen][i]['scale'] = o.scale
            self.wConfig[self.screen][i]['rotation'] = o.rotation
            o.updateIt()
            #except:
            #    print("EE - static widget no set POS")
        else:
            pass
            #if self.clockUWFS != None:
            #    self.clockUWFS.cancel()
            #    self.clockUWFS = None
       
    def debOnTouchWhatWhat(self):
        print("on_touch_---------------------")
        for ss in range(self.screens):
            print('''screen{0}: 
    fls[{0}]:    {1}
    in org:    {2}'''.format(
                ss, 
                self.fls[ss].on_touch_down,
                self.flsOrgs[ss]))
        print("------------------------------")
       
    def updateIt(self,a='',b=''):
        print("ScreenWidgets.updateIt")
        self.debOnTouchWhatWhat()
        if self.gui.rl.current == "Widgets":
            self.gui.screenChange("Widgets0")
            return 0
        
        
        
        print("current screen:",self.gui.rl.current[7:])
        self.screen = int(self.gui.rl.current[7:])
        print("wConfig",self.wConfig)
        print("len",len(self.wConfig))
        print("screen",self.screen)

        if len(self.wConfig) > self.screen:
            print("updating widgets on screen...")
            for w in self.wConfig[self.screen]:
                o = w['obj']
                try:
                    o.updateIt()
                except:
                    pass
        else:
            print("EE - nothing to update :( no widgets in screen",self.screen)
        
        
    def clikOn(self, clickPos, opos, osize):
        print("ScreenWidgets.clickOn")
        if 0 :print("""        cpos: {}
        opos: {}
        osize:{}""".format(
            clickPos, opos, osize
            ))
        if( clickPos[0]>=opos[0] 
                    and clickPos[0]<= (opos[0]+osize[0]) 
                    and clickPos[1]>=opos[1]
                    and clickPos[1]<= (opos[1]+osize[1])
            ):
            return True
        else:
            return False
        
    def navBtChk(self, pos):
        print("ScreenWidgets.navBtChk")
        btH = self.gui.btH
        y = self.flSize[1]-self.gui.btH
        
        if self.clikOn(pos,[0.0,y],[btH,btH]):
            print("    clikc on <")
            self.on_screenLeft()
            return True
        
        if self.clikOn(pos,[2*btH,y],[btH,btH]):
            print("    clikc on >")
            self.on_screenRight()
            return True
            
        if self.clikOn(pos,[1*btH,y],[btH,btH]):
            print("    clikc on +")
            self.startAddWidgetDialog()
            return True
        
        
        return False
        
    def on_touch(self,a=0):
        print("screeWidgets.on_touch screen:",self.screen)
        pos = a.pos
        btH = self.gui.btH
        
        
        self.debOnTouchWhatWhat()          
        
        if self.navBtChk(pos):
            return True
        
        print("    pos ",a.pos," -------------------")
        
        if len(self.wConfig) <= self.screen:
            return False
        
        for i,w in enumerate(self.wConfig[self.screen]):
            o = w['obj']
            print("screen:",self.screen," widget nr:",i," objName:",w['objName'])
            if 1:
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
                    
                    for bt in self.navAddBts:
                        bt.text = "-"
                        bt.on_release = self.on_removeWidget
                    
                    
                    addS = True
                    try:
                        s = self.s
                        par = self.s.parent
                        if par:
                            if self.sIsOnScreen != self.screen:
                                par.remove_widget(s)
                                addS = True
                            else:
                                addS = False
                                
                            
                        else:
                            print("EE - no parent :/")
                            #sys.exit(9)
                        
                    except:
                        
                        print("DONE")
                    
                    if addS:
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
                    self.bindScatter()
                    self.editMode = True
                    
                    #if self.clockUWFS == None:
                    #    self.clockUWFS = Clock.schedule_interval( self.updateWidgetFromScatter,0.1)
                    
                    
                    return False
                
            
                        
        
        return False
        
    def on_removeWidget(self,a='',b=''):
        print("ScreenWidgets.on_removeWidget")
        print("remove obj from screen ",self.screen)
        print("widgetEdit",self.widgetEdit)
        
        self.q = QueryPopup()
        self.q.setAction(
            "Remove widget", 
            "Really remove widget: %s"%self.widgetEdit,
            None, "Cancel", 
            self.on_removeWidgetConfirme, "Remove" 
        )
        self.q.run()
        
    def on_removeWidgetConfirme(self,a='',b=''):
        print("on_removeWidgetConfirme")
        print("looking for object in wConfig")
        for si,s in enumerate(self.wConfig):
            print("screen",si)
            for wi,w in enumerate(s):
                print("widget",wi," -> ",w['objName'])
                if w['obj'] == self.widgetEdit:
                    self.cleanAll()
                    self.wConfig[si].pop(wi)
                    tScreen = self.screen
                    self.buildW()
                    self.gui.screenChange("Widgets%s"%tScreen)
                    return True
        
    def on_btEdit(self,a=''):
        print("ScreenWidgets.on_btEdit")
        if self.editMode:
            print("    setting to !edit")
            for bt in self.navAddBts:
                bt.text = "+"
                bt.on_release = None
            
            self.unbindScatter()
            self.fls[self.screen].on_touch_down = self.on_touch
            self.editMode = False
            self.s.pos = [0,0]
            self.s.size = [0,0]
            self.s.scale = 1.0
            self.s.rotation = 0.0
        else:
            print("    it's !edit")
        
    def on_bgRelease(self,a='',b=''):
        print("ScreenWidgets.on_bgRelease")
        if self.editMode == True:
            self.on_btEdit(a)
            return True
        
    def setPSR(self,obj,val):
        print("ScreenWidgets.setPSR")
        obj.setPos( val['pos'] )
        obj.setScale( val['scale'] )
        obj.setRot( val['rotation'] )
        return obj
        
    def setUpGui(self, screen, bWidget, widgets):  
        print("ScreenWidgets.setUpGui ",bWidget," widgets\n",widgets)      
        btEdit = Button(
            background_color = (1,.1,.1,0.5)
            )
        btEdit.bind( on_release = self.on_btEdit)
        bWidget.add_widget(btEdit)
        
        #self.flsOrgs[screen] = bWidget.on_touch_down
        bWidget.on_touch_down = self.on_touch
        
        
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
    
    
    
    def on_screenLeft(self,a=''):
        print("ScreenWidgets.on_screenLeft")
        self.on_btEdit()
        s = self.screen-1
        if s < 0:
            s = self.screens-1
        self.screen = s
        self.gui.screenChange( "Widgets%s"%s )
        
    def on_screenRight(self,a=''):
        print("ScreenWidgets.on_screenRight")
        self.on_btEdit()
        s = self.screen+1
        if s >= self.screens:
            s = 0
        self.screen = s
        self.gui.screenChange( "Widgets%s"%s )
        
    def startAddWidgetDialog(self,a=''):
        print("ScreenWidgets.on_screenLeft")
        self.WAEDV = WidgetsAEDV(self)
        self.WAEDV.startWizard()
            
    
    def addNavBts(self, w):
        print("ScreenWidgets.addNavBts")
        print("w",w)
        print("w.pos",w.pos)
        print("w.size",w.size)
        
        wp = w.parent
        print("wp",wp)
        print("wp.pos",wp.pos)
        print("wp.size",wp.size)
        
        rl = self.gui.rl
        print("rl",rl)
        print("rl.pos",rl.pos)
        print("rl.size",rl.size)
        
        #sys.exit()
        btAdd = Button(
            text="<",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            #on_release=self.on_screenLeft
            y = 0
            )
        w.add_widget(btAdd)
        self.navBts.append(btAdd)
        
        
        
        btAdd = Button(
            text="+",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            #on_release=self.startAddWidgetDialog
            )
        w.add_widget(btAdd)
        #btAdd.top = self.gui.btH
        btAdd.x = self.gui.btH
        self.navBts.append(btAdd)
        self.navAddBts.append(btAdd)
        
        btAdd = Button(
            text=">",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            #on_release=self.on_screenRight
            )
        w.add_widget(btAdd)
        btAdd.x = self.gui.btH*2.0
        self.navBts.append(btAdd)
    
    
    def on_widRel(self,nr):
        print("ScreenWidgets.on_widRel",nr)     
        
    
        