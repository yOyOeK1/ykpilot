
import sys
from kivy.clock import Clock
from kivy.core.image import Image
from kivy.graphics.texture import Texture
import numpy as np
from kivy.cache import Cache
try:
    import cv2
except:
    print("E    no cv2!")
    sys.exit(-43)
class ScreenVirtualButtons:
    
    def __init__(self,gui):
        self.gui = gui
        self.running = False
        self.cam = cv2.VideoCapture(0)
        self.tex = None
        self.objs = {
            'lighter': cv2.imread("ocv/lighter.png")#,
            #'sharpyEnd': cv2.imread('ocv/sharpyEnd.png'),
            #'pinch' : cv2.imread("ocv/pinch.png")
            }
        
        
    def on_displayNow(self):
        if self.running == False:
            self.running = True
            self.iter(0)
    def on_noMoreDisplayd(self):
        self.running = False
            
    def iter(self,a):
        #print("svb")
        r,img = self.cam.read() 
        img = cv2.flip(img,1)
        
        """
        if self.tex == None:
            s = img.shape
            self.tex = Texture.create(size=(s[0],s[1]), colorfmt='rgb')
        self.tex.blit_buffer(img, colorfmt='rgb',bufferfmt='ubyte')
        """
        
        
        
        for k in self.objs.keys():
            res = cv2.matchTemplate(img, self.objs[k], cv2.TM_CCOEFF_NORMED)
            thresh = 0.4
            loc = np.where( res >= thresh )
            w,h,_ = self.objs[k].shape
            
            for pt in zip(*loc[::-1]):
                img = cv2.putText(img, k, pt, cv2.FONT_HERSHEY_SIMPLEX,1,255,2,cv2.LINE_AA )
                img = cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
                break
            

        cv2.imwrite('/tmp/svb.png',img)
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        
        self.gui.rl.ids.iVirButCam.texture = Image('/tmp/svb.png').texture
        
        if self.running:
            Clock.schedule_once(self.iter,0.1)
        
        
        