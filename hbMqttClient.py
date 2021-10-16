

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
    gui = None
    
    fpsLimitUpdate = 1.0
    
    stackWorkerIn = 0
    stackWorkerOut = 0
    stackWorkerOEvent = None
    stackWorkerIEvent = None
    
    def __init__(self):
        print("hbMqttClient init gui")
        print("----------------------------------------\n"*100)
        self.ready = True
        self.inBuf = []
        self.outBuf = []
        self.makeCli()
        self.th = TimeHelper()
        
        self.stackWorkerIn = 0
        self.stackWorkerOut = 0
        self.stackWorkerOEvent = None
        self.stackWorkerIEvent = None
        
        
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
        
        #print("II - force update on load")
        if self.gui != None:
            #print("    yes")
            self.gui.sen.hbmq.iter()
            #print("    DONE")
        
        return 0
    
    def pub(self, topic, msg):
        #print("hbMqttClient pub ")
        self.ready = False
        self.outBuf.append([topic,msg])
        self.ready = True
        self.hbStackMkOut()
        '''print("mqc.pub on stack: out({}) in({}) self.cli{}".format(
            len(self.outBuf),
            len(self.inBuf),
            self.cli
            ))
        '''
        
    def hbStackMkOut(self,aa='',bb='',cc=''):
        if self.stackWorkerOut == 0:
            self.stackWorkerOut = 1
            
            #print("    OUT from clock")
            while len(self.outBuf)>0:
                self.cli.publish( self.outBuf[0][0], self.outBuf[0][1] )
                self.outBuf.pop(0)
                #print("mqc.pub to broker m:",m)
            
            self.stackWorkerOut = 0
            #print("    OUT DONE")
    
    def hbStackMkIn(self,gui, aa='',bb='',cc=''):
        
        if self.stackWorkerIn == 0:
            self.stackWorkerIn = 1
            #print("    IN from clock")
        
            if self.gui != None:
                gui = self.gui
            else:
                return 0
            
            while len(self.inBuf)>0:
                m = self.inBuf[0]
                self.inBuf.pop(0)
                topic = m[0]
                sTopic = topic.replace("/","o").replace(".","o").replace(" ","o").replace("_","o")
                sTopic = topic
                try:
                    msg = m[1].decode("ascii")
                except:
                    print("EE - IN hbMqttClient msg decode 134")
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
                    item = hbmq.values[sTopic]
                    gui.sen.sensorsList.append( obj )
                    gui.sen.sensorsListStr.append(sTopic)
                    
                    print("new topic DONE topic:{}\n\t\tmsg:{}".format(topic,msg))
                    
                if item != None:
                    #print("update topic")
                    hbmq.values[sTopic]['msg'] = msg
                    hbmq.values[sTopic]['tim'] = self.th.getTimestamp(True)
                    hbmq.values[sTopic]['obj'].update(msg)
                    
                    #print("update topic DONE")
                
                
                if sTopic[-4:] == "/stk":
                    #print("seatalk ????",msg)
                    senSeaTalPar = gui.sen.nodeMcu
                    #print("------ START")
                    senSeaTalPar.seatalkParse(msg)
                    #print("------ END")
                
                
            self.stackWorkerIn = 0
            #print("    IN DONE")
        
        
    def hbmakeStacks(self,gui, onlyAdd = False):
        self.gui = gui
        if 0:
            print("hbmakeStacks o({}) i({}) od:{}".format(
                len(self.outBuf),
                len(self.inBuf),
                onlyAdd
                ))
            print("o:",self.outBuf)
            print("\ni:",self.inBuf)
        if onlyAdd == False:
            self.hbStackMkOut()
            
        self.hbStackMkIn(gui)        
        
            
        
    def runIt(self,a=0,b=0):
        print("hbMqttClient.runIt")
        print(11," ->",self)
        print("self.cli",self.cli)
        #if self.cli == None:
        #    self.makeCli()
            
        #Clock.schedule_once(self.intRunIt,1)
        _thread.start_new(self.intRunIt,())
        #print(12)
        #print("so mq client running")
        #sys.exit(9)
        #self.intRunIt()
        
    def intRunIt(self,a=0,bb=0):
        print("hbMqttClient.intRunIt()",a,"  b",bb)
        print("self.cli:",self.cli," self",self)
        conRes = self.cli.connect('localhost',12883,60)
        print("con:",conRes)
        self.cli.loop_start()
        print("hbMqttClient inRunIt DONE")
        
    def hbClientStats(self):
        #print("hbClientStats")
        try:
            isCon = self.cli.is_connected()
            if isCon == False:
                print("EE - hbClientStats cli is not connected !")
            return True
        except:
            isCon = "no Client obj"
            return False
        
            
if __name__=="__main__":
    sys.exit(1)
    print("main test")
    sys.exit(9)
    hbc = hbMqttClient()
    hbc.runIt()
    while True:
        print("i")
        time.sleep(1)
        
        
        