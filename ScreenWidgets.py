from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from Widget_cn import Widget_cn
from ScreenCompass import ScreenCompass
from ScreenRace import ScreenRace
import sys
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from Widget_cnDiff import Widget_cnDiff
from WidgetBubble import WidgetBubble

class MSLabel(Label):
    pass

class MyScatterWidgetOnScatter(Scatter):
    pass

class Widget_n:
    
    def __init__(self, title, callback, valk, unit, round_ ):
        self.title = title
        self.callback = callback
        self.valk = valk
        self.unit = unit
        self.round = round_
        
        self.bl = BoxLayout(orientation="vertical")
        
        self.bl.bind(on_release=self.on_release)
        
        title = MSLabel(text = self.title )
        self.l = MSLabel(text=self.title)
        
        self.bl.add_widget(title)
        self.bl.add_widget( self.l )
        
    def on_release(self, obj):
        print("on_release title:",self.title)
        
    def getWidget(self):
        print("getWidget",self.title)
        return self.bl
    
    def setGui(self, gui):
        self.gui = gui
        
    def update(self, fromWho, vals):
        #print("update from widget_n[{}] from:{} callback:{} gotvals:{}".format(
        #    self.title, fromWho, self.callback, vals
        #    ))
        if fromWho == self.callback:
            
            if self.callback == 'comCal':
                vals = {
                    self.valk: vals
                    }
            
            self.l.text = str( "%s %s"%( 
                round( vals[self.valk], self.round ) if self.round > 0 else int( vals[self.valk] ), self.unit 
                ) )
        
        
class ScreenWidgets:
    
    def setGui(self, gui):
        #b = Builder.load_file('MyScatterWidget.kv')
        #self.w = MyWidgets()
        
        #sys.exit(0)
        self.gui = gui
        self.editMode = False
        
        nSOG = Widget_cn()
        nSOG.setValues('SOG', 'gps', 'speed', 'kts', 1,4)
        
        nCOG = Widget_cn()
        nCOG.setValues('COG', 'gps', 'bearing', '`', 0,4)
        
        cnHDG = Widget_cn()
        cnHDG.setValues('HDG', 'comCal', 2, '`', 1, 4)
        
        cnHeel = Widget_cn()
        cnHeel.setValues('heel', 'orientation', 4, '`', 0, 3)
        
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
                'name': "nCOG",
                'obj': nCOG,
                'callback': ['gpsD']
                },
            {   
                'name': "cnHDG",
                'obj': cnHDG,
                'callback': ['comCal']
                },
            {   
                'name': "heel",
                'obj': cnHeel,
                'callback': ['orientation']
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
        a = '''    {
                'name': 'SOGText',
                'obj': WidgetSOG(),
                'callback': ['gpsD']
                }
            ]'''
        a = '''{
                'name': 'ScreenRace',
                'obj': ScreenRace(),
                'callback': ['gpsD']
                },'''
        
        #self.setUpGui()
        
        
    def updateWidgetFromScatter(self,a=0):
        Clock.schedule_once( self.updateWidgetFromScatter,0.1)
        
        if self.editMode:
            o = self.widgetEdit
            print("self.s.pos",self.s.pos)
            try:
                o.setPos( [self.s.center_x,self.s.center_y] )
                o.setScale( self.s.scale )
                o.setRot( self.s.rotation )
            except:
                print("EE - static widget no set POS")
        
    def on_touch(self,a=0):
        print("screeWidgets.on_touch")
        print("    pos ",a.pos)
        pos = a.pos
        
        for i,w in enumerate(self.widgets):
            o = w['obj']
            print("widget nr",i)
            try:
                osize = o.getSize()
                print("    pos",o.pos," size",o.size," getSize", osize)
                try:
                    print(o.mtitle)
                except:
                    pass
                
                opos = [o.pos[0]-osize[0]*.5, o.pos[1]-osize[1]*.5]
                
                if( pos[0]>=opos[0] 
                    and pos[0]<= (opos[0]+osize[0]) 
                    and pos[1]>=opos[1]
                    and pos[1]<= (opos[1]+osize[1])
                    ):
                    print("klik!!")
                    self.widgetEdit = o
                    self.gui.rl.ids.bl_wid.on_touch_down = self.org_on_touch_down
                    self.s.size = osize
                    self.s.scale = o.scale
                    self.s.rotation = o.rotation
                    self.s.center_x = o.pos[0]
                    self.s.center_y = o.pos[1]
                    self.editMode = True
                    return False
                
            except:
                print("ee - no pos  or size")
        
        return False
        
    def on_btEdit(self,a=''):
        print("on_btEdit")
        self.gui.rl.ids.bl_wid.on_touch_down = self.on_touch
        self.editMode = False
        self.s.pos = [0,0]
        self.s.size = [0,0]
        self.s.scale = 1.0
        self.s.rotation = 0.0
        
        
    def setUpGui(self):
        
        btEdit = Button()
        btEdit.bind( on_release = self.on_btEdit)
        self.gui.rl.ids.bl_wid.add_widget(btEdit)
        
        self.org_on_touch_down = self.gui.rl.ids.bl_wid.on_touch_down
        self.gui.rl.ids.bl_wid.on_touch_down = self.on_touch
        
        b = Builder.load_file('MyScatterWidget.kv')

        self.s = MyScatterWidgetOnScatter(
            pos=(-100,-100),
            size=(1,1),
            size_hint=(None,None),
            )
    
        self.gui.rl.ids.bl_wid.add_widget(self.s)
        for i,w in enumerate( self.widgets ):
            
            bl = BoxLayout(
                orientation = "vertical",
                padding = 5,
                spacing = 5
                )
            print("building widget [",w['name'],"]")
            o = w['obj']
            o.setGui(self.gui)
            
            
            self.gui.rl.ids.bl_wid.add_widget( o.getWidget() )
            osize = o.getSize()
            try:
                o.setPos([ osize[0]*.5, 150+i*(self.gui.lineH*2.0) ])
            except:
                print("EE - no setPos")
            #bl.add_widget(o.getWidget())
            
            
            print("\- - adding callbacks:")
            for c in w['callback']:
                print(c)
                eval("self.gui.sen.%s.addCallBack(o)"%(
                    c
                    ))
                
            #s.ids.bl_sca.add_widget(o)
            
        self.updateWidgetFromScatter()
       
    def on_widRel(self,nr):
        print("on_widRel",nr)     
        
    def oyoeoio(self):
        
        self.compass = ScreenCompass()
        self.compass.setGui(self.gui)
        
        self.gui.sen.gpsD.addCallBack( self.compass )
        self.gui.sen.comCal.addCallBack( self.compass )
        self.gui.sen.comCalAccelGyro.addCallBack( self.compass )
        
        s = MyScatterWidget(
            size=(400,400),
            size_hint=(None,None)
            )
        bl.add_widget( s )
        s.ids.bl_sca.add_widget( self.compass, index = 0)
        self.compass.pos = [100,50]
        print("compass pos :",self.compass.pos)        
        
        