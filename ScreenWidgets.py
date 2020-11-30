from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, FadeTransition
from kivy.properties import ObjectProperty

from WidgetsAEDV import WidgetsAEDV

from Widget_cn import Widget_cn
from Widget_niddle import Widget_niddle
from ScreenCompass import ScreenCompass
from WidgetBubble import WidgetBubble

from FileActions import FileActions
from DataSaveRestore import DataSR_save, DataSR_restore
from QueryPopup import QueryPopup

from functools import partial
import sys
from kivy.uix.bubble import Bubble
from Widget_circularProgress import Widget_circularProgress
from kivy.animation import Animation, AnimationTransition



Builder.load_file('layoutScatterForWidget.kv')

# /usr/local/share/kivy-examples/demo/pictures


class MyScatterWidgetOnScatter(Scatter):
    pass
      
      
class ScatterForWidget(Scatter):
    widgetSize = ObjectProperty([200,200])
    
class bubbleRemEdit(Bubble):
    widgetPos = ObjectProperty([0,0])
    destroyTimer = None
    deb = False
    
    def setPosForWidget(self,sfw='',pos=''):
        if self.deb: print("setPosForWidget")
        self.widgetPos = [
            pos[0],
            pos[1]+(sfw.size[1]*sfw.scale)
            ]
    
    def startTimer(self,sw, timeOut):
        self.sw = sw
        if self.destroyTimer != None:
            try:
                Clock.unschedule(self.destroyTimer)
            except:
                pass
            
        self.destroyTimer = Clock.schedule_once(self.hideIt, timeOut)
        
    def hideIt(self,a='',b=''):
        if self.deb: print("bubble hideIT!!")
        
        if self.destroyTimer != None:
            try:
                Clock.unschedule(self.destroyTimer)
            except:
                pass
        
        self.widgetPos = [-1000,0]  
        
        
    def on_remove(self):
        if self.deb: print("on_remove")
        self.hideIt()
        self.sw.on_removeWidget()
        
    def on_edit(self):
        if self.deb: print("on_edit")
        self.hideIt()
        self.sw.on_editWidget()
    
    
    
    
    
        
