from TimeHelper import TimeHelper
from fftAnalisy import fftPlotData
import _thread


class micData:
    def __init__(self,gui):
        self.gui = gui
        self.th = TimeHelper()
        self.work = False
        
    def on_record(self,o):
        print("o.active",o.active)
        if self.work:
            self.work = False
        else:
            self.work = True
            _thread.start_new(self.runIt,())
        
        
    def runIt(self):
        import pyaudio
        import struct
        import matplotlib.pyplot as plt
        import numpy as np
        import time
        
        pyaudioDisplay = True
        
        
        mic = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 64*4
        stream = mic.open(
            format=FORMAT, 
            channels=CHANNELS, 
            rate=RATE, 
            input=True, 
            frames_per_buffer=CHUNK)
        
        reciter = 1
        dataHistory = []
        dataMem = 10
        lastTime = self.th.getTimestamp()
        recIterLast = 0
        im = np.zeros( (512,512,3), dtype=np.uint8)
        imY = 0
        imX = 0
        while self.work:
            reciter+= 1
            
            
            
            dataHistory.append( stream.read(CHUNK) )
            if len(dataHistory) > dataMem:
                dataHistory.pop(0)
            
            #print(".")
            if pyaudioDisplay and len(dataHistory)>5:
                dataHistory[-1] = np.frombuffer( dataHistory[-1], np.int16)
                
                if len(dataHistory)>3:                
                    fftPlotData(self.gui.pMic2, np.array([ *dataHistory[-1], *dataHistory[-2], *dataHistory[-3] ]))
                    #fftPlotData(self.gui.pMic1, np.array([ *dataHistory[-1], *dataHistory[-2]] ))
                    fftPlotData(self.gui.pMic, dataHistory[-1])
                #self.gui.pMic
                
            else:
                time.sleep(0.1)

            
            t = self.th.getTimestamp()
            if (t-lastTime)>1:
                print("iters in sec ",(reciter-recIterLast)," y ",imY)
                recIterLast = reciter
                lastTime = t
                
                if imY > 20:
                    imY = 0
                    print('save img')
                    from PIL import Image
                    new_img = Image.fromarray(im)
                    new_img.save("fox.png")
                
            if True:
                res = fftPlotData(None, dataHistory[-1])
                a = []
                b = []
                try:
                    for i in res:
                        a.append(i[0])
                        b.append(i[1])
                    
                    m = max(b)
                    i = b.index(m)
                    
                    if b[10] >0.5:
                        im[imY][imX][0] = 250
                        im[imY][imX][1] = 250
                        im[imY][imX][2] = 250
                except:
                    pass
                
                imX+= 1
                if imX > 274*2:
                    imX = 0
                    imY+= 1

