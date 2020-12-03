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
from kivy.clock import Clock
from QueryPopup import QueryPopup

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
            bl.add_widget(MSLabel(text="Widgets wizard"))
            #bl.add_widget(Button(
            #    text="rebuild!",
            #    on_release=self.sw.rebuildWs
            #    ))
            bl.add_widget(
                Label(
                    text="Awalable widgets to add to screen:",
                    size_hint_y = None,
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
                    #width = cm(3.0),
                    height = cm(1.0)
                    )
                bv.add_widget(ki)
                #bv.add_widget(ki)
                
                
                print("3")
            
            
            
            for c in self.gui.rl.ids.bl_selWidToAdd.children:
                self.gui.rl.ids.bl_selWidToAdd.remove_widget(c)
            self.gui.rl.ids.bl_selWidToAdd.clear_widgets()
            self.gui.rl.ids.bl_selWidToAdd.add_widget(bl) 
            self.gui.screenChange("SelectWidgetToAdd")
            self.gui.rl.ids.bl_selWidToAdd.size = self.sw.solveScrolSize( self.gui.rl.ids.bl_selWidToAdd )
        
            
        
    def getWByName(self,name):
        for wi, w in enumerate(self.sw.widgetsTypeList):
            if name == w['name']:
                return self.sw.widgetsTypeList[wi]
        return None
    
    def getWByObj(self, obj):
        for si,s in enumerate(self.sw.wConfig):
            for wi,w in enumerate(s):
                if w['obj'] == obj:
                    return w,si,wi
        return None
    
    def on_start_addW(self,w):
        print("on_start_addW",w.text)
        wName = w.text
        self.actionType = "addW %s"%wName
        
        dw = self.getWByName(wName)
        
        
        print("working on ",dw['obj'])
        obj = dw['obj']
        self.settingUpWidget = dw
        if obj.settingsNeedIt() == False:
            print("no need for more steps ")
            self.sw.addWidgetOnScreen(dw)
        else:
            print("it need settings step !")
            
            #self.q1 = QueryPopup()
            #self.q1.size_hint = [.8,.97]
            
            
            self.bl = BoxLayout(
                orientation="vertical"
                )
            
            self.bl.add_widget(MSLabel(text="Set it up:")) 
             
            l0 = MSLabel(text="Widget settings:")
            self.bl.add_widget(l0)
            self.bl = obj.addSettingsDialogPart(self.bl)
            
            srcSett = False
            try:
                aoeuoeu = obj.wvfh
                srcSett = True
            except:
                pass
            if srcSett:
                l1 = MSLabel(text="Source settings:")
                self.bl.add_widget(l1)
                self.bl = obj.wvfh.makeSourceSettingsPart(
                    self.bl,
                    self.gui.sen.sensorsList
                    )
            print("prerun")
            #Clock.schedule_once(self.q1.run,0.1)
            #self.q1.run()
            print("postrun")
            print("0predissmiss")
            #self.q.dismiss()
            print("0postdissmiss")
            
            for c in self.gui.rl.ids.bl_setUpWid.children:
                self.gui.rl.ids.bl_setUpWid.remove_widget(c)
            self.gui.rl.ids.bl_setUpWid.clear_widgets()
            self.gui.rl.ids.bl_setUpWid.add_widget(self.bl) 
            self.gui.screenChange("SettingUpWidget")
            self.gui.rl.ids.bl_setUpWid.size = self.sw.solveScrolSize( self.gui.rl.ids.bl_setUpWid )
            
                
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
            print("wobj don't have wvfh",o['objName'])
            pass
        if srcSett:
            wvfh = obj.wvfh.getSettingsFromWidgetsToDict() 
        
        atr = obj.getAttrFromDialog()
        print("atr",atr)
        print("wvfh",wvfh)
        
        if wvfh == 0:
            print("EE - no src or chn selected !")
            return 0
        
        
        #sys.exit(9)
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
            'pos': [0.1,0.1],
            'rotation' : 0.0,
            'scale': 1.0
            })
        wi = len(self.sw.wConfig[self.sw.screen])-1
        print("-----------------------------------")
        print(self.sw.wConfig)
        self.sw.saveConfig()
        #sys.exit(9)
        
        #tScreen = self.sw.screen 
        #self.sw.rebuildWs()
        self.sw.fromWConfigBuildWidget(
            self.sw.screen,
            wi, 
            self.sw.fls[self.sw.screen]
            )
        self.sw.gui.screenChange(("Widgets%s"%self.sw.screen))
        
        
    def on_next_setup_widget(self):
        print("on_next_setup_widget")
        self.actionType = "step2"
            
    def on_start_remove(self):
        print("on_start_remove TODO")

    def startEditWizard(self):
        print("startEditWizard")
        obj = self.sw.wConfig[
            self.sw.widgetEdit['screen'] 
            ][
            self.sw.widgetEdit['wi']
            ]['obj']
        
        print("""screen {} wi {} obj{} all wConf{}""".format(
            self.sw.widgetEdit['screen'],
            self.sw.widgetEdit['wi'],
            obj,
            self.sw.wConfig[
                self.sw.widgetEdit['screen'] 
                ][
                self.sw.widgetEdit['wi']
                ]
            ))
        if obj.settingsNeedIt() == False:
            print("no need for more steps ")
            q = QueryPopup()
            q.setAction(
                "Widget edit", 
                "This widget don't have a settings :/",
                None, "OK", 
                None, None)
            q.run()
        else:
            self.actionType = 'edit'
            self.on_start_editW()
        
    def on_start_editW(self):
        print("on_start_editW")
        si = self.sw.widgetEdit['screen']
        wi = self.sw.widgetEdit['wi']
        inWConf = self.sw.wConfig[si][wi] 
        obj = inWConf['obj']
                    
        if inWConf != None:
            print("GOT Widget !",inWConf)
            #obj = inWConf['obj']

        
        bl = BoxLayout(orientation='vertical')

        bl.add_widget(MSLabel(text="Widget edit"))
        
        bl.add_widget(MSLabel(text="Widget Settings:"))
        bl = obj.addSettingsDialogPart(bl,inWConf)
        
        #sys.exit()
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
                self.gui.sen.sensorsList,
                inWConf
                )
        
        
        for c in self.gui.rl.ids.bl_EditWid.children:
            self.gui.rl.ids.bl_EditWid.remove_widget(c)
        self.gui.rl.ids.bl_EditWid.clear_widgets()
        self.gui.rl.ids.bl_EditWid.add_widget(bl) 
        self.gui.screenChange("EditWidget")
        self.gui.rl.ids.bl_EditWid.size = self.sw.solveScrolSize( 
            self.gui.rl.ids.bl_EditWid 
            )
            
        
    def on_editDoneSaveSettings(self):
        print("on_editDoneSaveSettings")
        si = self.sw.widgetEdit['screen']
        wi = self.sw.widgetEdit['wi']
        obj = self.sw.getWeObj( si, wi )
        inWConf = self.sw.wConfig[si][wi] 
        
        
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
        
        screen = self.sw.screen
        self.sw.cleanAll()
        print("inWConfig",inWConf)
        #sys.exit()
        self.sw.wConfig[si][wi]['callback'] = callback
        self.sw.wConfig[si][wi]['atr'] = atr
        self.sw.wConfig[si][wi]['valHandler'] = wvfh
        
        print("inWConfig after change!",inWConf)
        
        tScreen = self.sw.screen 
        self.sw.buildW()
        self.gui.screenChange(("Widgets%s"%tScreen))
        self.sw.updateIt()    
        
        #sys.exit()
        
        
        
        