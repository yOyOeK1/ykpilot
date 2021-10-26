from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import cm
from kivy.uix.textinput import TextInput
from MyLabel import MyLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
#from kivymd.uix.textfield import MDTextField

class WidgetHelper:
    
    def getDialogRow(self):
        return MDBoxLayout(
                orientation='horizontal',
                adaptive_height = True
                )
        '''BoxLayout(
            orientation="horizontal",
            height=cm(1),
            size_hint_y = None
            )'''
        
    def addDialogRow(self, bl, title, val, helpText = None):
        #bh = self.getDialogRow()
        #bh.add_widget(MDLabel(text="%s:"%title))
        ti = MDTextField(
            text=str(val),
            )
        ti.hint_text = "%s:"%title
        if helpText:
            ti.helper_text = helpText
            ti.helper_text_mode = "on_focus"
        bl.add_widget(ti)
        #ti = MDTextField(text = str(val))
        #bh.add_widget( ti )
        #bl.add_widget( bh )
        return bl,ti
    