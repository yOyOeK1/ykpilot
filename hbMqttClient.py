

import paho.mqtt.client as mqtt
import time
import _thread
import sys
from kivy.clock import Clock
from TimeHelper import TimeHelper
from senMqttTopic import senMqttTopic

class hbMqttClient:
    outBuf = []
    inBuf = []
    ready = False
    cli = None
    ff = None
    def __init__(self):
        print("hbMqttClient init gui")
        print("----------------------------------------\n"*100)
        self.ready = True
        self.inBuf = []
        self.outBuf = []
        self.makeCli()
        self.th = TimeHelper()
        
        
    def makeCli(self):
        self.cli = mqtt.Client("aaacb")
        self.cli.on_connect = self.on_connect
        self.cli.on_message = self.on_message
        
    
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.cli = client
        self.cli.subscribe("#")
        return 0
    
    def on_message(self, client, userdata, msg):
        #print("on_message")
        #print(msg.topic+" "+str(msg.payload))
        self.inBuf.append([msg.topic,msg.payload])
        return 0
    
    def pub(self, topic, msg):
        #print("hbMqttClient pub ")
        self.ready = False
        self.outBuf.append([topic,msg])
        self.ready = True
        '''print("mqc.pub on stack: out({}) in({}) self.cli{}".format(
            len(self.outBuf),
            len(self.inBuf),
            self.cli
            ))
        '''
    def hbmakeStacks(self,gui, onlyAdd = False):
        if onlyAdd == False:
            isCon = self.cli.is_connected()
            print("hbmakeStacks out({}) in({}) connect{}".format(
                len(self.outBuf),
                len(self.inBuf),
                isCon
                ))
            
            if isCon:
                while len(self.outBuf)>0:
                    m = self.outBuf[0]
                    #print("mqc.pub to broker m:",m)
                    self.cli.publish(m[0],m[1])
                    self.outBuf.pop(0)
            else:
                print("hbc not connected")
                
            
        if len(self.inBuf)>0:
            print("inBuf \nlen:{}\n[0]:{}".format(
                len(self.inBuf),
                self.inBuf[0]
                ))
            while len(self.inBuf):
                m = self.inBuf[0]
                topic = m[0]
                sTopic = topic.replace("/","o").replace(".","o").replace(" ","o").replace("_","o")
                msg = m[1]
                
                
                hbmq = gui.sen.hbmq
                item = hbmq.values.get(sTopic)
                if item == None:
                    obj = senMqttTopic(gui,sTopic)
                    hbmq.values[sTopic] = {
                        'top':topic,
                        'msg': msg,
                        'tim': self.th.getTimestamp(True),
                        'obj':obj
                        }
                    gui.sen.sensorsList.append( obj )
                    gui.sen.sensorsListStr.append(sTopic)
                    
                    print("new topic DONE"*2000)
                
                item = hbmq.values.get(sTopic)
                if item != None:
                    #print("update topic")
                    hbmq.values[sTopic]['msg'] = msg
                    hbmq.values[sTopic]['tim'] = self.th.getTimestamp(True)
                    hbmq.values[sTopic]['obj'].update(msg)
                    
                    #print("update topic DONE")
                
                self.inBuf.pop(0)
            
        
    def runIt(self,a=0,b=0):
        print("hbMqttClient.runIt")
        print(11," ->",self)
        print("self.cli",self.cli)
        #if self.cli == None:
        #    self.makeCli()
            
        #Clock.schedule_once(self.intRunIt,1)
        _thread.start_new(self.intRunIt,())
        print(12)
        #print("so mq client running")
        #sys.exit(9)
        #self.intRunIt()
        
    def intRunIt(self,a=0,bb=0):
        print("hbMqttClient.intRunIt()",a,"  b",bb)
        print("self.cli:",self.cli," self",self)
        conRes = self.cli.connect('localhost',12883,60)
        print("con:",conRes)
        self.cli.loop_start()
        while True:
            time.sleep(1)
            print("i")
        
    def mqClientStats(self):
        print("mqClientStats out({}) in({})".format(
            len(self.outBuf),
            len(self.inBuf)
            ))
            
if __name__=="__main__":
    sys.exit(1)
    print("main test")
    sys.exit(9)
    hbc = hbMqttClient()
    hbc.runIt()
    while True:
        print("i")
        time.sleep(1)
        
        
        