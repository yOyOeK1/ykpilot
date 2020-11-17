from kivy.uix.label import Label
from kivy.metrics import cm

class MyLabel(Label):
    def __init__(self,**kwargs):
        super(MyLabel,self).__init__(**kwargs)
        self.size_hint = [None,None]
        self.height = cm(1)
        