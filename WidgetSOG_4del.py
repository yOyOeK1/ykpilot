from kivy.uix.widget import Widget
from kivy.core.text import Label
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

class WidgetSOG(BoxLayout):
    
    sog = StringProperty("")
    
    def setGui(self, gui):
        self.gui = gui
        
        self.up = False
        #self.setUpGui()
        
    def setUpGui(self):
        self.up = True
        print("self. type",type(self))
        self.l = Label()
        self.add_widget(self.l)
        
    def update(self, fromWho, vals):
        if self.up == False:
            self.setUpGui()
        
        if fromWho == 'gps':
            print("got gps",vals)
            self.l.text = str( round(vals['speed'],2) )