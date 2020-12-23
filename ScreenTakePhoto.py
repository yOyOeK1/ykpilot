import datetime
from kivy.lang import Builder
from kivymd.app import MDApp

kv = """
#:import XCamera kivy.garden.xcamera.XCamera

FloatLayout:
    orientation: 'vertical'

    MDIconButton:
        pos: [40, root.height-100]
        icon: 'cancel'
        on_release: app.stp.on_cancel()
        
    #MDIconButton:
    #    pos: [120, root.height-100]
    #    icon: 'cancel'
    #    on_release: app.stp.take_stap()
        
    #MDIconButton:
    #    pos: [220, root.height-100]
    #    icon: 'cancel'
    #    on_release: xcamera.restore_orientation()


    XCamera:
        id: xcamera
        on_picture_taken: app.stp.picture_taken(*args)
        
        #canvas.before:
        #    Translate:
        #        xy: self.center_x,self.center_y
        #    Rotate:
        #        angle:-90
        #        axis:0,0,1
        #    Translate:
        #        xy: -self.center_x,-self.center_y
            
        canvas:
            Color:
                rgba: 1,0,0,.5
            Line:
                points: [ self.size[0]*.5,0, self.size[0]*.5,self.size[1]*.5 ]
                width: 10

    MDBoxLayout:
        id: bl_xCam
        size_hint:[1,None]
        height: app.btH*1.5


    #BoxLayout:
    #    orientation: 'horizontal'
    #    size_hint: 1, None
    #    height: sp(50)

     
    #   Button:
    #        text: 'Set landscape'
    #        on_release: xcamera.force_landscape()

    #    Button:
    #        text: 'Restore orientation'
    #        on_release: xcamera.restore_orientation()
"""


class ScreenTakePhoto:
    
    def __init__(self, gui):
        self.gui = gui
        self.guiSetup = False
        
    def takePhoto(self, callBackOnDone, widgets = None):
        self.callOnDone = callBackOnDone
        self.screenToGoBack = self.gui.rl.current
        if self.guiSetup == False:
            self.guiSetup = True
            w = self.gui.rl.ids.fl_takPic
            self.x = Builder.load_string(kv)
            w.clear_widgets()
            w.add_widget(self.x)
            
        self.x.ids.bl_xCam.clear_widgets()
        if widgets:
            self.x.ids.bl_xCam.add_widget(widgets)
            
            
        self.x.ids.xcamera.force_landscape()
        self.gui.on_fullScreen(True)
        self.gui.rl.current = 'Take picture'
        
    def picture_taken(self, xcam=0, fileName=0, c=0):
        print("picture taken !",xcam,' fileName:',fileName,' c',c)
        self.x.ids.xcamera.restore_orientation()
        self.gui.on_fullScreen(False)
        self.callOnDone('DONE',fileName)
        self.gui.rl.current = self.screenToGoBack

    def on_cancel(self):
        print("on_cancel")
        #self.x.ids.xcamera.stop()
        self.x.ids.xcamera.restore_orientation()
        self.gui.on_fullScreen(False)
        self.callOnDone('cancel',None)
        self.gui.rl.current = self.screenToGoBack
        
    def take_stap(self):
        w = self.x.ids.xcamera
        w.export_to_png('/tmp/a.png')

class CameraApp(MDApp):
    btH = 20
    def build(self):
        return Builder.load_string(kv)

    def picture_taken(self, obj, filename):
        print('Picture taken and saved to {}'.format(filename))

if __name__ == '__main__':
    CameraApp().run()
