from QueryPopup import QueryPopup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.loader import Loader
from kivy.uix.spinner import Spinner

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
            bl.add_widget(
                Label(text="Awalable widgets to add to screen:")
                )
            wl = self.sw.getWidgetsTypeList()
            for w in wl:
                print("w",w)
                bv = BoxLayout(
                    orientation="horizontal",
                    height = self.gui.btH,
                    size_hint = [None,None]
                    )
                
                b = Button(
                    text = w['name'],
                    height = self.gui.btH,
                    size_hint = [None,None],
                    on_release=self.on_start_addW,
                    )
                bv.add_widget(b)
                
                ki = CoreImage("icons/%s"%w['thumb'])
                #bv.add_widget(ki)
                
                
                bl.add_widget(bv)
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
            obj.setGui(self.gui)
            self.sw.addWidgetOnScreen(obj)
        else:
            print("need settings step !")
            
        
        
    def on_selectSensor(self,a='',b=''):
        print("on_selectSensor",a," || ",b)
        
    def on_next_setup_widget(self):
        print("on_next_setup_widget")
        self.actionType = "step2"
            
    def on_start_remove(self):
        print("on_start_remove TODO")
        
        