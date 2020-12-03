from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import cm
from kivy.uix.textinput import TextInput
from MyLabel import MyLabel
#from kivymd.uix.textfield import MDTextField

class WidgetHelper:
    
    def getDialogRow(self):
        return BoxLayout(
            orientation="horizontal",
            height=cm(1),
            size_hint_y = None
            )
        
    def addDialogRow(self, bl, title, val):
        bh = self.getDialogRow()
        bh.add_widget(MyLabel(text="%s:"%title))
        ti = TextInput(text=str(val))
        #ti = MDTextField(text = str(val))
        bh.add_widget( ti )
        bl.add_widget( bh )
        return bl,ti
    