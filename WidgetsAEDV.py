from QueryPopup import QueryPopup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image as uixImage
from kivy.loader import Loader
from kivy.uix.spinner import Spinner
from Widget_n import MSLabel
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import cm


import sys
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from MyLabel import MyLabel

class WidgetsAEDV:
    
    def __init__(self,screenWidgets):
        self.sw = screenWidgets
        self.gui = self.sw.gui
        
        self.actionType = ""
        
    def startWizard(self):
        self.actionType = 'start'
        
        self.buildGuiForAction()
        
        
    def buildGuiForAction(self):
        print("build gui for action ", self.actionType)
        
        if self.actionType == 'start':
            
            bl = BoxLayout(orientation='vertical')
            #bl.add_widget(Button(
            #    text="rebuild!",
            #    on_release=self.sw.rebuildWs
            #    ))
            bl.add_widget(
                Label(
                    text="Awalable widgets to add to screen:",
                    size_hint = [None, None],
                    height = cm(1)
                    )
                )
            wl = self.sw.getWidgetsTypeList()
            for w in wl:
                print("w",w)
                
                bv = BoxLayout(
                    orientation="horizontal",
                    height = self.gui.btH,
                    width = bl.width,
                    size_hint = [None,None]
                    )
                bl.add_widget(bv)
                
                b = Button(
                    text = w['name'],
                    #height = self.gui.btH,
                    size_hint = [None,None],
                    on_release=self.on_start_addW,
                    size = [cm(3.0),cm(1.0)]
                    )
                bv.add_widget(b)
                ki = uixImage( 
                    source = ("icons/%s"%w['thumb']),
                    size_hint = [None,None],
                    size = [cm(3.0),cm(1.0)] 
                    )
                bv.add_widget(ki)
                #bv.add_widget(ki)
                
                
                print("3")
            
            
            self.q = QueryPopup()
            self.q.setAction(
                "Widgets wizard", 
                bl,
                None, "Cancel", 
                self.on_start_remove, "Remove One" 
                )
            self.q.run()
        
    def getWByName(self,name):
        wl = self.sw.getWidgetsTypeList()
        for w in wl:
            if name == w['name']:
                return w
        return None
                
            
    def on_start_addW(self,w):
        print("on_start_addW",w.text)
        wName = w.text
        self.actionType = "addW %s"%wName
        
        dw = self.getWByName(wName)
        
        self.q.dismiss()
        
        print("working on ",dw['obj'])
        obj = dw['obj']
        self.settingUpWidget = dw
        if obj.settingsNeedIt() == False:
            print("no need for more steps ")
            self.sw.addWidgetOnScreen(dw)
        else:
            print("it need settings step !")
            
            q = QueryPopup()
            q.size_hint = [.8,.97]
            
            
            bl = BoxLayout(
                orientation="vertical"
                )
            q.setAction("Set it up:", 
                bl, 
                self.on_widgetSetUpDone, "Add", 
                q.dismiss, "Cancel"
                )
            #sv.height = 5000
            
            l0 = MSLabel(text="Widget settings:")
            bl.add_widget(l0)
            bl = obj.addSettingsDialogPart(bl)
            
            srcSett = False
            try:
                aoeuoeu = obj.wvfh
                srcSett = True
            except:
                pass
            if srcSett:
                l1 = MSLabel(text="Source settings:")
                bl.add_widget(l1)
                bl = obj.wvfh.makeSourceSettingsPart(
                    bl,
                    self.gui.sen.sensorsList
                    )
            
            q.run()
    
                
    def on_widgetSetUpDone(self,a='',b=''):
        print("on_widgetSetUpDone")
        
        print("settingUpWidget",self.settingUpWidget)
        o = self.settingUpWidget 
        obj = o['obj']
        srcSett = False
        wvfh = 'direct'
        try:
            aoeuoeu = obj.wvfh
            srcSett = True
            
        except:
            pass
        if srcSett:
            wvfh = obj.wvfh.getSettingsFromWidgetsToDict() 
        
        atr = obj.getAttrFromDialog()
        print("atr",atr)
        print("wvfh",wvfh)
        if srcSett:
            callback = wvfh['callback']
        else:
            callback = obj.getCallbacks()
        
        #sys.exit()
        
        if len(self.sw.wConfig)<=self.sw.screen:
            print("adding first widget on screen !",self.sw.screen)
            self.sw.wConfig.append([])
        self.sw.wConfig[self.sw.screen].append({
            'name': o['name'],
            'obj': o['obj'],
            'objName': o['objName'],
            'callback': callback,
            'atr':atr,
            'valHandler': wvfh,
            'pos': [100,100],
            'rotation' : 0.0,
            'scale': 1.0
            })
        
        print("-----------------------------------")
        print(self.sw.wConfig)
        self.sw.saveConfig()
        #sys.exit(9)
        
        tScreen = self.sw.screen 
        self.sw.rebuildWs()        
        self.sw.gui.screenChange(("Widgets%s"%tScreen))
        
    def on_selectSensor(self,a='',b=''):
        print("on_selectSensor",a," || ",b)
        
    def on_next_setup_widget(self):
        print("on_next_setup_widget")
        self.actionType = "step2"
            
    def on_start_remove(self):
        print("on_start_remove TODO")
        
        