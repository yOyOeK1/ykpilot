

from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout


class MSLabel(Label):
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
            
            