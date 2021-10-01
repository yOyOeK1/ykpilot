

import paho.mqtt.client as mqtt
import time
import _thread

class hbMqttClient:
    buf = []
    ready = False
    def __init__(self, gui = None):
        self.gui = gui
        self.ready = True
        self.buf = []
    
    
    def pub(self, topic, msg):
        #print("hbMqttClient pub ")
        self.ready = False
        self.buf.append([topic,msg])
        self.ready = True
        #print("    on stack:",len(self.buf))
    
    def runIt(self,a=0,b=0):
        _thread.start_new(self.intRunIt,())
        
    def intRunIt(self,a=0,b=0):
        print("hbMqttClient.runIt()")
        self.c = mqtt.Client()
        i = 0
        c = 0
        while True:
            print("connect....",c)
            #try:
            self.c.connect('localhost',12883)
        
            while True:
                print("hbMqttClient connect",c," iter",i)
                if len(self.buf) > 0 and self.ready:
                    #print("hbMqttClient pub ",self.buf[0])
                    for m in self.buf:
                        b = self.buf[0]
                        self.c.publish(str(b[0]),str(b[1]))
                        self.buf.pop(0)
                
                i+=1
                time.sleep(1)
            #except:
            #    print("EE - hbMqttClient")
            #    time.sleep(1)
                
            
            c+=1
            i=0
            
if __name__=="__main__":
    print("main test")
    hbc = hbMqttClient()
    hbc.runIt()
    while True:
        print("i")
        time.sleep(1)
        