class ScreenWidgets:
    deb = False

    def __init__(self,gui):
        self.gui = gui
    
    def makeSensorsList(self):
        if self.deb: print("ScreenWidgets.makeSensorsList")
        sl = self.gui.sen.sensorsList
        if self.deb: print("have now: ",len(sl)," sensors registered")
        for s in sl:
            if self.deb: print('''    sensor: {}        class:{}
        values: {}
        '''.format(
                s.getTitle(), type(s), s.getValuesOptions()
                ))
            
         
        #sys.exit(0)
        
    def solveScrolSize(self, bl):
        #bl = bl.parent
        hs = 0.0
        try:
            bl = bl.children[0]
        except:
            self.deb: print("EE - no children[0]")
        if self.deb: print("type",type(bl))
        if self.deb: print("children count",len(bl.children))
        if self.deb: print("parent type",type(bl.parent))
        
        for c in bl.children:
            
            hs+= c.height
        #self.queryWidget.size = [self.queryWidget.size[0],hs+cm(1)]
        return [bl.size[0],hs+self.gui.btH]
            
        
        
    def getWidgetsTypeList(self):
        if self.deb: print("ScreenWidgets.getWidgetsTypeList")
        return self.widgetsTypeList
    
    def updateValsInWConfig(self,si='',wi='',sfw='', c =''):
        #if self.deb: print("updateValsInWConfig si",si," wi",wi,"\n    sfw",sfw,"\n    c",c)
        posScale = self.pixelToScreenScale(list(sfw.pos))
        try:
            oScaleToScreen = self.wConfig[si][wi]['oScaleToScreen']
        except:
            oScaleToScreen = 1.0
        self.wConfig[si][wi]['pos'] = posScale#list(sfw.pos)
        self.wConfig[si][wi]['scale'] = sfw.scale/ oScaleToScreen
        self.wConfig[si][wi]['rotation'] = sfw.rotation
        self.bubble.startTimer(self,self.bubbleTimeOut)
        
        
    def saveConfig(self):
        if self.deb: print("ScreenWidgets.saveConfig")#,self.wConfig)
        
        if self.deb: print(" clean stuff befoare save to file")
        for s in self.wConfig:
            for w in s:
                w['obj'] = ''
                
        #if self.deb: print("-------------------------------------------")
        #if self.deb: print(self.wConfig)
        #if self.deb: print("-------------------------------------------")
        
        #res = DataSR_save(self.wConfig, self.wConfigPath)
        res = self.fa.pickleMake(self.wConfig, self.wConfigPath, makeAsList=False)
        if self.deb: print("save config Widgets res:",res)
        return res

    def setGui(self,a='',b=''):
        if self.deb: print("ScreenWidgets.setGui")
        self.flSize = ObjectProperty([.0,.0])
        
        
        self.widgetsTypeList = [
            {   'name': "Numeric",
                'obj': Widget_cn(),
                'objName': 'Widget_cn',
                'thumb': 'widget_numeric.png'
                },                
            {   'name': 'Bubble',
                'obj': WidgetBubble(),
                'objName': 'WidgetBubble',
                'thumb': 'widget_bubble.png'
                },
            {   'name': 'Niddle guage',
                'obj': Widget_niddle(),
                'objName': 'Widget_niddle',
                'thumb': 'widget_niddle.png'
                },
            {   'name': "Compass",
                'obj' : ScreenCompass(),
                'objName': 'ScreenCompass',
                'thumb': 'widget_compass.png' 
                },
            {   'name': "Circular progress",
                'obj' : Widget_circularProgress(),
                'objName': 'Widget_circularProgress',
                'thumb': 'widget_niddle_circular.png' 
                },
            ]
        
        
        self.fa = FileActions()
        self.wConfigPath = self.fa.join(
            self.gui.homeDirPath, 
            'ykpilotWidgets.conf'
            )
        if self.fa.isFile(self.wConfigPath) == False:
            if self.deb: print("screen widgets no config file setting default")
            self.wConfig = [[{
                'name': 'ScreenCompass',
                'obj': "",
                'objName': 'ScreenCompass',
                'callback': ['gpsD','comCal', 'comCalAccelGyro'],
                'pos': [0.0,0.0],
                'scale':1.0,
                'rotation':0.0
                }
                ]]
        else:
            if self.deb: print("screen widgets resuming config")
            self.wConfig = self.fa.pickleLoad(self.wConfigPath)#DataSR_restore(self.wConfigPath)
            if self.deb: print(self.wConfig)
            if self.deb: print("------------------------------") 
            #sys.exit(0)

        self.screen = 0
        self.screens = len(self.wConfig)+1
        self.bubble = None
        self.bubbleTimeOut = 5.0
        self.goFullscreenIn = 8.0
        #self.gui = gui
        self.editMode = False
        #self.clockUWFS = None
        self.WAEDV = WidgetsAEDV(self)
        
        
        self.buildW()
        return 0
    
    
    def screenBack(self,a='',b=''):
        self.gui.screenChange("Widgets{}".format(self.screen))
    
    def getWeObj(self,si,wi):
        return self.getWe(si,wi)['obj']
    
    def getWe(self,si,wi):
        return self.wConfig[si][wi]
    
    def on_widgetReleased(self, screen='', wi='', sfw='',d=''):
        if self.deb: print("on_widgetReleased")
        colision = sfw.collide_point(d.pos[0],d.pos[1]) 
        if colision:
            rot = self.wConfig[screen][wi]['rotation']%360.0
            if self.deb: print("ok do correction!")
            if self.deb: print("rotation of widget is",rot)
            
            if rot < 10.0 or rot > 350.0:
                if self.deb: print("set 0.0")
                self.wConfig[screen][wi]['rotation'] = 0.0
                
            elif rot > 80.0 and rot < 100.0:
                if self.deb: print("set 0.0")
                self.wConfig[screen][wi]['rotation'] = 90.0
                
            elif rot > 170.0 and rot < 190.0:
                if self.deb: print("set 0.0")
                self.wConfig[screen][wi]['rotation'] = 180.0
                
            elif rot > 260.0 and rot < 280.0:
                if self.deb: print("set 0.0")
                self.wConfig[screen][wi]['rotation'] = 270.0
                
            #sfw.rotation = self.wConfig[screen][wi]['rotation']
            if self.gui.animation:
                Animation.cancel_all(sfw,'rotation')
                r = self.wConfig[screen][wi]['rotation']
                #if self.deb: print("rotation sfw.rotation",sfw.rotation," to ",r)
                
                if (sfw.rotation-r)>180.0:
                    r+= 360.0
                     
                    
                anim = Animation(
                    rotation=r,
                    t='out_quad' 
                    )
                anim.start( sfw )
                
            else:
                sfw.rotation = self.wConfig[screen][wi]['rotation']
            
            
    def pixelToScreenScale(self,xy):
        x = xy[0]/self.gui.windowSize[0]
        y = xy[1]/self.gui.windowSize[1]
        return [x,y]
    
    def screenScaleToPixel(self, xyScale):
        x = xyScale[0]*self.gui.windowSize[0]
        y = xyScale[1]*self.gui.windowSize[1]
        return [x,y]
        
            
    def on_widgetSelected(self,screen='',wi='',sfw='',d=''):
        if self.deb: print("on_widgetSelected d",d)
        if self.deb: print("    ->pos",d.pos)
        colision = sfw.collide_point(d.pos[0],d.pos[1]) 
        if colision == False:
            return False
        
        #self.widgetEdit = self.wConfig[screen][wi]['obj']
        self.widgetEdit = {
            'screen': screen,
            'wi': wi
            } 
        weObj = self.getWeObj(screen,wi)
        
        if self.deb: print("    -> ",weObj)
        if self.deb: print("    -> col",colision)
        
        try:
            sfw = weObj.parent
        except:
            sfw = weObj.getWidget().parent
        fl = sfw.parent
        
        if self.bubble == None:
            self.bubble = bubbleRemEdit()
        else:
            p = self.bubble.parent
            p.remove_widget(self.bubble)
            
        self.bubble.startTimer(self,self.bubbleTimeOut)
        sfw.bind(pos=self.bubble.setPosForWidget)
        self.bubble.setPosForWidget(sfw, sfw.pos)
        
        fl.add_widget(self.bubble) 
       
    def bindScatter(self,sfw, si, wi):
        sfw.bind(pos=partial(self.updateValsInWConfig,si,wi))
        sfw.bind(scale=partial(self.updateValsInWConfig,si,wi))
        sfw.bind(rotation=partial(self.updateValsInWConfig,si,wi))
        sfw.bind(on_touch_down=partial(self.on_widgetSelected,si,wi))
        sfw.bind(on_touch_up=partial(self.on_widgetReleased,si,wi))
        
        
    def unbindScatter(self, sfw, si,wi):
        sfw.unbind(pos=partial(self.updateValsInWConfig,si,wi))
        sfw.unbind(scale=partial(self.updateValsInWConfig,si,wi))
        sfw.unbind(rotation=partial(self.updateValsInWConfig,si,wi))
        sfw.unbind(on_touch_down=partial(self.on_widgetSelected,si,wi))
        sfw.unbind(on_touch_up=partial(self.on_widgetReleased,si,wi))
        
    def rebuildWs(self,a='',b=''):
        if self.deb: print("ScreenWidgets.rebuildWs")
        tScreen = self.screen 
        if self.deb: print("--- so cleanAll !!")
        self.cleanAll()
        if self.deb: print("--- so cleanAll !! DONE")
        
        if self.deb: print("--- so build !!")
        self.buildW()
        if self.deb: print("--- so build !! DONE")
        self.updateIt()    
        self.gui.screenChange(("Widgets%s"%tScreen))
        
        
        
    def cleanAll(self,a='',b=''):
        if self.deb: print("ScreenWidgets.cleanAll")
        if self.editMode:
            if self.deb: print("is in edit mode exiting ...")
            self.on_btEdit()
        
        if self.deb: print("goint by widgets in wConfig")
        for si,s in enumerate(self.wConfig):
            for wi,w in enumerate(s):
                obj = w['obj']
                
                if obj == "":
                    w['obj'] = None
                else:
                    if self.deb: print("widget ",w['objName'],' type',type(obj))
                    try:
                        p = obj.parent
                        obj2Remove = obj
                    except:
                        ot = obj.getWidget()
                        p = ot.parent
                        obj2Remove = ot
                    if self.deb: print("remove from parent [",p,"]...")
                    if p == None:
                        break
                    
                    if self.deb: print("remove from parent scatter")
                    p.remove_widget(obj2Remove)
                    pScater = p.parent
                    if self.deb: print("remove scater from fLayout")
                    pScater.remove_widget(p)
                    if self.deb: print("unbind scatter")
                    self.unbindScatter(p, si,wi)
                    
                    
                    if self.deb: print("remove callbacks...")
                    for cal in w['callback']:
                        if self.deb: print("sensor",cal)
                        unSub = "self.gui.sen.{}.removeCallBack(obj)".format(cal)
                        #if self.deb: print("go with:",unSub)
                        exec(unSub)
                    w['obj'] = None
        
        if self.deb: print("removing nav bt's...")
        for bt in self.navBts:
            p = bt.parent
            p.remove_widget(bt)
        
        if self.deb: print("removing fls...")
        for fl in self.fls:
            p = fl.parent
            p.remove_widget(fl)
        
        self.gui.rl.current = "Widgets"
        if self.deb: print("removing screens...")
        for scr in self.screenObjs:
            self.gui.rl.remove_widget(scr)
            
            
        if self.deb: print("DONE")
        #sys.exit(0)
        
    def buildW(self):
        if self.deb: print("ScreenWidgets.buildW")
        
        if self.deb: print("- screens now count is",self.screens)
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
            #self.flsOrgs[si] = fl.on_touch_down 
            #fl.on_touch_down = self.on_touch
            screen.add_widget(fl)
            
            try:
                self.setUpGui( si, fl , self.wConfig[si])
            except:
                self.setUpGui( si, fl , [])
            
            self.gui.rl.add_widget(screen)
            self.flChangeSize(b=fl.size)
        
        if self.deb: print("    DONE")
           
        
        
    def flChangeSize(self,a='',b=''):
        if self.deb: print("flChangeSize",a,"\n",b)
        self.flSize = b
        y = b[1]-self.gui.btH
        for b in self.navBts:
            b.y = y
      
    def addWidgetOnScreen(self, wObj, callback=None):
        if self.deb: print("ScreenWidgets.add widget on screen",wObj)
        
        if len(self.wConfig)<=self.screen:
            if self.deb: print("adding first widget on screen !",self.screen)
            self.wConfig.append([])
        
        self.wConfig[self.screen].append({
            'name': wObj['name'],
            'obj': "",
            'objName': wObj['objName'],
            'callback': wObj['obj'].getCallbacks(),
            'pos': [10,10],
            'scale':1.0,
            'rotation':0.0
            
            })
        
        '''
        self.wConfig[self.screen].append({
            'name': 'ScreenCompass',
            'obj': ScreenCompass(),
            'objName': 'ScreenCompass',
            'callback': ['gpsD','comCal', 'comCalAccelGyro'],
            'pos': [200,200],
            'scale':1.0,
            'rotation':0.0
            })'''
        
        #sys.exit(0)
        self.saveConfig()
        
        tScreen = self.screen 
        self.rebuildWs()
        self.gui.screenChange(("Widgets%s"%tScreen))
        
         
        
    def updateIt(self,a='',b=''):
        if self.deb: print("ScreenWidgets.updateIt")
        if self.gui.rl.current == "Widgets":
            self.gui.screenChange("Widgets0")
            return 0
        
        
        
        if self.deb: print("current screen:",self.gui.rl.current[7:])
        self.screen = int(self.gui.rl.current[7:])
        #if self.deb: print("wConfig",self.wConfig)
        #if self.deb: print("len",len(self.wConfig))
        #if self.deb: print("screen",self.screen)

        if len(self.wConfig) > self.screen:
            if self.deb: print("updating widgets on screen...")
            for w in self.wConfig[self.screen]:
                o = w['obj']
                try:
                    o.updateIt()
                except:
                    pass
        else:
            if self.deb: print("EE - nothing to update :( no widgets in screen",self.screen)
        
        
    def on_toggleFullScreen(self,a='',b=''):
        if self.deb: print("on_toggleFullScreen")
        if self.gui.ab.height > 0.0:
            self.gui_ab_height = self.gui.ab.height
            self.gui.ab.height = 0.0
        else:
            self.gui.ab.height = self.gui_ab_height
        
    
    def on_editWidget(self, a='',b=''):
        if self.deb: print("on_editWidget")
        if self.deb: print("widgetEdit",self.widgetEdit)
        #self.WAEDV = WidgetsAEDV(self)
        self.WAEDV.startEditWizard()
        
        
        
    def on_removeWidget(self,a='',b=''):
        if self.deb: print("ScreenWidgets.on_removeWidget")
        if self.deb: print("remove obj from screen ",self.screen)
        if self.deb: print("widgetEdit",self.widgetEdit)
        
        self.q = QueryPopup()
        self.q.setAction(
            "Remove widget", 
            "Really remove widget: %s"%self.widgetEdit,
            None, "Cancel", 
            self.on_removeWidgetConfirme, "Remove" 
        )
        self.q.run()
        
    def on_removeWidgetConfirme(self,a='',b=''):
        if self.deb: print("on_removeWidgetConfirme")
        if self.deb: print("looking for object in wConfig")
        for si,s in enumerate(self.wConfig):
            if self.deb: print("screen",si)
            for wi,w in enumerate(s):
                if self.deb: print("widget",wi," -> ",w['objName'])
                if [si,wi] == [self.widgetEdit['screen'], self.widgetEdit['wi']]:
                    self.cleanAll()
                    self.wConfig[si].pop(wi)
                    if self.deb: print("so widget removed. save new config")
                    self.saveConfig()
                    tScreen = self.screen
                    self.buildW()
                    self.gui.screenChange("Widgets%s"%tScreen)
                    return True
        
    def on_bgRelease(self,a='',b=''):
        if self.deb: print("ScreenWidgets.on_bgRelease")
        if self.editMode == True:
            self.on_btEdit(a)
            return True
        
    def setUpGui(self, screen, bWidget, widgets):  
        if self.deb: print("ScreenWidgets.setUpGui ")#,bWidget," widgets\n",widgets)      
        
        for i,w in enumerate( widgets ):
            if self.deb: print("building widget [",w['name'],"]")
            exec("widgets[i]['obj'] = %s()"%w['objName'])
            o = widgets[i]['obj']

            if w['objName'] != 'ScreenCompass':
                if self.deb: print("passing atr setting to Widget_cn or 'Widget_niddle or WidgetBubble")
                atr = w['atr']
                atr['screen'] = screen
                atr['valHandler'] = w['valHandler']
                o.setValuesFromDic(atr)
                if self.deb: print("    done")
            if self.deb: print("setGui")
            o.setGui(self.gui)
            
            if self.deb: print("add widget")
            
            oSize = o.getSize()
            self.wConfig[screen][i]['oSize'] = oSize
            oScaleToScreen = 1.0
            print("o.getSize",oSize)
            print("windowSize",self.gui.windowSize)
            if oSize[2] and oSize[3] == -1.0:
                print("by X scaling")
                screenPixInX = self.gui.windowSize[0]*oSize[2]
                print("screenPixInX",screenPixInX)
                oScaleToScreen = screenPixInX/oSize[0] 
                print("oSccaleToScreen",oScaleToScreen)
            elif oSize[3] and oSize[2] == -1.0:
                print("by Y scaling")
                screenPixInY = self.gui.windowSize[1]*oSize[3]
                print("screenPixInY",screenPixInY)
                oScaleToScreen = screenPixInY/oSize[1] 
                print("oSccaleToScreen",oScaleToScreen)
            
            self.wConfig[screen][i]['oScaleToScreen'] = oScaleToScreen
            
            
            
            sfw = ScatterForWidget(
                widgetSize = [oSize[0],oSize[1]]
                )
            sfw.rotation = self.wConfig[screen][i]['rotation']
            sfw.scale = self.wConfig[screen][i]['scale']*oScaleToScreen
            sfw.pos = self.screenScaleToPixel(
                self.wConfig[screen][i]['pos']
                )
            
            sfw.add_widget( o.getWidget() )
            self.bindScatter(sfw, screen,i)
            bWidget.add_widget( sfw )
            
            
       
            if self.deb: print("\- - adding callbacks:",w['callback'])
            for c in w['callback']:
                if c != '':
                    if self.deb: print("callback to:",c)
                    if c == 'gps':
                        if self.deb: print("changing gps to gpsD")
                        c = 'gpsD'
                    if self.deb: print("add it ....")
                    eval("self.gui.sen.%s.addCallBack(o)"%(
                        c
                        ))
                    if self.deb: print("    DONE")
                    #if self.deb: print("o",o)
                    #if self.deb: print("widgets[i]['obj']",widgets[i]['obj'])
                    #if self.deb: print("self.gui.sen.gps",self.gui.sen.gpsD.callBacksForUpdate)
        
        
        self.addNavBts( bWidget )          
        #self.updateWidgetFromScatter()
    
    
    
    def on_screenLeft(self,a=''):
        if self.deb: print("ScreenWidgets.on_screenLeft")
        #self.on_btEdit()
        s = self.screen-1
        if s < 0:
            s = self.screens-1
        self.screen = s
        self.gui.screenChange( "Widgets%s"%s )
        
    def on_screenRight(self,a=''):
        if self.deb: print("ScreenWidgets.on_screenRight")
        #self.on_btEdit()
        s = self.screen+1
        if s >= self.screens:
            s = 0
        self.screen = s
        self.gui.screenChange( "Widgets%s"%s )
        
    def startAddWidgetDialog(self,a=''):
        if self.deb: print("ScreenWidgets.on_screenLeft")
        #self.WAEDV = WidgetsAEDV(self)
        self.WAEDV.startWizard()
            
    
    def addNavBts(self, w):
        if self.deb: print("ScreenWidgets.addNavBts")
        navBtColor = ( .9, .0, .0, 0.6)
        
        #sys.exit()
        btAdd = Button(
            text="<",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            background_color = navBtColor,
            on_release = self.on_screenLeft
            )
        w.add_widget(btAdd)
        self.navBts.append(btAdd)
        
        btAdd = Button(
            text="+",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            background_color = navBtColor,
            on_release=self.startAddWidgetDialog
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
            background_color = navBtColor,
            on_release = self.on_screenRight
            )
        w.add_widget(btAdd)
        btAdd.x = self.gui.btH*2.0
        self.navBts.append(btAdd)
        
        btAdd = Button(
            text="F",
            size = [self.gui.btH,self.gui.btH],
            size_hint=(None,None),
            background_color = navBtColor,
            on_release=self.on_toggleFullScreen
            )
        w.add_widget(btAdd)
        btAdd.x = self.gui.btH*3.0
        self.navBts.append(btAdd)
    
    
         